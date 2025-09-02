#!/usr/bin/env python3
"""
Test SGR Demo Components
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent / "src"
sys.path.insert(0, str(project_root))

print("🧪 Testing SGR Demo Components...")

try:
    from open_deep_research.sgr_streaming.demo_enhanced_streaming import demo_json_streaming_parsing, demo_schema_specific_displays
    print("✅ Demo functions imported successfully")
    
    # Test individual components
    print("\n🎯 Testing JSON Streaming Parser...")
    try:
        demo_json_streaming_parsing()
        print("✅ JSON Streaming Parser demo completed")
    except Exception as e:
        print(f"❌ JSON Streaming Parser error: {e}")
    
    print("\n🎨 Testing Schema-Specific Displays...")
    try:
        demo_schema_specific_displays()
        print("✅ Schema-Specific Displays demo completed")
    except Exception as e:
        print(f"❌ Schema-Specific Displays error: {e}")
    
    print("\n🔄 Testing Full SGR Process Demo...")
    try:
        from open_deep_research.sgr_streaming.sgr_visualizer import demo_sgr_visualization
        demo_sgr_visualization()
        print("✅ Full SGR Process demo completed")
    except Exception as e:
        print(f"❌ Full SGR Process demo error: {e}")
    
    print("\n🎉 All demo components tested!")
    
except Exception as e:
    print(f"❌ Import error: {e}")