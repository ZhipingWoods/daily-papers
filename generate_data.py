#!/usr/bin/env python3
"""
Generate papers data JSON from markdown for the daily papers website
"""

import re
import json
import os
from datetime import datetime

def parse_papers_markdown(md_path):
    """Parse the papers markdown file and extract paper info"""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    papers = []
    current_category = "LLM Quantization"
    
    # Categories to look for
    categories = ['LLM Quantization', 'Edge Deployment', 'UAV Vision']
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        # Check for category headers
        for cat in categories:
            if f'## 🎯 {cat}' in line or f'## 📱 {cat}' in line or f'## 🚁 {cat}' in line:
                current_category = cat
                break
        
        # Parse paper entries (look for links)
        # Pattern: - [Title](url) [source]
        if line.strip().startswith('- ['):
            match = re.search(r'- \[([^\]]+)\]\(([^)]+)\)\s*\[([^\]]+)\]', line)
            if match:
                title = match.group(1)
                url = match.group(2)
                source = match.group(3)
                
                # Try to get authors from next line
                authors = ""
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line.startswith('📝'):
                        authors = next_line.replace('📝', '').strip()
                
                papers.append({
                    'title': title,
                    'url': url,
                    'source': source,
                    'authors': authors,
                    'category': current_category,
                    'date': datetime.now().strftime('%Y-%m-%d')
                })
    
    return papers

def generate_html_with_data(papers, template_path, output_path):
    """Generate HTML with papers data embedded"""
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Replace placeholder with actual data
    papers_json = json.dumps(papers, ensure_ascii=False, indent=2)
    html = html.replace('{{PAPERS_DATA}}', papers_json)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Generated {output_path} with {len(papers)} papers")

def main():
    # Paths
    papers_md = '/root/.openclaw/workspace/papers/papers_20260318.md'
    template_path = '/root/.openclaw/workspace/daily-papers/index.html'
    output_path = '/root/.openclaw/workspace/daily-papers/index.html'
    
    # Parse papers
    print(f"📄 Reading papers from {papers_md}...")
    papers = parse_papers_markdown(papers_md)
    print(f"📊 Found {len(papers)} papers")
    
    # Generate HTML
    generate_html_with_data(papers, template_path, output_path)
    
    # Print summary
    categories = {}
    for p in papers:
        categories[p['category']] = categories.get(p['category'], 0) + 1
    
    print("\n📈 Summary:")
    for cat, count in categories.items():
        print(f"   {cat}: {count}")

if __name__ == '__main__':
    main()