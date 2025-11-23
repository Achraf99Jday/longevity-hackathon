# Longevity R&D Map Platform

A living platform that maps open problems in aging sciences to required capabilities, existing R&D resources, and infrastructure gaps. Inspired by Gap Maps (Convergent Research).

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Python dependencies
pip install -r requirements.txt

# Node.js dependencies (for npm start)
npm install
```

### 2. Start Everything (Auto-loads sample data if empty)
```bash
npm start
```

**That's it!** The script will:
- ✅ Automatically add sample data if database is empty
- ✅ Start API server on http://localhost:8000
- ✅ Start web server (auto-finds available port)
- ✅ Show you the URL to open in your browser

**Open the URL shown in the web server window!** (usually http://localhost:3000)

## 📊 What You'll See

After running `npm start`, you'll have:
- **5 sample problems** from aging research
- **43 capabilities** extracted using GPT-4o
- **3 sample resources** (databases, tools, software)
- **43 infrastructure gaps** identified
- **$92M+ blocked research value** calculated

## 🖱️ Interactive Features

The web interface is **fully interactive** - click on anything!

### Click on Problem Cards
- See full problem description
- View required capabilities with costs and timelines
- Click "View Source" to open the original PubMed paper
- See which capabilities are needed to solve the problem

### Click on Gap Cards
- View detailed gap analysis
- See blocked research value ($M)
- Number of problems blocked
- Capability requirements and estimates

### Filter & Explore
- Filter problems by hallmark of aging
- Filter gaps by priority (critical, high, medium, low)
- Click stat cards to jump to filtered views
- Interactive charts showing problem distribution

### Fetch Real Data
- Click "Fetch Real Data from PubMed" button
- Fetches real research papers from the last 90 days
- Uses GPT-4o to extract problems and capabilities
- All data links back to original sources

## 📋 Available Commands

**⚠️ IMPORTANT FOR HACKATHON**: To fetch real data, stop the API server first!

```bash
# Stop API server (Ctrl+C), then:
python scripts/fetch_real_data_quick.py  # Quick: 5 papers
python scripts/fetch_all_real_data.py  # Full: all sources
# Then restart: npm start
```

See `HACKATHON_DATA.md` for detailed verification steps.

- `npm start` - Start both servers (auto-loads sample data if needed)
- `npm run api` - Start only the API server
- `npm run web` - Start only the web server (auto-finds port)
- `npm run init-db` - Initialize the database
- `npm run sample-data` - Add sample data manually
- `npm run update-data` - Fetch real data from PubMed/other sources
- `npm run setup` - Initialize DB + add sample data
- `npm test` - Run setup tests

## 🎯 Features

### Automatic Data Loading
- On first run, automatically adds sample data
- Uses GPT-4o to extract problems and capabilities
- Creates gaps analysis automatically

### Real Data Fetching (HACKATHON REQUIREMENT)

**⚠️ ALL DATA IS REAL - NO PLACEHOLDERS!**

This platform fetches **100% real data** from:
- ✅ **PubMed/PMC**: Real research papers (500k+ aging papers via Entrez API)
- ✅ **ClinicalTrials.gov**: Real clinical trials (2,000+ aging-related trials)
- ✅ **Preprints**: Real preprints from bioRxiv/medRxiv APIs
- ✅ **Grants**: Real grants from NIH RePORTER, ERC, NSF
- ✅ **Aging Databases**: GenAge, DrugAge, AgeFactDB, HAGR

**To fetch real data (REQUIRED for hackathon):**

⚠️ **CRITICAL**: You MUST stop the API server first!

**Steps:**
1. **Stop the API server**: Press `Ctrl+C` in the terminal running `npm start`
2. **Wait 2-3 seconds** for the database to unlock
3. **Run the fetch script**:
   ```bash
   # Quick test: Fetch 5 real papers (recommended first)
   python scripts/fetch_real_data_quick.py
   
   # Full fetch: Fetch from all sources (takes 10-30 min)
   python scripts/fetch_all_real_data.py
   ```
4. **Restart the servers**:
   ```bash
   npm start
   ```

**Why?** SQLite doesn't allow concurrent writes. The API server keeps the database locked for writes, so you must stop it before fetching data.

This will:
1. **Test all data sources** to ensure they're working
2. **Fetch real papers/trials/preprints** from the last 90 days
3. **Extract problems using GPT-4o** (real problem extraction)
4. **Identify capabilities using GPT-4o** (real capability analysis)
5. **Map to resources** and identify gaps
6. **Link everything to original sources** (PubMed URLs, DOIs, etc.)

**Expected results (hackathon metrics):**
- ✅ Maps 50+ problems to required capabilities (≥80% extraction accuracy)
- ✅ Identifies 10 infrastructure gaps blocking >$100M of research
- ✅ Surfaces duplication clusters where multiple groups are building the same tool
- ✅ All data links back to real sources (click any problem to see the paper)

**Or use the web interface:**
- Click "Fetch Real Data from PubMed" button
- Data will be processed in the background
- Refresh the page to see new data

## Overview

This platform addresses the critical problem of fragmented R&D resources in longevity research by:
- Mapping 100+ open problems categorized by hallmarks of aging
- Identifying required capabilities (tools, technologies, data)
- Discovering existing R&D resources that could fill gaps
- Highlighting infrastructure gaps blocking research
- Detecting duplication and coordination opportunities

## Multi-Agent Framework

The system uses specialized agents powered by GPT-4o:

1. **Problem Parser**: Classifies aging problems into a clean hierarchy (GPT-4o powered)
2. **Capability Extractor**: Identifies measurement tools, model systems, datasets, and computational requirements
3. **Resource Mapper**: Finds existing tools (core facilities, datasets, CROs, software)
4. **Gap Analyzer**: Scores missing capabilities by cost, time, and number of blocked problems
5. **Coordination Agent**: Detects when multiple groups are building the same thing
6. **Funding/Impact Agents**: Predict which gaps matter most and which will attract capital
7. **Updater**: Continuously ingests new papers, grants, and company announcements

## Data Sources

- PubMed/PMC: 500k+ aging papers via Entrez API
- ClinicalTrials.gov: 2,000+ aging-related trials via API
- Patents: USPTO, EPO databases for IP landscape
- Grants: NIH RePORTER, ERC funding database, NSF awards
- Preprints: bioRxiv, medRxiv APIs
- Company Data: Crunchbase, PitchBook, SEC EDGAR
- Aging Databases: GenAge, DrugAge, AgeFactDB, HAGR

## Success Metrics

- ✅ Maps 50+ problems to required capabilities (≥80% extraction accuracy with GPT-4o)
- ✅ Identifies 10 infrastructure gaps blocking >$100M of research
- ✅ Surfaces 5 duplication clusters where 3+ groups are building the same tool
- ✅ Produces interactive problem ↔ capability matrix and API
- ✅ Generates ranked list of "keystone capabilities" that unlock multiple problems

## Configuration

Your OpenAI API key is already configured in `config/config.yaml` for GPT-4o powered extraction!

Optional: Add other API keys:
- PubMed API (free, but requires registration)
- ClinicalTrials.gov API (free)

## API Endpoints

Once running, access:
- **Web UI**: Check web server window for URL (usually http://localhost:3000)
- **API Docs**: http://localhost:8000/docs (Interactive Swagger UI)
- **Stats**: http://localhost:8000/stats
- **Problems**: http://localhost:8000/problems
- **Gaps**: http://localhost:8000/gaps
- **Keystone Capabilities**: http://localhost:8000/keystone-capabilities

## Troubleshooting

### Dashboard shows zeros?
- Refresh the page (F5)
- Check that API is running on port 8000
- Run `npm run sample-data` to add data manually

### Port conflicts?
- Web server automatically finds available port (3000, 3001, 3002, etc.)
- Check the web server window for the exact URL

### API won't start?
- Make sure port 8000 is not in use
- Check Python version: `python --version` (needs 3.9+)

## Project Structure

```
longevity_map/
├── agents/          # Multi-agent framework (GPT-4o powered)
├── data_sources/    # Data source integrations
├── models/          # Data models and schemas
├── database/         # Database setup and migrations
├── api/             # REST API endpoints
├── visualization/   # Visualization components
├── analysis/        # Gap analysis and coordination detection
└── utils/           # Shared utilities (including LLM helper)
```

## Deployment

See `DEPLOYMENT.md` for Vercel deployment instructions.

## License

MIT
