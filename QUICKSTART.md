# ⚡ Quick Start Guide - DocAuthAI

Get your Document Authenticity Scanner running in 5 minutes!

---

## 🚀 Local Development (5 Minutes)

### Prerequisites
- Python 3.9+
- Git
- Web browser

### Steps

**1. Clone & Navigate**
```bash
git clone https://github.com/yourusername/doc-scanner.git
cd doc-scanner
```

**2. Start Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Backend running at `http://localhost:8000` ✅

**3. Start Frontend** (in new terminal)
```bash
cd frontend
python -m http.server 3000
```

Frontend running at `http://localhost:3000` ✅

**4. Test It**
- Open browser to `http://localhost:3000`
- Upload a document (PDF or image)
- See the magic happen! ✨

---

## ☁️ Deploy to Production (10 Minutes)

### Backend → Render

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy on Render**
   - Go to [render.com](https://render.com)
   - New → Web Service
   - Connect GitHub repo
   - Settings:
     - Root: `backend`
     - Build: `pip install -r requirements.txt`
     - Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Deploy!

3. **Copy URL**
   - Wait for deployment
   - Copy service URL (e.g., `https://doc-scanner.onrender.com`)

### Frontend → GitHub Pages

1. **Update API URL**
   ```javascript
   // frontend/script.js
   const CONFIG = {
       API_URL: 'https://YOUR-RENDER-URL.onrender.com',
       ...
   };
   ```

2. **Push Changes**
   ```bash
   git add frontend/script.js
   git commit -m "Update API URL"
   git push origin main
   ```

3. **Enable GitHub Pages**
   - Repo → Settings → Pages
   - Source: main branch, /frontend folder
   - Save

4. **Access Your App**
   - `https://yourusername.github.io/doc-scanner/`
   - You're live! 🎉

---

## 🧪 Test Your Deployment

**1. Test Backend Health**
```bash
curl https://YOUR-RENDER-URL.onrender.com/health
```

Expected: `{"status": "healthy", ...}`

**2. Test Document Analysis**
```bash
curl -X POST https://YOUR-RENDER-URL.onrender.com/analyze \
  -F "file=@test-image.jpg"
```

Expected: `{"score": 78.4, "label": "Suspicious", ...}`

**3. Test Frontend**
- Open GitHub Pages URL
- Upload a document
- Verify results display correctly

---

## 📁 Project Structure

```
doc-scanner/
├── frontend/              ← Static files (GitHub Pages)
│   ├── index.html        ← Main page
│   ├── styles.css        ← Styling
│   └── script.js         ← Logic (update API_URL here!)
│
├── backend/              ← API server (Render)
│   ├── main.py          ← FastAPI app
│   └── requirements.txt  ← Dependencies
│
├── docs/                 ← Documentation
│   ├── DEPLOYMENT.md
│   ├── API.md
│   └── LINKEDIN_SHOWCASE.md
│
└── README.md            ← You are here!
```

---

## 🔧 Common Issues

### "Cannot connect to backend"
✅ **Solution:** Update `API_URL` in `frontend/script.js` to your Render URL

### "502 Bad Gateway" on Render
✅ **Solution:** Free tier spins down after 15 min. First request takes ~30 sec. Wait and try again.

### "GitHub Pages not updating"
✅ **Solution:** Wait 1-2 minutes, clear cache, hard refresh (Ctrl+Shift+R)

### "CORS error"
✅ **Solution:** Check CORS settings in `backend/main.py`. Should allow your GitHub Pages domain.

---

## 📝 Next Steps

**Customize:**
- Update colors in `frontend/styles.css`
- Add your name/info in HTML
- Customize detection weights in `backend/main.py`

**Enhance:**
- Add more detection methods
- Implement user authentication
- Add database for history
- Create mobile app

**Share:**
- Add to LinkedIn portfolio
- Write blog post about it
- Share on GitHub
- Demo in interviews!

---

## 🎯 Development Workflow

### Making Changes

**Backend Changes:**
```bash
cd backend
# Make changes to main.py
git add .
git commit -m "Update detection algorithm"
git push origin main
# Render auto-deploys!
```

**Frontend Changes:**
```bash
cd frontend
# Make changes to HTML/CSS/JS
git add .
git commit -m "Improve UI"
git push origin main
# GitHub Pages auto-deploys!
```

### Testing Locally
```bash
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend
cd frontend
python -m http.server 3000

# Browser
# http://localhost:3000
```

---

## 🆘 Getting Help

1. **Check documentation:** Read `docs/` folder
2. **Review logs:** Render Dashboard → Logs tab
3. **Test API:** Use `curl` commands above
4. **GitHub Issues:** Create issue with error details
5. **Email:** your.email@example.com

---

## ✨ Pro Tips

**Tip 1:** Free Render tier sleeps after 15 min. First load is slow. Upgrade to paid if needed.

**Tip 2:** GitHub Pages can take 1-2 min to update. Be patient!

**Tip 3:** Use browser DevTools (F12) → Network tab to debug API calls

**Tip 4:** Add Google Analytics to track usage (optional)

**Tip 5:** Star the repo and share with friends! 🌟

---

## 🎓 Learn More

- **FastAPI Tutorial:** [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **Computer Vision:** [opencv.org](https://opencv.org)
- **Deployment:** `docs/DEPLOYMENT.md`
- **API Reference:** `docs/API.md`

---

## 🎉 You're All Set!

Your AI Document Authenticity Scanner is now:
- ✅ Running locally
- ✅ Deployed to production
- ✅ Accessible worldwide
- ✅ Portfolio-ready
- ✅ LinkedIn-worthy

**Now go show it off!** 🚀

---

*Need help? Found a bug? Want to contribute? Open an issue on GitHub!*
