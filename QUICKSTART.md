# Quick Start Guide

## Installation

1. **Clone and setup environment:**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

2. **Configure the application:**
```bash
# Copy example config
cp config/config.example.yaml config/config.yaml

# Edit config/config.yaml and add your API keys:
# - PubMed email (required for PubMed API)
# - OpenAI API key (optional, for LLM-based extraction)
```

3. **Initialize the database:**
```bash
python -c "from longevity_map.database.session import init_db; init_db()"
```

## Running the Platform

### 1. Update Data from Sources

Fetch data from PubMed, ClinicalTrials.gov, and other sources:

```bash
python scripts/update_data.py
```

This will:
- Fetch recent papers, trials, and grants
- Parse problems and extract capabilities
- Map capabilities to existing resources
- Identify gaps

### 2. Run Gap Analysis

Analyze capabilities and identify gaps:

```bash
python -m longevity_map.analysis.gap_analyzer
```

This will:
- Analyze all capabilities
- Create gap records for missing capabilities
- Find keystone capabilities
- Detect duplication clusters
- Rank gaps by funding potential

### 3. Start the API Server

```bash
python scripts/run_api.py
```

Or:
```bash
uvicorn longevity_map.api.main:app --reload
```

API will be available at `http://localhost:8000`

### 4. View Interactive Dashboard

```bash
python scripts/run_dashboard.py
```

Dashboard will be available at `http://localhost:8050`

## API Endpoints

- `GET /` - API information
- `GET /problems` - List problems (filter by category)
- `GET /problems/{id}/capabilities` - Get capabilities for a problem
- `GET /capabilities` - List capabilities
- `GET /capabilities/{id}/resources` - Get resources for a capability
- `GET /gaps` - List infrastructure gaps
- `GET /matrix/problem-capability` - Problem-capability matrix
- `GET /keystone-capabilities` - Top keystone capabilities
- `GET /duplication-clusters` - Duplication clusters
- `GET /gaps/funding-potential` - Gaps ranked by funding potential
- `GET /stats` - Overall statistics

## Example Usage

### Query problems by category:
```bash
curl "http://localhost:8000/problems?category=cellular_senescence&limit=10"
```

### Get problem-capability matrix:
```bash
curl "http://localhost:8000/matrix/problem-capability?category=mitochondrial_dysfunction"
```

### Get top gaps:
```bash
curl "http://localhost:8000/gaps?priority=critical&min_blocked_value=100000000"
```

## Success Metrics

Track progress toward the goals:

1. **50+ problems mapped** - Check `/stats` endpoint
2. **10 infrastructure gaps blocking >$100M** - Check `/gaps?min_blocked_value=100000000`
3. **5 duplication clusters** - Check `/duplication-clusters?min_groups=3`
4. **Keystone capabilities** - Check `/keystone-capabilities`

## Next Steps

1. **Add more data sources**: Extend `longevity_map/data_sources/` with additional sources
2. **Improve extraction**: Enhance agents with better NLP models
3. **Add more visualizations**: Extend `longevity_map/visualization/`
4. **Deploy**: Set up production database and deploy API

## Troubleshooting

### Database errors
- Make sure database directory exists: `mkdir -p data`
- Check config file has correct database settings

### API key errors
- PubMed requires email (free)
- OpenAI key is optional but improves extraction quality

### Import errors
- Make sure you're in the project root directory
- Activate virtual environment
- Install all requirements: `pip install -r requirements.txt`

