#!/usr/bin/env python3
"""
Local testing script for PBT
Run this to verify your setup is working
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_api_health():
    """Test if API is running"""
    print("🔍 Testing API health...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ API is running!")
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure backend is running on port 8000")
        return False

def test_prompt_generation():
    """Test prompt generation endpoint"""
    print("\n🤖 Testing prompt generation...")
    
    data = {
        "goal": "Summarize customer feedback into actionable insights",
        "model": "claude",
        "style": "professional",
        "variables": ["feedback_text", "product_category"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/promptgen/generate", json=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Prompt generation working!")
            if result.get("success"):
                print(f"   Generated prompt: {result.get('prompt_yaml', {}).get('name', 'N/A')}")
            else:
                print(f"   Raw response: {result.get('raw_content', '')[:100]}...")
            return True
        else:
            print(f"❌ Prompt generation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing prompt generation: {e}")
        return False

def test_prompt_comparison():
    """Test model comparison endpoint"""
    print("\n🔍 Testing model comparison...")
    
    data = {
        "prompt": "Explain quantum computing in simple terms",
        "models": ["claude", "gpt-4"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/promptgen/compare", json=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Model comparison working!")
            results = result.get("results", {})
            for model, output in results.items():
                print(f"   {model}: {output[:50]}...")
            return True
        else:
            print(f"❌ Model comparison failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing model comparison: {e}")
        return False

def test_prompt_packs():
    """Test prompt packs endpoints"""
    print("\n📦 Testing prompt packs...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/promptpacks/list")
        if response.status_code == 200:
            result = response.json()
            prompts = result.get("prompts", [])
            print(f"✅ Found {len(prompts)} prompt packs!")
            for prompt in prompts[:3]:
                print(f"   - {prompt.get('name', 'Unknown')} v{prompt.get('version', '0.0.0')}")
            return True
        else:
            print(f"❌ Prompt packs failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing prompt packs: {e}")
        return False

def test_marketplace():
    """Test marketplace endpoint"""
    print("\n🛒 Testing marketplace...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/promptpacks/marketplace")
        if response.status_code == 200:
            result = response.json()
            packs = result.get("packs", [])
            print(f"✅ Marketplace has {len(packs)} packs!")
            return True
        else:
            print(f"❌ Marketplace failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing marketplace: {e}")
        return False

def test_analytics():
    """Test analytics endpoint"""
    print("\n📊 Testing analytics...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/stats/dashboard")
        if response.status_code == 200:
            result = response.json()
            print("✅ Analytics working!")
            print(f"   Total prompts: {result.get('totalPrompts', 0)}")
            print(f"   Total evaluations: {result.get('totalEvaluations', 0)}")
            print(f"   Average score: {result.get('avgScore', 0):.1f}")
            return True
        else:
            print(f"❌ Analytics failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing analytics: {e}")
        return False

def test_export():
    """Test export endpoints"""
    print("\n📤 Testing export...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/export/formats")
        if response.status_code == 200:
            result = response.json()
            formats = result.get("formats", [])
            print(f"✅ Export supports {len(formats)} formats!")
            for fmt in formats:
                print(f"   - {fmt.get('name', 'Unknown')}")
            return True
        else:
            print(f"❌ Export failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing export: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Starting PBT Local Tests")
    print("=" * 50)
    
    tests = [
        test_api_health,
        test_prompt_packs,
        test_marketplace,
        test_analytics,
        test_export,
        test_prompt_generation,
        test_prompt_comparison
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        time.sleep(0.5)  # Brief pause between tests
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your PBT setup is working perfectly!")
        print("\n🚀 Next steps:")
        print("   1. Visit http://localhost:8000/docs for API documentation")
        print("   2. Try the CLI: python cli/pbt.py --help")
        print("   3. Test prompt generation: python cli/pbt.py generate-prompt --goal 'Test prompt'")
    else:
        print("⚠️  Some tests failed. Check your configuration:")
        print("   1. Ensure all required API keys are in .env")
        print("   2. Verify Supabase database is set up")
        print("   3. Check that backend is running on port 8000")

if __name__ == "__main__":
    main()