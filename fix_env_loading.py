#!/usr/bin/env python3
"""
Quick fix to enable .env file loading in PBT
"""

import os
from pathlib import Path

def patch_pbt_env_loading():
    """Add .env loading to PBT core modules"""
    
    # Find PBT installation path
    try:
        import pbt
        pbt_path = Path(pbt.__file__).parent
        print(f"Found PBT at: {pbt_path}")
    except ImportError:
        print("❌ PBT not installed. Run: pip install -e .")
        return False
    
    # Patch the config module to load .env files
    config_file = pbt_path / "core" / "config.py"
    
    if not config_file.exists():
        print(f"❌ Config file not found: {config_file}")
        return False
    
    # Read current config
    with open(config_file, 'r') as f:
        content = f.read()
    
    # Check if already patched
    if "load_dotenv" in content:
        print("✅ .env loading already enabled")
        return True
    
    # Add dotenv import and loading
    if "import os" in content:
        # Add after existing imports
        new_content = content.replace(
            "import os",
            """import os
from dotenv import load_dotenv

# Load .env file from current directory or parent directories
load_dotenv()"""
        )
        
        # Write back
        with open(config_file, 'w') as f:
            f.write(new_content)
        
        print("✅ Added .env loading to PBT config")
        return True
    else:
        print("❌ Could not patch config file")
        return False

if __name__ == "__main__":
    print("🔧 Fixing PBT .env loading...")
    
    # Install python-dotenv if not present
    try:
        import dotenv
    except ImportError:
        print("📦 Installing python-dotenv...")
        os.system("pip install python-dotenv")
    
    if patch_pbt_env_loading():
        print("\n✅ PBT should now load .env files automatically!")
        print("\n🧪 Test it:")
        print("  pbt generate --goal 'Summarize customer feedback' --variables 'feedback'")
    else:
        print("\n❌ Patch failed. Use manual workaround:")
        print("  export $(cat .env | xargs) && pbt generate --goal 'test'")