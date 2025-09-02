"""SGR Streaming Integration for Open Deep Research"""

try:
    from .sgr_langgraph_adapter import SGRStreamingNode
    SGR_ADAPTER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  SGRStreamingNode not available: {e}")
    SGR_ADAPTER_AVAILABLE = False

try:
    from .unified_workflow import UnifiedSGRWorkflow
    UNIFIED_WORKFLOW_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  UnifiedSGRWorkflow not available: {e}")
    UNIFIED_WORKFLOW_AVAILABLE = False

try:
    from .streaming_researcher import StreamingResearcher
    STREAMING_RESEARCHER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  StreamingResearcher not available: {e}")
    STREAMING_RESEARCHER_AVAILABLE = False

# Export what's available
__all__ = []

if SGR_ADAPTER_AVAILABLE:
    __all__.append("SGRStreamingNode")
if UNIFIED_WORKFLOW_AVAILABLE:
    __all__.append("UnifiedSGRWorkflow")
if STREAMING_RESEARCHER_AVAILABLE:
    __all__.append("StreamingResearcher")

SGR_INTEGRATION_AVAILABLE = any([
    SGR_ADAPTER_AVAILABLE,
    UNIFIED_WORKFLOW_AVAILABLE,
    STREAMING_RESEARCHER_AVAILABLE
])