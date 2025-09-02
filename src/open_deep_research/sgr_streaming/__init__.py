"""SGR Streaming Components for Open Deep Research"""

try:
    from .sgr_streaming import SGRAgent, NextStep
    SGR_AGENT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  SGRAgent not available: {e}")
    SGR_AGENT_AVAILABLE = False
    
try:
    from .enhanced_streaming import enhanced_streaming_display, EnhancedSchemaParser
    ENHANCED_STREAMING_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Enhanced streaming not available: {e}")
    ENHANCED_STREAMING_AVAILABLE = False
    
try:
    from .sgr_visualizer import SGRLiveMonitor
    VISUALIZER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  SGR visualizer not available: {e}")
    VISUALIZER_AVAILABLE = False
    
try:
    from .sgr_step_tracker import SGRStepTracker
    STEP_TRACKER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  SGR step tracker not available: {e}")
    STEP_TRACKER_AVAILABLE = False

# Export what's available
__all__ = []

if SGR_AGENT_AVAILABLE:
    __all__.extend(["SGRAgent", "NextStep"])
if ENHANCED_STREAMING_AVAILABLE:
    __all__.extend(["enhanced_streaming_display", "EnhancedSchemaParser"])
if VISUALIZER_AVAILABLE:
    __all__.append("SGRLiveMonitor")
if STEP_TRACKER_AVAILABLE:
    __all__.append("SGRStepTracker")

SGR_COMPONENTS_AVAILABLE = any([
    SGR_AGENT_AVAILABLE,
    ENHANCED_STREAMING_AVAILABLE, 
    VISUALIZER_AVAILABLE,
    STEP_TRACKER_AVAILABLE
])