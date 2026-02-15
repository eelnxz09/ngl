// Configuration
const CONFIG = {
    // Railway backend URL (NO trailing slash)
    API_URL: 'https://ngl-production-2009.up.railway.app',
    MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
    SUPPORTED_TYPES: ['application/pdf', 'image/jpeg', 'image/png', 'image/webp']
};

// DOM Elements
const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
const browseBtn = document.getElementById('browseBtn');
const uploadSection = document.getElementById('uploadSection');
const analysisSection = document.getElementById('analysisSection');
const loadingState = document.getElementById('loadingState');
const resultsContainer = document.getElementById('resultsContainer');
const previewImage = document.getElementById('previewImage');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const newScanBtn = document.getElementById('newScanBtn');
const analyzeAnotherBtn = document.getElementById('analyzeAnotherBtn');
const downloadReportBtn = document.getElementById('downloadReportBtn');
const clearHistoryBtn = document.getElementById('clearHistoryBtn');
const historyList = document.getElementById('historyList');

// State
let currentAnalysis = null;
let analysisHistory = JSON.parse(localStorage.getItem('analysisHistory')) || [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    renderHistory();
    checkAPIConnection();
});

// Setup Event Listeners
function setupEventListeners() {
    // Upload zone interactions
    uploadZone.addEventListener('click', () => fileInput.click());
    browseBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.click();
    });
    
    // File selection
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop
    uploadZone.addEventListener('dragover', handleDragOver);
    uploadZone.addEventListener('dragleave', handleDragLeave);
    uploadZone.addEventListener('drop', handleDrop);
    
    // Button actions
    newScanBtn.addEventListener('click', resetToUpload);
    analyzeAnotherBtn.addEventListener('click', resetToUpload);
    downloadReportBtn.addEventListener('click', downloadReport);
    clearHistoryBtn.addEventListener('click', clearHistory);
}

// Check API Connection
async function checkAPIConnection() {
    try {
        const response = await fetch(`${CONFIG.API_URL}/health`);
        if (!response.ok) throw new Error('API not responding');
        console.log('✅ API connection successful');
    } catch (error) {
        console.warn('⚠️ Could not connect to API. Make sure the backend is running.');
        showNotification('Backend API not connected. Please start the server.', 'warning');
    }
}

// File Handling
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) processFile(file);
}

function handleDragOver(e) {
    e.preventDefault();
    uploadZone.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadZone.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadZone.classList.remove('dragover');
    
    const file = e.dataTransfer.files[0];
    if (file) processFile(file);
}

function processFile(file) {
    // Validate file
    if (!CONFIG.SUPPORTED_TYPES.includes(file.type)) {
        showNotification('Unsupported file type. Please upload PDF, JPG, PNG, or WEBP.', 'error');
        return;
    }
    
    if (file.size > CONFIG.MAX_FILE_SIZE) {
        showNotification('File too large. Maximum size is 10MB.', 'error');
        return;
    }
    
    // Show preview
    displayFilePreview(file);
    
    // Start analysis
    analyzeDocument(file);
}

function displayFilePreview(file) {
    // Show analysis section
    uploadSection.style.display = 'none';
    analysisSection.style.display = 'block';
    loadingState.style.display = 'block';
    resultsContainer.style.display = 'none';
    
    // Set file info
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    
    // Show preview image
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
    };
    
    if (file.type.startsWith('image/')) {
        reader.readAsDataURL(file);
    } else {
        // For PDFs, show a placeholder
        previewImage.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200"%3E%3Crect fill="%231f1f1f" width="200" height="200"/%3E%3Ctext x="100" y="100" text-anchor="middle" dominant-baseline="middle" fill="%23606060" font-size="48" font-family="Arial"%3EPDF%3C/text%3E%3C/svg%3E';
    }
}

// Analysis
async function analyzeDocument(file) {
    // Animate loading steps
    animateLoadingSteps();
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${CONFIG.API_URL}/analyze`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Analysis failed: ${response.statusText}`);
        }
        
        const result = await response.json();
        currentAnalysis = {
            ...result,
            filename: file.name,
            filesize: file.size,
            timestamp: new Date().toISOString()
        };
        
        // Show results after animation completes
        setTimeout(() => {
            displayResults(currentAnalysis);
            saveToHistory(currentAnalysis);
        }, 3000);
        
    } catch (error) {
        console.error('Analysis error:', error);
        showNotification('Analysis failed. Please check your connection and try again.', 'error');
        resetToUpload();
    }
}

function animateLoadingSteps() {
    const steps = document.querySelectorAll('.loading-steps .step');
    steps.forEach((step, index) => {
        setTimeout(() => {
            step.classList.add('active');
        }, index * 600);
    });
}

function displayResults(analysis) {
    // Hide loading, show results
    loadingState.style.display = 'none';
    resultsContainer.style.display = 'block';
    
    // Set label
    const label = analysis.label.toLowerCase().replace(' ', '-');
    const resultLabel = document.getElementById('resultLabel');
    resultLabel.textContent = analysis.label;
    resultLabel.className = `result-label ${label}`;
    
    // Animate score
    animateScore(analysis.score);
    
    // Set confidence
    document.getElementById('confidenceLevel').textContent = `${(analysis.confidence * 100).toFixed(0)}%`;
    
    // Set breakdown
    setBreakdownItem('metadata', analysis.breakdown.metadata_anomaly);
    setBreakdownItem('noise', analysis.breakdown.noise_uniformity);
    setBreakdownItem('edge', analysis.breakdown.edge_consistency);
    setBreakdownItem('compression', analysis.breakdown.compression_artifacts);
    
    // Set SynthID status
    document.getElementById('synthidStatus').textContent = analysis.synthid.message;
}

function animateScore(targetScore) {
    const scoreNumber = document.getElementById('scoreNumber');
    const scoreRing = document.getElementById('scoreRing');
    
    // Calculate ring stroke
    const circumference = 2 * Math.PI * 85;
    const offset = circumference - (targetScore / 100) * circumference;
    
    // Animate number
    let currentScore = 0;
    const duration = 1500;
    const steps = 60;
    const increment = targetScore / steps;
    const stepDuration = duration / steps;
    
    const interval = setInterval(() => {
        currentScore += increment;
        if (currentScore >= targetScore) {
            currentScore = targetScore;
            clearInterval(interval);
        }
        scoreNumber.textContent = Math.round(currentScore);
    }, stepDuration);
    
    // Animate ring
    setTimeout(() => {
        scoreRing.style.strokeDashoffset = offset;
        
        // Change color based on score
        if (targetScore >= 75) {
            scoreRing.style.stroke = 'var(--accent-primary)';
        } else if (targetScore >= 50) {
            scoreRing.style.stroke = 'var(--accent-warning)';
        } else {
            scoreRing.style.stroke = 'var(--accent-danger)';
        }
    }, 100);
}

function setBreakdownItem(type, value) {
    const scoreEl = document.getElementById(`${type}Score`);
    const barEl = document.getElementById(`${type}Bar`);
    
    scoreEl.textContent = `${value}%`;
    
    setTimeout(() => {
        barEl.style.width = `${value}%`;
    }, 200);
}

// History Management
function saveToHistory(analysis) {
    analysisHistory.unshift({
        filename: analysis.filename,
        score: analysis.score,
        label: analysis.label,
        timestamp: analysis.timestamp
    });
    
    // Keep only last 10
    if (analysisHistory.length > 10) {
        analysisHistory = analysisHistory.slice(0, 10);
    }
    
    localStorage.setItem('analysisHistory', JSON.stringify(analysisHistory));
    renderHistory();
}

function renderHistory() {
    if (analysisHistory.length === 0) {
        historyList.innerHTML = '<p class="history-empty">No scans yet. Upload a document to get started.</p>';
        return;
    }
    
    historyList.innerHTML = analysisHistory.map(item => {
        const label = item.label.toLowerCase().replace(' ', '-');
        const date = new Date(item.timestamp).toLocaleString();
        
        return `
            <div class="history-item">
                <div class="history-item-info">
                    <div class="history-item-name">${item.filename}</div>
                    <div class="history-item-meta">${date}</div>
                </div>
                <div class="history-item-score">${item.score}%</div>
                <div class="history-item-label ${label}">${item.label}</div>
            </div>
        `;
    }).join('');
}

function clearHistory() {
    if (confirm('Clear all scan history?')) {
        analysisHistory = [];
        localStorage.removeItem('analysisHistory');
        renderHistory();
        showNotification('History cleared', 'success');
    }
}

// Download Report
function downloadReport() {
    if (!currentAnalysis) return;
    
    const report = generateReportText(currentAnalysis);
    const blob = new Blob([report], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `authenticity-report-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    
    showNotification('Report downloaded', 'success');
}

function generateReportText(analysis) {
    return `
═══════════════════════════════════════════════════════
    DOCUMENT AUTHENTICITY ANALYSIS REPORT
═══════════════════════════════════════════════════════

File: ${analysis.filename}
Size: ${formatFileSize(analysis.filesize)}
Analyzed: ${new Date(analysis.timestamp).toLocaleString()}

─────────────────────────────────────────────────────

OVERALL RESULT: ${analysis.label}
Authenticity Score: ${analysis.score}%
Confidence Level: ${(analysis.confidence * 100).toFixed(0)}%

─────────────────────────────────────────────────────

DETAILED BREAKDOWN:

1. Metadata Anomaly: ${analysis.breakdown.metadata_anomaly}%
   Analysis of EXIF data and file properties

2. Noise Uniformity: ${analysis.breakdown.noise_uniformity}%
   Detection of AI-characteristic noise patterns

3. Edge Consistency: ${analysis.breakdown.edge_consistency}%
   Edge smoothness and artifact detection

4. Compression Artifacts: ${analysis.breakdown.compression_artifacts}%
   Analysis of compression patterns and manipulation

─────────────────────────────────────────────────────

METADATA INFORMATION:

Format: ${analysis.metadata.format || 'N/A'}
Mode: ${analysis.metadata.mode || 'N/A'}
Dimensions: ${analysis.metadata.size ? `${analysis.metadata.size[0]}x${analysis.metadata.size[1]}` : 'N/A'}
EXIF Data: ${analysis.metadata.has_exif ? 'Present' : 'Not found'}
${analysis.metadata.has_exif ? `EXIF Fields: ${analysis.metadata.exif_fields}` : ''}

─────────────────────────────────────────────────────

SYNTHID WATERMARK DETECTION:

Status: ${analysis.synthid.message}

Note: This system is designed to support Google SynthID
watermark detection for enhanced AI content verification.
Integration pending API credentials.

─────────────────────────────────────────────────────

INTERPRETATION:

${getInterpretation(analysis.score, analysis.label)}

─────────────────────────────────────────────────────

Generated by DocAuthAI
AI Document Authenticity Scanner
https://github.com/yourusername/doc-scanner

═══════════════════════════════════════════════════════
    `.trim();
}

function getInterpretation(score, label) {
    if (label === 'Verified') {
        return 'This document shows strong indicators of authenticity. The analysis\ndetected natural patterns consistent with genuine documents or photos.\nHowever, always use professional judgment for critical decisions.';
    } else if (label === 'Suspicious') {
        return 'This document shows mixed indicators. Some patterns suggest potential\nAI generation or manipulation. Further manual verification is recommended\nbefore making important decisions based on this document.';
    } else {
        return 'This document shows strong indicators of AI generation or significant\nmanipulation. Multiple detection methods flagged suspicious patterns.\nExercise caution and verify through alternative means if authenticity\nis critical.';
    }
}

// UI Helpers
function resetToUpload() {
    uploadSection.style.display = 'block';
    analysisSection.style.display = 'none';
    fileInput.value = '';
    currentAnalysis = null;
    
    // Reset loading steps
    document.querySelectorAll('.loading-steps .step').forEach(step => {
        step.classList.remove('active');
    });
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'error' ? 'var(--accent-danger)' : type === 'warning' ? 'var(--accent-warning)' : 'var(--accent-primary)'};
        color: var(--bg-primary);
        border-radius: 8px;
        font-weight: 600;
        z-index: 1000;
        animation: slideIn 0.3s ease;
        box-shadow: var(--shadow-lg);
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add fadeOut animation
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        from { opacity: 1; transform: translateX(0); }
        to { opacity: 0; transform: translateX(100px); }
    }
`;
document.head.appendChild(style);
