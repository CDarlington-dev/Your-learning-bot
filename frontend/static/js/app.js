// Main application JavaScript

// State management
let currentData = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('credlyForm');
    form.addEventListener('submit', handleSubmit);
});

// Handle form submission
async function handleSubmit(e) {
    e.preventDefault();
    
    const username = document.getElementById('credlyUsername').value.trim();
    
    if (!username) {
        showError('Please enter a Credly username');
        return;
    }
    
    // Show loading state
    showLoading();
    
    try {
        const response = await fetch('/api/recommendations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                credly_username: username
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to fetch recommendations');
        }
        
        // Store data and display results
        currentData = data;
        displayResults(data);
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'An error occurred while fetching recommendations');
    }
}

// Show loading state
function showLoading() {
    document.getElementById('loadingSection').style.display = 'block';
    document.getElementById('errorSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
    
    // Disable submit button
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = true;
    submitBtn.querySelector('.btn-text').style.display = 'none';
    submitBtn.querySelector('.btn-loading').style.display = 'inline-flex';
}

// Show error
function showError(message) {
    document.getElementById('errorMessage').textContent = message;
    document.getElementById('errorSection').style.display = 'block';
    document.getElementById('loadingSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
    
    // Re-enable submit button
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = false;
    submitBtn.querySelector('.btn-text').style.display = 'inline';
    submitBtn.querySelector('.btn-loading').style.display = 'none';
}

// Display results
function displayResults(data) {
    // Hide loading and error
    document.getElementById('loadingSection').style.display = 'none';
    document.getElementById('errorSection').style.display = 'none';
    
    // Show results
    document.getElementById('resultsSection').style.display = 'block';
    
    // Re-enable submit button
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = false;
    submitBtn.querySelector('.btn-text').style.display = 'inline';
    submitBtn.querySelector('.btn-loading').style.display = 'none';
    
    // Display summary
    displaySummary(data.summary);
    
    // Display recommendations
    displayAllRecommendations(data.all_sorted);
    displayCategoryRecommendations('next-level', data.recommendations.next_level);
    displayCategoryRecommendations('new-paths', data.recommendations.new_paths);
    displayCategoryRecommendations('parallel', data.recommendations.parallel);
    
    // Scroll to results
    document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
}

// Display summary
function displaySummary(summary) {
    document.getElementById('completedCount').textContent = summary.total_completed;
    document.getElementById('availableCount').textContent = summary.total_available;
    document.getElementById('completionPercent').textContent = summary.completion_percentage + '%';
    
    // Display top platforms
    const platformsList = document.getElementById('platformsList');
    platformsList.innerHTML = '';
    
    const platforms = Object.entries(summary.user_platforms)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);
    
    platforms.forEach(([platform, count]) => {
        const item = document.createElement('div');
        item.className = 'platform-item';
        item.innerHTML = `
            <span>${platform}</span>
            <strong>${count} badges</strong>
        `;
        platformsList.appendChild(item);
    });
}

// Display all recommendations
function displayAllRecommendations(recommendations) {
    const container = document.getElementById('allRecommendations');
    container.innerHTML = '';
    
    if (!recommendations || recommendations.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>No recommendations available</p></div>';
        return;
    }
    
    recommendations.forEach((rec, index) => {
        container.appendChild(createRecommendationCard(rec, index + 1));
    });
}

// Display category recommendations
function displayCategoryRecommendations(category, recommendations) {
    const containerId = category === 'next-level' ? 'nextLevelRecommendations' :
                       category === 'new-paths' ? 'newPathsRecommendations' :
                       'parallelRecommendations';
    
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    
    if (!recommendations || recommendations.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>No recommendations in this category</p></div>';
        return;
    }
    
    recommendations.forEach((rec, index) => {
        container.appendChild(createRecommendationCard(rec, index + 1));
    });
}

// Create recommendation card
function createRecommendationCard(rec, rank) {
    const card = document.createElement('div');
    card.className = 'recommendation-item';
    
    const priorityEmoji = {
        'next_level': '📈',
        'new_paths': '🌟',
        'parallel': '📚',
        'advanced': '🚀'
    };
    
    const priorityLabel = {
        'next_level': 'Next Level',
        'new_paths': 'New Path',
        'parallel': 'Parallel',
        'advanced': 'Advanced'
    };
    
    card.innerHTML = `
        <div class="rec-header">
            <div class="rec-title">
                <h3>${rank}. ${rec.badge_name}</h3>
            </div>
            <div class="rec-score">${rec.score.toFixed(1)}</div>
        </div>
        
        <div class="rec-meta">
            <span class="rec-badge">
                ${priorityEmoji[rec.priority] || '📌'} ${priorityLabel[rec.priority] || rec.priority}
            </span>
            <span class="rec-badge">
                📊 ${rec.level_name}
            </span>
        </div>
        
        <div class="rec-category">
            <strong>Platform:</strong> ${rec.l1_header || 'N/A'}<br>
            <strong>Category:</strong> ${rec.l2_category || 'N/A'}
            ${rec.l3_category ? ` > ${rec.l3_category}` : ''}
        </div>
        
        ${rec.ibm_link || rec.bp_link ? `
            <div class="rec-links">
                ${rec.ibm_link ? `<a href="${rec.ibm_link}" target="_blank" class="rec-link">🔗 IBM Learning</a>` : ''}
                ${rec.bp_link ? `<a href="${rec.bp_link}" target="_blank" class="rec-link">📘 Business Partner</a>` : ''}
            </div>
        ` : ''}
    `;
    
    return card;
}

// Tab switching
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    const tabId = `tab-${tabName}`;
    document.getElementById(tabId).classList.add('active');
    
    // Add active class to clicked button
    event.target.classList.add('active');
}

// Reset form
function resetForm() {
    document.getElementById('credlyForm').reset();
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('errorSection').style.display = 'none';
    document.getElementById('loadingSection').style.display = 'none';
    currentData = null;
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Made with Bob
