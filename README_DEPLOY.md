# Quick Deploy to Vercel

## 🚀 One-Click Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/longevity-map)

## Manual Deployment

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/longevity-map.git
   git push -u origin main
   ```

2. **Deploy to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Add environment variable: `OPENAI_API_KEY` (optional)
   - Click "Deploy"

3. **Access Your App**
   - Web UI: `https://your-project.vercel.app`
   - API: `https://your-project.vercel.app/api/stats`

## Environment Variables

Add these in Vercel dashboard:

- `OPENAI_API_KEY` - For GPT-powered extraction (optional)
- `DATABASE_URL` - PostgreSQL connection string (optional, uses SQLite by default)

## Features

✅ **Web Interface** - Beautiful dashboard at `/`
✅ **REST API** - Full API at `/api/*`
✅ **LLM Integration** - GPT-powered problem extraction
✅ **Real-time Stats** - Live statistics dashboard
✅ **Gap Analysis** - Infrastructure gap identification
✅ **Visualizations** - Interactive charts

## API Endpoints

- `GET /api/stats` - Overall statistics
- `GET /api/problems` - List problems
- `GET /api/gaps` - List infrastructure gaps
- `GET /api/keystone-capabilities` - Top keystone capabilities
- `GET /api/duplication-clusters` - Duplication detection
- `GET /api/gaps/funding-potential` - Gaps ranked by funding potential

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run API server
python scripts/run_api.py

# Run web interface (served from public/)
# API will be at http://localhost:8000
# Web UI should proxy to API or run separately
```

## Troubleshooting

**Import errors?**
- Make sure all dependencies are in `requirements.txt`
- Check Python version (3.9+)

**Database errors?**
- SQLite works for demo
- For production, use PostgreSQL (add `DATABASE_URL` env var)

**API timeout?**
- Vercel free tier has 10s timeout
- Optimize responses or use background jobs

