#!/usr/bin/env python3
"""
Test script to verify PBT installation
"""

import sys
import subprocess
import importlib
from pathlib import Path

def test_imports():
    """Test that all core modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import pbt
        print(f"✅ pbt version: {pbt.__version__}")
    except ImportError as e:
        print(f"❌ Failed to import pbt: {e}")
        return False
    
    modules_to_test = [
        "pbt.cli.main",
        "pbt.core.config",
        "pbt.core.project", 
        "pbt.core.generator",
        "pbt.core.evaluator",
        "pbt.core.deployer"
    ]
    
    for module in modules_to_test:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            return False
    
    return True

def test_cli_command():
    """Test that the CLI command is available"""
    print("\n🔍 Testing CLI command...")
    
    try:
        result = subprocess.run(
            ["pbt", "--version"], 
            capture_output=True, 
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"✅ CLI working: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ CLI failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ CLI command timed out")
        return False
    except FileNotFoundError:
        print("❌ 'pbt' command not found in PATH")
        return False
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False

def test_help_command():
    """Test help command"""
    print("\n🔍 Testing help command...")
    
    try:
        result = subprocess.run(
            ["pbt", "--help"], 
            capture_output=True, 
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and "Prompt Build Tool" in result.stdout:
            print("✅ Help command working")
            return True
        else:
            print(f"❌ Help command failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Help test failed: {e}")
        return False

def test_project_init():
    """Test project initialization"""
    print("\n🔍 Testing project initialization...")
    
    test_dir = Path("test_pbt_project")
    
    try:
        # Clean up any existing test directory
        if test_dir.exists():
            import shutil
            shutil.rmtree(test_dir)
        
        # Test init command
        result = subprocess.run(
            ["pbt", "init", "--name", "Test Project", "--directory", str(test_dir)], 
            capture_output=True, 
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # Check if files were created
            expected_files = [
                test_dir / "pbt.yaml",
                test_dir / ".env.example",
                test_dir / "prompts",
                test_dir / "tests",
                test_dir / "evaluations"
            ]
            
            all_exist = all(path.exists() for path in expected_files)
            
            if all_exist:
                print("✅ Project initialization working")
                
                # Clean up
                import shutil
                shutil.rmtree(test_dir)
                return True
            else:
                print("❌ Not all expected files/directories were created")
                return False
        else:
            print(f"❌ Init command failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Project init test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing PBT Installation")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("CLI Command", test_cli_command),
        ("Help Command", test_help_command),
        ("Project Init", test_project_init)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} error: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! PBT is installed correctly.")
        print("\n🚀 Next steps:")
        print("1. Add API keys to .env file")
        print("2. Run: pbt init --name 'My Project'")
        print("3. Run: pbt generate --goal 'Your prompt goal'")
        return True
    else:
        print("⚠️ Some tests failed. Check the installation.")
        print("\n🔧 Try:")
        print("1. source venv/bin/activate")
        print("2. pip install -e '.[all]'")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)