"""
Daily LLM Quantization Papers - Vercel Web App
Flask application for serving paper cards with date and category filtering
"""

import os
import re
import glob
from datetime import datetime
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Papers directory - Vercel uses /var/task
PAPERS_DIR = os.path.join(os.path.dirname(__file__), 'papers')

def get_all_paper_files():
    """Get all paper files sorted by date"""
    papers_files = glob.glob(os.path.join(PAPERS_DIR, 'papers_*.md'))
    # Sort by filename (date) descending
    papers_files.sort(reverse=True)
    return papers_files


def parse_papers_from_file(filepath):
    """Parse papers from a single markdown file"""
    papers = []
    current_category = "LLM Quantization"
    
    with open(filepath, 'r', encoding='utf-8') as f:
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


def get_latest_papers():
    """Get papers from the latest markdown file"""
    papers_files = get_all_paper_files()
    
    if not papers_files:
        return []
    
    # Get latest file
    latest_file = papers_files[0]
    return parse_papers_from_file(latest_file)


def get_papers_by_date(year=None, month=None, day=None):
    """Get papers filtered by date"""
    papers_files = get_all_paper_files()
    
    # Filter by year
    if year:
        papers_files = [f for f in papers_files if f'papers_{year}' in os.path.basename(f)]
    
    # Filter by month
    if month:
        papers_files = [f for f in papers_files if f'{month:02d}' in os.path.basename(f)]
    
    # Filter by day
    if day:
        papers_files = [f for f in papers_files if f'{day:02d}' in os.path.basename(f)]
    
    all_papers = []
    for f in papers_files:
        all_papers.extend(parse_papers_from_file(f))
    
    return all_papers


def get_papers_by_category(category):
    """Get papers filtered by category"""
    all_papers = get_latest_papers()
    
    if category == 'all':
        return all_papers
    
    return [p for p in all_papers if p.get('category') == category]


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


def get_available_dates():
    """Get all available dates from paper files"""
    papers_files = get_all_paper_files()
    dates = []
    for f in papers_files:
        basename = os.path.basename(f)
        # Extract date from filename: papers_YYYYMMDD.md
        match = re.search(r'papers_(\d{4})(\d{2})(\d{2})\.md', basename)
        if match:
            year, month, day = match.groups()
            dates.append({
                'year': year,
                'month': month,
                'day': day,
                'display': f'{year}-{month}-{day}'
            })
    return dates


@app.route('/')
def index():
    """Main page with paper cards"""
    # Get filter parameters
    view_type = request.args.get('view', 'latest')  # latest, date, category
    category = request.args.get('category', 'all')
    year = request.args.get('year')
    month = request.args.get('month')
    day = request.args.get('day')
    
    # Get papers based on filter
    if view_type == 'date' and year:
        papers = get_papers_by_date(int(year), int(month) if month else None, int(day) if day else None)
    elif view_type == 'category':
        papers = get_papers_by_category(category)
    else:
        papers = get_latest_papers()
    
    stats = get_stats(papers)
    available_dates = get_available_dates()
    
    return render_template('index.html', 
                         papers=papers, 
                         stats=stats,
                         available_dates=available_dates,
                         view_type=view_type,
                         selected_category=category,
                         selected_year=year,
                         selected_month=month,
                         selected_day=day)


@app.route('/api/papers')
def api_papers():
    """API endpoint for papers data"""
    view_type = request.args.get('view', 'latest')
    category = request.args.get('category', 'all')
    year = request.args.get('year')
    month = request.args.get('month')
    day = request.args.get('day')
    
    if view_type == 'date' and year:
        papers = get_papers_by_date(int(year), int(month) if month else None, int(day) if day else None)
    elif view_type == 'category':
        papers = get_papers_by_category(category)
    else:
        papers = get_latest_papers()
    
    return jsonify({
        'papers': papers,
        'stats': get_stats(papers)
    })


@app.route('/api/dates')
def api_dates():
    """API endpoint for available dates"""
    return jsonify(get_available_dates())


@app.route('/api/categories')
def api_categories():
    """API endpoint for categories"""
    papers = get_latest_papers()
    stats = get_stats(papers)
    return jsonify(stats['categories'])


# For local development
if __name__ == '__main__':
    app.run(debug=True, port=5000)
@app.route('/api/paper/<int:paper_id>')
def api_paper_detail(paper_id):
    """Get detailed analysis for a single paper"""
    try:
        from paper_analysis import analyze_paper
        papers = get_latest_papers()
        if paper_id < 0 or paper_id >= len(papers):
            return jsonify({'error': 'Paper not found'}), 404
        paper = papers[paper_id]
        analysis = analyze_paper(paper)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
