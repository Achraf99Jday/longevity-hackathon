# Longevity R&D Map Platform

A living platform that maps open problems in aging sciences to required capabilities, existing R&D resources, and infrastructure gaps. Inspired by Gap Maps (Convergent Research).

## Overview

This platform addresses the critical problem of fragmented R&D resources in longevity research by:
- Mapping 100+ open problems categorized by hallmarks of aging
- Identifying required capabilities (tools, technologies, data)
- Discovering existing R&D resources that could fill gaps
- Highlighting infrastructure gaps blocking research
- Detecting duplication and coordination opportunities

## Multi-Agent Framework

The system uses specialized agents:

1. **Problem Parser**: Classifies aging problems into a clean hierarchy
2. **Capability Extractor**: Identifies measurement tools, model systems, datasets, and computational requirements
3. **Resource Mapper**: Finds existing tools (core facilities, datasets, CROs, software)
4. **Gap Analyst**: Scores missing capabilities by cost, time, and number of blocked problems
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

- ✅ Maps 50+ problems to required capabilities (≥80% extraction accuracy)
- ✅ Identifies 10 infrastructure gaps blocking >$100M of research
- ✅ Surfaces 5 duplication clusters where 3+ groups are building the same tool
- ✅ Produces interactive problem ↔ capability matrix and API
- ✅ Generates ranked list of "keystone capabilities" that unlock multiple problems

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Copy `config/config.example.yaml` to `config/config.yaml` and fill in API keys for:
- PubMed API (free, but requires registration)
- ClinicalTrials.gov API (free)
- Other data sources as needed

## Usage

```bash
# Run the updater to ingest new data
python -m longevity_map.updater.main

# Start the API server
python -m longevity_map.api.main

# Run analysis
python -m longevity_map.analysis.gap_analyzer
```

## Project Structure

```
longevity_map/
├── agents/          # Multi-agent framework
├── data_sources/    # Data source integrations
├── models/          # Data models and schemas
├── database/         # Database setup and migrations
├── api/             # REST API endpoints
├── visualization/   # Visualization components
├── analysis/        # Gap analysis and coordination detection
└── utils/           # Shared utilities
```

## License

MIT

