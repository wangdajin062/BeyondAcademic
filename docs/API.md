# API Documentation

## Overview

The BeyondAcademic API provides comprehensive endpoints for academic writing management, editing assistance, and AI-powered recommendations.

**Base URL**: `http://localhost:8000/api`

## Authentication

Currently, the API uses a simple author parameter for user identification. In production, implement proper authentication (JWT, OAuth2, etc.).

## Article Management API

### Create Article

Create a new academic article.

**Endpoint**: `POST /articles/`

**Parameters**:
- `author` (query, optional): Author username (default: "default_user")

**Request Body**:
```json
{
  "title": "Deep Learning for Image Recognition",
  "abstract": "This paper presents a novel approach...",
  "content": "# Introduction\n\nDeep learning has...",
  "template": "IEEE",
  "authors": ["Dr. John Smith", "Dr. Jane Doe"],
  "keywords": ["deep learning", "computer vision", "neural networks"]
}
```

**Response**: `201 Created`
```json
{
  "article_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Deep Learning for Image Recognition",
  "abstract": "This paper presents a novel approach...",
  "content": "# Introduction\n\nDeep learning has...",
  "status": "draft",
  "template": "IEEE",
  "authors": ["Dr. John Smith", "Dr. Jane Doe"],
  "keywords": ["deep learning", "computer vision", "neural networks"],
  "references": [],
  "current_version": 1,
  "versions": [...],
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T10:00:00Z"
}
```

### List Articles

Get a list of all articles.

**Endpoint**: `GET /articles/`

**Parameters**:
- `status` (query, optional): Filter by status (draft, in_review, revised, submitted, published)
- `skip` (query, optional): Number of articles to skip (default: 0)
- `limit` (query, optional): Maximum articles to return (default: 100, max: 1000)

**Response**: `200 OK`
```json
[
  {
    "article_id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Deep Learning for Image Recognition",
    "status": "draft",
    "current_version": 1,
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:00:00Z"
  }
]
```

### Get Article

Get a specific article by ID.

**Endpoint**: `GET /articles/{article_id}`

**Response**: `200 OK` - Returns full article details

**Error Responses**:
- `404 Not Found` - Article not found

### Update Article

Update an existing article. If content is changed, a new version is automatically created.

**Endpoint**: `PUT /articles/{article_id}`

**Parameters**:
- `author` (query, optional): Author making the update

**Request Body**:
```json
{
  "content": "Updated content...",
  "status": "in_review",
  "changes_summary": "Added methodology section"
}
```

**Response**: `200 OK` - Returns updated article

### Delete Article

Delete an article.

**Endpoint**: `DELETE /articles/{article_id}`

**Response**: `204 No Content`

### Get Version History

Get all versions of an article.

**Endpoint**: `GET /articles/{article_id}/versions`

**Response**: `200 OK`
```json
[
  {
    "version_id": "v1",
    "version_number": 1,
    "content": "Original content",
    "created_at": "2024-01-01T10:00:00Z",
    "changes_summary": "Initial version",
    "author": "researcher"
  },
  {
    "version_id": "v2",
    "version_number": 2,
    "content": "Updated content",
    "created_at": "2024-01-02T10:00:00Z",
    "changes_summary": "Added methodology",
    "author": "researcher"
  }
]
```

### Get Specific Version

Get a specific version of an article.

**Endpoint**: `GET /articles/{article_id}/versions/{version_number}`

**Response**: `200 OK` - Returns version details

### Revert to Version

Revert an article to a previous version.

**Endpoint**: `POST /articles/{article_id}/revert/{version_number}`

**Parameters**:
- `author` (query, optional): Author performing the revert

**Response**: `200 OK` - Returns updated article with new version containing reverted content

## Academic Editor API

### Check Grammar

Check text for grammar and spelling errors.

**Endpoint**: `POST /editor/check/grammar`

**Request Body**:
```json
{
  "text": "This is the text to check for grammar errors.",
  "template": "IEEE"
}
```

**Response**: `200 OK`
```json
[
  {
    "type": "grammar",
    "position": 15,
    "length": 3,
    "original": "dont",
    "suggestion": "don't",
    "explanation": "Replace 'dont' with 'don't'",
    "confidence": 0.95
  }
]
```

### Check Formatting

Check text formatting against academic template.

**Endpoint**: `POST /editor/check/formatting`

**Request Body**:
```json
{
  "text": "Introduction\n\nThis paper...",
  "template": "IEEE"
}
```

**Response**: `200 OK` - Returns list of formatting suggestions

### Convert to LaTeX

Convert plain text to LaTeX format.

**Endpoint**: `POST /editor/convert/latex`

**Request Body**:
```json
{
  "text": "Introduction\n\nThis is a paragraph.",
  "from_format": "plain",
  "to_format": "latex"
}
```

**Response**: `200 OK`
```json
{
  "latex": "\\documentclass{article}\n\\begin{document}\n...\n\\end{document}"
}
```

### Get Improvement Suggestions

Get suggestions to improve paragraph.

**Endpoint**: `POST /editor/improve`

**Request Body**:
```json
{
  "paragraph": "We use a lot of data to show that the method is good."
}
```

**Response**: `200 OK`
```json
[
  "Consider replacing 'a lot of' with 'numerous' for more academic tone",
  "Consider replacing 'good' with 'effective' for more academic tone"
]
```

### Get Formatting Rules

Get formatting rules for a specific template.

**Endpoint**: `GET /editor/templates/{template}/rules`

**Response**: `200 OK`
```json
[
  {
    "rule_id": "ieee_title",
    "template": "IEEE",
    "category": "Title",
    "description": "Title should use title case",
    "example": "Deep Learning for Image Recognition"
  }
]
```

### Validate Citations

Validate citation formatting.

**Endpoint**: `POST /editor/validate/citations`

**Request Body**:
```json
{
  "text": "As shown in [1], deep learning...",
  "template": "IEEE"
}
```

**Response**: `200 OK`
```json
{
  "citation_count": 1,
  "style_detected": "numbered",
  "consistent": true,
  "suggestions": []
}
```

## AI Recommendation API

### Search Papers

Search for academic papers.

**Endpoint**: `POST /recommendations/search`

**Request Body**:
```json
{
  "query": "deep learning image recognition",
  "limit": 10,
  "recommendation_type": "high_citation"
}
```

**Response**: `200 OK`
```json
[
  {
    "paper_id": "p1",
    "title": "Deep Residual Learning for Image Recognition",
    "authors": ["He, K.", "Zhang, X.", "Ren, S."],
    "abstract": "Deeper neural networks...",
    "year": 2016,
    "venue": "CVPR",
    "citations": 100000,
    "doi": "10.1109/CVPR.2016.90",
    "relevance_score": 0.95
  }
]
```

### Get Recommendations

Get paper recommendations based on content.

**Endpoint**: `POST /recommendations/recommend`

**Request Body**:
```json
{
  "context": "This paper presents a novel approach using neural networks...",
  "limit": 5
}
```

**Response**: `200 OK` - Returns list of recommended papers

### Optimize Sentence

Optimize a sentence for academic writing.

**Endpoint**: `POST /recommendations/optimize/sentence`

**Request Body**:
```json
{
  "sentence": "We use a lot of data to get good results."
}
```

**Response**: `200 OK`
```json
{
  "original_sentence": "We use a lot of data to get good results.",
  "optimized_sentence": "We utilize numerous data to obtain effective results.",
  "improvements": [
    "Replaced 'a lot of' with 'numerous' for formal tone",
    "Replaced 'use' with 'utilize' for formal tone"
  ],
  "formality_score": 0.9,
  "clarity_score": 0.8
}
```

### Optimize Paragraph

Optimize an entire paragraph.

**Endpoint**: `POST /recommendations/optimize/paragraph`

**Request Body**:
```json
{
  "paragraph": "We use a lot of data. The results show good performance."
}
```

**Response**: `200 OK`
```json
{
  "original": "We use a lot of data. The results show good performance.",
  "optimized": "We utilize numerous data. The results demonstrate effective performance.",
  "sentence_optimizations": [...],
  "overall_formality": 0.85,
  "overall_clarity": 0.80
}
```

### Get Citation Suggestions

Get citation suggestions for a topic.

**Endpoint**: `POST /recommendations/citations`

**Request Body**:
```json
{
  "topic": "deep learning"
}
```

**Response**: `200 OK`
```json
[
  "[1] He, K., Zhang, X., Ren, S. et al., \"Deep Residual Learning for Image Recognition\", CVPR, 2016."
]
```

### Get High-Impact Papers

Get high-impact papers in a field.

**Endpoint**: `GET /recommendations/papers/high-impact`

**Parameters**:
- `field` (query, optional): Research field
- `limit` (query, optional): Maximum papers to return (default: 10, max: 50)

**Response**: `200 OK` - Returns list of high-impact papers

### Get Recent Papers

Get recent publications in a field.

**Endpoint**: `GET /recommendations/papers/recent`

**Parameters**:
- `field` (query, optional): Research field
- `limit` (query, optional): Maximum papers to return (default: 10, max: 50)

**Response**: `200 OK` - Returns list of recent papers

## Error Responses

All endpoints may return the following error responses:

- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

Error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Rate Limiting

Currently no rate limiting is implemented. In production, implement appropriate rate limiting to prevent abuse.

## Best Practices

1. Always include proper error handling in client code
2. Use appropriate pagination for list endpoints
3. Include meaningful `changes_summary` when updating articles
4. Validate input data before sending requests
5. Cache responses when appropriate
6. Use bulk operations when possible to reduce API calls
