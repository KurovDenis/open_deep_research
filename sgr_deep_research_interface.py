#!/usr/bin/env python3
"""
SGR + Deep Research Interactive Interface
Test the Deep Research agent with SGR streaming visualization
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent / "src"
sys.path.insert(0, str(project_root))

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.layout import Layout
from rich.live import Live
from rich.text import Text

class SGRDeepResearchInterface:
    """Interactive interface for testing Deep Research with SGR streaming"""
    
    def __init__(self):
        self.console = Console()
        self.config = None
        self.deep_researcher = None
        self.sgr_monitor = None
        
    def setup(self):
        """Setup Deep Research and SGR components"""
        try:
            # Import Deep Research components
            from open_deep_research.deep_researcher import deep_researcher
            from open_deep_research.configuration import Configuration
            from open_deep_research.sgr_config import config as sgr_config
            
            # Import SGR components
            from open_deep_research.sgr_streaming.sgr_visualizer import SGRLiveMonitor
            from open_deep_research.sgr_streaming.enhanced_streaming import EnhancedSchemaParser
            
            if not sgr_config:
                self.console.print("❌ [red]SGR configuration not available. Please check your .env file.[/red]")
                return False
            
            self.config = sgr_config
            self.deep_researcher = deep_researcher
            self.sgr_monitor = SGRLiveMonitor(self.console)
            
            self.console.print("✅ [green]Deep Research + SGR integration ready![/green]")
            return True
            
        except Exception as e:
            self.console.print(f"❌ [red]Setup error: {e}[/red]")
            return False
    
    def show_welcome(self):
        """Display welcome screen"""
        self.console.clear()
        
        welcome_panel = Panel(
            "[bold cyan]🚀 Deep Research + SGR Streaming Interface[/bold cyan]\n\n"
            "Test the complete Open Deep Research workflow with real-time SGR visualization!\n\n"
            "✨ [bold]What you'll see:[/bold]\n"
            "• 🔍 Real research workflow execution\n"
            "• 🎬 SGR streaming visualization\n"
            "• 📊 Live progress monitoring\n"
            "• 🧠 Step-by-step reasoning display\n"
            "• 📝 Final research report generation\n\n"
            "[bold yellow]Experience PhD-level research with AI transparency![/bold yellow]",
            title="🎯 Deep Research Lab",
            border_style="cyan",
            expand=False
        )
        
        self.console.print(welcome_panel)
        
        # Show configuration
        if self.config:
            config_table = Table(show_header=False, box=None, padding=(0, 1))
            config_table.add_column("Setting", style="cyan", width=20)
            config_table.add_column("Value", style="white")
            
            config_table.add_row("🤖 Research Model", self.config.RESEARCHER_MODEL_NAME)
            config_table.add_row("📝 Report Model", self.config.WRITER_MODEL_NAME)
            config_table.add_row("🔍 Search Provider", "Tavily")
            config_table.add_row("🎚️ SGR Streaming", "Enabled" if self.config.STREAMING_ENABLED else "Disabled")
            config_table.add_row("📊 Max Iterations", str(self.config.MAX_SUPERVISOR_ITERATIONS))
            
            self.console.print(Panel(
                config_table,
                title="⚙️ Research Configuration",
                border_style="blue",
                expand=False
            ))
    
    def get_research_query(self):
        """Get research query from user with examples"""
        self.console.print("\n📝 [bold]Enter Your Research Query[/bold]")
        
        examples = [
            "Analyze the impact of generative AI on software development productivity in 2024",
            "Compare renewable energy adoption policies across European Union countries",
            "Research the current state of quantum computing applications in financial services",
            "Investigate the effects of remote work on team collaboration and innovation",
            "Study blockchain technology adoption in supply chain management",
            "Analyze recent developments in autonomous vehicle safety regulations",
            "Research the impact of social media algorithms on information consumption patterns"
        ]
        
        example_table = Table(show_header=False, box=None)
        example_table.add_column("💡 Example Research Queries", style="dim yellow")
        
        for example in examples:
            example_table.add_row(f"• {example}")
        
        self.console.print(example_table)
        
        while True:
            research_query = Prompt.ask(
                "\n🔍 [bold cyan]Your research query[/bold cyan]", 
                default="Analyze the impact of generative AI on software development productivity in 2024"
            )
            
            if len(research_query.strip()) < 15:
                self.console.print("❌ [red]Please provide a more detailed research query (at least 15 characters)[/red]")
                continue
            
            # Show confirmation
            self.console.print(f"\n📋 [bold]Research Query:[/bold]")
            self.console.print(Panel(research_query, border_style="cyan", expand=False))
            
            if Confirm.ask("🤔 [bold]Proceed with this research query?[/bold]", default=True):
                return research_query
    
    async def run_deep_research_with_sgr(self, research_query):
        """Run Deep Research workflow with SGR streaming visualization"""
        
        self.console.print("\n" + "="*80)
        self.console.print("🎬 [bold yellow]Starting Deep Research with SGR Streaming[/bold yellow]")
        self.console.print("🎯 [dim]Watch the complete research workflow with real-time visualization![/dim]")
        self.console.print("="*80 + "\n")
        
        # Start SGR monitoring
        self.sgr_monitor.start_monitoring()
        self.sgr_monitor.update_context({
            "task": research_query,
            "workflow": "Deep Research",
            "streaming_enabled": True
        })
        
        try:
            # Create research configuration
            research_config = {
                "configurable": {
                    "research_model": self.config.get_openrouter_model_name("researcher"),
                    "final_report_model": self.config.get_openrouter_model_name("writer"),
                    "compression_model": self.config.get_openrouter_model_name("researcher"),
                    "allow_clarification": True,
                    "max_researcher_iterations": self.config.MAX_SUPERVISOR_ITERATIONS,
                    "max_concurrent_research_units": 3,
                    "max_react_tool_calls": 5,
                    "research_model_max_tokens": self.config.RESEARCH_MODEL_MAX_TOKENS,
                    "final_report_model_max_tokens": self.config.FINAL_REPORT_MODEL_MAX_TOKENS,
                    "compression_model_max_tokens": self.config.COMPRESSION_MODEL_MAX_TOKENS,
                    "max_structured_output_retries": 3
                }
            }
            
            # Prepare input state
            input_state = {
                "messages": [{"role": "user", "content": research_query}]
            }
            
            self.console.print("🔄 [bold]Phase 1: Clarification & Planning[/bold]")
            self.sgr_monitor.update_context({"current_phase": "clarification"})
            
            # Execute Deep Research workflow
            self.console.print("🚀 [bold green]Executing Deep Research Workflow...[/bold green]")
            
            result = await self.deep_researcher.ainvoke(
                input_state, 
                config=research_config
            )
            
            # Show completion
            self.sgr_monitor.stop_monitoring()
            
            self.console.print("\n" + "="*80)
            self.console.print("✅ [bold green]Deep Research Completed Successfully![/bold green]")
            self.console.print("="*80)
            
            # Display results
            await self.display_research_results(result, research_query)
            
        except Exception as e:
            self.sgr_monitor.stop_monitoring()
            self.console.print(f"\n❌ [red]Research error: {e}[/red]")
            import traceback
            self.console.print(f"[dim]Traceback: {traceback.format_exc()}[/dim]")
    
    async def display_research_results(self, result, research_query):
        """Display the research results in a formatted way"""
        
        # Extract final report
        final_report = result.get("final_report", "No final report generated")
        messages = result.get("messages", [])
        
        # Show summary
        summary_table = Table(show_header=False, box=None, padding=(0, 1))
        summary_table.add_column("Metric", style="cyan", width=20)
        summary_table.add_column("Value", style="white")
        
        summary_table.add_row("🎯 Query", research_query[:60] + "..." if len(research_query) > 60 else research_query)
        summary_table.add_row("📝 Report Length", f"{len(final_report)} characters")
        summary_table.add_row("💬 Messages", f"{len(messages)} generated")
        summary_table.add_row("🔍 Workflow", "Deep Research + SGR")
        
        self.console.print(Panel(
            summary_table,
            title="📊 Research Summary",
            border_style="green"
        ))
        
        # Show final report preview
        if final_report and len(final_report) > 100:
            report_preview = final_report[:500] + "..." if len(final_report) > 500 else final_report
            
            self.console.print(Panel(
                report_preview,
                title="📄 Final Report Preview",
                border_style="blue",
                expand=False
            ))
            
            # Option to save report
            if Confirm.ask("\n💾 [bold]Save full report to file?[/bold]", default=True):
                await self.save_research_report(final_report, research_query)
        
        return result
    
    async def save_research_report(self, report, query):
        """Save the research report to a file"""
        try:
            # Create filename from query
            import re
            safe_filename = re.sub(r'[^\w\s-]', '', query)
            safe_filename = re.sub(r'[-\s]+', '-', safe_filename)
            filename = f"research_report_{safe_filename[:50]}.md"
            
            # Write report
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# Research Report\n\n")
                f.write(f"**Query:** {query}\n\n")
                f.write(f"**Generated:** {self.console._environ.get('TODAY', 'Unknown')}\n\n")
                f.write(f"---\n\n")
                f.write(report)
            
            self.console.print(f"✅ [green]Report saved to: {filename}[/green]")
            
        except Exception as e:
            self.console.print(f"❌ [red]Error saving report: {e}[/red]")
    
    def show_features_overview(self):
        """Show what features will be demonstrated"""
        features_table = Table(show_header=True, header_style="bold cyan")
        features_table.add_column("🎯 Phase", style="cyan", width=20)
        features_table.add_column("📋 Description", style="white", width=50)
        features_table.add_column("🎬 SGR Visualization", style="yellow", width=25)
        
        features_table.add_row(
            "Clarification", 
            "AI analyzes query and asks clarifying questions if needed",
            "Real-time reasoning display"
        )
        features_table.add_row(
            "Research Planning", 
            "Creates structured research brief and strategy",
            "Schema-guided planning"
        )
        features_table.add_row(
            "Research Execution", 
            "Conducts web searches and gathers information",
            "Live search monitoring"
        )
        features_table.add_row(
            "Report Generation", 
            "Synthesizes findings into comprehensive report",
            "Streaming report creation"
        )
        
        self.console.print(Panel(
            features_table,
            title="🎭 Research Workflow Features",
            border_style="magenta"
        ))

async def main():
    """Main interface function"""
    
    interface = SGRDeepResearchInterface()
    
    # Setup components
    if not interface.setup():
        interface.console.print("❌ [red]Failed to setup interface. Please check your configuration.[/red]")
        return
    
    try:
        # Show welcome and features
        interface.show_welcome()
        interface.show_features_overview()
        
        # Get research query
        research_query = interface.get_research_query()
        
        # Run research with SGR streaming
        await interface.run_deep_research_with_sgr(research_query)
        
        # Ask if user wants to try another query
        if Confirm.ask("\n🔄 [bold]Try another research query?[/bold]", default=False):
            await main()  # Recursive call for another round
    
    except KeyboardInterrupt:
        interface.console.print("\n👋 [yellow]Research session interrupted by user[/yellow]")
    except Exception as e:
        interface.console.print(f"\n❌ [red]Interface error: {e}[/red]")

if __name__ == "__main__":
    asyncio.run(main())