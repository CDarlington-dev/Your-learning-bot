# IBM Badge Recommendations Web Application

A modern web interface for getting personalized IBM course recommendations based on your Credly badges.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 2. Start the Web Server

```bash
python3 backend/app.py
```

The server will start on `http://localhost:5001`

### 3. Open in Browser

Navigate to `http://localhost:5001` in your web browser.

## 📖 How to Use

1. **Enter Your Credly Username**
   - Go to your Credly profile (e.g., `https://www.credly.com/users/christopher-darlington.bc0d040c`)
   - Copy the username part from the URL (e.g., `christopher-darlington.bc0d040c`)
   - Paste it into the input field on the web page

2. **Get Recommendations**
   - Click "Get Recommendations"
   - The system will:
     - Fetch your badges from Credly
     - Match them against the IBM course catalog
     - Generate personalized recommendations

3. **View Results**
   - **Summary**: See your learning progress and top platforms
   - **All Recommendations**: View all courses sorted by relevance score
   - **Next Level**: Courses that continue your current learning paths
   - **New Paths**: Foundation courses to start new learning areas
   - **Parallel**: Same-level courses in different topics

4. **Enroll in Courses**
   - Click the "IBM Learning" or "Business Partner" links to enroll

## 🎯 Features

- **Real-time Badge Fetching**: Automatically fetches your latest badges from Credly
- **Smart Recommendations**: Uses AI-powered scoring based on:
  - Your learning history
  - Course prerequisites
  - Category relevance
  - Level progression
- **Beautiful UI**: Modern, responsive design that works on all devices
- **Multiple Views**: Filter recommendations by priority category
- **Direct Enrollment**: One-click access to course enrollment pages

## 📁 Project Structure

```
.
├── backend/
│   ├── app.py                      # Flask web server
│   ├── credly_api.py              # Credly API integration
│   ├── convert_api_to_progress.py # Badge processing
│   ├── recommend_courses.py       # Recommendation engine
│   ├── data/
│   │   └── course_catalog.json    # IBM course catalog
│   └── output/                    # Generated files
├── frontend/
│   ├── templates/
│   │   └── index.html            # Main web page
│   └── static/
│       ├── css/
│       │   └── style.css         # Styles
│       └── js/
│           └── app.js            # Frontend logic
└── requirements.txt              # Python dependencies
```

## 🔧 API Endpoints

### `POST /api/recommendations`

Get course recommendations for a Credly user.

**Request Body:**
```json
{
  "credly_username": "username.userid"
}
```

**Response:**
```json
{
  "success": true,
  "username": "username.userid",
  "summary": {
    "total_completed": 9,
    "total_available": 342,
    "completion_percentage": 2.6
  },
  "recommendations": {
    "next_level": [...],
    "new_paths": [...],
    "parallel": [...]
  },
  "all_sorted": [...]
}
```

### `GET /api/health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "IBM Badge Recommendations API"
}
```

## 🛠️ Development

### Running in Development Mode

The app runs in debug mode by default, which includes:
- Auto-reload on code changes
- Detailed error messages
- Debug toolbar

### Port Configuration

If port 5001 is in use, edit `backend/app.py`:

```python
app.run(debug=True, host='0.0.0.0', port=YOUR_PORT)
```

## 📝 Notes

- **Credly Profile Privacy**: Your Credly profile must be public for the API to fetch badges
- **API Rate Limiting**: The Credly API has rate limits; avoid excessive requests
- **Data Storage**: Badge data and recommendations are saved in `backend/output/`
- **Course Catalog**: The catalog is stored in `backend/data/course_catalog.json`

## 🐛 Troubleshooting

### Port Already in Use

If you see "Address already in use":
- On macOS: Disable AirPlay Receiver in System Settings
- Or: Change the port in `backend/app.py`

### No Badges Found

If the system can't find badges:
- Verify your Credly username is correct
- Ensure your Credly profile is public
- Check your internet connection

### Module Not Found

If you see import errors:
```bash
pip install -r backend/requirements.txt
```

## 🎨 Customization

### Styling

Edit `frontend/static/css/style.css` to customize the appearance.

### Recommendation Algorithm

Modify `backend/recommend_courses.py` to adjust scoring weights:
- L3 category match: 35 points
- L2 category match: 25 points
- L1 platform match: 15 points
- Level progression: 20 points
- Priority bonus: 25 points

## 📄 License

Made with ❤️ by Bob

---

**YourLearningBot v1.0** - Empowering your IBM learning journey! 🚀