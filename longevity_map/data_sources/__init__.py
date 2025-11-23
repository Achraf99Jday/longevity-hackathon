"""Data source integrations for longevity R&D map."""

# Import modules (lazy import to avoid circular dependencies)
def get_pubmed():
    from . import pubmed
    return pubmed

def get_clinical_trials():
    from . import clinical_trials
    return clinical_trials

def get_grants():
    from . import grants
    return grants

def get_preprints():
    from . import preprints
    return preprints

# For direct imports
try:
    from . import pubmed
    from . import clinical_trials
    from . import grants
    from . import preprints
except ImportError:
    pass

__all__ = ["pubmed", "clinical_trials", "grants", "preprints"]
