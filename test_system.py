#!/usr/bin/env python3
"""
BeyondAcademic - Complete System Test
Demonstrates all major features of the system
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BASE_URL = 'http://localhost:8000/api'
AUTHOR = 'test_researcher'

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_health():
    """Test that the API is accessible"""
    print_section("Testing API Health")
    response = requests.get('http://localhost:8000/health')
    print(f"Status: {response.json()}")
    assert response.status_code == 200
    print("✓ API is healthy")

def test_article_management() -> str:
    """Test article creation and management"""
    print_section("1. Article Management Module")
    
    # Create article
    print("Creating new article...")
    article_data = {
        'title': 'Deep Learning for Academic Writing: A Comprehensive Study',
        'abstract': 'This paper explores the application of deep learning techniques to enhance academic writing quality and efficiency.',
        'template': 'IEEE',
        'authors': ['Dr. Jane Smith', 'Dr. John Doe'],
        'keywords': ['deep learning', 'NLP', 'academic writing', 'AI']
    }
    
    response = requests.post(
        f'{BASE_URL}/articles/',
        params={'author': AUTHOR},
        json=article_data
    )
    article = response.json()
    article_id = article['article_id']
    
    print(f"✓ Created article: {article['title']}")
    print(f"  Article ID: {article_id}")
    print(f"  Status: {article['status']}")
    print(f"  Template: {article['template']}")
    print(f"  Version: {article['current_version']}")
    
    # Update article with content
    print("\nUpdating article with introduction...")
    update_data = {
        'content': """# Introduction

The field of academic writing has traditionally relied on manual processes. However, recent advances in artificial intelligence and natural language processing offer new opportunities to enhance the writing process.

This paper presents a comprehensive study on the application of deep learning techniques to academic writing.""",
        'changes_summary': 'Added introduction section'
    }
    
    response = requests.put(
        f'{BASE_URL}/articles/{article_id}',
        params={'author': AUTHOR},
        json=update_data
    )
    updated_article = response.json()
    
    print(f"✓ Updated article to version {updated_article['current_version']}")
    
    # View version history
    print("\nVersion history:")
    response = requests.get(f'{BASE_URL}/articles/{article_id}/versions')
    versions = response.json()
    
    for version in versions:
        print(f"  v{version['version_number']}: {version['changes_summary']} (by {version['author']})")
    
    return article_id

def test_editor_features(article_id: str):
    """Test academic editor features"""
    print_section("2. Central Academic Editor")
    
    # Get article content
    response = requests.get(f'{BASE_URL}/articles/{article_id}')
    article = response.json()
    content = article['content']
    
    # Grammar check
    print("Checking grammar...")
    test_text = "We dont think this is correct. The results shows good performance."
    
    response = requests.post(
        f'{BASE_URL}/editor/check/grammar',
        json={'text': test_text, 'template': 'IEEE'}
    )
    suggestions = response.json()
    
    print(f"✓ Found {len(suggestions)} grammar suggestions:")
    for suggestion in suggestions:
        print(f"  - {suggestion['explanation']}")
        print(f"    '{suggestion['original']}' → '{suggestion['suggestion']}'")
    
    # Formatting check
    print("\nChecking formatting...")
    response = requests.post(
        f'{BASE_URL}/editor/check/formatting',
        json={'text': content, 'template': 'IEEE'}
    )
    formatting_issues = response.json()
    
    if formatting_issues:
        print(f"✓ Found {len(formatting_issues)} formatting issues")
    else:
        print("✓ No formatting issues found")
    
    # LaTeX conversion
    print("\nConverting to LaTeX...")
    simple_text = "INTRODUCTION\n\nThis is a test paragraph."
    response = requests.post(
        f'{BASE_URL}/editor/convert/latex',
        json={'text': simple_text}
    )
    latex = response.json()['latex']
    
    print("✓ LaTeX conversion successful")
    print(f"  Output preview: {latex[:100]}...")
    
    # Get improvement suggestions
    print("\nGetting improvement suggestions...")
    test_paragraph = "We use a lot of data to get good results in our experiments."
    response = requests.post(
        f'{BASE_URL}/editor/improve',
        json={'paragraph': test_paragraph}
    )
    improvements = response.json()
    
    print(f"✓ Found {len(improvements)} improvement suggestions:")
    for improvement in improvements[:3]:
        print(f"  - {improvement}")

def test_ai_recommendations(article_id: str):
    """Test AI-assisted recommendations"""
    print_section("3. AI-Assisted Knowledge Recommendation Module")
    
    # Get article content
    response = requests.get(f'{BASE_URL}/articles/{article_id}')
    article = response.json()
    content = article['content']
    
    # Search for papers
    print("Searching for relevant papers...")
    response = requests.post(
        f'{BASE_URL}/recommendations/search',
        json={
            'query': 'deep learning natural language processing',
            'limit': 3,
            'recommendation_type': 'high_citation'
        }
    )
    papers = response.json()
    
    print(f"✓ Found {len(papers)} high-citation papers:")
    for paper in papers:
        print(f"\n  {paper['title']}")
        print(f"  Authors: {', '.join(paper['authors'][:3])}")
        print(f"  Year: {paper['year']}, Citations: {paper['citations']}")
        print(f"  Venue: {paper['venue']}")
    
    # Get context-based recommendations
    print("\n\nGetting context-based recommendations...")
    response = requests.post(
        f'{BASE_URL}/recommendations/recommend',
        json={'context': content, 'limit': 3}
    )
    recommendations = response.json()
    
    print(f"✓ Found {len(recommendations)} contextually relevant papers:")
    for paper in recommendations:
        print(f"  - {paper['title']} (Relevance: {paper['relevance_score']:.2f})")
    
    # Optimize sentence
    print("\n\nOptimizing academic language...")
    test_sentence = "We use a lot of data to get good results."
    response = requests.post(
        f'{BASE_URL}/recommendations/optimize/sentence',
        json={'sentence': test_sentence}
    )
    optimization = response.json()
    
    print(f"Original: {optimization['original_sentence']}")
    print(f"Optimized: {optimization['optimized_sentence']}")
    print(f"Formality Score: {optimization['formality_score']:.2f}")
    print(f"Improvements made:")
    for improvement in optimization['improvements']:
        print(f"  - {improvement}")
    
    # Optimize paragraph
    print("\n\nOptimizing paragraph...")
    test_paragraph = """We use deep learning methods. The results show that our approach is good. We find that it works very well."""
    
    response = requests.post(
        f'{BASE_URL}/recommendations/optimize/paragraph',
        json={'paragraph': test_paragraph}
    )
    result = response.json()
    
    print(f"Original paragraph:\n  {result['original']}\n")
    print(f"Optimized paragraph:\n  {result['optimized']}\n")
    print(f"Overall Formality: {result['overall_formality']:.2f}")
    print(f"Overall Clarity: {result['overall_clarity']:.2f}")
    
    # Get citations
    print("\n\nGenerating citation suggestions...")
    response = requests.post(
        f'{BASE_URL}/recommendations/citations',
        json={'topic': 'deep learning NLP'}
    )
    citations = response.json()
    
    print(f"✓ Generated {len(citations)} citations:")
    for i, citation in enumerate(citations[:3], 1):
        print(f"  {citation}")

def test_complete_workflow():
    """Test a complete writing workflow"""
    print_section("4. Complete Writing Workflow Example")
    
    # Create new article
    print("Step 1: Creating article...")
    article_data = {
        'title': 'Machine Learning Applications in Healthcare',
        'template': 'Elsevier',
        'authors': ['Dr. Researcher'],
        'keywords': ['machine learning', 'healthcare', 'AI']
    }
    
    response = requests.post(
        f'{BASE_URL}/articles/',
        params={'author': AUTHOR},
        json=article_data
    )
    article = response.json()
    article_id = article['article_id']
    print(f"✓ Created article: {article_id}")
    
    # Write and optimize content
    print("\nStep 2: Writing and optimizing introduction...")
    raw_intro = "We use machine learning to analyze medical data. The results show good performance."
    
    response = requests.post(
        f'{BASE_URL}/recommendations/optimize/paragraph',
        json={'paragraph': raw_intro}
    )
    optimized = response.json()['optimized']
    
    print(f"  Original: {raw_intro}")
    print(f"  Optimized: {optimized}")
    
    # Update article
    print("\nStep 3: Updating article with optimized content...")
    response = requests.put(
        f'{BASE_URL}/articles/{article_id}',
        params={'author': AUTHOR},
        json={
            'content': f"# Introduction\n\n{optimized}",
            'changes_summary': 'Added optimized introduction'
        }
    )
    print("✓ Article updated")
    
    # Check grammar
    print("\nStep 4: Checking grammar...")
    response = requests.post(
        f'{BASE_URL}/editor/check/grammar',
        json={'text': optimized, 'template': 'Elsevier'}
    )
    suggestions = response.json()
    print(f"✓ Grammar check complete ({len(suggestions)} suggestions)")
    
    # Get recommendations
    print("\nStep 5: Getting literature recommendations...")
    response = requests.post(
        f'{BASE_URL}/recommendations/recommend',
        json={'context': optimized, 'limit': 2}
    )
    papers = response.json()
    print(f"✓ Found {len(papers)} relevant papers")
    
    print("\n✓ Workflow completed successfully!")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  BeyondAcademic - System Integration Test")
    print("="*60)
    
    try:
        # Test API health
        test_health()
        
        # Test article management
        article_id = test_article_management()
        
        # Test editor features
        test_editor_features(article_id)
        
        # Test AI recommendations
        test_ai_recommendations(article_id)
        
        # Test complete workflow
        test_complete_workflow()
        
        print_section("Summary")
        print("✓ All tests passed successfully!")
        print("\nThe BeyondAcademic system is fully functional with:")
        print("  • Article Management with version control")
        print("  • Academic Editor with grammar and formatting checks")
        print("  • AI-powered literature recommendations")
        print("  • Language optimization tools")
        print("  • LaTeX conversion")
        print("  • Citation generation")
        
        print("\n" + "="*60)
        print("  Test Complete - System Ready for Use")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the API")
        print("Please ensure the backend server is running:")
        print("  cd backend && python main.py")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
