#!/usr/bin/env python3
"""
Enhanced Deep Research with SGR Streaming Integration
Modified version of deep_researcher.py with integrated SGR streaming visualization
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent / "src"
sys.path.insert(0, str(project_root))

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

async def run_enhanced_deep_research():
    """Run Deep Research with enhanced SGR streaming integration"""
    
    console = Console()
    
    console.print(Panel(
        "[bold cyan]🚀 Enhanced Deep Research with SGR Streaming[/bold cyan]\n\n"
        "Experience the complete research workflow with real-time visualization!",
        title="🎯 Research Lab",
        border_style="cyan"
    ))
    
    try:
        # Import required components
        from open_deep_research.deep_researcher import deep_researcher
        from open_deep_research.sgr_config import config
        from open_deep_research.sgr_streaming.sgr_visualizer import SGRLiveMonitor
        
        if not config:
            console.print("❌ [red]Configuration not available. Check your .env file.[/red]")
            return
        
        console.print("✅ [green]Components loaded successfully[/green]")
        
        # Get research query
        research_query = Prompt.ask(
            "\n🔍 [bold cyan]Enter your research query[/bold cyan]",
            default="Analyze the impact of AI on healthcare diagnostics in 2024"
        )
        
        console.print(f"\n📋 [bold]Research Query:[/bold] {research_query}")
        
        # Setup SGR monitoring
        monitor = SGRLiveMonitor(console)
        monitor.start_monitoring()
        monitor.update_context({
            "task": research_query,
            "workflow": "Deep Research Enhanced"
        })
        
        console.print("\n🎬 [bold yellow]Starting Enhanced Research...[/bold yellow]")
        
        # Create configuration for Deep Research
        research_config = {
            "configurable": {
                "research_model": config.get_openrouter_model_name("researcher"),
                "final_report_model": config.get_openrouter_model_name("writer"),
                "compression_model": config.get_openrouter_model_name("researcher"),
                "allow_clarification": False,  # Skip clarification for demo
                "max_researcher_iterations": 3,
                "max_concurrent_research_units": 2,
                "max_react_tool_calls": 4,
                "research_model_max_tokens": config.RESEARCH_MODEL_MAX_TOKENS,
                "final_report_model_max_tokens": config.FINAL_REPORT_MODEL_MAX_TOKENS,
                "compression_model_max_tokens": config.COMPRESSION_MODEL_MAX_TOKENS,
                "max_structured_output_retries": 3,
                # Add SGR-specific configuration
                "streaming_enabled": True,
                "sgr_monitoring": True
            }
        }
        
        # Prepare input
        input_state = {
            "messages": [{"role": "user", "content": research_query}]
        }
        
        # Execute with monitoring
        console.print("🔄 [bold]Executing research workflow...[/bold]")
        
        result = await deep_researcher.ainvoke(
            input_state, 
            config=research_config
        )
        
        # Stop monitoring
        monitor.stop_monitoring()
        
        console.print("\n✅ [bold green]Research completed![/bold green]")
        
        # Display results
        if "final_report" in result:
            report = result["final_report"]
            console.print(f"\n📄 [bold]Final Report ({len(report)} characters):[/bold]")
            
            # Show preview
            preview = report[:800] + "..." if len(report) > 800 else report
            console.print(Panel(preview, title="📄 Report Preview", border_style="green"))
            
            # Save option
            from rich.prompt import Confirm
            if Confirm.ask("💾 Save full report to file?", default=True):
                filename = f"research_report_{hash(research_query) % 10000}.md"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"# Research Report\n\n**Query:** {research_query}\n\n---\n\n{report}")
                console.print(f"✅ Report saved to: {filename}")
        
    except Exception as e:
        console.print(f"❌ [red]Error: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")

if __name__ == "__main__":
    asyncio.run(run_enhanced_deep_research())