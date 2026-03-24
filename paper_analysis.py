"""
Enhanced Paper Analysis Module
Analyzes papers and extracts: motivation, contributions, methodology, comparisons, limitations
"""

import re
import urllib.request
import urllib.parse
import json
import os

def fetch_arxiv_abstract(arxiv_id):
    """Fetch paper abstract from arXiv API"""
    try:
        url = f'http://export.arxiv.org/api/query?id_list={arxiv_id}'
        with urllib.request.urlopen(url, timeout=10) as response:
            content = response.read().decode('utf-8')
        
        # Parse XML to extract title, abstract, authors
        title_match = re.search(r'<title>([^<]+)</title>', content)
        summary_match = re.search(r'<summary>(.*?)</summary>', content, re.DOTALL)
        authors_match = re.findall(r'<name>([^<]+)</name>', content)
        
        result = {
            'title': title_match.group(1).strip() if title_match else '',
            'abstract': summary_match.group(1).strip() if summary_match else '',
            'authors': authors_match
        }
        
        # Also get published date
        published_match = re.search(r'<published>([^<]+)</published>', content)
        if published_match:
            result['published'] = published_match.group(1)[:10]
            
        return result
    except Exception as e:
        print(f"Error fetching: {e}")
        return None


def extract_arxiv_id(url):
    """Extract arXiv ID from URL"""
    match = re.search(r'arxiv\.org/abs/([0-9.]+v?\d*)', url)
    return match.group(1) if match else None


def analyze_paper(paper):
    """
    Analyze a paper and extract structured information
    """
    arxiv_id = extract_arxiv_id(paper.get('url', ''))
    
    # Get abstract from arXiv
    abstract_data = {}
    if arxiv_id:
        abstract_data = fetch_arxiv_abstract(arxiv_id) or {}
    
    # Build analysis
    analysis = {
        'arxiv_id': arxiv_id,
        'title': abstract_data.get('title', paper.get('title', '')),
        'authors': paper.get('authors', ', '.join(abstract_data.get('authors', []))),
        'abstract': abstract_data.get('abstract', ''),
        'published': abstract_data.get('published', paper.get('date', '').replace('- ', '')),
        
        # Analysis fields
        'motivation': analyze_motivation(abstract_data.get('abstract', '')),
        'contributions': analyze_contributions(abstract_data.get('abstract', '')),
        'related_work': infer_related_work(paper.get('category', ''), abstract_data.get('abstract', '')),
        'method_steps': analyze_methodology(abstract_data.get('abstract', '')),
        'why_better': analyze_advantages(abstract_data.get('abstract', '')),
        'limitations': analyze_limitations(abstract_data.get('abstract', '')),
        'optimization': suggest_optimization(abstract_data.get('abstract', '')),
        'multimodal_support': check_multimodal(abstract_data.get('abstract', '')),
        'category': paper.get('category', ''),
    }
    
    return analysis


def analyze_motivation(abstract):
    """Analyze research motivation from abstract"""
    if not abstract:
        return "需要查看原文"
    
    # Look for common motivation phrases
    motivation_keywords = [
        'however', 'but', 'despite', 'although', 'limitations', 'problems',
        'challenges', 'gap', 'issue', 'shortcomings', 'need', 'require'
    ]
    
    abstract_lower = abstract.lower()
    
    # Extract sentences with motivation
    sentences = abstract.split('. ')
    motivation_points = []
    
    for sentence in sentences[:3]:  # Check first few sentences
        sentence_lower = sentence.lower()
        if any(kw in sentence_lower for kw in motivation_keywords):
            if len(sentence) > 30:
                motivation_points.append(sentence.strip() + '.')
    
    if motivation_points:
        return ' '.join(motivation_points[:2])
    
    # Default: use first sentence if no clear motivation found
    if sentences and len(sentences[0]) > 20:
        return sentences[0].strip() + '.'
    
    return "需要查看原文分析"


def analyze_contributions(abstract):
    """Analyze main contributions"""
    if not abstract:
        return "需要查看原文"
    
    # Look for contribution keywords
    contribution_keywords = [
        'propose', 'introduce', 'present', 'develop', 'create', 'design',
        'novel', 'new', 'first', 'breakthrough', 'improve', 'advance'
    ]
    
    abstract_lower = abstract.lower()
    sentences = abstract.split('. ')
    
    contributions = []
    for sentence in sentences:
        sentence_lower = sentence.lower()
        if any(kw in sentence_lower for kw in contribution_keywords):
            if 20 < len(sentence) < 200:
                contributions.append(sentence.strip() + '.')
    
    if contributions:
        return ' '.join(contributions[:2])
    
    return "需要查看原文分析"


def infer_related_work(category, abstract):
    """Infer related work based on category and abstract"""
    category_related = {
        'LLM Quantization': [
            'GPTQ: Accurate Post-Training Quantization for LLMs',
            'AWQ: Activation-aware Weight Quantization',
            'SmoothQuant: Accurate and Efficient PTQ for LLMs',
            'SpQR: Sparsity-aware Quantization',
            'ZeroQuant: Efficient PTQ for Transformers'
        ],
        'Edge Deployment': [
            'TensorRT: NVIDIA inference optimization',
            'ONNX Runtime: Cross-platform inference',
            'NCNN: Mobile neural network framework',
            'Knowledge Distillation methods',
            'Model pruning techniques'
        ],
        'UAV Vision': [
            'YOLO series for object detection',
            'DeepSORT for multi-object tracking',
            'FPN for multi-scale detection',
            'CenterNet for anchor-free detection',
            'Transformer-based detection (DETR)'
        ]
    }
    
    related = category_related.get(category, ['相关研究需要查看原文'])
    return '; '.join(related[:3])


def analyze_methodology(abstract):
    """Analyze methodology - how the method works"""
    if not abstract:
        return "需要查看原文"
    
    # Look for methodology keywords
    method_keywords = [
        'use', 'employ', 'adopt', 'apply', 'utilize', 'leverage',
        'combine', 'integrate', 'fuse', 'encode', 'decode', 'train'
    ]
    
    sentences = abstract.split('. ')
    methods = []
    
    for sentence in sentences:
        sentence_lower = sentence.lower()
        if any(kw in sentence_lower for kw in method_keywords):
            if 30 < len(sentence) < 150:
                methods.append(sentence.strip() + '.')
    
    if methods:
        return ' '.join(methods[:3])
    
    return "需要查看原文分析"


def analyze_advantages(abstract):
    """Analyze why this method is better"""
    if not abstract:
        return "需要查看原文"
    
    # Look for comparison keywords
    comparison_keywords = [
        'outperform', 'exceed', 'surpass', 'better', 'improve',
        'state-of-the-art', 'SOTA', 'higher', 'lower', 'faster',
        'more accurate', 'more efficient', 'achieve', 'record'
    ]
    
    abstract_lower = abstract.lower()
    sentences = abstract.split('. ')
    
    advantages = []
    for sentence in sentences:
        sentence_lower = sentence.lower()
        if any(kw in sentence_lower for kw in comparison_keywords):
            if 20 < len(sentence) < 120:
                advantages.append(sentence.strip() + '.')
    
    if advantages:
        return ' '.join(advantages[:2])
    
    return "相比现有方法有改进，需要查看原文获取详细对比"


def analyze_limitations(abstract):
    """Analyze limitations of the method"""
    if not abstract:
        return "需要查看原文"
    
    limitation_keywords = [
        'however', 'but', 'limitations', 'challenges', 'difficult',
        'cannot', 'unable', 'may not', 'might not', 'struggle'
    ]
    
    sentences = abstract.split('. ')
    limitations = []
    
    for sentence in sentences:
        sentence_lower = sentence.lower()
        if any(kw in sentence_lower for kw in limitation_keywords):
            if 20 < len(sentence) < 100:
                limitations.append(sentence.strip() + '.')
    
    if limitations:
        return ' '.join(limitations[:2])
    
    return "需要查看原文分析潜在局限"


def suggest_optimization(abstract):
    """Suggest optimization methods"""
    # Generic suggestions based on common patterns
    suggestions = [
        "可尝试知识蒸馏进一步压缩模型",
        "可结合量化感知训练提升精度",
        "可使用更高效的注意力机制",
        "可探索动态量化策略",
        "可考虑混合精度量化"
    ]
    
    # Check for specific optimization opportunities
    if 'large' in abstract.lower() or 'heavy' in abstract.lower():
        suggestions.append("可使用模型剪枝减少参数量")
    
    if 'slow' in abstract.lower() or 'computational' in abstract.lower():
        suggestions.append("可使用知识蒸馏加速推理")
    
    if 'memory' in abstract.lower() or 'gpu' in abstract.lower():
        suggestions.append("可使用INT8/INT4量化减少显存")
    
    return '; '.join(suggestions[:3])


def check_multimodal(abstract):
    """Check if paper supports multimodal"""
    if not abstract:
        return "不确定"
    
    multimodal_keywords = [
        'multimodal', 'vision-language', 'VLM', 'image', 'video', 
        'audio', 'visual', 'image-text', 'video-text', 'cross-modal',
        'multimodal', ' CLIP', 'BLIP', 'LLaVA', 'GPT-4V'
    ]
    
    abstract_lower = abstract.lower()
    
    if any(kw in abstract_lower for kw in multimodal_keywords):
        return "是 - 支持多模态"
    
    return "否 - 单模态（文本为主）"


def generate_papers_with_analysis(papers):
    """Generate papers with full analysis"""
    analyzed_papers = []
    
    for i, paper in enumerate(papers):
        print(f"Analyzing paper {i+1}/{len(papers)}: {paper.get('title', '')[:30]}...")
        analysis = analyze_paper(paper)
        analyzed_papers.append(analysis)
    
    return analyzed_papers


# Test
if __name__ == '__main__':
    test_paper = {
        'title': 'Test Paper',
        'url': 'http://arxiv.org/abs/2603.20193v1',
        'authors': 'Test Author',
        'category': 'LLM Quantization',
        'date': '2026-03-20'
    }
    result = analyze_paper(test_paper)
    print(json.dumps(result, ensure_ascii=False, indent=2))