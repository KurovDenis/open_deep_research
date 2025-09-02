#!/usr/bin/env python3
"""
Quick Deep Research + SGR Test
Test critical dependencies for the integration
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent / "src"
sys.path.insert(0, str(project_root))

def test_core_imports():
    """Test core Deep Research imports"""
    print("🧪 Testing Core Deep Research Imports...")
    
    try:
        from open_deep_research.deep_researcher import deep_researcher
        print("  ✅ deep_researcher imported")
    except Exception as e:
        print(f"  ❌ deep_researcher failed: {e}")
        return False
    
    try:
        from open_deep_research.configuration import Configuration
        print("  ✅ Configuration imported")
    except Exception as e:
        print(f"  ❌ Configuration failed: {e}")
    
    try:
        from open_deep_research.sgr_config import config
        print("  ✅ SGR config imported")
    except Exception as e:
        print(f"  ❌ SGR config failed: {e}")
        return False
    
    return True

def test_langchain_imports():
    """Test LangChain imports"""
    print("\n🧪 Testing LangChain Imports...")
    
    critical_imports = [
        ("langchain_openai", "LangChain OpenAI"),
        ("langchain_core", "LangChain Core"),
        ("langgraph", "LangGraph"),
        ("langchain.chat_models", "Chat Models")
    ]
    
    success_count = 0
    for module, name in critical_imports:
        try:
            __import__(module)
            print(f"  ✅ {name}")
            success_count += 1
        except ImportError as e:
            print(f"  ❌ {name}: {e}")
    
    return success_count == len(critical_imports)

def test_sgr_imports():
    """Test SGR streaming imports"""
    print("\n🧪 Testing SGR Streaming Imports...")
    
    try:
        from open_deep_research.sgr_streaming.sgr_visualizer import SGRLiveMonitor
        print("  ✅ SGRLiveMonitor")
    except Exception as e:
        print(f"  ❌ SGRLiveMonitor: {e}")
        return False
    
    try:
        from open_deep_research.sgr_streaming.enhanced_streaming import enhanced_streaming_display
        print("  ✅ enhanced_streaming_display")
    except Exception as e:
        print(f"  ❌ enhanced_streaming_display: {e}")
        return False
    
    return True

def test_configuration():
    """Test configuration loading"""
    print("\n🧪 Testing Configuration...")
    
    try:
        from open_deep_research.sgr_config import config
        
        if config:
            print("  ✅ SGR configuration loaded")
            print(f"  📊 Research Model: {config.RESEARCHER_MODEL_NAME}")
            print(f"  📊 Writer Model: {config.WRITER_MODEL_NAME}")
            print(f"  📊 Streaming: {config.STREAMING_ENABLED}")
            return True
        else:
            print("  ❌ Configuration is None")
            return False
    except Exception as e:
        print(f"  ❌ Configuration error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 QUICK DEEP RESEARCH + SGR TEST")
    print("=" * 50)
    
    tests = [
        ("Core Imports", test_core_imports),
        ("LangChain Imports", test_langchain_imports), 
        ("SGR Imports", test_sgr_imports),
        ("Configuration", test_configuration)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        if test_func():
            passed += 1
    
    print(f"\n📊 RESULTS: {passed}/{len(tests)} tests passed")
    print("=" * 50)
    
    if passed == len(tests):
        print("🎉 ALL TESTS PASSED!")
        print("✅ Ready to run the full interface!")
        print("\n🚀 Next steps:")
        print("   python sgr_deep_research_interface.py")
    else:
        print("⚠️ SOME TESTS FAILED")
        print("💡 Run dependency installer:")
        print("   python install_dependencies.py")

if __name__ == "__main__":
    main()