#!/usr/bin/env python3
"""Simple test for SGR integration"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent / "src"
sys.path.insert(0, str(project_root))

print("🚀 Simple SGR Integration Test")
print("=" * 40)

# Test 1: Basic imports
print("1. Testing basic imports...")
try:
    from open_deep_research.sgr_config import config
    print("  ✅ sgr_config imported")
except Exception as e:
    print(f"  ❌ sgr_config failed: {e}")

# Test 2: SGR streaming imports
print("\n2. Testing SGR streaming imports...")
try:
    from open_deep_research.sgr_streaming import SGRAgent
    print("  ✅ SGRAgent imported")
except Exception as e:
    print(f"  ❌ SGRAgent failed: {e}")

try:
    from open_deep_research.sgr_streaming.enhanced_streaming import enhanced_streaming_display
    print("  ✅ enhanced_streaming_display imported")
except Exception as e:
    print(f"  ❌ enhanced_streaming_display failed: {e}")

# Test 3: Configuration check
print("\n3. Testing configuration...")
try:
    from open_deep_research.sgr_config import config
    if config:
        print("  ✅ Configuration loaded")
        streaming_config = config.get_sgr_streaming_config()
        print(f"  ✅ Streaming config has {len(streaming_config)} settings")
    else:
        print("  ⚠️  Configuration is None (no .env file or missing keys)")
except Exception as e:
    print(f"  ❌ Configuration error: {e}")

# Test 4: Integration components
print("\n4. Testing integration components...")
try:
    from open_deep_research.sgr_integration.sgr_langgraph_adapter import SGRStreamingNode
    print("  ✅ SGRStreamingNode imported")
except Exception as e:
    print(f"  ❌ SGRStreamingNode failed: {e}")

print("\n📊 Test completed!")
print("If you see ✅ for most tests, the integration is working!")
