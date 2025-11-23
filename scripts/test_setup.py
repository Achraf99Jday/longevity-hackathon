"""Test script to verify the setup is working."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from longevity_map.database.session import init_db, get_db
        print("[OK] Database imports OK")
    except Exception as e:
        print(f"[FAIL] Database imports failed: {e}")
        return False
    
    try:
        from longevity_map.models import Problem, Capability, Resource, Gap
        print("[OK] Model imports OK")
    except Exception as e:
        print(f"[FAIL] Model imports failed: {e}")
        return False
    
    try:
        from longevity_map.agents import (
            ProblemParser, CapabilityExtractor, ResourceMapper,
            GapAnalyzer, CoordinationAgent, FundingAgent, Updater
        )
        print("[OK] Agent imports OK")
    except Exception as e:
        print(f"[FAIL] Agent imports failed: {e}")
        return False
    
    try:
        from longevity_map.data_sources import pubmed, clinical_trials
        print("[OK] Data source imports OK")
    except Exception as e:
        print(f"[FAIL] Data source imports failed: {e}")
        return False
    
    try:
        from longevity_map.api.main import app
        print("[OK] API imports OK")
    except Exception as e:
        print(f"[FAIL] API imports failed: {e}")
        return False
    
    return True


def test_database():
    """Test database initialization."""
    print("\nTesting database...")
    
    try:
        from longevity_map.database.session import init_db
        init_db()
        print("[OK] Database initialization OK")
        return True
    except Exception as e:
        print(f"[FAIL] Database initialization failed: {e}")
        return False


def test_agents():
    """Test agent initialization."""
    print("\nTesting agents...")
    
    try:
        from longevity_map.agents.problem_parser import ProblemParser
        parser = ProblemParser()
        
        # Test parsing
        test_text = "Understanding the role of cellular senescence in aging and developing senolytic interventions."
        problem = parser.process(test_text, source="test", source_id="test_1")
        
        if problem and problem.category:
            print(f"[OK] ProblemParser OK (category: {problem.category.value})")
        else:
            print("[FAIL] ProblemParser failed to parse")
            return False
        
        from longevity_map.agents.capability_extractor import CapabilityExtractor
        extractor = CapabilityExtractor()
        capabilities = extractor.process(test_text)
        
        if capabilities:
            print(f"[OK] CapabilityExtractor OK (extracted {len(capabilities)} capabilities)")
        else:
            print("[WARN] CapabilityExtractor returned no capabilities (may be OK)")
        
        return True
    except Exception as e:
        print(f"[FAIL] Agent testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("Longevity R&D Map - Setup Test")
    print("=" * 50)
    
    success = True
    
    if not test_imports():
        success = False
    
    if not test_database():
        success = False
    
    if not test_agents():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("[SUCCESS] All tests passed! Setup is working correctly.")
        print("\nNext steps:")
        print("1. Configure API keys in config/config.yaml")
        print("2. Run: python scripts/update_data.py")
        print("3. Run: python scripts/run_api.py")
    else:
        print("[FAIL] Some tests failed. Please check the errors above.")
    print("=" * 50)
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

