#!/usr/bin/env python3
"""
Extract all badge data from Seismic page HTML.
Parses HTML tables directly to extract badge information.
"""

import json
import re
from bs4 import BeautifulSoup

def load_html(html_file):
    """Load and parse the HTML file."""
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    print(f"✓ Successfully loaded HTML file")
    return soup

def extract_text_from_html(html_str, preserve_breaks=False, add_spaces_between_elements=False):
    """Extract plain text from HTML string."""
    if not html_str:
        return ""
    
    if preserve_breaks:
        # Replace <br> tags with newlines for earning criteria
        html_str = html_str.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
        soup = BeautifulSoup(html_str, 'html.parser')
        text = soup.get_text()
        
        # Replace non-breaking spaces (U+00A0) with regular spaces
        text = text.replace('\u00a0', ' ')
        
        # Clean up excessive newlines but preserve intentional ones
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(line for line in lines if line)
        
        # Add newline after each "Level #" pattern
        import re
        text = re.sub(r'(Level \d+)', r'\1\n', text)
        
        # Remove any whitespace between \n and the next letter
        text = re.sub(r'\n\s+', r'\n', text)
        
        # Remove trailing newline at the end
        text = text.rstrip('\n')
        
        return text
    elif add_spaces_between_elements:
        # For badge names: add space between elements to prevent concatenation
        soup = BeautifulSoup(html_str, 'html.parser')
        # Get all text nodes and join them with spaces
        texts = []
        for element in soup.descendants:
            if isinstance(element, str) and element.strip():
                texts.append(element.strip())
        text = ' '.join(texts)
        # Clean up multiple spaces
        text = ' '.join(text.split())
        return text
    else:
        # Replace <br> tags with spaces before parsing
        html_str = html_str.replace('<br>', ' ').replace('<br/>', ' ').replace('<br />', ' ')
        soup = BeautifulSoup(html_str, 'html.parser')
        text = soup.get_text(strip=True)
        # Clean up multiple spaces
        text = ' '.join(text.split())
        return text

def extract_link_from_element(element):
    """Extract href from a BeautifulSoup element."""
    if not element:
        return ""
    link = element.find('a')
    if link and hasattr(link, 'get'):
        return link.get('href', '')
    return ''

def parse_html_table(table_element):
    """Parse an HTML table element and extract badge data."""
    badges = []
    
    # Find all rows in the table (tr elements)
    rows = table_element.find_all('tr', class_='seismic-page-components-table-Row')
    
    if not rows:
        return []
    
    # First row is the header
    header_row = rows[0]
    headers = []
    header_cells = header_row.find_all('td', class_='seismic-page-components-table-Column')
    for cell in header_cells:
        # Get text from the Cell div inside the Column td
        cell_div = cell.find('div', class_='seismic-page-components-table-Cell')
        if cell_div:
            header_text = cell_div.get_text(strip=True)
            headers.append(header_text)
    
    # Check if this looks like a badge table
    if not any('badge' in h.lower() or 'name' in h.lower() for h in headers):
        return []
    
    # Process data rows (skip header row)
    for row in rows[1:]:
        badge = {}
        cells = row.find_all('td', class_='seismic-page-components-table-Column')
        
        for col, cell in enumerate(cells):
            if col >= len(headers):
                continue
            
            # Get the Cell div inside the Column td
            cell_div = cell.find('div', class_='seismic-page-components-table-Cell')
            if not cell_div:
                continue
                
            cell_text = cell_div.get_text(strip=True)
            cell_link = extract_link_from_element(cell_div)
            
            # Map to badge fields based on header
            header = headers[col].lower()
            if 'badge name' in header or header == 'badge name':
                # For badge names, get the raw HTML and add spaces between elements
                rich_text_div = cell_div.find('div', class_='seismic-page-RichTextView-content')
                if rich_text_div:
                    name_html = str(rich_text_div)
                    badge['badge_name'] = extract_text_from_html(name_html, add_spaces_between_elements=True)
                else:
                    badge['badge_name'] = cell_text
            elif 'badge link' in header:
                badge['badge_link'] = cell_link
            elif 'earning criteria' in header or 'criteria' in header:
                # Get the raw HTML for earning criteria to preserve line breaks
                rich_text_div = cell_div.find('div', class_='seismic-page-RichTextView-content')
                if rich_text_div:
                    criteria_html = str(rich_text_div)
                    badge['earning_criteria'] = extract_text_from_html(criteria_html, preserve_breaks=True)
                else:
                    badge['earning_criteria'] = cell_text
            elif 'ibm link' in header:
                badge['ibm_link'] = cell_link
            elif 'bp link' in header or 'partner' in header:
                badge['bp_link'] = cell_link
        
        # Only add if we have at least a badge name
        if badge.get('badge_name'):
            badges.append(badge)
    
    return badges

def get_l1_from_l2(l2_category):
    """Map L2 category to its L1 parent category."""
    l2_to_l1_mapping = {
        # Automation Platform
        'Application Development & Integration': 'Automation Platform',
        'Infrastructure Automation': 'Automation Platform',
        'Security Threat Management': 'Automation Platform',
        'Technology Business Management': 'Automation Platform',
        'Network Management': 'Automation Platform',
        'Observability': 'Automation Platform',
        
        # Data Platform
        'AI Productivity': 'Data Platform',
        'AI/ML Ops': 'Data Platform',
        'Data Fabric': 'Data Platform',
        'AI Governance': 'Data Platform',
        'Business Analytics': 'Data Platform',
        'Data Lakehouse': 'Data Platform',
        
        # Hybrid Cloud Platform
        'Power': 'Hybrid Cloud Platform',
        'Public Cloud Platform': 'Hybrid Cloud Platform',
        'Storage': 'Hybrid Cloud Platform',
        'Technology Lifecycle Services': 'Hybrid Cloud Platform',
        'Engineering Lifecycle Management': 'Hybrid Cloud Platform',
        'Workflow Automation': 'Hybrid Cloud Platform',
        
        # Transaction Processing Platform
        'Application Development': 'Transaction Processing Platform',
        'Application and Data Management': 'Transaction Processing Platform',
        'IT Operations Management': 'Transaction Processing Platform',
        'IBM Z': 'Transaction Processing Platform',
        'Content Management': 'Transaction Processing Platform',
    }
    
    return l2_to_l1_mapping.get(l2_category, 'Other')

def find_headers_before_table(soup, table_element):
    """Find the L1, L2 and L3 headers for a table by looking backward in the DOM."""
    l1_header = ""
    l2_header = ""
    l3_header = ""
    
    # Get all h1, h2 and h3 elements in the document
    all_h1s = soup.find_all('h1')
    all_h2s = soup.find_all('h2')
    all_h3s = soup.find_all('h3')
    
    # Find the position of this table in the document
    # We'll look for h1/h2/h3 elements that appear before this table
    table_position = None
    for i, elem in enumerate(soup.find_all()):
        if elem == table_element:
            table_position = i
            break
    
    if table_position is None:
        return l1_header, l2_header, l3_header
    
    # Find the closest h1 before this table
    closest_h1 = None
    closest_h1_pos = -1
    for h1 in all_h1s:
        h1_pos = None
        for i, elem in enumerate(soup.find_all()):
            if elem == h1:
                h1_pos = i
                break
        if h1_pos is not None and h1_pos < table_position and h1_pos > closest_h1_pos:
            closest_h1 = h1
            closest_h1_pos = h1_pos
    
    if closest_h1:
        l1_header = closest_h1.get_text(strip=True)
    
    # Find the closest h2 before this table (but after the h1)
    # If we find another h1 between the h2 and the table, ignore the h2
    closest_h2 = None
    closest_h2_pos = -1
    for h2 in all_h2s:
        h2_pos = None
        for i, elem in enumerate(soup.find_all()):
            if elem == h2:
                h2_pos = i
                break
        # h2 must be after the h1 and before the table
        if h2_pos is not None and h2_pos < table_position and h2_pos > closest_h1_pos and h2_pos > closest_h2_pos:
            # Check if there's another h1 between this h2 and the table
            has_h1_after = False
            for h1 in all_h1s:
                h1_pos_check = None
                for i, elem in enumerate(soup.find_all()):
                    if elem == h1:
                        h1_pos_check = i
                        break
                if h1_pos_check is not None and h1_pos_check > h2_pos and h1_pos_check < table_position:
                    has_h1_after = True
                    break
            
            if not has_h1_after:
                closest_h2 = h2
                closest_h2_pos = h2_pos
    
    if closest_h2:
        l2_header = closest_h2.get_text(strip=True)
    
    # Find the closest h3 before this table (but after the h2)
    # If we find another h2 or h1 between the h3 and the table, ignore the h3
    closest_h3 = None
    closest_h3_pos = -1
    for h3 in all_h3s:
        h3_pos = None
        for i, elem in enumerate(soup.find_all()):
            if elem == h3:
                h3_pos = i
                break
        # h3 must be after the h2 and before the table
        if h3_pos is not None and h3_pos < table_position and h3_pos > closest_h2_pos and h3_pos > closest_h3_pos:
            # Check if there's another h2 or h1 between this h3 and the table
            has_h2_or_h1_after = False
            for h2 in all_h2s:
                h2_pos_check = None
                for i, elem in enumerate(soup.find_all()):
                    if elem == h2:
                        h2_pos_check = i
                        break
                if h2_pos_check is not None and h2_pos_check > h3_pos and h2_pos_check < table_position:
                    has_h2_or_h1_after = True
                    break
            
            if not has_h2_or_h1_after:
                for h1 in all_h1s:
                    h1_pos_check = None
                    for i, elem in enumerate(soup.find_all()):
                        if elem == h1:
                            h1_pos_check = i
                            break
                    if h1_pos_check is not None and h1_pos_check > h3_pos and h1_pos_check < table_position:
                        has_h2_or_h1_after = True
                        break
            
            if not has_h2_or_h1_after:
                closest_h3 = h3
                closest_h3_pos = h3_pos
    
    if closest_h3:
        l3_header = closest_h3.get_text(strip=True)
    
    # If we don't have an L1 from H1, try to get it from L2 using the mapping
    if not l1_header and l2_header:
        l1_header = get_l1_from_l2(l2_header)
    
    return l1_header, l2_header, l3_header

def extract_all_badges(soup):
    """Extract all badges from all HTML tables in the document."""
    all_badges = []
    badge_id = 1
    
    # Find all table elements (actual <table> tags with InnerTable class)
    tables = soup.find_all('table', class_='seismic-page-components-tableViewer-InnerTable')
    
    print(f"Found {len(tables)} tables in the HTML")
    
    for table in tables:
        # Find headers before this table
        l1_header, l2_header, l3_header = find_headers_before_table(soup, table)
        
        # Parse the table
        badges = parse_html_table(table)
        
        # Add headers and IDs to each badge
        for badge in badges:
            badge['id'] = badge_id
            badge['l1_header'] = l1_header
            badge['l2_category'] = l2_header
            badge['l3_category'] = l3_header
            badge['title'] = badge.get('badge_name', '')
            
            all_badges.append(badge)
            badge_id += 1
        
        if badges:
            l3_display = f", L3: {l3_header}" if l3_header else ""
            print(f"  ✓ Extracted {len(badges)} badges from table (L1: {l1_header}, L2: {l2_header}{l3_display})")
    
    return all_badges
def determine_badge_level(badge_name):
    """Determine the level of a badge based on its name.
    L1 = Sales Foundation
    L2 = Intermediate
    L3 = Advanced
    L4 = Mastery
    """
    name_lower = badge_name.lower()
    
    # Check for Mastery (Level 4)
    if 'mastery' in name_lower:
        return 4
    
    # Check for Advanced (Level 3)
    if 'advanced' in name_lower:
        return 3
    
    # Check for Intermediate (Level 2)
    if 'intermediate' in name_lower:
        return 2
    
    # Check for Sales Foundation (Level 1)
    if 'sales foundation' in name_lower or 'foundation' in name_lower:
        return 1
    
    # Default to Level 1 for fundamentals or unspecified
    if 'fundamentals' in name_lower or 'level 1' in name_lower:
        return 1
    
    # If we can't determine, return None
    return None

def extract_base_product_name(badge_name):
    """Extract the base product name from a badge name by removing level indicators."""
    # Remove common suffixes
    name = badge_name
    suffixes = [
        'Practitioner Mastery',
        'Technical Sales Advanced',
        'Practitioner Advanced',
        'Sales Foundation',
        'Intermediate',
        'Advanced',
        'Mastery',
        'for Technical Sales',
        'for Practitioners',
        'for Practitioner',
    ]
    
    for suffix in suffixes:
        if name.endswith(suffix):
            name = name[:-len(suffix)].strip()
    
    return name

def find_prerequisites(badge, all_badges):
    """Find prerequisites for a badge based on its level and product family.
    Only looks at badges that come BEFORE this badge (lower IDs)."""
    prereqs = []
    
    badge_level = determine_badge_level(badge['badge_name'])
    current_id = badge['id']
    
    # Hardcode: ID 1 requires ID 2
    if current_id == 1:
        prereqs.append({'id': 2})
        return prereqs
    
    # Hardcode: ID 162 (watsonx platform Practitioner Advanced) requires specific badges and their prereqs
    if current_id == 162:
        # Add the three main badges
        prereqs.extend([
            {'id': 217},
            {'id': 244},
            {'id': 206},
        ])
        # Add their prerequisites
        prereqs.extend([
            {'id': 215},
            {'id': 214},
            {'id': 243},
            {'id': 242},
            {'id': 205},
            {'id': 204},
        ])
        return prereqs
    
    if not badge_level or badge_level == 1:
        # Level 1 badges have no prerequisites
        return prereqs
    
    base_name = extract_base_product_name(badge['badge_name'])
    l2_category = badge.get('l2_category', '')
    l3_category = badge.get('l3_category', '')
    
    # For Level 2 (Intermediate), look for the FIRST Level 1 course that came before
    if badge_level == 2:
        # Go backwards through IDs to find the first L1
        for other_badge in reversed(all_badges):
            # Only look at badges with lower IDs (previous badges)
            if other_badge['id'] >= current_id:
                continue
            
            other_level = determine_badge_level(other_badge['badge_name'])
            
            # Stop at the first L1 found
            if other_level == 1:
                prereqs.append({'id': other_badge['id']})
                break
    
    # For Level 3 (Advanced), look for only the Level 2 course (L2 already implies L1)
    elif badge_level == 3:
        # Go backwards through IDs to find the first L2
        for other_badge in reversed(all_badges):
            # Only look at badges with lower IDs (previous badges)
            if other_badge['id'] >= current_id:
                continue
            
            other_level = determine_badge_level(other_badge['badge_name'])
            
            # Stop at first L2 found
            if other_level == 2:
                prereqs.append({'id': other_badge['id']})
                break
    
    # For Level 4 (Mastery), assume all L3s in the same product family are required
    # Check the description for "OR" to determine if prerequisites are optional
    elif badge_level == 4:
        earning_criteria = badge.get('earning_criteria', '')
        has_or = ' OR ' in earning_criteria.upper() or ' or ' in earning_criteria
        
        # If there's an OR, group all L3 prerequisites together
        group_id = "or_group_1" if has_or else None
        
        for other_badge in all_badges:
            # Only look at badges with lower IDs (previous badges)
            if other_badge['id'] >= current_id:
                continue
            
            other_level = determine_badge_level(other_badge['badge_name'])
            other_base = extract_base_product_name(other_badge['badge_name'])
            
            # Include all L3 (Advanced) courses from the same product
            if other_level == 3 and (base_name in other_badge['badge_name'] or
                                     other_base in badge['badge_name']):
                prereq = {'id': other_badge['id']}
                if group_id:
                    prereq['group'] = group_id
                    prereq['group_type'] = 'one_of'  # Indicates "one of these is required"
                prereqs.append(prereq)
    
    return prereqs

def add_prerequisites_to_badges(badges):
    """Add prerequisites and level to all badges."""
    print("\nAdding prerequisites and levels to badges...")
    
    for badge in badges:
        # Add level to badge
        level = determine_badge_level(badge['badge_name'])
        badge['level'] = level if level else 0
        
        # Add prerequisites
        prereqs = find_prerequisites(badge, badges)
        badge['prerequisites'] = prereqs
        
        if prereqs:
            print(f"  ✓ Added {len(prereqs)} prerequisite(s) to '{badge['badge_name']}' (Level {level})")
    
    return badges


def save_badges_to_json(badges, output_file):
    """Save badges to JSON file."""
    output_data = {
        "courses": badges
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Saved {len(badges)} badges to {output_file}")

def main():
    html_file = 'page.html'
    output_file = 'course_catalog.json'
    
    print(f"Extracting badges from {html_file}...")
    print("="*60)
    
    # Load and parse HTML
    soup = load_html(html_file)
    
    # Extract all badges
    print("\nExtracting badges from tables...")
    badges = extract_all_badges(soup)
    
    # Add prerequisites to badges
    badges = add_prerequisites_to_badges(badges)
    
    # Save to JSON
    save_badges_to_json(badges, output_file)
    
    print("="*60)
    print(f"✓ Extraction complete! Total badges: {len(badges)}")
    
    # Print summary by category
    categories = {}
    for badge in badges:
        l1 = badge.get('l1_header', 'Unknown')
        l2 = badge.get('l2_category', 'Unknown')
        key = f"{l1} > {l2}"
        categories[key] = categories.get(key, 0) + 1
    
    print("\nBadges by category:")
    for category, count in sorted(categories.items()):
        print(f"  {category}: {count}")

if __name__ == '__main__':
    main()

# Made with Bob
