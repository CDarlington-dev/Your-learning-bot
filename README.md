# YourLearningBot

An intelligent learning recommendation system for IBM badge courses, helping users navigate their learning journey through personalized course recommendations.

## Overview

YourLearningBot analyzes IBM's badge catalog and provides intelligent course recommendations based on prerequisites, learning paths, and user progress. The system understands the hierarchical structure of IBM badges (L1-L4) and can recommend the next best courses to take.

## Features

- **Badge Catalog Extraction**: Automated scraping and parsing of IBM badge data from HTML tables
- **Prerequisite Management**: Intelligent prerequisite tracking with support for:
  - Direct prerequisites (one level below)
  - OR-grouped prerequisites (alternative paths)
  - Multi-level learning paths (L1 → L2 → L3 → L4)
- **Course Levels**:
  - **L1**: Sales Foundation
  - **L2**: Intermediate
  - **L3**: Advanced
  - **L4**: Mastery

## Project Structure

```
YourLearningBot/
├── backend/
│   ├── extract_badges.py       # Main badge extraction script
│   ├── parse_html.py           # HTML parsing utilities
│   ├── page.html               # Source HTML with badge tables
│   ├── course_catalog.json     # Generated badge catalog with prerequisites
│   ├── requirements.txt        # Python dependencies
│   ├── HOW_TO_SCRAPE.md       # Scraping instructions
│   └── SCRAPER_README.md      # Scraper documentation
├── SYSTEM_OVERVIEW.md          # System architecture overview
├── PROJECT_VISION.md           # Project vision and goals
├── ALGORITHM_DESIGN.md         # Recommendation algorithm design
├── ML_CONSIDERATIONS.md        # Machine learning considerations
└── README.md                   # This file
```

## Getting Started

### Prerequisites

- Python 3.7+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/YourLearningBot.git
cd YourLearningBot
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

### Usage

#### Extract Badge Data

To extract badge data from the HTML source:

```bash
cd backend
python3 extract_badges.py
```

This will:
1. Parse `page.html` containing IBM badge tables
2. Extract badge information (name, links, criteria, etc.)
3. Determine badge levels (L1-L4)
4. Calculate prerequisites based on badge hierarchy
5. Generate `course_catalog.json` with 351+ badges

#### Course Catalog Structure

Each badge in `course_catalog.json` includes:

```json
{
  "badge_name": "Badge Name",
  "badge_link": "https://credly.com/...",
  "earning_criteria": "Course requirements...",
  "ibm_link": "https://yourlearning.ibm.com/...",
  "bp_link": "https://learn.ibm.com/...",
  "id": 1,
  "l1_header": "Platform Category",
  "l2_category": "Subcategory",
  "l3_category": "Specific Area",
  "title": "Badge Name",
  "level": 2,
  "prerequisites": [
    {"id": 2}
  ]
}
```

For badges with OR prerequisites (alternatives):

```json
"prerequisites": [
  {
    "id": 120,
    "group": "or_group_1",
    "group_type": "one_of"
  },
  {
    "id": 121,
    "group": "or_group_1",
    "group_type": "one_of"
  }
]
```

## Prerequisite Logic

The system uses intelligent prerequisite rules:

- **L1 (Sales Foundation)**: No prerequisites
- **L2 (Intermediate)**: Requires the first L1 found going backwards
- **L3 (Advanced)**: Requires only the first L2 (L2 already implies L1 knowledge)
- **L4 (Mastery)**: Requires L3s from the same product family (L3s already imply L2s and L1s)

This approach ensures:
- Clean, minimal dependencies
- No redundant lower-level prerequisites
- Efficient recommendation algorithms
- Clear alternative paths (OR groups)

## Badge Categories

The system organizes badges into four main platforms:

1. **Automation Platform**: Application development, infrastructure automation, security
2. **Data Platform**: AI/ML, data fabric, analytics
3. **Hybrid Cloud Platform**: Power, storage, public cloud
4. **Transaction Processing Platform**: IBM Z, application management

## Development

### Adding New Features

1. Create a new branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

### Running Tests

```bash
# Add test commands here
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Add your license here]

## Contact

[Add contact information]

## Acknowledgments

- IBM YourLearning platform for badge data
- Credly for badge verification system