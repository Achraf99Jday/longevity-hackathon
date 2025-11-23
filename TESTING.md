# Local Testing Guide

## Quick Start for Local Testing

### Step 1: Install Dependencies (if not already done)
```bash
pip install -r requirements.txt
```

### Step 2: Initialize Database
```bash
python -c "from longevity_map.database.session import init_db; init_db()"
```

### Step 3: Start the API Server

Open a terminal and run:
```bash
python scripts/run_api.py
```

Or alternatively:
```bash
uvicorn longevity_map.api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will start at: **http://localhost:8000**

### Step 4: Open the Web Interface

**Option A: Direct File Access**
- Open `public/index.html` in your browser
- The page will try to connect to `http://localhost:8000/api`

**Option B: Simple HTTP Server (Recommended)**

Open a **second terminal** and run:
```bash
# Python 3
python -m http.server 3000 --directory public

# Or if you have Node.js
npx http-server public -p 3000
```

Then open in browser: **http://localhost:3000**

### Step 5: Test the Application

1. **Check API is running**: Visit http://localhost:8000/stats
   - Should return JSON with statistics

2. **Check Web Interface**: Visit http://localhost:3000
   - Should show the dashboard with stats, problems, gaps

3. **Add Some Test Data** (Optional):
   ```bash
   python scripts/update_data.py
   ```
   This will fetch data from PubMed and other sources (may take a few minutes)

## Testing Different Features

### Test API Endpoints Directly

1. **Stats**: http://localhost:8000/stats
2. **Problems**: http://localhost:8000/problems
3. **Gaps**: http://localhost:8000/gaps
4. **Keystone Capabilities**: http://localhost:8000/keystone-capabilities

### Test with Sample Data

If you want to add sample data manually:

```python
from longevity_map.database.session import SessionLocal, init_db
from longevity_map.models.problem import Problem, ProblemCategory
from longevity_map.agents.problem_parser import ProblemParser
from longevity_map.agents.capability_extractor import CapabilityExtractor

init_db()
db = SessionLocal()

# Create a test problem
parser = ProblemParser()
problem = parser.process(
    "Understanding the role of cellular senescence in aging and developing senolytic interventions to clear senescent cells.",
    source="test",
    source_id="test_1"
)
db.add(problem)
db.commit()

# Extract capabilities
extractor = CapabilityExtractor()
capabilities = extractor.process(problem.description)
for cap in capabilities:
    db.add(cap)
db.commit()

db.close()
```

## Troubleshooting

### API not starting?
- Check if port 8000 is already in use
- Try a different port: `uvicorn longevity_map.api.main:app --port 8001`

### Web interface can't connect to API?
- Make sure API is running on port 8000
- Check browser console for errors (F12)
- Verify CORS is enabled (it should be by default)

### No data showing?
- Run the update script to fetch data
- Or add sample data manually (see above)

### Database errors?
- Make sure `data/` directory exists
- Check that database file is writable

## Quick Test Script

Run this to verify everything works:

```bash
python scripts/test_setup.py
```

## Expected Results

When everything is working:
- ✅ API responds at http://localhost:8000/stats
- ✅ Web interface loads at http://localhost:3000
- ✅ Dashboard shows statistics (may be 0 if no data yet)
- ✅ No console errors in browser


