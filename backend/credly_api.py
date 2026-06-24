"""
Alternative: Use Credly's public API to fetch user badges.
This is more reliable than web scraping.
"""

import requests
import json
import time

def get_user_badges_via_api(credly_username):
    """
    Fetch user badges using Credly's public API.
    
    Args:
        credly_username: The Credly username
    
    Returns:
        List of badge dictionaries
    """
    badges = []
    page = 1
    per_page = 100
    
    # Extract the user ID from username if it has a dot
    # Format: username.userid
    if '.' in credly_username:
        user_id = credly_username.split('.')[-1]
    else:
        user_id = credly_username
    
    print(f"Fetching badges for user ID: {user_id}")
    
    while True:
        # Credly's public API endpoint
        url = f"https://www.credly.com/users/{credly_username}/badges.json"
        params = {
            'page': page,
            'per_page': per_page
        }
        
        try:
            print(f"Fetching page {page}...")
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 404:
                print("User not found or profile is private")
                break
            
            response.raise_for_status()
            data = response.json()
            
            # Check if we got any badges
            if 'data' in data and data['data']:
                page_badges = data['data']
                print(f"  Found {len(page_badges)} badges on page {page}")
                
                for badge_data in page_badges:
                    badge = {
                        'badge_name': badge_data.get('badge_template', {}).get('name', ''),
                        'badge_link': f"https://www.credly.com/badges/{badge_data.get('id', '')}",
                        'earned_date': badge_data.get('issued_at', ''),
                        'issuer': badge_data.get('badge_template', {}).get('issuer', {}).get('name', ''),
                        'description': badge_data.get('badge_template', {}).get('description', '')
                    }
                    
                    if badge['badge_name']:
                        badges.append(badge)
                
                # Check if there are more pages
                if len(page_badges) < per_page:
                    break
                
                page += 1
                time.sleep(0.5)  # Be nice to the API
            else:
                break
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching badges: {e}")
            break
        except json.JSONDecodeError:
            print("Error parsing JSON response")
            break
    
    print(f"\nTotal badges found: {len(badges)}")
    return badges

def main():
    """Test the API fetcher."""
    credly_username = 'christopher-darlington.bc0d040c'
    
    print(f"Fetching badges via API for {credly_username}...")
    badges = get_user_badges_via_api(credly_username)
    
    if badges:
        print(f"\n✓ Successfully fetched {len(badges)} badges")
        print("\nFirst 5 badges:")
        for i, badge in enumerate(badges[:5], 1):
            print(f"{i}. {badge['badge_name']}")
            print(f"   Earned: {badge.get('earned_date', 'Unknown')}")
        
        # Save to file
        import os
        os.makedirs('backend/output', exist_ok=True)
        output_file = f'backend/output/badges_api_{credly_username.split(".")[0]}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(badges, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Saved to {output_file}")
    else:
        print("\n✗ No badges found")

if __name__ == '__main__':
    main()

# Made with Bob
