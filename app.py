"""
Daily LLM Quantization Papers - Vercel Web App
Flask application for serving paper cards
"""

from flask import Flask, render_template, jsonify
import os
import json
import glob
from datetime import datetime

app = Flask(__name__)

# Papers directory
PAPERS_DIR = os.path.join(os.path.dirname(__file__), 'papers')
TEMPLATE_DIR = os.path.dirname(__file__)


def get_latest_papers():
    """Get papers from the latest markdown file"""
    papers_files = glob.glob(os.path.join(PAPERS_DIR, 'papers_*.md'))
    
    if not papers_files:
        return []
    
    # Get latest file
    latest_file = max(papers_files, key=os.path.getmtime)
    
    papers = []
    current_category = "LLM Quantization"
    import re
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Detect category
        if '## 🎯 LLM Quantization' in line:
            current_category = 'LLM Quantization'
        elif '## 📱 Edge Deployment' in line:
            current_category = 'Edge Deployment'
        elif '## 🚁 UAV Vision' in line:
            current_category = 'UAV Vision'
        
        # Parse paper title
        title_match = re.match(r'### \d+\. (.+)', line)
        if title_match:
            title = title_match.group(1).strip()
            paper = {
                'title': title,
                'authors': '',
                'source': 'arXiv',
                'category': current_category,
                'date': '',
                'url': ''
            }
            
            # Parse metadata
            j = i + 1
            while j < len(lines) and not re.match(r'### \d+\. ', lines[j]) and not lines[j].startswith('## '):
                meta_line = lines[j].strip()
                
                if '**Authors**:' in meta_line:
                    paper['authors'] = meta_line.replace('**Authors**:', '').strip()
                elif '**Published**:' in meta_line:
                    paper['date'] = meta_line.replace('**Published**:', '').strip()
                elif '**arXiv**:' in meta_line:
                    url_match = re.search(r'\[([^\]]+)\]\(([^)]+)\)', meta_line)
                    if url_match:
                        paper['url'] = url_match.group(2)
                
                j += 1
            
            if paper['url']:
                papers.append(paper)
        
        i += 1
    
    return papers


def get_stats(papers):
    """Calculate statistics"""
    categories = {}
    for p in papers:
        cat = p.get('category', 'Other')
        categories[cat] = categories.get(cat, 0) + 1
    
    return {
        'total': len(papers),
        'categories': categories,
        'last_updated': datetime.now().strftime('%Y-%m-%d')
    }


@app.route('/')
def index():
    """Main page with paper cards"""
    papers = get_latest_papers()
    stats = get_stats(papers)
    return render_template('index.html', papers=papers, stats=stats)


@app.route('/api/papers')
def api_papers():
    """API endpoint for papers data"""
    papers = get_latest_papers()
    return jsonify({
        'papers': papers,
        'stats': get_stats(papers)
    })


@app.route('/api/categories')
def api_categories():
    """API endpoint for categories"""
    papers = get_latest_papers()
    stats = get_stats(papers)
    return jsonify(stats['categories'])


# For Vercel serverless function
def handler(request):
    """Vercel handler function"""
    return app(request.environ, start_response)


# For local development
if __name__ == '__main__':
    app.run(debug=True, port=5000)