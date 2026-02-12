# 🔍 DocAuthAI - AI Document Authenticity Scanner

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688)

**Production-ready AI-powered document verification system**

[Live Demo](#) | [Documentation](#features) | [Report Bug](#) | [Request Feature](#)

</div>

---

## 📋 Overview

DocAuthAI is a sophisticated document authenticity scanner that uses AI and computer vision techniques to detect AI-generated content, manipulated documents, and verify authenticity. Built with a modern tech stack featuring FastAPI backend and vanilla JavaScript frontend, it's designed for easy deployment and scalability.

### 🎯 Key Features

- **Multi-Layer AI Detection** - Analyzes documents through 4+ detection methods
- **Real-time Processing** - Instant analysis with visual feedback
- **Production Architecture** - Separate frontend/backend for scalable deployment
- **SynthID Ready** - Structured for Google SynthID watermark integration
- **Professional UI** - Modern, responsive interface with smooth animations
- **Detailed Reports** - Comprehensive breakdown of all detection methods
- **History Tracking** - Local storage of analysis history
- **Downloadable Reports** - Export results as text reports

---

## 🏗️ Architecture

```
doc-scanner/
├── frontend/              # Static web interface (GitHub Pages)
│   ├── index.html        # Main HTML structure
│   ├── styles.css        # Modern, brutalist design
│   └── script.js         # Frontend logic & API integration
│
├── backend/              # FastAPI server (Render/Railway)
│   ├── main.py          # API endpoints & analysis engine
│   └── requirements.txt # Python dependencies
│
└── docs/                # Documentation
    ├── DEPLOYMENT.md    # Step-by-step deployment guide
    └── API.md           # API documentation
```

---

## 🧠 Detection Methods

### 1. **Metadata Anomaly Detection**
- Analyzes EXIF data presence and completeness
- Checks file format inconsistencies
- Detects missing camera information (common in AI-generated images)

### 2. **Noise Pattern Analysis**
- Examines pixel-level noise distribution
- Identifies unnatural uniformity (AI characteristic)
- Uses coefficient of variation for detection

### 3. **Edge Consistency Detection**
- Applies Sobel edge detection
- Analyzes edge smoothness and artifacts
- Detects AI's tendency for over-smoothing

### 4. **Compression Artifact Analysis**
- Examines color distribution patterns
- Detects re-compression indicators
- Identifies manipulation signatures

### 5. **SynthID Watermark Detection** (Placeholder)
- Structured for future Google SynthID API integration
- Placeholder implementation ready for credentials
- Designed for seamless plug-and-play activation

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js (optional, for local testing)
- Git

### Local Development

**1. Clone the Repository**
```bash
git clone https://github.com/yourusername/doc-scanner.git
cd doc-scanner
```

**2. Setup Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
Backend will run on `http://localhost:8000`

**3. Setup Frontend**
```bash
cd frontend
# Option 1: Simple HTTP server (Python)
python -m http.server 3000

# Option 2: Node.js http-server
npx http-server -p 3000
```
Frontend will run on `http://localhost:3000`

**4. Update API URL**
In `frontend/script.js`, update:
```javascript
const CONFIG = {
    API_URL: 'http://localhost:8000',  // Your backend URL
    ...
};
```

---

## 🌐 Deployment

### Deploy Backend (Render)

1. **Create Render Account** → [render.com](https://render.com)

2. **New Web Service** → Connect GitHub repo

3. **Configuration:**
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Python Version:** 3.9+

4. **Deploy** → Copy your service URL (e.g., `https://your-app.onrender.com`)

### Deploy Frontend (GitHub Pages)

1. **Update API URL** in `frontend/script.js`:
```javascript
const CONFIG = {
    API_URL: 'https://your-app.onrender.com',  // Your Render URL
    ...
};
```

2. **Push to GitHub:**
```bash
git add .
git commit -m "Deploy to GitHub Pages"
git push origin main
```

3. **Enable GitHub Pages:**
   - Go to repo **Settings** → **Pages**
   - Source: **Deploy from branch**
   - Branch: **main** → Folder: **`/frontend`**
   - Save

4. **Access** → `https://yourusername.github.io/doc-scanner/`

---

## 📊 API Documentation

### Endpoints

#### `GET /`
Health check endpoint
```json
{
  "status": "online",
  "service": "Document Authenticity Scanner API",
  "version": "1.0.0"
}
```

#### `POST /analyze`
Analyze document for authenticity

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `file` (PDF, JPG, PNG, WEBP)

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
    "has_exif": false
  },
  "synthid": {
    "synthid_enabled": false,
    "message": "SynthID integration pending"
  }
}
```

#### `GET /health`
Detailed health check
```json
{
  "status": "healthy",
  "analyzer_ready": true,
  "supported_formats": ["PDF", "JPG", "PNG", "WEBP"],
  "synthid_available": false
}
```

---

## 🎨 UI Features

### Design Highlights
- **Dark Brutalist Theme** - Modern, high-contrast interface
- **Smooth Animations** - Loading states, score animations, progress bars
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Real-time Feedback** - Visual scanning animation during analysis
- **Circular Score Meter** - Animated ring showing authenticity percentage
- **Detailed Breakdown** - Visual progress bars for each detection method

### User Flow
1. **Upload** → Drag & drop or click to browse
2. **Preview** → Instant file preview with metadata
3. **Analysis** → Animated scanning with real-time progress
4. **Results** → Score, label, confidence, and detailed breakdown
5. **Report** → Downloadable text report
6. **History** → Local storage of recent scans

---

## 🔧 Technology Stack

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Custom properties, animations, grid layout
- **JavaScript (ES6+)** - Modern vanilla JS, no frameworks
- **LocalStorage API** - History persistence
- **Fetch API** - Backend communication

### Backend
- **FastAPI** - Modern Python web framework
- **Pillow (PIL)** - Image processing
- **NumPy** - Numerical computations
- **pypdfium2** - PDF handling
- **ImageHash** - Perceptual hashing
- **Uvicorn** - ASGI server

---

## 🔬 How It Works

### Analysis Pipeline

```
Document Upload
    ↓
PDF → Image Conversion (if PDF)
    ↓
Parallel Analysis:
├─ Metadata Extraction
├─ Noise Pattern Analysis
├─ Edge Detection (Sobel)
├─ Compression Analysis
└─ SynthID Check (placeholder)
    ↓
Score Calculation (Weighted Average)
    ↓
Label Assignment:
• 75-100% → Verified
• 50-74%  → Suspicious  
• 0-49%   → AI Generated
    ↓
Return Results with Confidence
```

### Scoring Algorithm

```python
suspicion_score = (
    metadata_score    * 0.2 +
    noise_score       * 0.3 +
    edge_score        * 0.3 +
    compression_score * 0.2
)

authenticity_score = (1.0 - suspicion_score) * 100
```

---

## 🛠️ Development

### Adding SynthID Integration

When Google SynthID API becomes available:

**1. Update `backend/main.py`:**
```python
def detect_synthid_watermark(self, image: Image.Image) -> Dict[str, Any]:
    """
    Google SynthID watermark detection
    """
    # Import SynthID SDK
    from synthid import SynthIDDetector
    
    detector = SynthIDDetector(api_key=os.getenv('SYNTHID_API_KEY'))
    result = detector.detect(image)
    
    return {
        'synthid_enabled': True,
        'watermark_detected': result.detected,
        'confidence': result.confidence,
        'message': 'SynthID watermark detected' if result.detected else 'No watermark found'
    }
```

**2. Add Environment Variable:**
```bash
SYNTHID_API_KEY=your_api_key_here
```

**3. Update `ai_patterns`:**
```python
self.ai_patterns = {
    ...
    'synthid_enabled': True
}
```

### Extending Detection Methods

Add new detection methods in `DocumentAnalyzer` class:

```python
def analyze_new_method(self, image: Image.Image) -> float:
    """
    Your new detection method
    Returns: AI suspicion score (0.0 - 1.0)
    """
    # Your implementation
    return score
```

Update `calculate_authenticity_score` to include new method.

---

## 📈 Performance

- **Analysis Time:** 2-4 seconds per document
- **Supported File Size:** Up to 10MB
- **Concurrent Requests:** Configurable (default: unlimited)
- **Image Processing:** Optimized with NumPy vectorization

### Optimization Tips
- Use image resizing for very large files
- Implement caching for repeated analyses
- Add request rate limiting for production
- Use CDN for frontend static files

---

## 🔒 Security Considerations

1. **File Validation** - Strict type and size checking
2. **CORS Configuration** - Update for production domains
3. **Rate Limiting** - Implement in production (not included)
4. **API Authentication** - Add authentication for sensitive deployments
5. **Input Sanitization** - All uploads are validated

### Production Hardening

```python
# Add to backend/main.py
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

@app.post("/analyze", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def analyze_document(...):
    ...
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Areas for Contribution
- Additional detection methods
- Performance optimizations
- UI/UX improvements
- Test coverage
- Documentation improvements
- SynthID integration (when available)

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **Anthropic** - Claude AI assistance
- **FastAPI** - Modern Python web framework
- **Google** - SynthID watermark technology (pending integration)
- **Render** - Backend hosting platform
- **GitHub Pages** - Frontend hosting

---

## 📧 Contact

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your Profile](https://linkedin.com/in/yourprofile)
- Email: your.email@example.com

**Project Link:** [https://github.com/yourusername/doc-scanner](https://github.com/yourusername/doc-scanner)

---

## 🚧 Roadmap

- [x] Core detection engine
- [x] Frontend interface
- [x] API implementation
- [x] Deployment guides
- [ ] SynthID integration
- [ ] Batch processing
- [ ] Advanced ML models
- [ ] Mobile app (React Native)
- [ ] Browser extension
- [ ] Enterprise features

---

<div align="center">

**Built with ❤️ for document authenticity**

⭐ Star this repo if you find it useful!

</div>
