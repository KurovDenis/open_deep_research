# 🚀 SGR Streaming - Enhanced Schema-Guided Reasoning

Enhanced SGR version with streaming output, animations and extended visualization.

## 📁 Files

### Core Components
- **`sgr_streaming.py`** - main file with streaming support
- **`enhanced_streaming.py`** - enhanced JSON schema streaming module
- **`sgr_visualizer.py`** - SGR process visualizer
- **`sgr_step_tracker.py`** - execution step tracker

### Utilities and Demos
- **`demo_enhanced_streaming.py`** - full feature demonstration
- **`compact_streaming_example.py`** - compact streaming example
- **`scraping.py`** - web scraping utilities

### Configuration
- **`config.yaml`** - configuration file

## 🚀 Usage

```bash
# Navigate to directory
cd sgr-streaming

# Main streaming system
python sgr_streaming.py

# Feature demonstration
python demo_enhanced_streaming.py

# Compact streaming example
python compact_streaming_example.py
```

## ✨ Features

### 🎨 Visual Enhancements
- ⚡ **Real-time JSON streaming** with animated progress bars
- 🌳 **Interactive schema trees** with field details
- 🎬 **Smooth animations** and color coding
- 📊 **Live performance metrics**

### 📊 Extended Analytics
- 🔍 **Real-time schema detection**
- ⏱️ **Timing metrics** for each step
- 📈 **Parsing statistics** and success rates
- 🎯 **Step grouping** (multiple searches)

### 🔄 SGR Process Monitor
- 📋 **Pipeline visualization** of all SGR steps
- 📚 **Execution history** with results
- 🔄 **Step transitions** with animations
- 📊 **Contextual task information**

### 🛠️ Fixes
- ✅ **Compact panels** - no large gaps after streaming
- ✅ **Proper step grouping** - no planning duplication
- ✅ **Clarification questions display** - correct post-streaming display

## 📋 Configuration

Copy `config.yaml.example` to `config.yaml` and configure:

```yaml
openai:
  api_key: "your-api-key"
  model: "gpt-4o-mini"
  base_url: ""  # Optional for custom endpoints
  
tavily:
  api_key: "your-tavily-key"
  
execution:
  max_steps: 6
  reports_dir: "reports"
```

## 🔧 Requirements

```bash
pip install openai tavily-python pydantic rich annotated-types
```

## 🎯 Demonstrations

### Main Demos
```bash
# Full feature demonstration
python demo_enhanced_streaming.py

# Choose demo:
# 1. JSON Streaming Parser - real-time parsing
# 2. Schema-Specific Displays - specialized displays
# 3. Full SGR Process Monitor - complete SGR monitoring
# 4. All Demos - run all demonstrations
```

### Compact Streaming
```bash
# Compact display solutions demonstration
python compact_streaming_example.py
```

## 🔍 Differences from Classic

| Feature | Classic | Streaming |
|---------|---------|-----------|
| JSON Parsing | Static | Streaming with animation |
| Metrics | Basic | Detailed + timing |
| Visualization | Simple | Interactive |
| SGR Steps | Text output | Visual pipeline |
| Display | Large blocks | Compact panels |
| Animations | None | Spinners, progress bars |
| History | Simple log | Grouping + statistics |

## 🐛 Resolved Issues

1. **Large gaps after streaming** ✅
   - Added `expand=False` and fixed panel widths
   
2. **Planning step duplication** ✅
   - Created `SGRStepTracker` for proper tracking
   
3. **Clarification questions not displayed** ✅
   - Added special handling and question display

4. **Schema overlapping Completed block** ✅
   - Added proper spacing and formatting

## 🎨 Visual Examples

When running, you'll see:
- 🌳 **Schema trees** with real-time field progress
- 📊 **Live performance metrics**
- 🎬 **Animated progress bars** for each JSON field
- 🔄 **SGR pipeline** with color-coded steps
- ❓ **Beautiful question panels** for clarification
- 📈 **Compact summaries** without large gaps

---

✨ **Enjoy beautiful and informative SGR streaming!** ✨