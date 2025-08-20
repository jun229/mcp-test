"""
Cohere Reranking Module

Handles large-scale document reranking with Cohere API.
Optimized for cost and performance with 15k+ documents.
"""

import os
import cohere
import math
from typing import List, Dict, Optional
from datetime import datetime
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CohereReranker:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Cohere client"""
        self.api_key = api_key or os.getenv("COHERE_API_KEY")
        if not self.api_key:
            raise ValueError("COHERE_API_KEY environment variable required")
        
        self.client = cohere.Client(self.api_key)
        
        # Cohere rerank limits
        self.MAX_BATCH_SIZE = 1000  # Cohere's max per request
        self.MAX_DOC_LENGTH = 512   # Max tokens per document
        
    def truncate_document(self, text: str, max_length: int = 512) -> str:
        """Truncate document to fit Cohere limits"""
        # Simple truncation - keep first part which usually has key info
        words = text.split()
        if len(words) <= max_length:
            return text
        return ' '.join(words[:max_length]) + '...'
    
    async def rerank_batch(self, query: str, documents: List[Dict], top_k: int = None) -> List[Dict]:
        """Rerank a single batch of documents"""
        if not documents:
            return []
                
        # Prepare documents for Cohere
        doc_texts = []
        for doc in documents:
            content = doc.get('content', '')
            truncated = self.truncate_document(content, self.MAX_DOC_LENGTH)
            doc_texts.append(truncated)
        
        batch_size = len(doc_texts)
        actual_top_k = min(top_k or batch_size, batch_size)
        
        try:
            logger.info(f"Reranking batch of {batch_size} documents, returning top {actual_top_k}")
            
            response = self.client.rerank(
                model='rerank-english-v3.0',  # Latest model
                query=query,
                documents=doc_texts,
                top_k=actual_top_k,
                return_documents=False  # Save bandwidth, we have originals
            )
            
            # Map results back to original documents
            reranked_docs = []
            for result in response.results:
                original_doc = documents[result.index].copy()
                original_doc['cohere_score'] = result.relevance_score
                original_doc['rerank_position'] = len(reranked_docs) + 1
                reranked_docs.append(original_doc)
                
            logger.info(f"Successfully reranked {len(reranked_docs)} documents")
            return reranked_docs
            
        except Exception as e:
            logger.error(f"Cohere reranking failed: {e}")
            # Fallback: return original documents with similarity scores
            return documents[:actual_top_k]
    
    async def rerank_large_corpus(
        self, 
        query: str, 
        documents: List[Dict], 
        final_top_k: int = 5,
        pre_filter_top_k: int = 1000
    ) -> List[Dict]:
        """
        Handle large document corpus reranking efficiently
        
        Strategy:
        1. Pre-filter to top N by vector similarity 
        2. Batch rerank the filtered set
        3. Return final top K
        """
        
        logger.info(f"Processing {len(documents)} documents -> {pre_filter_top_k} -> {final_top_k}")
        
        if len(documents) == 0:
            return []
        
        # Step 1: Pre-filter by vector similarity if we have too many docs
        if len(documents) > pre_filter_top_k:
            logger.info(f"Pre-filtering {len(documents)} -> {pre_filter_top_k} by similarity")
            # Sort by vector similarity first
            documents = sorted(
                documents, 
                key=lambda x: x.get('similarity', 0), 
                reverse=True
            )[:pre_filter_top_k]
        
        # Step 2: Batch process through Cohere if still large
        if len(documents) <= self.MAX_BATCH_SIZE:
            # Single batch
            return await self.rerank_batch(query, documents, final_top_k)
        else:
            # Multiple batches
            return await self._rerank_multiple_batches(query, documents, final_top_k)
    
    async def _rerank_multiple_batches(self, query: str, documents: List[Dict], final_top_k: int) -> List[Dict]:
        """Handle multiple batch reranking"""
        
        # Calculate batch sizes
        num_batches = math.ceil(len(documents) / self.MAX_BATCH_SIZE)
        per_batch_top_k = max(10, final_top_k * 2)  # Get more per batch, then final filter
        
        logger.info(f"Processing {num_batches} batches, {per_batch_top_k} results per batch")
        
        all_reranked = []
        
        # Process each batch
        for i in range(num_batches):
            start_idx = i * self.MAX_BATCH_SIZE
            end_idx = min((i + 1) * self.MAX_BATCH_SIZE, len(documents))
            batch = documents[start_idx:end_idx]
            
            logger.info(f"Processing batch {i+1}/{num_batches} ({len(batch)} docs)")
            
            batch_results = await self.rerank_batch(query, batch, per_batch_top_k)
            all_reranked.extend(batch_results)
            
            # Small delay to avoid rate limits
            await asyncio.sleep(0.1)
        
        # Final ranking across all batch results
        logger.info(f"Final ranking of {len(all_reranked)} documents")
        final_results = sorted(
            all_reranked, 
            key=lambda x: x.get('cohere_score', 0), 
            reverse=True
        )[:final_top_k]
        
        return final_results

    def build_enhanced_query(
        self, 
        title: str, 
        department: str, 
        requirements: List[str],
        current_year: int = 2024
    ) -> str:
        """Build contextually rich query for better reranking"""
        
        # Add temporal context
        temporal_context = f"Current {current_year} job posting"
        
        # Enhanced requirements context
        if requirements:
            req_context = f"Must have: {', '.join(requirements)}"
        else:
            req_context = "Open to various technical backgrounds"
        
        query = f"""
        {temporal_context} for {title} position in {department} department.
        {req_context}
        
        Looking for job descriptions with:
        - Modern development practices and tools
        - Current market compensation and benefits  
        - Recent technology requirements
        - Relevant experience levels and qualifications
        
        Prioritize recent, well-structured job descriptions that match the role requirements.
        """
        
        return query.strip()

# Convenience function for easy integration
async def rerank_job_descriptions(
    title: str,
    department: str, 
    requirements: List[str],
    similar_chunks: List[Dict],
    final_count: int = 5
) -> List[Dict]:
    """
    Easy-to-use function for reranking job descriptions
    
    Args:
        title: Job title
        department: Department name
        requirements: List of requirements
        similar_chunks: Documents from vector search
        final_count: Number of final results wanted
        
    Returns:
        Reranked documents with Cohere scores
    """
    
    if not similar_chunks:
        return []
    
    try:
        reranker = CohereReranker()
        
        # Build enhanced query
        query = reranker.build_enhanced_query(title, department, requirements)
        
        # Rerank
        reranked = await reranker.rerank_large_corpus(
            query=query,
            documents=similar_chunks,
            final_top_k=final_count,
            pre_filter_top_k=min(1000, len(similar_chunks))  # Cost optimization
        )
        
        logger.info(f"✅ Reranking complete: {len(similar_chunks)} -> {len(reranked)} documents")
        
        return reranked
        
    except Exception as e:
        logger.error(f"Reranking failed, returning original results: {e}")
        return similar_chunks[:final_count]

# Cost estimation helper
def estimate_rerank_cost(num_documents: int, cost_per_1k: float = 1.0) -> float:
    """Estimate Cohere reranking cost"""
    return (num_documents / 1000) * cost_per_1k

if __name__ == "__main__":
    # Quick test
    print("Cohere Reranker module loaded successfully")
    print(f"Estimated cost for 15k documents: ${estimate_rerank_cost(15000):.2f}")
