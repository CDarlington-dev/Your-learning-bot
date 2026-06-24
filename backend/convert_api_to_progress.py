"""
Convert Credly API output to user progress format for recommendations.
"""

import json

def convert_api_to_progress(api_file, catalog_file='backend/data/course_catalog.json'):
    """
    Convert API badge data to user progress format.
    
    Args:
        api_file: Path to badges_api_*.json file
        catalog_file: Path to course catalog
    
    Returns:
        Progress data dictionary
    """
    # Load API data
    with open(api_file, 'r', encoding='utf-8') as f:
        api_badges = json.load(f)
    
    # Load catalog
    with open(catalog_file, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    
    # Create catalog mapping
    catalog_map = {}
    for course in catalog['courses']:
        normalized_name = course['badge_name'].lower().strip()
        catalog_map[normalized_name] = course
    
    # Match badges
    matched_badges = []
    unmatched_badges = []
    
    for api_badge in api_badges:
        badge_name = api_badge.get('badge_name', '').strip()
        normalized_name = badge_name.lower().strip()
        
        if normalized_name in catalog_map:
            catalog_course = catalog_map[normalized_name]
            matched_badges.append({
                'id': catalog_course['id'],
                'badge_name': catalog_course['badge_name'],
                'level': catalog_course['level'],
                'earned_date': api_badge.get('earned_date', ''),
                'l1_header': catalog_course.get('l1_header'),
                'l2_category': catalog_course.get('l2_category'),
                'l3_category': catalog_course.get('l3_category')
            })
        else:
            unmatched_badges.append(badge_name)
    
    progress_data = {
        'completed_badges': matched_badges,
        'completed_ids': [b['id'] for b in matched_badges],
        'unmatched_badges': unmatched_badges,
        'total_completed': len(matched_badges),
        'total_unmatched': len(unmatched_badges)
    }
    
    return progress_data

def main():
    """Convert API output to progress format."""
    import sys
    
    if len(sys.argv) > 1:
        api_file = sys.argv[1]
    else:
        api_file = 'backend/output/badges_api_christopher-darlington.json'
    
    print(f"Converting {api_file} to progress format...")
    
    try:
        progress_data = convert_api_to_progress(api_file)
        
        # Save progress file
        import os
        os.makedirs('backend/output', exist_ok=True)
        output_file = api_file.replace('badges_api_', 'user_progress_')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Matched {progress_data['total_completed']} badges to catalog")
        if progress_data['total_unmatched'] > 0:
            print(f"⚠ {progress_data['total_unmatched']} badges not found in catalog")
            print("\nUnmatched badges (first 10):")
            for badge in progress_data['unmatched_badges'][:10]:
                print(f"  - {badge}")
        
        print(f"\n✓ Saved to {output_file}")
        print(f"\nNow run: python3 recommend_courses.py {output_file}")
        
    except FileNotFoundError:
        print(f"Error: File '{api_file}' not found")
        sys.exit(1)

if __name__ == '__main__':
    main()

# Made with Bob
