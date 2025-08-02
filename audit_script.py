#!/usr/bin/env python3
"""Script to audit LouieAI notebook API against documentation."""

import sys
import os
import traceback
from collections import defaultdict

# Add the src directory to the path so we can import without installation
sys.path.insert(0, "/home/lmeyerov/Work/louie-py/src")

def test_import(description, import_func):
    """Test an import and return result."""
    try:
        result = import_func()
        return True, result, None
    except Exception as e:
        return False, None, str(e)

def test_attribute(obj, attr_name, description):
    """Test if an object has an attribute."""
    try:
        value = getattr(obj, attr_name)
        return True, value, None
    except Exception as e:
        return False, None, str(e)

def main():
    """Run the audit."""
    results = defaultdict(list)
    
    print("🔍 LouieAI Notebook API Documentation Audit")
    print("=" * 60)
    
    # 1. Test import methods
    print("\n1. IMPORT METHODS")
    print("-" * 30)
    
    # Test: from louieai.notebook import lui
    success, lui_notebook, error = test_import(
        "from louieai.notebook import lui",
        lambda: exec("from louieai.notebook import lui") or globals().get('lui')
    )
    if success:
        print("✅ from louieai.notebook import lui - WORKS")
        exec("from louieai.notebook import lui")
        lui_notebook = lui
        results["working"].append("from louieai.notebook import lui")
    else:
        print(f"❌ from louieai.notebook import lui - FAILS: {error}")
        results["broken"].append(f"from louieai.notebook import lui: {error}")
    
    # Test: from louieai.globals import lui
    success, lui_globals, error = test_import(
        "from louieai.globals import lui",
        lambda: exec("from louieai.globals import lui") or globals().get('lui')
    )
    if success:
        print("✅ from louieai.globals import lui - WORKS")
        exec("from louieai.globals import lui")
        lui_globals = lui
        results["working"].append("from louieai.globals import lui")
    else:
        print(f"❌ from louieai.globals import lui - FAILS: {error}")
        results["broken"].append(f"from louieai.globals import lui: {error}")
    
    # Test: import louieai; lui = louieai()
    try:
        import louieai
        lui_factory = louieai()
        print("✅ import louieai; lui = louieai() - WORKS")
        results["working"].append("import louieai; lui = louieai()")
    except Exception as e:
        print(f"❌ import louieai; lui = louieai() - FAILS: {e}")
        results["broken"].append(f"import louieai; lui = louieai(): {e}")
        lui_factory = None
    
    # Test: louie() factory function
    try:
        from louieai import louie
        lui_louie_factory = louie()
        print("✅ from louieai import louie; lui = louie() - WORKS")
        results["working"].append("from louieai import louie; lui = louie()")
    except Exception as e:
        print(f"❌ from louieai import louie; lui = louie() - FAILS: {e}")
        results["broken"].append(f"from louieai import louie; lui = louie(): {e}")
        lui_louie_factory = None
    
    # 2. Test properties on available lui objects
    print("\n2. PROPERTIES TEST")
    print("-" * 30)
    
    # Get the first working lui object
    test_lui = None
    lui_source = None
    
    if 'lui_notebook' in locals():
        test_lui = lui_notebook
        lui_source = "louieai.notebook"
    elif 'lui_globals' in locals():
        test_lui = lui_globals  
        lui_source = "louieai.globals"
    elif 'lui_factory' in locals() and lui_factory:
        test_lui = lui_factory
        lui_source = "louieai()"
    elif 'lui_louie_factory' in locals() and lui_louie_factory:
        test_lui = lui_louie_factory
        lui_source = "louie()"
    
    if test_lui:
        print(f"Testing properties on lui from {lui_source}")
        
        # Test documented properties
        properties = [
            "text", "texts", "df", "dfs", "elements", 
            "errors", "has_errors", "traces"
        ]
        
        for prop in properties:
            success, value, error = test_attribute(test_lui, prop, f"lui.{prop}")
            if success:
                print(f"✅ lui.{prop} - EXISTS (type: {type(value).__name__})")
                results["working"].append(f"lui.{prop} property")
            else:
                print(f"❌ lui.{prop} - MISSING: {error}")
                results["broken"].append(f"lui.{prop} property: {error}")
        
        # Test callable
        if callable(test_lui):
            print("✅ lui() - IS CALLABLE")
            results["working"].append("lui is callable")
        else:
            print("❌ lui() - NOT CALLABLE")
            results["broken"].append("lui is not callable")
            
        # Test negative indexing (without making actual calls)
        try:
            # This should not raise an error even with no history
            proxy = test_lui[-1]
            print("✅ lui[-1] - NEGATIVE INDEXING WORKS")
            results["working"].append("lui[-1] negative indexing")
        except Exception as e:
            print(f"❌ lui[-1] - NEGATIVE INDEXING FAILS: {e}")
            results["broken"].append(f"lui[-1] negative indexing: {e}")
    else:
        print("❌ No working lui object found to test properties")
        results["broken"].append("No working lui object found")
    
    # 3. Test environment variable support
    print("\n3. ENVIRONMENT VARIABLES")
    print("-" * 30)
    
    # Check which environment variables are documented vs actually supported
    documented_env_vars = [
        "GRAPHISTRY_PERSONAL_KEY_ID",
        "GRAPHISTRY_PERSONAL_KEY_SECRET", 
        "GRAPHISTRY_ORG_NAME",
        "GRAPHISTRY_API_KEY",
        "GRAPHISTRY_USERNAME",
        "GRAPHISTRY_PASSWORD",
        "LOUIE_URL",
        "LOUIE_TIMEOUT",
        "LOUIE_STREAMING_TIMEOUT",
        "GRAPHISTRY_SERVER"
    ]
    
    # Check if environment variables are referenced in cursor.py
    try:
        from louieai.notebook.cursor import Cursor
        import inspect
        
        cursor_source = inspect.getsource(Cursor.__init__)
        
        supported_vars = []
        unsupported_vars = []
        
        for var in documented_env_vars:
            if var in cursor_source:
                supported_vars.append(var)
                print(f"✅ {var} - SUPPORTED in code")
            else:
                unsupported_vars.append(var)
                print(f"❓ {var} - NOT FOUND in Cursor.__init__")
        
        results["working"].extend([f"{var} environment variable" for var in supported_vars])
        results["maybe_broken"].extend([f"{var} environment variable" for var in unsupported_vars])
        
    except Exception as e:
        print(f"❌ Could not check environment variable support: {e}")
        results["broken"].append(f"Environment variable check: {e}")
    
    # 4. Test other factory patterns
    print("\n4. FACTORY FUNCTIONS")
    print("-" * 30)
    
    try:
        from louieai import louie, Cursor
        
        # Test louie() returns Cursor
        cursor = louie()
        if isinstance(cursor, Cursor):
            print("✅ louie() returns Cursor instance")
            results["working"].append("louie() returns Cursor")
        else:
            print(f"❌ louie() returns {type(cursor)}, expected Cursor")
            results["broken"].append(f"louie() returns {type(cursor)}, not Cursor")
            
    except Exception as e:
        print(f"❌ louie() factory test failed: {e}")
        results["broken"].append(f"louie() factory: {e}")
    
    # 5. Summary
    print("\n" + "=" * 60)
    print("📊 AUDIT SUMMARY")
    print("=" * 60)
    
    if results["working"]:
        print(f"\n✅ WORKING ({len(results['working'])} items):")
        for item in results["working"]:
            print(f"   • {item}")
    
    if results.get("maybe_broken"):
        print(f"\n❓ UNCLEAR ({len(results['maybe_broken'])} items):")
        for item in results["maybe_broken"]:
            print(f"   • {item}")
    
    if results["broken"]:
        print(f"\n❌ BROKEN/MISSING ({len(results['broken'])} items):")
        for item in results["broken"]:
            print(f"   • {item}")
    
    print(f"\nTotal items checked: {sum(len(v) for v in results.values())}")
    
    if not results["broken"]:
        print("\n🎉 All documented features appear to be working!")
        return 0
    else:
        print(f"\n⚠️  Found {len(results['broken'])} issues that need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())