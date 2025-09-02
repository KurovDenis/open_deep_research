#!/usr/bin/env python3
"""
SGR Research Agent - Schema-Guided Reasoning with Streaming Support
Simplified version for Open Deep Research integration
"""

import json
import os
import time
from datetime import datetime
from typing import List, Union, Literal, Optional, Dict, Any
try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

from pydantic import BaseModel, Field
from annotated_types import MinLen, MaxLen
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .enhanced_streaming import enhanced_streaming_display, EnhancedSchemaParser
from .sgr_visualizer import SGRLiveMonitor
from .sgr_step_tracker import SGRStepTracker

# =============================================================================
# SGR SCHEMAS - Essential schemas for integration
# =============================================================================

class Clarification(BaseModel):
    """Ask clarifying questions when facing ambiguous requests"""
    tool: Literal["clarification"]
    reasoning: str = Field(description="Why clarification is needed")
    unclear_terms: Annotated[List[str], MinLen(1), MaxLen(5)] = Field(description="List of unclear terms or concepts")
    assumptions: Annotated[List[str], MinLen(2), MaxLen(4)] = Field(description="Possible interpretations to verify")
    questions: Annotated[List[str], MinLen(3), MaxLen(5)] = Field(description="3-5 specific clarifying questions")

class GeneratePlan(BaseModel):
    """Generate research plan based on clear user request"""
    tool: Literal["generate_plan"]
    reasoning: str = Field(description="Justification for research approach")
    research_goal: str = Field(description="Primary research objective")
    planned_steps: Annotated[List[str], MinLen(3), MaxLen(4)] = Field(description="List of 3-4 planned steps")
    search_strategies: Annotated[List[str], MinLen(2), MaxLen(3)] = Field(description="Information search strategies")

class WebSearch(BaseModel):
    """Search for information with credibility focus"""
    tool: Literal["web_search"]
    reasoning: str = Field(description="Why this search is needed and what to expect")
    query: str = Field(description="Search query in same language as user request")
    max_results: int = Field(default=10, description="Maximum results (1-15)")
    plan_adapted: bool = Field(default=False, description="Is this search after plan adaptation?")

class CreateReport(BaseModel):
    """Create comprehensive research report with citations"""
    tool: Literal["create_report"]
    reasoning: str = Field(description="Why ready to create report now")
    title: str = Field(description="Report title in same language as user request")
    user_request_language_reference: str = Field(description="Copy of original user request to ensure language consistency")
    content: str = Field(description="Detailed technical content (800+ words) with in-text citations [1], [2], [3]")
    confidence: Literal["high", "medium", "low"] = Field(description="Confidence in findings")

class NextStep(BaseModel):
    """SGR Core - Determines next reasoning step with adaptive planning"""
    
    reasoning_steps: Annotated[List[str], MinLen(2), MaxLen(4)] = Field(
        description="Step-by-step reasoning process leading to decision"
    )
    current_situation: str = Field(description="Current research situation analysis")
    plan_status: str = Field(description="Status of current plan execution")
    searches_done: int = Field(default=0, description="Number of searches completed (MAX 3-4 searches)")
    enough_data: bool = Field(default=False, description="Sufficient data for report? (True after 2-3 searches)")
    remaining_steps: Annotated[List[str], MinLen(1), MaxLen(3)] = Field(description="1-3 remaining steps to complete task")
    task_completed: bool = Field(description="Is the research task finished?")
    
    function: Union[
        Clarification,
        GeneratePlan,
        WebSearch,
        CreateReport
    ]

# =============================================================================
# SGR AGENT CLASS
# =============================================================================

class SGRAgent:
    """SGR Agent with streaming support for Open Deep Research integration"""
    
    def __init__(self, config: dict):
        self.config = config
        
        # Initialize OpenAI client
        openai_kwargs = {'api_key': config.get('openai_api_key', '')}
        if config.get('openai_base_url'):
            openai_kwargs['base_url'] = config['openai_base_url']
        
        self.client = OpenAI(**openai_kwargs)
        self.console = Console()
        
        # SGR Process Monitor
        self.step_tracker = SGRStepTracker()
        self.monitor = SGRLiveMonitor(self.console, self.step_tracker)
        
        # Context for research session
        self.context = {
            "plan": None,
            "searches": [],
            "sources": {},
            "citation_counter": 0,
            "clarification_used": False
        }
    
    def get_system_prompt(self, user_request: str) -> str:
        """Generate system prompt with user request for language detection"""
        return f"""
You are an expert researcher with adaptive planning and Schema-Guided Reasoning capabilities.

USER REQUEST: "{user_request}"
↑ CRITICAL: Use the SAME LANGUAGE as this request for ALL outputs.

CORE PRINCIPLES:
1. CLARIFICATION FIRST: For ANY uncertainty - ask clarifying questions
2. DO NOT make assumptions - better ask than guess wrong
3. Follow planned steps systematically
4. Search queries in SAME LANGUAGE as user request
5. Report ENTIRELY in SAME LANGUAGE as user request
6. Every fact in report MUST have inline citation [1], [2], [3]

WORKFLOW:
0. clarification (HIGHEST PRIORITY) - when request unclear
1. generate_plan - create research plan
2. web_search - gather information (2-3 searches MAX)
3. create_report - create detailed report with citations

SEARCH STRATEGY:
- After generating a plan, FOLLOW IT step by step
- Each search should address a different aspect from your planned_steps
- Don't stop after 1 search - continue until you have comprehensive data
- Only create report when you have sufficient data from multiple searches

LANGUAGE RULE: Always respond in the SAME LANGUAGE as the user's request.
        """.strip()
    
    def stream_next_step(self, messages: List[Dict[str, str]]) -> tuple:
        """Generate next step using streaming"""
        
        try:
            with self.client.beta.chat.completions.stream(
                model=self.config.get('openai_model', 'gpt-4o-mini'),
                messages=messages,
                response_format=NextStep,
                max_tokens=self.config.get('max_tokens', 8000),
                temperature=self.config.get('temperature', 0.4)
            ) as stream:
                
                final_response, raw_content, metrics = enhanced_streaming_display(
                    stream, "Planning Next Step", self.console
                )
                
                # Update field durations for current step
                if 'field_durations' in metrics:
                    self.step_tracker.update_field_durations(metrics['field_durations'])
                
                if final_response and final_response.choices:
                    content = final_response.choices[0].message.content
                    if content:
                        try:
                            json_data = json.loads(content)
                            parsed = NextStep(**json_data)
                            return parsed, raw_content, metrics
                        except (json.JSONDecodeError, Exception) as e:
                            self.console.print(f"❌ [red]JSON parsing error: {e}[/red]")
                            return None, raw_content, metrics
                
                return None, raw_content, metrics
                
        except Exception as e:
            self.console.print(f"❌ [bold red]NextStep streaming error: {e}[/bold red]")
            raise
    
    def execute_command(self, cmd: BaseModel) -> Any:
        """Execute SGR commands - simplified for integration"""
        
        if isinstance(cmd, Clarification):
            self.context["clarification_used"] = True
            
            questions_text = "\n".join([f"  {i}. {q}" for i, q in enumerate(cmd.questions, 1)])
            
            clarification_panel = Panel(
                f"[yellow]{questions_text}[/yellow]",
                title="❓ Please Answer These Questions",
                border_style="yellow",
                expand=False
            )
            self.console.print(clarification_panel)
            
            return {
                "tool": "clarification",
                "questions": cmd.questions,
                "status": "waiting_for_user"
            }
        
        elif isinstance(cmd, GeneratePlan):
            plan = {
                "research_goal": cmd.research_goal,
                "planned_steps": cmd.planned_steps,
                "search_strategies": cmd.search_strategies,
                "created_at": datetime.now().isoformat()
            }
            
            self.context["plan"] = plan
            
            plan_table = Table(show_header=False, box=None, padding=(0, 1))
            plan_table.add_column("", style="cyan", width=8)
            plan_table.add_column("", style="white")
            
            plan_table.add_row("🎯 Goal:", cmd.research_goal[:50] + "..." if len(cmd.research_goal) > 50 else cmd.research_goal)
            plan_table.add_row("📝 Steps:", f"{len(cmd.planned_steps)} planned steps")
            
            plan_panel = Panel(
                plan_table,
                title="📋 Research Plan Created",
                border_style="cyan",
                expand=False
            )
            self.console.print(plan_panel)
            
            return plan
        
        elif isinstance(cmd, WebSearch):
            self.console.print(f"🔍 [bold cyan]Search query:[/bold cyan] [white]'{cmd.query}'[/white]")
            
            # For integration purposes, return search request
            # The actual search will be handled by Open Deep Research's search system
            search_result = {
                "query": cmd.query,
                "max_results": cmd.max_results,
                "timestamp": datetime.now().isoformat(),
                "status": "search_requested"
            }
            
            self.context["searches"].append(search_result)
            
            search_table = Table(show_header=False, box=None, padding=(0, 1))
            search_table.add_column("", style="cyan", width=10)
            search_table.add_column("", style="white")
            
            search_table.add_row("🔍 Query:", cmd.query[:40] + "..." if len(cmd.query) > 40 else cmd.query)
            search_table.add_row("📎 Results:", f"Requested {cmd.max_results}")
            
            search_panel = Panel(
                search_table,
                title="🔍 Search Requested",
                border_style="blue",
                expand=False
            )
            self.console.print(search_panel)
            
            return search_result
        
        elif isinstance(cmd, CreateReport):
            self.console.print(f"📝 [bold cyan]Creating Report...[/bold cyan]")
            
            report = {
                "title": cmd.title,
                "content": cmd.content,
                "confidence": cmd.confidence,
                "word_count": len(cmd.content.split()),
                "timestamp": datetime.now().isoformat()
            }
            
            report_table = Table(show_header=False, box=None, padding=(0, 1))
            report_table.add_column("", style="green", width=10)
            report_table.add_column("", style="white")
            
            report_table.add_row("📄 Title:", cmd.title[:45] + "..." if len(cmd.title) > 45 else cmd.title)
            report_table.add_row("📊 Content:", f"{report['word_count']} words")
            report_table.add_row("📈 Quality:", f"{cmd.confidence} confidence")
            
            report_panel = Panel(
                report_table,
                title="📝 Report Created",
                border_style="green", 
                expand=False
            )
            self.console.print(report_panel)
            
            return report
        
        else:
            return f"Unknown command: {type(cmd)}"
    
    def start_research_session(self, task: str):
        """Start a new research session"""
        self.console.print(Panel(task, title="🔍 Research Task", title_align="left"))
        
        # Start monitoring
        self.monitor.start_monitoring()
        self.monitor.update_context({
            "task": task,
            "plan": self.context.get("plan"),
            "searches": self.context.get("searches", []),
            "sources": self.context.get("sources", {})
        })
        
        self.console.print(f"\n[bold green]🚀 SGR RESEARCH STARTED (Streaming Mode)[/bold green]")
        
    def get_conversation_log(self, task: str) -> List[Dict[str, str]]:
        """Get conversation log for LLM"""
        system_prompt = self.get_system_prompt(task)
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task}
        ]
    
    def add_search_results_to_context(self, search_results: Dict[str, Any]):
        """Add search results from Open Deep Research to SGR context"""
        if "searches" in self.context:
            # Update the last search with results
            if self.context["searches"]:
                self.context["searches"][-1].update(search_results)
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get summary of current research context"""
        return {
            "plan": self.context.get("plan"),
            "searches_completed": len(self.context.get("searches", [])),
            "sources_count": len(self.context.get("sources", {})),
            "clarification_used": self.context.get("clarification_used", False),
            "session_summary": self.step_tracker.get_session_summary()
        }

# =============================================================================
# MAIN INTERFACE
# =============================================================================

def main():
    """Main application interface"""
    console = Console()
    console.print("[bold]🧠 SGR Research Agent - Streaming Mode[/bold]")
    console.print("Schema-Guided Reasoning with real-time streaming progress")
    console.print()
    console.print("New features:")
    console.print("  🔄 Real-time streaming progress")
    console.print("  📊 Performance metrics")
    console.print("  📡 JSON generation visualization")
    console.print("  ⚡ Faster feedback")
    console.print()
    console.print("[dim]💡 Tip: During schema generation, you can scroll up to see the live JSON creation process[/dim]")
    console.print()
    
    # Initialize agent
    try:
        agent = StreamingSGRAgent(CONFIG)
    except Exception as e:
        console.print(f"❌ Failed to initialize agent: {e}")
        return
    
    awaiting_clarification = False
    original_task = ""
    
    while True:
        try:
            console.print("=" * 60)
            if awaiting_clarification:
                response = input("💬 Your clarification response (or 'quit'): ").strip()
                awaiting_clarification = False
                
                if response.lower() in ['quit', 'exit']:
                    break
                
                task = f"Original request: '{original_task}'\nClarification: {response}\n\nProceed with research based on clarification."
                agent.context["clarification_used"] = False
            else:
                task = input("🔍 Enter research task (or 'quit'): ").strip()
            
            if task.lower() in ['quit', 'exit']:
                console.print("👋 Goodbye!")
                break
            
            if not task:
                console.print("❌ Empty task. Try again.")
                continue
            
            # Reset context for new task
            if not awaiting_clarification:
                agent.context = {
                    "plan": None,
                    "searches": [],
                    "sources": {},
                    "citation_counter": 0,
                    "clarification_used": False
                }
                original_task = task
            
            result = agent.execute_research_task(task)
            
            if result == "CLARIFICATION_NEEDED":
                awaiting_clarification = True
                continue
            
            # Show statistics using step tracker
            summary = agent.step_tracker.get_step_summary()
            clean_history = agent.step_tracker.get_clean_history()
            
            # Count web searches properly (look for steps containing 'web_search')
            web_search_count = sum(1 for step_name in summary['step_counts'].keys() if 'web_search' in step_name)
            console.print(f"\n📊 Session stats: 🔍 {web_search_count} searches, 📎 {len(agent.context.get('sources', {}))} sources")
            console.print(f"⏱️ Total time: {summary['total_time']:.1f}s, 📋 Steps: {summary['total_steps']}")
            console.print(f"📁 Reports saved to: ./{CONFIG['reports_directory']}/")
            
            # Показываем очищенную историю
            if clean_history:
                console.print(f"\n📚 [bold]Clean execution history:[/bold]")
                for i, step in enumerate(clean_history, 1):
                    duration_str = f"{step['duration']:.1f}s"
                    console.print(f"   {i}. [cyan]{step['name']}[/cyan] ({duration_str})")
            
        except KeyboardInterrupt:
            console.print("\n👋 Interrupted by user.")
            break
        except Exception as e:
            console.print(f"❌ Error: {e}")
            continue

if __name__ == "__main__":
    # Check required parameters
    if not CONFIG['openai_api_key']:
        print("ERROR: OPENAI_API_KEY not set in config.yaml or environment")
        exit(1)
    
    if not CONFIG['tavily_api_key']:
        print("ERROR: TAVILY_API_KEY not set in config.yaml or environment")
        exit(1)
    
    main()
