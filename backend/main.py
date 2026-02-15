"""
AI Document Authenticity Scanner - Hybrid AI + Heuristic Backend
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import io
import os
import numpy as np
import requests
import base64
from PIL import Image, ImageStat
from datetime import datetime
import pypdfium2 as pdfium

# ==============================
# 🔐 YOUR CREDENTIALS
# ==============================
API_USER = "301528576"
API_SECRET = "zWH9kRpV8uZezQqkUnkqx3fRqPcZiAah"
AI_DETECTOR_URL = "https://api.sightengine.com/1.0/check.json"
# ==============================

app = FastAPI(
    title="Document Authenticity Scanner API",
    description="Hybrid AI + Heuristic document verification",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DocumentAnalyzer:
    def __init__(self):
        self.ai_patterns = {
            "noise_threshold": 0.15,
            "edge_variance_threshold": 0.25,
        }

    # -------------------------
    # AI MODEL DETECTION
    # -------------------------
    def analyze_ai_model(self, image: Image.Image):
    try:
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        buffered.seek(0)

        response = requests.post(
            "https://api.sightengine.com/1.0/check.json",
            files={"media": ("image.jpg", buffered, "image/jpeg")},
            data={
                "models": "genai",
                "api_user": "301528576",
                "api_secret": "zWH9kRpV8uZezQqkUnkqx3fRqPcZiAah"
            },
            timeout=15
        )

        if response.status_code == 200:
            result = response.json()

            # Sightengine returns something like:
            # result["type"]["ai_generated"]
            ai_probability = result.get("type", {}).get("ai_generated", 0.5)

            return float(ai_probability)

    except Exception:
        pass

    return 0.5
 # fallback neutral

    # -------------------------
    # Metadata Analysis
    # -------------------------
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

    # -------------------------
    # Noise Analysis
    # -------------------------
    def analyze_noise_patterns(self, image: Image.Image):
        gray = image.convert("L")
        img_array = np.array(gray)

        window_size = 8
        variances = []

        h, w = img_array.shape

        for i in range(0, h - window_size, window_size):
            for j in range(0, w - window_size, window_size):
                window = img_array[i:i+window_size, j:j+window_size]
                variances.append(np.var(window))

        if variances:
            mean_var = np.mean(variances)
            std_var = np.std(variances)
            cv = std_var / mean_var if mean_var > 0 else 0
            return 1.0 - min(cv / self.ai_patterns["noise_threshold"], 1.0)

        return 0.5

    # -------------------------
    # Edge Analysis
    # -------------------------
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

        padded = np.pad(image, ((pad_h, pad_h), (pad_w, pad_w)), mode='edge')

        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                region = padded[i:i+k_height, j:j+k_width]
                output[i, j] = np.sum(region * kernel)

        return output

    # -------------------------
    # Compression Analysis
    # -------------------------
    def analyze_compression_artifacts(self, image: Image.Image):
        stats = ImageStat.Stat(image)

        if len(stats.stddev) >= 3:
            avg_stddev = sum(stats.stddev[:3]) / 3
            return 1.0 - min(avg_stddev / 50.0, 1.0)

        return 0.5

    # -------------------------
    # HYBRID SCORING
    # -------------------------
    def calculate_authenticity_score(
        self,
        metadata_score,
        noise_score,
        edge_score,
        compression_score,
        ai_probability
    ):

        heuristic_suspicion = (
            metadata_score * 0.2 +
            noise_score * 0.3 +
            edge_score * 0.3 +
            compression_score * 0.2
        )

        # 60% AI model weight
        combined_suspicion = (
            heuristic_suspicion * 0.4 +
            ai_probability * 0.6
        )

        authenticity_score = (1 - combined_suspicion) * 100

        if authenticity_score >= 75:
            label = "Verified"
        elif authenticity_score >= 50:
            label = "Suspicious"
        else:
            label = "AI Generated"

        return {
            "score": round(authenticity_score, 1),
            "label": label,
            "confidence": round(abs(authenticity_score - 50) / 50, 2)
        }


analyzer = DocumentAnalyzer()


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

        elif file.content_type in [
            "image/jpeg",
            "image/png",
            "image/webp",
            "image/jpg"
        ]:
            pil_image = Image.open(io.BytesIO(contents))
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type"
            )

        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")

        metadata, metadata_score = analyzer.analyze_metadata(
            pil_image, file.filename
        )

        noise_score = analyzer.analyze_noise_patterns(pil_image)
        edge_score = analyzer.analyze_edge_consistency(pil_image)
        compression_score = analyzer.analyze_compression_artifacts(pil_image)

        # 🔥 AI MODEL CALL
        ai_probability = analyzer.analyze_ai_model(pil_image)

        result = analyzer.calculate_authenticity_score(
            metadata_score,
            noise_score,
            edge_score,
            compression_score,
            ai_probability
        )

        return JSONResponse(content={
            "score": result["score"],
            "label": result["label"],
            "confidence": result["confidence"],
            "ai_model_probability": round(ai_probability * 100, 1),
            "analyzed_at": datetime.now().isoformat()
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
