"""
AI Document Authenticity Scanner - Backend API
Analyzes documents for authenticity using multiple detection methods
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import io
import hashlib
import numpy as np
from PIL import Image, ImageStat
from datetime import datetime
import pypdfium2 as pdfium
from typing import Dict, Any
import imagehash

app = FastAPI(
    title="Document Authenticity Scanner API",
    description="AI-powered document verification and authenticity detection",
    version="1.0.0"
)

# CORS configuration for GitHub Pages frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your GitHub Pages URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DocumentAnalyzer:
    """Core document analysis engine"""
    
    def __init__(self):
        self.ai_patterns = self._load_ai_detection_patterns()
    
    def _load_ai_detection_patterns(self) -> Dict[str, Any]:
        """
        Placeholder for AI-generated content detection patterns.
        In production, this would load trained ML models or connect to APIs like SynthID.
        """
        return {
            'noise_threshold': 0.15,
            'edge_variance_threshold': 0.25,
            'compression_artifacts_threshold': 0.3,
            'synthid_enabled': False  # Placeholder for future SynthID integration
        }
    
    def analyze_metadata(self, image: Image.Image, filename: str) -> Dict[str, Any]:
        """Extract and analyze image metadata for anomalies"""
        metadata = {
            'format': image.format,
            'mode': image.mode,
            'size': image.size,
            'filename': filename
        }
        
        # Check EXIF data
        exif = image.getexif()
        if exif:
            metadata['has_exif'] = True
            metadata['exif_fields'] = len(exif)
        else:
            metadata['has_exif'] = False
            metadata['exif_fields'] = 0
        
        # Metadata anomaly score (lack of metadata can indicate AI generation)
        anomaly_score = 0.0
        if not metadata['has_exif']:
            anomaly_score += 0.3
        if metadata['mode'] == 'RGB' and metadata['format'] in ['PNG', 'WEBP']:
            anomaly_score += 0.1  # AI generators often use PNG
        
        return metadata, min(anomaly_score, 1.0)
    
    def analyze_noise_patterns(self, image: Image.Image) -> float:
        """
        Analyze noise distribution to detect AI-generated images.
        Real photos have natural noise; AI images often have uniform or absent noise.
        """
        # Convert to grayscale for noise analysis
        gray = image.convert('L')
        img_array = np.array(gray)
        
        # Calculate local variance (noise indicator)
        # Use a sliding window approach
        window_size = 8
        variances = []
        
        for i in range(0, img_array.shape[0] - window_size, window_size):
            for j in range(0, img_array.shape[1] - window_size, window_size):
                window = img_array[i:i+window_size, j:j+window_size]
                variances.append(np.var(window))
        
        # Calculate coefficient of variation of variances
        if len(variances) > 0:
            mean_var = np.mean(variances)
            std_var = np.std(variances)
            cv = std_var / mean_var if mean_var > 0 else 0
            
            # Low CV indicates uniform noise (AI characteristic)
            # High CV indicates natural noise variation (authentic)
            ai_score = 1.0 - min(cv / self.ai_patterns['noise_threshold'], 1.0)
            return ai_score
        
        return 0.5  # Uncertain
    
    def analyze_edge_consistency(self, image: Image.Image) -> float:
        """
        Detect AI generation through edge analysis.
        AI-generated images often have suspiciously smooth or perfect edges.
        """
        # Convert to grayscale
        gray = image.convert('L')
        img_array = np.array(gray)
        
        # Sobel edge detection
        sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
        sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
        
        # Apply Sobel filters (simplified implementation)
        edges_x = self._convolve2d(img_array, sobel_x)
        edges_y = self._convolve2d(img_array, sobel_y)
        
        edge_magnitude = np.sqrt(edges_x**2 + edges_y**2)
        
        # Analyze edge strength distribution
        edge_variance = np.var(edge_magnitude)
        edge_mean = np.mean(edge_magnitude)
        
        # Very low variance relative to mean suggests AI processing
        if edge_mean > 0:
            edge_cv = edge_variance / (edge_mean ** 2)
            ai_score = 1.0 - min(edge_cv / self.ai_patterns['edge_variance_threshold'], 1.0)
            return ai_score
        
        return 0.5
    
    def _convolve2d(self, image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        """Simple 2D convolution for edge detection"""
        output = np.zeros_like(image, dtype=float)
        k_height, k_width = kernel.shape
        pad_h, pad_w = k_height // 2, k_width // 2
        
        for i in range(pad_h, image.shape[0] - pad_h):
            for j in range(pad_w, image.shape[1] - pad_w):
                region = image[i-pad_h:i+pad_h+1, j-pad_w:j+pad_w+1]
                output[i, j] = np.sum(region * kernel)
        
        return output
    
    def analyze_compression_artifacts(self, image: Image.Image) -> float:
        """
        Detect manipulation through compression artifact analysis.
        Multiple saves/edits create detectable compression patterns.
        """
        # Calculate image hash for similarity detection
        hash_val = imagehash.average_hash(image)
        
        # Analyze color distribution uniformity
        stats = ImageStat.Stat(image)
        
        # Get standard deviation for each channel
        if len(stats.stddev) >= 3:
            # High uniformity in compression patterns suggests AI generation
            avg_stddev = sum(stats.stddev[:3]) / 3
            # Lower stddev can indicate compression or AI generation
            compression_score = 1.0 - min(avg_stddev / 50.0, 1.0)
            return compression_score
        
        return 0.5
    
    def detect_synthid_watermark(self, image: Image.Image) -> Dict[str, Any]:
        """
        Placeholder for Google SynthID watermark detection.
        This is where you would integrate the actual SynthID API when available.
        
        Returns:
            Dict with watermark detection results
        """
        # TODO: Integrate actual SynthID API
        # For now, return placeholder structure
        return {
            'synthid_enabled': False,
            'watermark_detected': None,
            'confidence': 0.0,
            'message': 'SynthID integration pending - API credentials required'
        }
    
    def calculate_authenticity_score(
        self,
        metadata_score: float,
        noise_score: float,
        edge_score: float,
        compression_score: float
    ) -> Dict[str, Any]:
        """
        Combine all detection methods into final authenticity score.
        Lower score = more likely authentic
        Higher score = more likely AI-generated or manipulated
        """
        # Weighted combination of scores
        weights = {
            'metadata': 0.2,
            'noise': 0.3,
            'edge': 0.3,
            'compression': 0.2
        }
        
        suspicion_score = (
            metadata_score * weights['metadata'] +
            noise_score * weights['noise'] +
            edge_score * weights['edge'] +
            compression_score * weights['compression']
        )
        
        # Convert suspicion to authenticity (invert)
        authenticity_score = (1.0 - suspicion_score) * 100
        
        # Determine label
        if authenticity_score >= 75:
            label = "Verified"
            confidence = min((authenticity_score - 75) / 25, 1.0)
        elif authenticity_score >= 50:
            label = "Suspicious"
            confidence = 0.7
        else:
            label = "AI Generated"
            confidence = min((50 - authenticity_score) / 50, 1.0)
        
        return {
            'score': round(authenticity_score, 1),
            'label': label,
            'confidence': round(confidence, 2),
            'breakdown': {
                'metadata_anomaly': round(metadata_score * 100, 1),
                'noise_uniformity': round(noise_score * 100, 1),
                'edge_consistency': round(edge_score * 100, 1),
                'compression_artifacts': round(compression_score * 100, 1)
            }
        }


# Initialize analyzer
analyzer = DocumentAnalyzer()


@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "online",
        "service": "Document Authenticity Scanner API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)):
    """
    Analyze uploaded document for authenticity.
    
    Accepts: PDF, JPG, PNG, WEBP
    Returns: Authenticity score, label, and detailed breakdown
    """
    try:
        # Read file
        contents = await file.read()
        
        # Check file type
        if file.content_type == "application/pdf":
            # Convert PDF first page to image
            pdf_file = io.BytesIO(contents)
            pdf = pdfium.PdfDocument(pdf_file)
            
            if len(pdf) == 0:
                raise HTTPException(status_code=400, detail="PDF has no pages")
            
            page = pdf[0]
            pil_image = page.render(scale=2).to_pil()
            pdf.close()
            
        elif file.content_type in ["image/jpeg", "image/png", "image/webp", "image/jpg"]:
            # Load image directly
            pil_image = Image.open(io.BytesIO(contents))
            
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.content_type}. Supported: PDF, JPG, PNG, WEBP"
            )
        
        # Ensure RGB mode
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Run all analysis methods
        metadata, metadata_score = analyzer.analyze_metadata(pil_image, file.filename)
        noise_score = analyzer.analyze_noise_patterns(pil_image)
        edge_score = analyzer.analyze_edge_consistency(pil_image)
        compression_score = analyzer.analyze_compression_artifacts(pil_image)
        
        # Check for SynthID watermark (placeholder)
        synthid_result = analyzer.detect_synthid_watermark(pil_image)
        
        # Calculate final score
        result = analyzer.calculate_authenticity_score(
            metadata_score,
            noise_score,
            edge_score,
            compression_score
        )
        
        # Add metadata and SynthID info
        result['metadata'] = metadata
        result['synthid'] = synthid_result
        result['analyzed_at'] = datetime.now().isoformat()
        
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Detailed health check for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "analyzer_ready": True,
        "supported_formats": ["PDF", "JPG", "PNG", "WEBP"],
        "synthid_available": analyzer.ai_patterns['synthid_enabled']
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
