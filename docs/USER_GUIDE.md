# User Guide - BeyondAcademic

## Getting Started

BeyondAcademic is an AI-powered academic writing system that helps researchers write better papers. This guide will walk you through using the system.

## Quick Start

### 1. Starting the Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

The backend will start at `http://localhost:8000`

### 2. Accessing the API Documentation

Open your browser and navigate to:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Using the Article Management Module

### Creating Your First Article

**Using cURL:**
```bash
curl -X POST "http://localhost:8000/api/articles/?author=your_name" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Your Paper Title",
    "abstract": "Your abstract text",
    "template": "IEEE",
    "authors": ["Your Name"],
    "keywords": ["keyword1", "keyword2"]
  }'
```

**Using Python:**
```python
import requests

response = requests.post(
    'http://localhost:8000/api/articles/',
    params={'author': 'your_name'},
    json={
        'title': 'Your Paper Title',
        'abstract': 'Your abstract text',
        'template': 'IEEE',
        'authors': ['Your Name'],
        'keywords': ['keyword1', 'keyword2']
    }
)

article = response.json()
article_id = article['article_id']
print(f"Created article with ID: {article_id}")
```

### Updating Your Article

When you update an article's content, a new version is automatically created:

```python
response = requests.put(
    f'http://localhost:8000/api/articles/{article_id}',
    params={'author': 'your_name'},
    json={
        'content': '# Introduction\n\nYour introduction text...',
        'changes_summary': 'Added introduction section'
    }
)

updated_article = response.json()
print(f"Now at version: {updated_article['current_version']}")
```

### Viewing Version History

```python
response = requests.get(
    f'http://localhost:8000/api/articles/{article_id}/versions'
)

versions = response.json()
for version in versions:
    print(f"Version {version['version_number']}: {version['changes_summary']}")
```

### Reverting to a Previous Version

```python
response = requests.post(
    f'http://localhost:8000/api/articles/{article_id}/revert/1',
    params={'author': 'your_name'}
)

reverted_article = response.json()
print(f"Reverted to version 1, now at version: {reverted_article['current_version']}")
```

## Using the Academic Editor

### Grammar and Spelling Check

```python
response = requests.post(
    'http://localhost:8000/api/editor/check/grammar',
    json={
        'text': 'Your paper text to check',
        'template': 'IEEE'
    }
)

suggestions = response.json()
for suggestion in suggestions:
    print(f"At position {suggestion['position']}: {suggestion['explanation']}")
    print(f"  Original: {suggestion['original']}")
    print(f"  Suggestion: {suggestion['suggestion']}")
```

### Formatting Check

```python
response = requests.post(
    'http://localhost:8000/api/editor/check/formatting',
    json={
        'text': 'Introduction\n\nYour content...',
        'template': 'IEEE'
    }
)

formatting_issues = response.json()
for issue in formatting_issues:
    print(f"Formatting issue: {issue['explanation']}")
```

### Converting to LaTeX

```python
response = requests.post(
    'http://localhost:8000/api/editor/convert/latex',
    json={
        'text': 'INTRODUCTION\n\nThis paper presents...'
    }
)

latex_output = response.json()['latex']
print(latex_output)
```

### Getting Improvement Suggestions

```python
response = requests.post(
    'http://localhost:8000/api/editor/improve',
    json={
        'paragraph': 'We use a lot of data to show that...'
    }
)

suggestions = response.json()
for suggestion in suggestions:
    print(f"Suggestion: {suggestion}")
```

## Using AI-Assisted Recommendations

### Searching for Papers

```python
# Search for high-citation papers
response = requests.post(
    'http://localhost:8000/api/recommendations/search',
    json={
        'query': 'deep learning',
        'limit': 10,
        'recommendation_type': 'high_citation'
    }
)

papers = response.json()
for paper in papers:
    print(f"{paper['title']} ({paper['year']})")
    print(f"  Authors: {', '.join(paper['authors'][:3])}")
    print(f"  Citations: {paper['citations']}")
    print(f"  DOI: {paper['doi']}")
```

### Getting Context-Based Recommendations

The system can analyze your content and recommend relevant papers:

```python
response = requests.post(
    'http://localhost:8000/api/recommendations/recommend',
    json={
        'context': 'We propose a novel neural network architecture...',
        'limit': 5
    }
)

recommendations = response.json()
for paper in recommendations:
    print(f"{paper['title']} - Relevance: {paper['relevance_score']}")
```

### Optimizing Your Writing

**Sentence Optimization:**
```python
response = requests.post(
    'http://localhost:8000/api/recommendations/optimize/sentence',
    json={
        'sentence': 'We use a lot of data to get good results.'
    }
)

optimization = response.json()
print(f"Original: {optimization['original_sentence']}")
print(f"Optimized: {optimization['optimized_sentence']}")
print(f"Formality Score: {optimization['formality_score']}")
for improvement in optimization['improvements']:
    print(f"  - {improvement}")
```

**Paragraph Optimization:**
```python
response = requests.post(
    'http://localhost:8000/api/recommendations/optimize/paragraph',
    json={
        'paragraph': 'We use a lot of data. The results show good performance. We find that the method is very effective.'
    }
)

result = response.json()
print(f"Original:\n{result['original']}\n")
print(f"Optimized:\n{result['optimized']}\n")
print(f"Overall Formality: {result['overall_formality']}")
print(f"Overall Clarity: {result['overall_clarity']}")
```

### Getting Citation Suggestions

```python
response = requests.post(
    'http://localhost:8000/api/recommendations/citations',
    json={
        'topic': 'deep learning'
    }
)

citations = response.json()
for citation in citations:
    print(citation)
```

## Complete Workflow Example

Here's a complete example of writing a paper:

```python
import requests

BASE_URL = 'http://localhost:8000/api'
AUTHOR = 'Dr. Researcher'

# Step 1: Create a new article
print("Creating article...")
article = requests.post(
    f'{BASE_URL}/articles/',
    params={'author': AUTHOR},
    json={
        'title': 'Deep Learning Applications in Medical Imaging',
        'template': 'IEEE',
        'authors': ['Dr. Researcher', 'Dr. Collaborator'],
        'keywords': ['deep learning', 'medical imaging', 'CNN']
    }
).json()

article_id = article['article_id']
print(f"Created article: {article_id}")

# Step 2: Write the introduction
intro = """# Introduction

We use deep learning to analyze medical images."""

# Step 3: Optimize the language
print("\nOptimizing language...")
optimized = requests.post(
    f'{BASE_URL}/recommendations/optimize/paragraph',
    json={'paragraph': intro}
).json()

improved_intro = optimized['optimized']
print(f"Improved introduction:\n{improved_intro}")

# Step 4: Update the article
print("\nUpdating article...")
updated = requests.put(
    f'{BASE_URL}/articles/{article_id}',
    params={'author': AUTHOR},
    json={
        'content': improved_intro,
        'changes_summary': 'Added optimized introduction'
    }
).json()

print(f"Article updated to version {updated['current_version']}")

# Step 5: Check grammar
print("\nChecking grammar...")
suggestions = requests.post(
    f'{BASE_URL}/editor/check/grammar',
    json={'text': updated['content'], 'template': 'IEEE'}
).json()

if suggestions:
    print(f"Found {len(suggestions)} suggestions")
else:
    print("No grammar issues found!")

# Step 6: Get literature recommendations
print("\nGetting literature recommendations...")
papers = requests.post(
    f'{BASE_URL}/recommendations/recommend',
    json={'context': updated['content'], 'limit': 3}
).json()

print("Recommended papers:")
for paper in papers:
    print(f"  - {paper['title']} ({paper['year']})")

# Step 7: Get citations
print("\nGenerating citations...")
citations = requests.post(
    f'{BASE_URL}/recommendations/citations',
    json={'topic': 'deep learning medical imaging'}
).json()

print("Suggested citations:")
for citation in citations:
    print(f"  {citation}")

print("\n✓ Workflow complete!")
```

## Tips and Best Practices

### 1. Use Version Control Effectively
- Always provide meaningful `changes_summary` when updating
- Review version history before major revisions
- Use revert feature if needed

### 2. Leverage AI Recommendations
- Run grammar check before finalizing sections
- Use paragraph optimization to improve academic tone
- Get paper recommendations early in the writing process

### 3. Template Selection
Choose the appropriate template for your target journal:
- **IEEE**: For engineering and computer science
- **Elsevier**: For various scientific disciplines
- **ACM**: For computer science and information technology
- **Nature/Science**: For high-impact journals

### 4. Iterative Writing Process
1. Write content
2. Optimize language
3. Check grammar and formatting
4. Add citations from recommendations
5. Review and refine

### 5. Citation Management
- Use the citation suggestion feature to find relevant papers
- Ensure consistent citation style throughout
- Validate citations before submission

## Advanced Features

### Batch Processing

Process multiple paragraphs:

```python
paragraphs = [
    "First paragraph to optimize...",
    "Second paragraph to optimize...",
    "Third paragraph to optimize..."
]

optimized_paragraphs = []
for paragraph in paragraphs:
    response = requests.post(
        f'{BASE_URL}/recommendations/optimize/paragraph',
        json={'paragraph': paragraph}
    )
    optimized_paragraphs.append(response.json()['optimized'])

final_content = '\n\n'.join(optimized_paragraphs)
```

### Custom Workflows

Create custom workflows combining multiple features:

```python
def process_paper_section(section_text, template='IEEE'):
    """Process a paper section with optimization and checking"""
    
    # Optimize
    optimized = requests.post(
        f'{BASE_URL}/recommendations/optimize/paragraph',
        json={'paragraph': section_text}
    ).json()
    
    # Check grammar
    suggestions = requests.post(
        f'{BASE_URL}/editor/check/grammar',
        json={'text': optimized['optimized'], 'template': template}
    ).json()
    
    # Check formatting
    formatting = requests.post(
        f'{BASE_URL}/editor/check/formatting',
        json={'text': optimized['optimized'], 'template': template}
    ).json()
    
    return {
        'optimized_text': optimized['optimized'],
        'grammar_suggestions': suggestions,
        'formatting_issues': formatting,
        'formality_score': optimized['overall_formality']
    }

# Use it
result = process_paper_section("We use machine learning...")
print(f"Formality: {result['formality_score']}")
print(f"Grammar issues: {len(result['grammar_suggestions'])}")
```

## Troubleshooting

### API Not Responding
- Check if backend is running: `curl http://localhost:8000/health`
- Verify port 8000 is not in use by another application

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Use a virtual environment to avoid conflicts

### Type Errors
- Ensure you're sending the correct data types
- Check API documentation for expected formats

## Next Steps

1. Explore the interactive API documentation at `/docs`
2. Try the complete workflow example
3. Customize the system for your specific needs
4. Integrate with your existing writing workflow

For more information, see:
- [API Documentation](docs/API.md)
- [Architecture Documentation](docs/ARCHITECTURE.md)
- [README](README.md)
