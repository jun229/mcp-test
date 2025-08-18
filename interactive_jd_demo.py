#!/usr/bin/env python3
"""
Interactive Job Description Generator Demo - Vercel API Version

A terminal script that demonstrates interactive job description generation
using the deployed Vercel API for vector database search.

Run with: python3 interactive_jd_demo.py
"""

import os
import sys
import json
import textwrap
import requests
from typing import Dict, List, Optional

def safe_exit(code=0):
    """Exit safely."""
    sys.exit(code)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_header(current_job=""):
    print("=" * 70)
    print("🎯 INTERACTIVE JOB DESCRIPTION GENERATOR (Vercel API)")
    if current_job:
        print(f"📋 Current Job: {current_job}")
    print("=" * 70)
    print()

def get_user_choice(prompt: str, choices: List[str]) -> int:
    """Display choices and get user selection"""
    print(prompt)
    print()
    for i, choice in enumerate(choices, 1):
        print(f"{i}. {choice}")
    print()
    
    while True:
        try:
            choice = int(input("Enter your choice (number): "))
            if 1 <= choice <= len(choices):
                return choice - 1
            else:
                print(f"Please enter a number between 1 and {len(choices)}")
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            safe_exit(0)

def get_user_input(prompt: str, required: bool = True) -> str:
    """Get user input with optional requirement check"""
    while True:
        try:
            value = input(prompt).strip()
            if required and not value:
                print("This field is required. Please enter a value.")
                continue
            return value
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            safe_exit(0)

def get_list_input(prompt: str, min_items: int = 1) -> List[str]:
    """Get comma-separated list input from user"""
    while True:
        try:
            print(prompt)
            print("Enter items separated by commas:")
            value = input("> ").strip()
            if not value and min_items > 0:
                print(f"Please enter at least {min_items} item(s).")
                continue
            
            items = [item.strip() for item in value.split(',') if item.strip()]
            if len(items) < min_items:
                print(f"Please enter at least {min_items} item(s).")
                continue
            
            return items
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            safe_exit(0)

def call_vercel_api(endpoint: str, data: dict) -> dict:
    """Call the Vercel API endpoint"""
    url = f"{VERCEL_API_URL}/api/{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"API call failed: {e}")

def generate_job_description(title: str, department: str, requirements: List[str]) -> dict:
    """Generate a job description using the Vercel API"""
    print("🔄 Calling Vercel API to generate job description...")
    
    try:
        response = call_vercel_api("search-and-generate", {
            "title": title,
            "department": department,
            "requirements": requirements
        })
        
        # Parse the JSON result from the API
        result_str = response.get("result", "{}")
        if isinstance(result_str, str):
            result = json.loads(result_str)
        else:
            result = result_str
            
        return result
    except Exception as e:
        raise Exception(f"Failed to generate job description: {e}")

def ingest_job_description(content: str) -> str:
    """Add a job description to the database"""
    print("💾 Adding job description to database...")
    
    try:
        response = call_vercel_api("ingest", {
            "content": content
        })
        return response.get("result", "Success")
    except Exception as e:
        raise Exception(f"Failed to ingest job description: {e}")

def display_job_description(job_desc: Dict):
    """Display a job description in formatted style"""
    print(f"\n{'='*70}")
    
    if isinstance(job_desc, dict) and 'generated_jd' in job_desc:
        # This is the API response format
        jd = job_desc['generated_jd']
        similar_count = job_desc.get('similar_jobs_found', 0)
        
        print(f"📄 {jd.get('title', 'Unknown')} - {jd.get('department', 'Unknown')}")
        print(f"🔍 Found {similar_count} similar jobs for reference")
        print(f"{'='*70}")
        
        print(f"\n{'🎯 JOB DESCRIPTION CONTENT':^70}")
        print(f"{'─'*70}")
        
        sections = jd.get('sections', {})
        
        if sections.get('intro'):
            print(f"\n**Job Description:**")
            print(f"{sections['intro'].strip()}")
        
        if sections.get('responsibilities'):
            print(f"\n**Key Responsibilities:**")
            for resp in sections['responsibilities']:
                print(f"• {resp}")
        
        if sections.get('requirements'):
            print(f"\n**Requirements:**")
            for req in sections['requirements']:
                print(f"• {req}")
        
        if sections.get('nice_to_haves'):
            print(f"\n**Nice to Have:**")
            for nice in sections['nice_to_haves']:
                print(f"• {nice}")
        
        # Show similar jobs reference
        if job_desc.get('similar_jobs'):
            print(f"\n**📚 Referenced Similar Jobs:**")
            for i, similar in enumerate(job_desc['similar_jobs'], 1):
                content_preview = similar.get('content', '')[:100]
                print(f"{i}. {content_preview}...")
    
    else:
        # Fallback for other formats
        print(f"📄 Job Description Result")
        print(f"{'='*70}")
        print(json.dumps(job_desc, indent=2))
    
    print(f"\n{'─'*70}")

def test_api_connection():
    """Test if the Vercel API is accessible"""
    try:
        response = requests.get(f"{VERCEL_API_URL}/health", timeout=10)
        return response.status_code == 200
    except:
        return False

def main():
    """Main demo function"""
    try:
        clear_screen()
        display_header()
        
        print("🚀 Testing connection to Vercel API...")
        if not test_api_connection():
            print("❌ Cannot connect to Vercel API. Please check:")
            print("   1. The API URL is correct")
            print("   2. The API is deployed and running")
            print("   3. Your internet connection")
            return
        
        print("✅ Connected to Vercel API successfully!")
        print("\n👋 Welcome to the Interactive Job Description Generator!")
        print("This tool creates professional job descriptions using AI and vector search.\n")
        
        # Store current job information
        current_job = {}
        generated_jobs = []
        
        # Main loop
        while True:
            clear_screen()
            current_job_str = ""
            if current_job and isinstance(current_job, dict):
                if 'generated_jd' in current_job:
                    jd = current_job['generated_jd']
                    current_job_str = f"{jd.get('title', '')} - {jd.get('department', '')}"
                else:
                    current_job_str = f"{current_job.get('title', '')} - {current_job.get('department', '')}"
            
            display_header(current_job_str)
            
            choices = [
                "🆕 Create new job description",
                "💾 Add job description to database", 
                "📋 View current job description",
                "📚 View generated jobs history",
                "💾 Export job description",
                "❌ Exit"
            ]
            
            choice = get_user_choice("What would you like to do?", choices)
            
            # Create new job description
            if choice == 0:
                clear_screen()
                display_header()
                print("Creating a new job description...\n")
                
                prompt = textwrap.dedent("""\
                    Department (e.g., choose from):
                    - Engineering
                    - Data Science
                    - Product Management
                    - Design
                    - Business Development
                    - Business Operations & Strategy
                    - People
                    - Marketing
                    - Customer Experience
                    - Communications
                    - Legal & Policy
                    - Research
                Enter your department: """)
                
                # Get basic information
                job_title = get_user_input("Job Title (e.g., 'Senior Software Engineer'): ")
                department = get_user_input(prompt)
                
                print(f"\n✅ Job: {job_title} in {department}")
                
                # Get requirements
                requirements = get_list_input("\n📋 Key Requirements:")
                print(f"Requirements: {', '.join(requirements)}")
                
                print(f"\n🚀 Generating job description for {job_title}...")
                
                try:
                    job_desc = generate_job_description(job_title, department, requirements)
                    current_job = job_desc
                    generated_jobs.append(job_desc)
                    
                    print("\n✅ Job description generated successfully!")
                    display_job_description(job_desc)
                    
                except Exception as e:
                    print(f"❌ Error generating job description: {e}")
                
                input("\nPress Enter to continue...")
            
            # Add job description to database
            elif choice == 1:
                clear_screen()
                display_header()
                print("💾 Adding job description to database...\n")
                
                content = get_user_input("Enter the job description content to add to the database:\n> ")
                
                try:
                    result = ingest_job_description(content)
                    print(f"\n✅ {result}")
                except Exception as e:
                    print(f"❌ Error adding to database: {e}")
                
                input("\nPress Enter to continue...")
            
            # View current job description
            elif choice == 2:
                if not current_job:
                    print("\nNo current job description. Please create one first.")
                    input("Press Enter to continue...")
                    continue
                
                clear_screen()
                display_header()
                print("📋 Current Job Description\n")
                display_job_description(current_job)
                input("\nPress Enter to continue...")
            
            # View generated jobs history
            elif choice == 3:
                clear_screen()
                display_header()
                print("📚 Generated Jobs History\n")
                
                if not generated_jobs:
                    print("No jobs generated yet.")
                else:
                    for i, job in enumerate(generated_jobs, 1):
                        if isinstance(job, dict) and 'generated_jd' in job:
                            jd = job['generated_jd']
                            print(f"{i}. {jd.get('title', 'Unknown')} - {jd.get('department', 'Unknown')}")
                        else:
                            print(f"{i}. Job {i}")
                        print("   (AI Generated via Vercel API)")
                        print()
                    
                    view_choice = get_user_input(f"\nEnter job number to view (1-{len(generated_jobs)}, or press Enter to skip): ", required=False)
                    if view_choice and view_choice.isdigit():
                        job_num = int(view_choice) - 1
                        if 0 <= job_num < len(generated_jobs):
                            display_job_description(generated_jobs[job_num])
                
                input("\nPress Enter to continue...")
            
            # Export job description
            elif choice == 4:
                if not current_job:
                    print("\n⚠️  No current job to export. Please create a job description first.")
                    input("Press Enter to continue...")
                    continue
                
                clear_screen()
                display_header()
                print("💾 Exporting job description...\n")
                
                # Generate filename
                if isinstance(current_job, dict) and 'generated_jd' in current_job:
                    jd = current_job['generated_jd']
                    title = jd.get('title', 'job_description')
                else:
                    title = 'job_description'
                
                filename = f"{title.replace(' ', '_').lower()}_job_description.json"
                
                try:
                    with open(filename, 'w') as f:
                        json.dump(current_job, f, indent=2)
                    print(f"✅ Job description exported to: {filename}")
                    
                    # Also create a readable text version
                    text_filename = filename.replace('.json', '.txt')
                    with open(text_filename, 'w') as f:
                        if isinstance(current_job, dict) and 'generated_jd' in current_job:
                            jd = current_job['generated_jd']
                            f.write(f"{jd.get('title', 'Job')} - {jd.get('department', 'Department')}\n")
                            f.write("=" * 70 + "\n\n")
                            
                            f.write("🎯 JOB DESCRIPTION CONTENT (Ready to Post)\n")
                            f.write("─" * 70 + "\n\n")
                            
                            sections = jd.get('sections', {})
                            
                            if sections.get('intro'):
                                f.write(f"Job Description:\n{sections['intro'].strip()}\n\n")
                            
                            if sections.get('responsibilities'):
                                f.write("Key Responsibilities:\n")
                                for resp in sections['responsibilities']:
                                    f.write(f"• {resp}\n")
                                f.write("\n")
                            
                            if sections.get('requirements'):
                                f.write("Requirements:\n")
                                for req in sections['requirements']:
                                    f.write(f"• {req}\n")
                                f.write("\n")
                            
                            if sections.get('nice_to_haves'):
                                f.write("Nice to Have:\n")
                                for nice in sections['nice_to_haves']:
                                    f.write(f"• {nice}\n")
                            
                            f.write("\n" + "─" * 70 + "\n")
                        else:
                            f.write("Job Description\n")
                            f.write("=" * 70 + "\n\n")
                            f.write(json.dumps(current_job, indent=2))
      
                    print(f"✅ Readable version exported to: {text_filename}")
                    
                except Exception as e:
                    print(f"❌ Error exporting: {e}")
                
                input("\nPress Enter to continue...")
            
            elif choice == 5:  # Exit
                print("\n👋 Thanks for using the Job Description Generator!")
                print("🚀 Your generated job descriptions are ready for use!")
                print("🌐 Powered by Vercel API")
                break
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main() 