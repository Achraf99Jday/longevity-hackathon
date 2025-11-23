# Architecture Overview

## System Design

The Longevity R&D Map Platform is built as a multi-agent system that processes research data to map problems → capabilities → resources → gaps.

### Core Components

1. **Data Models** (`longevity_map/models/`)
   - `Problem`: Open problems in aging research, categorized by hallmarks
   - `Capability`: Required tools, technologies, methods
   - `Resource`: Existing R&D resources (facilities, datasets, tools)
   - `Gap`: Missing capabilities (infrastructure gaps)
   - `Mappings`: Relationships between problems, capabilities, and resources

2. **Multi-Agent Framework** (`longevity_map/agents/`)
   - **ProblemParser**: Classifies problems into hallmarks of aging
   - **CapabilityExtractor**: Extracts required capabilities from problem descriptions
   - **ResourceMapper**: Maps capabilities to existing resources using semantic similarity
   - **GapAnalyzer**: Identifies and scores missing capabilities
   - **CoordinationAgent**: Detects duplication clusters
   - **FundingAgent**: Predicts funding attractiveness of gaps
   - **Updater**: Continuously ingests new data from sources

3. **Data Sources** (`longevity_map/data_sources/`)
   - PubMed/PMC: Research papers
   - ClinicalTrials.gov: Clinical trials
   - Grants: NIH RePORTER, ERC, NSF
   - Preprints: bioRxiv, medRxiv

4. **API** (`longevity_map/api/`)
   - RESTful API built with FastAPI
   - Endpoints for problems, capabilities, resources, gaps
   - Matrix endpoints for problem-capability mappings
   - Analysis endpoints for keystone capabilities and duplication

5. **Visualization** (`longevity_map/visualization/`)
   - Plotly-based visualizations
   - Interactive Dash dashboard
   - Problem-capability heatmaps
   - Gap priority charts

## Data Flow

```
Data Sources → Updater → Problem Parser → Capability Extractor
                                                    ↓
                                    Resource Mapper → Gap Analyzer
                                                    ↓
                                    Coordination Agent → Funding Agent
                                                    ↓
                                    Database ← API ← Visualization
```

## Database Schema

- **problems**: Open problems with categories
- **capabilities**: Required capabilities with cost/time estimates
- **resources**: Existing resources
- **gaps**: Missing capabilities with impact scores
- **problem_capability_mappings**: Links problems to required capabilities
- **capability_resource_mappings**: Links capabilities to existing resources

## Agent Workflow

1. **Ingestion**: Updater fetches data from sources
2. **Parsing**: ProblemParser classifies problems
3. **Extraction**: CapabilityExtractor identifies required capabilities
4. **Mapping**: ResourceMapper finds existing resources
5. **Analysis**: GapAnalyzer identifies gaps
6. **Coordination**: CoordinationAgent detects duplicates
7. **Funding**: FundingAgent ranks gaps by funding potential

## Key Features

- **Semantic Matching**: Uses sentence transformers for capability-resource matching
- **Impact Scoring**: Calculates impact based on cost, time, and blocked research value
- **Keystone Detection**: Identifies capabilities that unlock multiple problems
- **Duplication Detection**: Finds when multiple groups build the same thing
- **Funding Prediction**: Ranks gaps by funding attractiveness

## Extensibility

The system is designed to be easily extended:

- **New Data Sources**: Add modules in `data_sources/`
- **New Agents**: Extend `BaseAgent` class
- **New Visualizations**: Add functions in `visualization/`
- **New API Endpoints**: Add routes in `api/main.py`

## Performance Considerations

- Batch processing for large datasets
- Semantic similarity caching
- Database indexing on key fields
- Rate limiting for external APIs

## Future Enhancements

- LLM-based extraction (GPT-4) for better accuracy
- Real-time updates via webhooks
- User contributions and curation
- Advanced ML models for gap prediction
- Integration with more data sources (patents, companies)

