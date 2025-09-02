#!/usr/bin/env python3
"""
Comprehensive Dependency Installation Script
Installs all required dependencies for SGR + Deep Research integration
"""

import subprocess
import sys
import importlib
from pathlib import Path

def run_command(command, description=""):
    """Run a command and handle errors"""
    print(f"🔄 {description}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        print(f"✅ {description} - Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed")
        print(f"Error: {e.stderr}")
        return False

def check_package(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name.replace('-', '_')
    
    try:
        importlib.import_module(import_name)
        return True
    except ImportError:
        return False

def main():
    """Main installation process"""
    print("🚀 SGR + Deep Research Dependency Installation")
    print("=" * 60)
    
    # Core LangChain packages
    langchain_packages = [
        "langchain-core",
        "langchain-community", 
        "langchain-openai",
        "langchain-anthropic",
        "langchain-google-genai",
        "langchain-tavily",
        "langchain-mcp-adapters",
        "langgraph",
        "langsmith"
    ]
    
    # SGR specific packages
    sgr_packages = [
        "openai",
        "tavily-python", 
        "rich",
        "pydantic",
        "httpx",
        "aiohttp",
        "python-dotenv",
        "tenacity"
    ]
    
    all_packages = langchain_packages + sgr_packages
    
    print(f"📦 Installing {len(all_packages)} packages...")
    
    # Method 1: Try requirements.txt
    print("\n🎯 Method 1: Installing from requirements.txt")
    if run_command("pip install -r requirements.txt", "Installing from requirements.txt"):
        print("✅ Requirements.txt installation successful")
    else:
        print("⚠️ Requirements.txt failed, trying individual packages...")
        
        # Method 2: Individual package installation
        print("\n🎯 Method 2: Installing packages individually")
        failed_packages = []
        
        for package in all_packages:
            if not run_command(f"pip install -U {package}", f"Installing {package}"):
                failed_packages.append(package)
        
        if failed_packages:
            print(f"\n⚠️ Failed to install: {', '.join(failed_packages)}")
            
            # Method 3: Try with pip upgrade
            print("\n🎯 Method 3: Trying with --upgrade --force-reinstall")
            for package in failed_packages:
                run_command(f"pip install --upgrade --force-reinstall {package}", f"Force installing {package}")
    
    # Verification
    print("\n🔍 Verifying installations...")
    verification_map = {
        "langchain-core": "langchain_core",
        "langchain-openai": "langchain_openai", 
        "langchain-anthropic": "langchain_anthropic",
        "langgraph": "langgraph",
        "openai": "openai",
        "rich": "rich",
        "tavily-python": "tavily"
    }
    
    success_count = 0
    for package, import_name in verification_map.items():
        if check_package(package, import_name):
            print(f"✅ {package} - Available")
            success_count += 1
        else:
            print(f"❌ {package} - Missing")
    
    print(f"\n📊 Verification Results: {success_count}/{len(verification_map)} packages available")
    
    if success_count == len(verification_map):
        print("\n🎉 All dependencies installed successfully!")
        print("🚀 Ready to run: python sgr_deep_research_interface.py")
    else:
        print("\n⚠️ Some dependencies are missing. Please check the errors above.")
        print("💡 Try running: pip install --upgrade --force-reinstall langchain-openai")
    
    print("\n📚 Next steps:")
    print("1. Run: python sgr_deep_research_interface.py")
    print("2. Enter your research query")
    print("3. Watch SGR streaming in action!")

if __name__ == "__main__":
    main()