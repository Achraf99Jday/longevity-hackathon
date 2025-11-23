# Deployment Guide for Vercel

## Prerequisites

1. Vercel account (free tier works)
2. GitHub repository with your code
3. OpenAI API key (optional but recommended)

## Deployment Steps

### 1. Prepare Your Repository

Make sure your code is pushed to GitHub.

### 2. Configure Environment Variables

In Vercel dashboard, add these environment variables:

- `OPENAI_API_KEY` - Your OpenAI API key (optional)
- `DATABASE_URL` - If using PostgreSQL (optional, SQLite works for demo)

### 3. Deploy to Vercel

**Option A: Via Vercel Dashboard**
1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository
4. Vercel will auto-detect the Python configuration
5. Click "Deploy"

**Option B: Via CLI**
```bash
npm i -g vercel
vercel login
vercel
```

### 4. Post-Deployment

After deployment:
1. The API will be available at `https://your-project.vercel.app/api/`
2. The web interface will be at `https://your-project.vercel.app/`

### 5. Initialize Database

For the first run, you may need to initialize the database. You can:
- Run locally and push the database file (not recommended for production)
- Use a cloud database like Supabase, Neon, or PlanetScale
- Use Vercel's serverless functions to initialize on first request

## Database Options

### Option 1: SQLite (Demo/Development)
- Works out of the box
- Data persists in serverless functions (limited)
- Not recommended for production

### Option 2: PostgreSQL (Production)
1. Set up a PostgreSQL database (Supabase, Neon, etc.)
2. Add `DATABASE_URL` environment variable in Vercel
3. Update `config/config.yaml` to use PostgreSQL

### Option 3: Serverless Database
- Use Vercel Postgres (if available)
- Or use a serverless-friendly database

## API Endpoints

Once deployed, your API endpoints will be:
- `https://your-project.vercel.app/api/stats` - Statistics
- `https://your-project.vercel.app/api/problems` - List problems
- `https://your-project.vercel.app/api/gaps` - List gaps
- `https://your-project.vercel.app/api/keystone-capabilities` - Keystone capabilities
- And more...

## Troubleshooting

### Import Errors
If you see import errors, make sure:
- All dependencies are in `requirements.txt`
- Python version is compatible (3.9+)

### Database Errors
- Check that database file path is writable
- For serverless, consider using a cloud database

### API Timeout
- Vercel has a 10s timeout for free tier
- Consider using background jobs for data updates
- Optimize API responses

## Custom Domain

1. Go to Vercel project settings
2. Add your custom domain
3. Follow DNS configuration instructions

## Monitoring

- Check Vercel dashboard for logs
- Set up error tracking (Sentry, etc.)
- Monitor API usage

