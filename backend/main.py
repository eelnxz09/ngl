"""
AI Document Authenticity Scanner - Backend API
Analyzes documents for authenticity using multiple detection methods
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import io
import os
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
    allow_origins=["*"],  # For production, replace with your GitHub Pages URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DocumentAnalyzer:
    def __init__(self):
        self.ai_patterns = {
            "noise_threshold": 0.15,
            "edge_variance_threshold": 0.25,
            "compression_artifacts_threshold": 0.3,
            "synthid_enabled": False
        }

    def analyze_metadata(self, image: Image.Image, filename: str):
        metadata = {
            "format": image.format,
            "mode": image.mode,
            "size": image.size,
            "filename": filename
        }

        exif = image.getexif()
        metadata["has_exif"] = bool(exif)
        metadata["exif_fields"] = len(exif) if exif else 0

        anomaly_score = 0.0
        if not metadata["has_exif"]:
            anomaly_score += 0.3
        if metadata["mode"] == "RGB" and metadata["format"] in ["PNG", "WEBP"]:
            anomaly_score += 0.1

        return metadata, min(anomaly_score, 1.0)

    def analyze_noise_patterns(self, image: Image.Image):
        gray = image.convert("L")
        img_array = np.array(gray)

        window_size = 8
        variances = []

        for i in range(0, img_array.shape[0] - window_size, window_size):
            for j in range(0, img_array.shape[1] - window_size, window_size):
                window = img_array[i:i+window_size, j:j+window_size]
                variances.append(np.var(window))

        if variances:
            mean_var = np.mean(variances)
            std_var = np.std(variances)
            cv = std_var / mean_var if mean_var > 0 else 0
            return 1.0 - min(cv / self.ai_patterns["noise_threshold"], 1.0)

        return 0.5

    def analyze_edge_consistency(self, image: Image.Image):
        gray = image.convert("L")
        img_array = np.array(gray)

        sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
        sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])

        edges_x = self._convolve2d(img_array, sobel_x)
        edges_y = self._convolve2d(img_array, sobel_y)

        edge_magnitude = np.sqrt(edges_x**2 + edges_y**2)

        edge_variance = np.var(edge_magnitude)
        edge_mean = np.mean(edge_magnitude)

        if edge_mean > 0:
            edge_cv = edge_variance / (edge_mean ** 2)
            return 1.0 - min(edge_cv / self.ai_patterns["edge_variance_threshold"], 1.0)

        return 0.5

    def _convolve2d(self, image: np.ndarray, kernel: np.ndarray):
        output = np.zeros_like(image, dtype=float)
        k_height, k_width = kernel.shape
        pad_h, pad_w = k_height // 2, k_width // 2

        for i in range(pad_h, image.shape[0] - pad_h):
            for j in range(pad_w, image.shape[1] - pad_w):
                region = image[i-pad_h:i+pad_h+1, j-pad_w:j+pad_w+1]
                output[i, j] = np.sum(region * kernel)

        return output

    def analyze_compression_artifacts(self, image: Image.Image):
        imagehash.average_hash(image)

        stats = ImageStat.Stat(image)

        if len(stats.stddev) >= 3:
            avg_stddev = sum(stats.stddev[:3]) / 3
            return 1.0 - min(avg_stddev / 50.0, 1.0)

        return 0.5

    def calculate_authenticity_score(self, metadata_score, noise_score, edge_score, compression_score):
        weights = {
            "metadata": 0.2,
            "noise": 0.3,
            "edge": 0.3,
            "compression": 0.2
        }

        suspicion_score = (
            metadata_score * weights["metadata"] +
            noise_score * weights["noise"] +
            edge_score * weights["edge"] +
            compression_score * weights["compression"]
        )

        authenticity_score = (1.0 - suspicion_score) * 100

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
            "score": round(authenticity_score, 1),
            "label": label,
            "confidence": round(confidence, 2)
        }


analyzer = DocumentAnalyzer()


@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Document Authenticity Scanner API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        if file.content_type == "application/pdf":
            pdf_file = io.BytesIO(contents)
            pdf = pdfium.PdfDocument(pdf_file)

            if len(pdf) == 0:
                raise HTTPException(status_code=400, detail="PDF has no pages")

            page = pdf[0]
            pil_image = page.render(scale=2).to_pil()
            pdf.close()

        elif file.content_type in ["image/jpeg", "image/png", "image/webp", "image/jpg"]:
            pil_image = Image.open(io.BytesIO(contents))

        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Supported: PDF, JPG, PNG, WEBP"
            )

        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")

        metadata, metadata_score = analyzer.analyze_metadata(pil_image, file.filename)
        noise_score = analyzer.analyze_noise_patterns(pil_image)
        edge_score = analyzer.analyze_edge_consistency(pil_image)
        compression_score = analyzer.analyze_compression_artifacts(pil_image)

        result = analyzer.calculate_authenticity_score(
            metadata_score,
            noise_score,
            edge_score,
            compression_score
        )

        result["metadata"] = metadata
        result["analyzed_at"] = datetime.now().isoformat()

        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "analyzer_ready": True,
        "supported_formats": ["PDF", "JPG", "PNG", "WEBP"]
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
