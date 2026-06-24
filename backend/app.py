"""
Flask web application for IBM Badge Recommendations.
Provides a web interface to get course recommendations based on Credly profile.
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import sys
import json
from credly_api import get_user_badges_via_api
from convert_api_to_progress import convert_api_to_progress
from recommend_courses import get_recommendations

app = Flask(__name__, 
            static_folder='../frontend/static',
            template_folder='../frontend/templates')
CORS(app)

# Ensure output directory exists
os.makedirs('backend/output', exist_ok=True)

@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations_api():
    """
    Get course recommendations for a Credly username.
    
    Expected JSON body:
    {
        "credly_username": "username.userid"
    }
    """
    try:
        data = request.get_json()
        credly_username = data.get('credly_username', '').strip()
        
        if not credly_username:
            return jsonify({
                'error': 'Please provide a Credly username'
            }), 400
        
        # Extract username for file naming
        username_part = credly_username.split('.')[0]
        
        # Step 1: Fetch badges from Credly API
        print(f"Fetching badges for {credly_username}...")
        badges = get_user_badges_via_api(credly_username)
        
        if not badges:
            return jsonify({
                'error': 'No badges found for this user. Please check the username or ensure the profile is public.'
            }), 404
        
        # Save badges to file
        badges_file = f'backend/output/badges_api_{username_part}.json'
        with open(badges_file, 'w', encoding='utf-8') as f:
            json.dump(badges, f, indent=2, ensure_ascii=False)
        
        # Step 2: Convert to progress format
        print(f"Converting badges to progress format...")
        progress_data = convert_api_to_progress(badges_file)
        
        # Save progress file
        progress_file = f'backend/output/user_progress_{username_part}.json'
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, indent=2, ensure_ascii=False)
        
        # Step 3: Generate recommendations
        print(f"Generating recommendations...")
        recommendations = get_recommendations(progress_file)
        
        # Save recommendations
        rec_file = f'backend/output/recommendations_{username_part}.json'
        with open(rec_file, 'w', encoding='utf-8') as f:
            json.dump(recommendations, f, indent=2, ensure_ascii=False)
        
        # Return recommendations
        return jsonify({
            'success': True,
            'username': credly_username,
            'summary': recommendations['summary'],
            'recommendations': recommendations['recommendations'],
            'all_sorted': recommendations['all_sorted'][:50]  # Limit to top 50 for web display
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'error': f'An error occurred: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'IBM Badge Recommendations API'
    })

if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                    IBM BADGE RECOMMENDATION SYSTEM                         ║
║                         YourLearningBot Web App                            ║
╚════════════════════════════════════════════════════════════════════════════╝

Starting web server...
Open your browser to: http://localhost:5001

Press Ctrl+C to stop the server.
""")
    app.run(debug=True, host='0.0.0.0', port=5001)

# Made with Bob