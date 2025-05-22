#!/usr/bin/env python3
"""
Test script to verify .env loading fix
"""

import os
import sys
from pathlib import Path
import tempfile
import subprocess

def test_env_loading():
    """Test that PBT loads .env files correctly"""
    
    print("🧪 Testing .env file loading in PBT...")
    
    # Create a temporary directory with .env file
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create .env file with test API key
        env_file = temp_path / ".env"
        env_file.write_text("ANTHROPIC_API_KEY=sk-ant-test-key-123\n")
        
        print(f"📁 Created test .env at: {env_file}")
        
        # Change to temp directory
        original_cwd = Path.cwd()
        os.chdir(temp_path)
        
        try:
            # Test 1: Import PBT and check if .env is loaded
            print("\n🔍 Test 1: Import pbt and check environment...")
            
            # Clear any existing env var
            if "ANTHROPIC_API_KEY" in os.environ:
                del os.environ["ANTHROPIC_API_KEY"]
            
            # Import PBT (should load .env)
            import pbt
            
            # Check if API key is now available
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key == "sk-ant-test-key-123":
                print("✅ PBT successfully loaded .env file!")
                return True
            else:
                print(f"❌ API key not loaded. Got: {api_key}")
                return False
                
        except Exception as e:
            print(f"❌ Error during test: {e}")
            return False
        finally:
            # Restore original directory
            os.chdir(original_cwd)

def test_cli_command():
    """Test CLI command with .env file"""
    
    print("\n🧪 Testing CLI command with .env...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create .env file with real format
        env_file = temp_path / ".env"
        env_file.write_text("ANTHROPIC_API_KEY=sk-ant-test-key-123\n")
        
        # Change to temp directory
        original_cwd = Path.cwd()
        os.chdir(temp_path)
        
        try:
            # Test pbt --version (should work without API key)
            result = subprocess.run(
                ["pbt", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print("✅ CLI working with .env present")
                return True
            else:
                print(f"❌ CLI failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ CLI test error: {e}")
            return False
        finally:
            os.chdir(original_cwd)

def main():
    """Run all tests"""
    print("🔧 Testing PBT .env loading fixes")
    print("=" * 50)
    
    tests = [
        ("Import & Load .env", test_env_loading),
        ("CLI with .env", test_cli_command),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} passed")
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} error: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! .env loading is working correctly.")
        print("\n🚀 Users can now simply:")
        print("1. Create .env file with ANTHROPIC_API_KEY")
        print("2. Run pbt commands directly")
        print("3. No manual environment variable setup needed!")
        return True
    else:
        print("⚠️ Some tests failed. .env loading may need more work.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)