#!/usr/bin/env python3
"""
Quick system test to verify NaijaTTS is working.
"""

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from utils.textnorm import normalize
        print("✓ utils.textnorm imported")
        
        from engines.xtts_engine import XTTSEngine
        print("✓ engines.xtts_engine imported")
        
        from backend.app import app
        print("✓ backend.app imported")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_text_normalization():
    """Test text normalization."""
    print("\nTesting text normalization...")
    
    try:
        from utils.textnorm import normalize
        
        test_cases = [
            "How you dey?",
            "Today go sweet well-well!",
            "Wetin dey happen?",
            "Abi you dey hear me?",
        ]
        
        for text in test_cases:
            normalized = normalize(text)
            print(f"  '{text}' -> '{normalized}'")
        
        print("✓ Text normalization working")
        return True
    except Exception as e:
        print(f"✗ Text normalization failed: {e}")
        return False

def test_fastapi_app():
    """Test FastAPI app creation."""
    print("\nTesting FastAPI app...")
    
    try:
        from backend.app import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/health")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health endpoint working: {data}")
            return True
        else:
            print(f"✗ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ FastAPI app test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("NaijaTTS System Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_text_normalization,
        test_fastapi_app,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready.")
        print("\nTo start the server:")
        print("  python backend/app.py")
        print("\nTo test synthesis (requires voice files):")
        print("  python scripts/test_synthesize_xtts.py --text 'How you dey?'")
    else:
        print("❌ Some tests failed. Check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

