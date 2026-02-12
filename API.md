# 📡 API Documentation - DocAuthAI

Complete reference for the Document Authenticity Scanner API.

---

## Base URL

**Development:** `http://localhost:8000`  
**Production:** `https://your-app.onrender.com`

---

## Table of Contents

1. [Authentication](#authentication)
2. [Endpoints](#endpoints)
3. [Data Models](#data-models)
4. [Error Handling](#error-handling)
5. [Rate Limits](#rate-limits)
6. [Code Examples](#code-examples)

---

## Authentication

**Current Version:** No authentication required  
**Future:** API key authentication planned for production environments

To add authentication in production:

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

API_KEY = os.getenv("API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key
```

---

## Endpoints

### 1. Health Check

```http
GET /
```

Basic health check endpoint.

**Response:**
```json
{
  "status": "online",
  "service": "Document Authenticity Scanner API",
  "version": "1.0.0",
  "timestamp": "2024-02-11T12:00:00.000000"
}
```

**Status Codes:**
- `200 OK` - Service is running

---

### 2. Detailed Health Check

```http
GET /health
```

Comprehensive system health information.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-02-11T12:00:00.000000",
  "analyzer_ready": true,
  "supported_formats": ["PDF", "JPG", "PNG", "WEBP"],
  "synthid_available": false
}
```

**Fields:**
- `status` (string): Overall health status
- `timestamp` (string): Current server time (ISO 8601)
- `analyzer_ready` (boolean): Whether analysis engine is initialized
- `supported_formats` (array): List of supported file formats
- `synthid_available` (boolean): SynthID integration status

**Status Codes:**
- `200 OK` - Service is healthy
- `503 Service Unavailable` - Service is degraded

---

### 3. Analyze Document

```http
POST /analyze
```

Analyze uploaded document for authenticity.

**Request:**

**Content-Type:** `multipart/form-data`

**Form Data:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| file | File | Yes | Document to analyze (PDF, JPG, PNG, WEBP) |

**cURL Example:**
```bash
curl -X POST https://your-app.onrender.com/analyze \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/document.pdf"
```

**Response:**
```json
{
  "score": 78.4,
  "label": "Suspicious",
  "confidence": 0.86,
  "breakdown": {
    "metadata_anomaly": 30.0,
    "noise_uniformity": 45.2,
    "edge_consistency": 38.7,
    "compression_artifacts": 42.1
  },
  "metadata": {
    "format": "JPEG",
    "mode": "RGB",
    "size": [1920, 1080],
    "filename": "document.jpg",
    "has_exif": false,
    "exif_fields": 0
  },
  "synthid": {
    "synthid_enabled": false,
    "watermark_detected": null,
    "confidence": 0.0,
    "message": "SynthID integration pending - API credentials required"
  },
  "analyzed_at": "2024-02-11T12:00:00.000000"
}
```

**Status Codes:**
- `200 OK` - Analysis successful
- `400 Bad Request` - Invalid file or format
- `413 Payload Too Large` - File exceeds size limit (10MB)
- `500 Internal Server Error` - Analysis failed

**Error Response:**
```json
{
  "detail": "Unsupported file type: text/plain. Supported: PDF, JPG, PNG, WEBP"
}
```

---

## Data Models

### AnalysisResult

Main response object from `/analyze` endpoint.

| Field | Type | Description | Range |
|-------|------|-------------|-------|
| score | float | Authenticity score | 0.0 - 100.0 |
| label | string | Classification label | "Verified", "Suspicious", "AI Generated" |
| confidence | float | Confidence in classification | 0.0 - 1.0 |
| breakdown | Breakdown | Detailed scores per method | - |
| metadata | Metadata | File metadata | - |
| synthid | SynthID | SynthID detection results | - |
| analyzed_at | string | Analysis timestamp (ISO 8601) | - |

### Breakdown

Detailed scores from each detection method.

| Field | Type | Description | Range |
|-------|------|-------------|-------|
| metadata_anomaly | float | Metadata anomaly score | 0.0 - 100.0 |
| noise_uniformity | float | Noise pattern score | 0.0 - 100.0 |
| edge_consistency | float | Edge analysis score | 0.0 - 100.0 |
| compression_artifacts | float | Compression detection score | 0.0 - 100.0 |

**Interpretation:**
- Lower scores indicate more authentic
- Higher scores indicate more suspicious/AI-generated

### Metadata

Extracted file metadata.

| Field | Type | Description |
|-------|------|-------------|
| format | string | Image format (JPEG, PNG, etc.) |
| mode | string | Color mode (RGB, RGBA, etc.) |
| size | array | Image dimensions [width, height] |
| filename | string | Original filename |
| has_exif | boolean | Whether EXIF data exists |
| exif_fields | integer | Number of EXIF fields |

### SynthID

Google SynthID watermark detection results.

| Field | Type | Description |
|-------|------|-------------|
| synthid_enabled | boolean | Whether SynthID is active |
| watermark_detected | boolean\|null | Watermark found (null if disabled) |
| confidence | float | Detection confidence (0.0 - 1.0) |
| message | string | Human-readable status message |

---

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message here"
}
```

### Common Errors

**400 Bad Request**
```json
{
  "detail": "Unsupported file type: application/zip. Supported: PDF, JPG, PNG, WEBP"
}
```

**413 Payload Too Large**
```json
{
  "detail": "File too large. Maximum size: 10MB"
}
```

**500 Internal Server Error**
```json
{
  "detail": "Analysis failed: Unable to process image"
}
```

### Error Codes

| Code | Meaning | Common Cause |
|------|---------|--------------|
| 400 | Bad Request | Invalid file type, corrupted file |
| 413 | Payload Too Large | File exceeds 10MB limit |
| 422 | Unprocessable Entity | Missing required fields |
| 500 | Internal Server Error | Analysis engine error |
| 503 | Service Unavailable | Service is down or restarting |

---

## Rate Limits

**Current:** No rate limits (development)  
**Recommended for Production:** 100 requests/hour per IP

### Implementation Example

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/analyze")
@limiter.limit("100/hour")
async def analyze_document(request: Request, ...):
    ...
```

### Rate Limit Headers

When rate limiting is enabled:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1707667200
```

**429 Too Many Requests Response:**
```json
{
  "detail": "Rate limit exceeded. Try again in 3600 seconds."
}
```

---

## Code Examples

### JavaScript (Frontend)

```javascript
async function analyzeDocument(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('https://your-app.onrender.com/analyze', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('Authenticity Score:', result.score);
        console.log('Label:', result.label);
        console.log('Confidence:', result.confidence);
        
        return result;
    } catch (error) {
        console.error('Analysis failed:', error);
        throw error;
    }
}

// Usage
const fileInput = document.getElementById('fileInput');
fileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (file) {
        const result = await analyzeDocument(file);
        displayResults(result);
    }
});
```

### Python (Requests)

```python
import requests

def analyze_document(file_path):
    url = 'https://your-app.onrender.com/analyze'
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Authenticity Score: {result['score']}%")
        print(f"Label: {result['label']}")
        print(f"Confidence: {result['confidence']}")
        return result
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        return None

# Usage
result = analyze_document('path/to/document.pdf')
```

### cURL

```bash
# Basic analysis
curl -X POST https://your-app.onrender.com/analyze \
  -F "file=@document.pdf"

# With verbose output
curl -v -X POST https://your-app.onrender.com/analyze \
  -F "file=@document.jpg"

# Save response to file
curl -X POST https://your-app.onrender.com/analyze \
  -F "file=@image.png" \
  -o result.json
```

### Node.js (Axios)

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

async function analyzeDocument(filePath) {
    const form = new FormData();
    form.append('file', fs.createReadStream(filePath));
    
    try {
        const response = await axios.post(
            'https://your-app.onrender.com/analyze',
            form,
            {
                headers: form.getHeaders()
            }
        );
        
        console.log('Score:', response.data.score);
        console.log('Label:', response.data.label);
        return response.data;
    } catch (error) {
        console.error('Error:', error.response?.data || error.message);
        throw error;
    }
}

// Usage
analyzeDocument('./document.pdf')
    .then(result => console.log('Result:', result))
    .catch(error => console.error('Failed:', error));
```

### Python (aiohttp - Async)

```python
import aiohttp
import asyncio

async def analyze_document_async(file_path):
    url = 'https://your-app.onrender.com/analyze'
    
    async with aiohttp.ClientSession() as session:
        with open(file_path, 'rb') as f:
            data = aiohttp.FormData()
            data.add_field('file', f, filename=file_path)
            
            async with session.post(url, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"Score: {result['score']}%")
                    return result
                else:
                    error = await response.json()
                    print(f"Error: {error}")
                    return None

# Usage
asyncio.run(analyze_document_async('document.pdf'))
```

---

## Response Time

**Typical Response Times:**
- Small images (< 1MB): 1-2 seconds
- Large images (5-10MB): 2-4 seconds
- PDFs: 2-5 seconds (depends on page count)

**Factors Affecting Speed:**
- File size
- Image dimensions
- Server load
- Cold start (Render free tier: +15-30s first request)

---

## Best Practices

### 1. File Size Optimization

```javascript
// Compress images before upload (client-side)
async function compressImage(file) {
    const options = {
        maxSizeMB: 5,
        maxWidthOrHeight: 1920,
        useWebWorker: true
    };
    
    const compressed = await imageCompression(file, options);
    return compressed;
}
```

### 2. Error Handling

```javascript
// Comprehensive error handling
async function analyzeWithRetry(file, maxRetries = 3) {
    for (let i = 0; i < maxRetries; i++) {
        try {
            return await analyzeDocument(file);
        } catch (error) {
            if (error.response?.status === 429) {
                // Rate limited - wait before retry
                await new Promise(resolve => setTimeout(resolve, 5000));
            } else if (i === maxRetries - 1) {
                throw error;
            }
        }
    }
}
```

### 3. Progress Tracking

```javascript
// Track upload progress
async function analyzeWithProgress(file, onProgress) {
    const xhr = new XMLHttpRequest();
    
    return new Promise((resolve, reject) => {
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const progress = (e.loaded / e.total) * 100;
                onProgress(progress);
            }
        });
        
        xhr.addEventListener('load', () => {
            if (xhr.status === 200) {
                resolve(JSON.parse(xhr.response));
            } else {
                reject(new Error(`HTTP ${xhr.status}`));
            }
        });
        
        xhr.open('POST', 'https://your-app.onrender.com/analyze');
        const formData = new FormData();
        formData.append('file', file);
        xhr.send(formData);
    });
}
```

---

## WebSocket Support (Future)

Real-time analysis updates (planned feature):

```javascript
const ws = new WebSocket('wss://your-app.onrender.com/ws');

ws.onmessage = (event) => {
    const update = JSON.parse(event.data);
    console.log('Analysis progress:', update.stage, update.progress);
};

// Send file for analysis
ws.send(JSON.stringify({
    action: 'analyze',
    file_id: 'abc123'
}));
```

---

## Batch Processing (Future)

Analyze multiple documents in one request:

```http
POST /analyze/batch
```

```json
{
  "files": [
    {"file_id": "1", "url": "https://..."},
    {"file_id": "2", "url": "https://..."}
  ]
}
```

---

## Changelog

### v1.0.0 (2024-02-11)
- Initial API release
- Basic authenticity detection
- PDF and image support
- Four detection methods
- SynthID placeholder structure

### Planned Features
- [ ] API key authentication
- [ ] Rate limiting
- [ ] Batch processing
- [ ] WebSocket support
- [ ] SynthID integration
- [ ] Advanced ML models
- [ ] Custom model upload

---

## Support

For API issues or questions:

- **Documentation:** [GitHub Wiki](https://github.com/yourusername/doc-scanner/wiki)
- **Issues:** [GitHub Issues](https://github.com/yourusername/doc-scanner/issues)
- **Email:** your.email@example.com

---

**API Documentation Version:** 1.0.0  
**Last Updated:** February 11, 2024
