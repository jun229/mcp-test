"""
Job Description Generation Module

RAG-based job description generation using vector similarity search.
Focused on extracting patterns from real job descriptions stored in Supabase.
"""

import re
from typing import Dict, List


def extract_responsibilities_from_chunks(similar_chunks: List[dict]) -> List[str]:
    """Extract responsibility patterns from similar job descriptions using RAG"""
    if not similar_chunks:
        return []
    
    responsibilities = []
    
    for chunk in similar_chunks[:5]:  # Use top 5 most similar
        content = chunk.get('content', '')
        
        # Find the Responsibilities section
        resp_match = re.search(r'Responsibilities:\s*\n(.*?)(?=\n\n[A-Z]|\nRequirements:|\nNice to have:|\Z)', 
                              content, re.DOTALL | re.IGNORECASE)
        
        if resp_match:
            resp_section = resp_match.group(1).strip()
            # Split by lines and clean up
            lines = resp_section.split('\n')
            for line in lines:
                line = line.strip()
                if line and len(line) > 15 and len(line) < 200:
                    # Remove any leading bullets or numbers
                    cleaned = re.sub(r'^[-•*\d+\.\s]+', '', line).strip()
                    if cleaned:
                        responsibilities.append(cleaned)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_responsibilities = []
    for resp in responsibilities:
        if resp.lower() not in seen:
            seen.add(resp.lower())
            unique_responsibilities.append(resp)
    
    return unique_responsibilities[:6]  # Return top 6


def extract_requirements_from_chunks(similar_chunks: List[dict], user_requirements: List[str]) -> List[str]:
    """Extract requirement patterns from similar job descriptions"""
    if not similar_chunks:
        return user_requirements
    
    # Start with user-provided requirements
    all_requirements = user_requirements.copy()
    
    extracted_reqs = []
    for chunk in similar_chunks[:3]:
        content = chunk.get('content', '')
        
        # Find the Requirements section
        req_match = re.search(r'Requirements:\s*\n(.*?)(?=\n\n[A-Z]|\nNice to have:|\nMinimum|\Z)', 
                             content, re.DOTALL | re.IGNORECASE)
        
        if req_match:
            req_section = req_match.group(1).strip()
            # Split by lines and clean up
            lines = req_section.split('\n')
            for line in lines:
                line = line.strip()
                if line and len(line) > 10 and len(line) < 150:
                    # Remove any leading bullets or numbers
                    cleaned = re.sub(r'^[-•*\d+\.\s]+', '', line).strip()
                    if cleaned:
                        extracted_reqs.append(cleaned)
    
    # Add unique extracted requirements
    seen = {req.lower() for req in all_requirements}
    for req in extracted_reqs:
        if req.lower() not in seen:
            all_requirements.append(req)
            seen.add(req.lower())
    
    return all_requirements[:8]  # Limit to 8 total


def extract_nice_to_haves_from_chunks(similar_chunks: List[dict]) -> List[str]:
    """Extract nice-to-have patterns from similar job descriptions"""
    if not similar_chunks:
        return []
    
    nice_to_haves = []
    
    for chunk in similar_chunks[:3]:
        content = chunk.get('content', '')
        
        # Find the Nice to have section
        nice_match = re.search(r'Nice to have:\s*\n(.*?)(?=\n\n[A-Z]|\nMinimum|\Z)', 
                              content, re.DOTALL | re.IGNORECASE)
        
        if nice_match:
            nice_section = nice_match.group(1).strip()
            # Split by lines and clean up
            lines = nice_section.split('\n')
            for line in lines:
                line = line.strip()
                if line and len(line) > 10 and len(line) < 120:
                    # Remove any leading bullets or numbers
                    cleaned = re.sub(r'^[-•*\d+\.\s]+', '', line).strip()
                    if cleaned:
                        nice_to_haves.append(cleaned)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_nice_to_haves = []
    for item in nice_to_haves:
        if item.lower() not in seen:
            seen.add(item.lower())
            unique_nice_to_haves.append(item)
    
    return unique_nice_to_haves[:4]  # Limit to 4


def extract_intro_context(similar_chunks: List[dict], title: str, department: str) -> str:
    """Generate intro based on patterns from similar job descriptions"""
    if not similar_chunks:
        return f"We are seeking a talented {title} to join our {department} team."
    
    # Look for intro paragraphs (text before "Responsibilities:")
    intro_patterns = []
    for chunk in similar_chunks[:2]:  # Use top 2
        content = chunk.get('content', '')
        
        # Extract text before "Responsibilities:"
        intro_match = re.search(r'^(.*?)(?=Responsibilities:)', content, re.DOTALL | re.IGNORECASE)
        
        if intro_match:
            intro_text = intro_match.group(1).strip()
            # Split into sentences and find good ones
            sentences = re.split(r'[.!?]+', intro_text)
            for sentence in sentences:
                sentence = sentence.strip()
                if (len(sentence) > 30 and len(sentence) < 300 and 
                    any(word in sentence.lower() for word in ['looking', 'seeking', 'join', 'team', 'role', 'position', 'opportunity'])):
                    intro_patterns.append(sentence)
    
    if intro_patterns:
        # Use the best intro pattern
        best_intro = intro_patterns[0].strip()
        # Clean up any HTML entities
        best_intro = re.sub(r'&[a-zA-Z]+;', '', best_intro)
        return best_intro
    
    return f"We are seeking a talented {title} to join our {department} team. This is an excellent opportunity to make a significant impact in a dynamic environment."


def generate_jd(title: str, department: str, requirements: List[str], similar_chunks: List[dict]) -> Dict:
    """
    Generate job description using RAG - extracting patterns from similar jobs
    
    Args:
        title: Job title
        department: Department name  
        requirements: User-provided requirements
        similar_chunks: Similar job descriptions from vector search
        
    Returns:
        Structured job description dictionary
    """
    
    # Extract content from similar jobs using RAG
    rag_responsibilities = extract_responsibilities_from_chunks(similar_chunks)
    rag_requirements = extract_requirements_from_chunks(similar_chunks, requirements)
    rag_nice_to_haves = extract_nice_to_haves_from_chunks(similar_chunks)
    intro = extract_intro_context(similar_chunks, title, department)
    
    return {
        "title": title,
        "department": department,
        "sections": {
            "intro": intro,
            "responsibilities": rag_responsibilities,
            "requirements": rag_requirements,
            "nice_to_haves": rag_nice_to_haves
        },
        "metadata": {
            "generated": True,
            "similar_jobs_used": len(similar_chunks),
            "generation_method": "rag_extraction"
        }
    }