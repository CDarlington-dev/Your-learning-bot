"""
Course recommendation algorithm based on user progress and prerequisites.
Recommends next courses the user should take based on completed badges.
"""

import json
import csv
from collections import defaultdict
from datetime import datetime

def load_catalog(catalog_file='backend/data/course_catalog.json'):
    """Load the course catalog."""
    with open(catalog_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_user_progress(progress_file):
    """Load user progress data."""
    with open(progress_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_prerequisites_met(course, completed_ids):
    """
    Check if all prerequisites for a course are met.
    
    Args:
        course: Course dictionary from catalog
        completed_ids: List of completed badge IDs
    
    Returns:
        tuple: (all_met: bool, missing_prereqs: list, or_group_met: bool)
    """
    prereqs = course.get('prerequisites', [])
    
    if not prereqs:
        return True, [], None
    
    # Check for OR groups
    or_groups = defaultdict(list)
    regular_prereqs = []
    
    for prereq in prereqs:
        if 'group' in prereq:
            or_groups[prereq['group']].append(prereq['id'])
        else:
            regular_prereqs.append(prereq['id'])
    
    # Check regular prerequisites
    missing_regular = [p for p in regular_prereqs if p not in completed_ids]
    
    # Check OR groups (at least one from each group must be completed)
    or_groups_met = True
    missing_or_groups = []
    
    for group_name, group_ids in or_groups.items():
        if not any(gid in completed_ids for gid in group_ids):
            or_groups_met = False
            missing_or_groups.append(group_name)
    
    all_met = (len(missing_regular) == 0) and or_groups_met
    
    return all_met, missing_regular, or_groups_met

def get_recommendations(user_progress_file, catalog_file='backend/data/course_catalog.json', max_recommendations=10):
    """
    Generate course recommendations for a user.
    
    Args:
        user_progress_file: Path to user progress JSON
        catalog_file: Path to course catalog JSON
        max_recommendations: Maximum number of recommendations to return
    
    Returns:
        Dictionary with recommendations organized by priority
    """
    catalog = load_catalog(catalog_file)
    user_progress = load_user_progress(user_progress_file)
    
    completed_ids = set(user_progress['completed_ids'])
    completed_badges = user_progress['completed_badges']
    
    # Analyze user's learning patterns
    user_platforms = defaultdict(int)
    user_categories = defaultdict(int)
    user_levels = defaultdict(int)
    
    for badge in completed_badges:
        user_platforms[badge.get('l1_header', 'Unknown')] += 1
        user_categories[badge.get('l2_category', 'Unknown')] += 1
        user_levels[badge.get('level', 0)] += 1
    
    # Find recommended courses
    recommendations = {
        'next_level': [],      # Direct next level in current paths
        'new_paths': [],       # New L1 courses to start new paths
        'parallel': [],        # Same level, different category
        'advanced': []         # Higher level courses with prerequisites met
    }
    
    for course in catalog['courses']:
        course_id = course['id']
        
        # Skip if already completed
        if course_id in completed_ids:
            continue
        
        # Check prerequisites
        prereqs_met, missing_prereqs, or_groups_met = check_prerequisites_met(course, completed_ids)
        
        if not prereqs_met:
            continue
        
        # Calculate relevance score (0-100 points)
        relevance_score = 0
        
        # L3 category match (0-35 points) - Most specific, highest weight
        l3_category = course.get('l3_category', '')
        user_l3_categories = defaultdict(int)
        for completed in completed_badges:
            if completed.get('l3_category'):
                user_l3_categories[completed['l3_category']] += 1
        
        if l3_category and l3_category in user_l3_categories:
            l3_weight = user_l3_categories[l3_category] / max(user_l3_categories.values()) if user_l3_categories else 0
            relevance_score += l3_weight * 35
        
        # L2 category match (0-25 points) - Medium specificity
        category = course.get('l2_category', '')
        if category in user_categories:
            category_weight = user_categories[category] / max(user_categories.values()) if user_categories else 0
            relevance_score += category_weight * 25
        
        # L1 platform match (0-15 points) - Least specific, lowest weight
        platform = course.get('l1_header', '')
        if platform in user_platforms:
            platform_weight = user_platforms[platform] / max(user_platforms.values()) if user_platforms else 0
            relevance_score += platform_weight * 15
        
        # Level progression bonus (0-20 points)
        course_level = course['level']
        if course_level in user_levels:
            # Bonus for continuing at current level
            relevance_score += 10
        if course_level == max(user_levels.keys(), default=0) + 1:
            # Extra bonus for next level up
            relevance_score += 20
        
        # Priority category bonus (0-25 points)
        is_next_level = False
        for completed in completed_badges:
            if (completed.get('l2_category') == category and
                course_level == completed['level'] + 1):
                is_next_level = True
                relevance_score += 25  # High priority for direct progression
                break
        
        # Round to 1 decimal place
        relevance_score = round(relevance_score, 1)
        
        # Create recommendation entry
        # Determine priority category
        priority_category = 'advanced'
        if is_next_level:
            priority_category = 'next_level'
        elif course_level == 1:
            priority_category = 'new_paths'
        elif course_level in user_levels:
            priority_category = 'parallel'
        
        rec = {
            'id': course_id,
            'badge_name': course['badge_name'],
            'level': course['level'],
            'level_name': {1: 'L1-Foundation', 2: 'L2-Intermediate', 3: 'L3-Advanced', 4: 'L4-Mastery'}.get(course['level'], f'L{course["level"]}'),
            'l1_header': course.get('l1_header', ''),
            'l2_category': course.get('l2_category', ''),
            'l3_category': course.get('l3_category', ''),
            'ibm_link': course.get('ibm_link', ''),
            'bp_link': course.get('bp_link', ''),
            'score': relevance_score,
            'priority': priority_category,
            'prerequisites': course.get('prerequisites', [])
        }
        
        recommendations[priority_category].append(rec)
    
    # Sort each category by score (highest first)
    # Keep top N for display, but don't limit for the all_sorted list
    for category in recommendations:
        recommendations[category].sort(key=lambda x: x['score'], reverse=True)
    
    # Create a combined sorted list of ALL recommendations
    all_recommendations = []
    for category in recommendations:
        all_recommendations.extend(recommendations[category])
    
    # Sort all by score (highest first)
    all_recommendations.sort(key=lambda x: x['score'], reverse=True)
    
    # Limit categories for display only
    recommendations_display = {}
    for category in recommendations:
        recommendations_display[category] = recommendations[category][:max_recommendations]
    
    # Add summary statistics
    summary = {
        'total_completed': len(completed_ids),
        'total_available': len(catalog['courses']) - len(completed_ids),
        'completion_percentage': round(len(completed_ids) / len(catalog['courses']) * 100, 1),
        'next_level_count': len(recommendations['next_level']),
        'new_paths_count': len(recommendations['new_paths']),
        'parallel_count': len(recommendations['parallel']),
        'advanced_count': len(recommendations['advanced']),
        'user_platforms': dict(user_platforms),
        'user_categories': dict(user_categories),
        'user_levels': dict(user_levels)
    }
    
    return {
        'summary': summary,
        'recommendations': recommendations_display,  # Limited for display
        'all_sorted': all_recommendations  # ALL recommendations, sorted by score
    }

def print_recommendations(recommendations_data):
    """Pretty print recommendations."""
    summary = recommendations_data['summary']
    recs = recommendations_data['recommendations']
    
    print("\n" + "="*80)
    print("COURSE RECOMMENDATIONS")
    print("="*80)
    
    print(f"\nProgress: {summary['total_completed']} completed / {summary['total_available']} available")
    print(f"Completion: {summary['completion_percentage']}%")
    
    print("\nYour Learning Focus:")
    print("  Top Platforms:")
    for platform, count in sorted(summary['user_platforms'].items(), key=lambda x: x[1], reverse=True)[:3]:
        print(f"    - {platform}: {count} badges")
    
    print("\n" + "-"*80)
    print("🎯 PRIORITY: Next Level Courses (Continue Current Paths)")
    print("-"*80)
    if recs['next_level']:
        for i, rec in enumerate(recs['next_level'][:5], 1):
            level_name = {1: 'L1', 2: 'L2', 3: 'L3', 4: 'L4'}.get(rec['level'], f"L{rec['level']}")
            print(f"\n{i}. {rec['badge_name']}")
            print(f"   Level: {level_name} | Category: {rec['l2_category']}")
            if rec['ibm_link']:
                print(f"   Link: {rec['ibm_link']}")
    else:
        print("No next-level courses available. Great job! Consider starting new paths.")
    
    print("\n" + "-"*80)
    print("🌟 NEW: Start New Learning Paths (L1 Foundations)")
    print("-"*80)
    if recs['new_paths']:
        for i, rec in enumerate(recs['new_paths'][:5], 1):
            print(f"\n{i}. {rec['badge_name']}")
            print(f"   Platform: {rec['l1_header']} | Category: {rec['l2_category']}")
            if rec['ibm_link']:
                print(f"   Link: {rec['ibm_link']}")
    else:
        print("No new L1 courses available.")
    
    print("\n" + "-"*80)
    print("📚 PARALLEL: Same Level, Different Topics")
    print("-"*80)
    if recs['parallel']:
        for i, rec in enumerate(recs['parallel'][:5], 1):
            level_name = {1: 'L1', 2: 'L2', 3: 'L3', 4: 'L4'}.get(rec['level'], f"L{rec['level']}")
            print(f"\n{i}. {rec['badge_name']}")
            print(f"   Level: {level_name} | Category: {rec['l2_category']}")
    else:
        print("No parallel courses available.")
    
    print("\n" + "="*80)

def save_recommendations(recommendations_data, output_file='backend/output/recommendations.json'):
    """Save recommendations to JSON and CSV files."""
    # Save JSON
    import os
    os.makedirs('backend/output', exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(recommendations_data, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Saved recommendations to {output_file}")
    
    # Save CSV
    csv_file = output_file.replace('.json', '.csv')
    save_recommendations_csv(recommendations_data, csv_file)

def save_recommendations_csv(recommendations_data, output_file='backend/output/recommendations.csv'):
    """Save recommendations to a CSV file sorted by score."""
    all_recs = recommendations_data.get('all_sorted', [])
    
    if not all_recs:
        print("No recommendations to save to CSV")
        return
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['rank', 'score', 'badge_name', 'level_name', 'priority',
                     'l1_header', 'l2_category', 'l3_category', 'ibm_link', 'bp_link']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        for i, rec in enumerate(all_recs, 1):
            writer.writerow({
                'rank': i,
                'score': rec['score'],
                'badge_name': rec['badge_name'],
                'level_name': rec['level_name'],
                'priority': rec['priority'],
                'l1_header': rec['l1_header'],
                'l2_category': rec['l2_category'],
                'l3_category': rec['l3_category'],
                'ibm_link': rec['ibm_link'],
                'bp_link': rec['bp_link']
            })
    
    print(f"✓ Saved recommendations to {output_file}")
    
    # Also save a simple text file with top recommendations
    txt_file = output_file.replace('.csv', '.txt')
    save_recommendations_txt(recommendations_data, txt_file)

def save_recommendations_txt(recommendations_data, output_file='backend/output/recommendations.txt'):
    """Save a human-readable text file with top recommendations."""
    all_recs = recommendations_data.get('all_sorted', [])
    summary = recommendations_data.get('summary', {})
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("IBM BADGE RECOMMENDATIONS - SORTED BY SCORE\n")
        f.write("="*80 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Completed: {summary.get('total_completed', 0)}\n")
        f.write(f"Completion: {summary.get('completion_percentage', 0)}%\n")
        f.write("="*80 + "\n\n")
        
        f.write("TOP 20 RECOMMENDED COURSES:\n")
        f.write("-"*80 + "\n\n")
        
        for i, rec in enumerate(all_recs[:20], 1):
            f.write(f"{i}. {rec['badge_name']}\n")
            f.write(f"   Score: {rec['score']:.1f}/100 | Level: {rec['level_name']} | Priority: {rec['priority']}\n")
            f.write(f"   Platform: {rec['l1_header']}\n")
            f.write(f"   Category: {rec['l2_category']}")
            if rec['l3_category']:
                f.write(f" > {rec['l3_category']}")
            f.write("\n")
            if rec['ibm_link']:
                f.write(f"   Link: {rec['ibm_link']}\n")
            f.write("\n")
        
        # Add breakdown by priority
        f.write("\n" + "="*80 + "\n")
        f.write("RECOMMENDATIONS BY PRIORITY:\n")
        f.write("="*80 + "\n\n")
        
        recs = recommendations_data.get('recommendations', {})
        for priority in ['next_level', 'new_paths', 'parallel', 'advanced']:
            priority_recs = recs.get(priority, [])
            if priority_recs:
                priority_name = {
                    'next_level': '🎯 NEXT LEVEL (Continue Current Paths)',
                    'new_paths': '🌟 NEW PATHS (Start New Foundations)',
                    'parallel': '📚 PARALLEL (Same Level, Different Topics)',
                    'advanced': '🚀 ADVANCED (Higher Level Courses)'
                }.get(priority, priority)
                
                f.write(f"\n{priority_name}\n")
                f.write("-"*80 + "\n")
                for rec in priority_recs[:10]:
                    f.write(f"  • {rec['badge_name']} (Score: {rec['score']:.1f})\n")
    
    print(f"✓ Saved recommendations to {output_file}")

def main():
    """Main function to generate recommendations."""
    import sys
    
    if len(sys.argv) > 1:
        progress_file = sys.argv[1]
    else:
        # Default to Christopher's progress file
        progress_file = 'backend/output/user_progress_christopher-darlington.json'
    
    print(f"Generating recommendations from {progress_file}...")
    
    try:
        recommendations = get_recommendations(progress_file)
        print_recommendations(recommendations)
        save_recommendations(recommendations)
    except FileNotFoundError:
        print(f"Error: Progress file '{progress_file}' not found.")
        print("Please run scrape_user_progress.py first to generate user progress data.")
        sys.exit(1)

if __name__ == '__main__':
    main()

# Made with Bob
