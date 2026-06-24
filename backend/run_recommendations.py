#!/usr/bin/env python3
"""
Main workflow script to generate course recommendations.
Runs the complete pipeline from Credly API to recommendations.
"""

import sys
import os
import subprocess

def run_command(cmd, description):
    """Run a command and print status."""
    print(f"\n{'='*80}")
    print(f"STEP: {description}")
    print(f"{'='*80}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ Error in: {description}")
        sys.exit(1)
    return result.returncode

def main():
    """Run the complete recommendation pipeline."""
    username = sys.argv[1] if len(sys.argv) > 1 else 'christopher-darlington.bc0d040c'
    
    print(f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                    IBM BADGE RECOMMENDATION SYSTEM                         ║
║                         YourLearningBot v1.0                               ║
╚════════════════════════════════════════════════════════════════════════════╝

User: {username}
""")
    
    # Step 1: Fetch badges from Credly API
    run_command(
        f"python3 backend/credly_api.py",
        "Fetching badges from Credly API"
    )
    
    # Step 2: Convert API output to progress format
    api_file = f"badges_api_{username.split('.')[0]}.json"
    run_command(
        f"python3 backend/convert_api_to_progress.py backend/output/{api_file}",
        "Converting badges to progress format"
    )
    
    # Step 3: Generate recommendations
    progress_file = f"user_progress_{username.split('.')[0]}.json"
    run_command(
        f"python3 backend/recommend_courses.py backend/output/{progress_file}",
        "Generating personalized recommendations"
    )
    
    print(f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                           ✅ COMPLETE!                                     ║
╚════════════════════════════════════════════════════════════════════════════╝

Your recommendations are ready in the backend/output/ directory:
  📊 recommendations.csv  - Spreadsheet with all recommendations
  📄 recommendations.txt  - Human-readable top recommendations
  📦 recommendations.json - Complete data for programmatic use

Next steps:
  1. Open backend/output/recommendations.csv in Excel/Google Sheets
  2. Sort by score to see your best matches
  3. Click the IBM links to enroll in courses!
""")

if __name__ == '__main__':
    main()

# Made with Bob
