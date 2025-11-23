# Quick Local Testing Guide

## 🚀 Fastest Way to Test

### Windows (PowerShell/CMD)

1. **Start the API** (Terminal 1):
   ```bash
   python scripts/run_api.py
   ```
   Wait for: `Uvicorn running on http://0.0.0.0:8000`

2. **Start the Web Server** (Terminal 2):
   ```bash
   cd public
   python -m http.server 3000
   ```

3. **Open Browser**:
   - Go to: **http://localhost:3000**
   - You should see the dashboard!

### Or Use the Batch Script (Windows)

Just double-click: `scripts/start_local.bat`

## 📋 Step-by-Step

### 1. Check Prerequisites
```bash
python --version  # Should be 3.9+
pip list | findstr fastapi  # Check if installed
```

### 2. Initialize Database (First Time Only)
```bash
python -c "from longevity_map.database.session import init_db; init_db()"
```

### 3. Start API Server
```bash
python scripts/run_api.py
```
**Keep this terminal open!**

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### 4. Test API (Optional)
Open another browser tab: http://localhost:8000/stats

Should return JSON like:
```json
{
  "num_problems": 0,
  "num_capabilities": 0,
  "num_resources": 0,
  "num_gaps": 0,
  "total_blocked_research_value": 0
}
```

### 5. Start Web Server
Open a **NEW terminal** (keep API running):
```bash
cd public
python -m http.server 3000
```

### 6. Open Dashboard
Go to: **http://localhost:3000**

## 🎯 What You Should See

1. **Header**: "🧬 Longevity R&D Map"
2. **Stats Cards**: 4 cards showing Problems, Capabilities, Resources, Gaps
3. **Problems Section**: Filterable list (empty if no data)
4. **Gaps Section**: Infrastructure gaps (empty if no data)
5. **Visualizations**: Charts (may be empty initially)

## 📊 Add Test Data

To see actual data, run:
```bash
python scripts/update_data.py
```

This will:
- Fetch papers from PubMed
- Extract problems and capabilities
- May take 2-5 minutes

## 🔍 Troubleshooting

### "Connection refused" error?
- Make sure API is running on port 8000
- Check terminal 1 for errors

### Blank page?
- Open browser console (F12)
- Check for JavaScript errors
- Verify API is accessible at http://localhost:8000/stats

### Port already in use?
- Change API port: `uvicorn longevity_map.api.main:app --port 8001`
- Update `public/index.html` line ~200: change `8000` to `8001`

### No data showing?
- This is normal if you haven't run `update_data.py` yet
- Stats will show 0 for everything
- Run the update script to fetch real data

## ✅ Success Checklist

- [ ] API server starts without errors
- [ ] http://localhost:8000/stats returns JSON
- [ ] Web server starts on port 3000
- [ ] http://localhost:3000 shows the dashboard
- [ ] No console errors in browser (F12)
- [ ] Stats cards are visible (even if showing 0)

## 🎉 Next Steps

Once it's working:
1. Add data: `python scripts/update_data.py`
2. Explore the API: http://localhost:8000/docs (FastAPI auto-docs)
3. Check gaps: http://localhost:8000/gaps
4. View keystone capabilities: http://localhost:8000/keystone-capabilities


