#!/usr/bin/env python3
"""
Enhanced Streaming Visualization for SGR JSON Schemas
Simplified version for Open Deep Research integration
"""

import json
import time
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

@dataclass
class StreamingMetrics:
    """Streaming metrics for detailed analysis"""
    start_time: float
    total_chars: int = 0
    total_chunks: int = 0
    field_durations: Dict[str, float] = None
    
    def __post_init__(self):
        if self.field_durations is None:
            self.field_durations = {}
    
    @property
    def elapsed_time(self) -> float:
        return time.time() - self.start_time
    
    @property
    def chars_per_second(self) -> float:
        elapsed = self.elapsed_time
        return self.total_chars / elapsed if elapsed > 0 else 0

class EnhancedSchemaParser:
    """Enhanced schema parser with streaming visualization"""
    
    def __init__(self, console: Console):
        self.console = console
        self.current_json = ""
        self.parsed_fields = {}
        self.schema_type = None
        self.metrics = StreamingMetrics(start_time=time.time())
        
        # Schema field definitions
        self.schema_fields = {
            "clarification": ["tool", "reasoning", "unclear_terms", "assumptions", "questions"],
            "generate_plan": ["tool", "reasoning", "research_goal", "planned_steps", "search_strategies"],
            "web_search": ["tool", "reasoning", "query", "max_results", "scrape_content"],
            "create_report": ["tool", "reasoning", "title", "content", "confidence"],
            "next_step": ["reasoning_steps", "current_situation", "plan_status", "searches_done", "enough_data", "remaining_steps", "task_completed", "function"]
        }
        
        # Field emojis
        self.field_emojis = {
            "tool": "🔧",
            "reasoning": "🧠",
            "reasoning_steps": "🧩",
            "current_situation": "📊",
            "query": "🔍",
            "research_goal": "🎯",
            "title": "📋",
            "content": "📝",
            "questions": "❓",
            "unclear_terms": "🤔",
            "planned_steps": "📋",
            "remaining_steps": "📅",
            "confidence": "📈",
            "searches_done": "🔎",
            "enough_data": "✅"
        }
    
    def detect_schema_type(self, json_content: str) -> str:
        """Detect schema type from JSON content"""
        if '"tool":"clarification"' in json_content:
            return "clarification"
        elif '"tool":"generate_plan"' in json_content:
            return "generate_plan"
        elif '"tool":"web_search"' in json_content:
            return "web_search"
        elif '"tool":"create_report"' in json_content:
            return "create_report"
        elif '"reasoning_steps"' in json_content:
            return "next_step"
        else:
            return "unknown"
    
    def extract_field(self, json_content: str, field_name: str) -> Optional[str]:
        """Extract field value from partial JSON"""
        patterns = [
            rf'"{field_name}"\s*:\s*"([^"]*)"',  # String
            rf'"{field_name}"\s*:\s*(\d+)',      # Number
            rf'"{field_name}"\s*:\s*(true|false)', # Boolean
        ]
        
        for pattern in patterns:
            match = re.search(pattern, json_content)
            if match:
                return match.group(1)
        return None
    
    def extract_array_items(self, json_content: str, field_name: str) -> List[str]:
        """Extract array elements from partial JSON"""
        pattern = rf'"{field_name}"\s*:\s*\[(.*?)\]'
        match = re.search(pattern, json_content, re.DOTALL)
        
        if match:
            array_content = match.group(1)
            items = re.findall(r'"([^"]*)"', array_content)
            return items
        return []
    
    def create_display_table(self, schema_type: str, parsed_fields: Dict[str, Any]) -> Table:
        """Create display table with parsed information"""
        
        if not parsed_fields:
            table = Table(title="📊 Parsing JSON...", show_header=False)
            table.add_column("Status", style="yellow")
            table.add_row("⏳ Waiting for more data...")
            return table
        
        # Compact table for all schemas
        table = Table(title="🤖 AI Response", show_header=True, header_style="bold cyan")
        table.add_column("Field", style="cyan", width=12)
        table.add_column("Value", style="white", width=45)
        
        # Reasoning steps
        if "reasoning_steps" in parsed_fields:
            steps = parsed_fields["reasoning_steps"]
            if isinstance(steps, list) and steps:
                table.add_row("🧠 Steps", f"{len(steps)} reasoning steps")
        
        # Current situation
        if "current_situation" in parsed_fields and parsed_fields["current_situation"]:
            situation = parsed_fields["current_situation"]
            table.add_row("📊 Situation", situation[:60] + "..." if len(situation) > 60 else situation)
        
        # Progress tracking
        progress_items = []
        if "searches_done" in parsed_fields:
            progress_items.append(f"{parsed_fields['searches_done']} searches")
        
        if "enough_data" in parsed_fields:
            status = "sufficient" if parsed_fields["enough_data"] else "need more"
            progress_items.append(status)
            
        if progress_items:
            table.add_row("📈 Progress", " • ".join(progress_items))
        
        # Function/tool decision
        if "function" in parsed_fields:
            func = parsed_fields["function"]
            if "tool" in func:
                tool_name = func['tool'].replace('_', ' ').title()
                table.add_row("🔧 Action", f"[bold green]{tool_name}[/bold green]")
            
            if "reasoning" in func:
                reasoning = func["reasoning"][:70] + "..." if len(func["reasoning"]) > 70 else func["reasoning"]
                table.add_row("💭 Why", reasoning)
            
            # Tool-specific fields
            if "query" in func:
                table.add_row("🔎 Query", func["query"][:50] + "..." if len(func["query"]) > 50 else func["query"])
                
            if "research_goal" in func:
                table.add_row("🎯 Goal", func["research_goal"][:50] + "..." if len(func["research_goal"]) > 50 else func["research_goal"])
            
            if "questions" in func and isinstance(func["questions"], list):
                table.add_row("❔ Questions", f"{len(func['questions'])} questions")
        
        return table
    
    def update_from_json(self, json_content: str) -> Tuple[Table, List[str]]:
        """Update parsing and return table + questions for display"""
        self.current_json = json_content
        
        # Detect schema type
        new_schema_type = self.detect_schema_type(json_content)
        if new_schema_type != "unknown":
            self.schema_type = new_schema_type
        
        # Try to parse JSON
        try:
            if json_content.strip().endswith('}'):
                parsed = json.loads(json_content)
                self.parsed_fields = parsed
            else:
                # Partial parsing
                self.parsed_fields = {}
                
                if self.schema_type == "next_step":
                    fields_to_extract = [
                        "current_situation", "plan_status", "searches_done", 
                        "enough_data", "task_completed"
                    ]
                    
                    for field in fields_to_extract:
                        value = self.extract_field(json_content, field)
                        if value is not None:
                            if field in ["searches_done"]:
                                try:
                                    self.parsed_fields[field] = int(value)
                                except:
                                    self.parsed_fields[field] = value
                            elif field in ["enough_data", "task_completed"]:
                                self.parsed_fields[field] = value.lower() == "true"
                            else:
                                self.parsed_fields[field] = value
                    
                    # Extract arrays
                    reasoning_steps = self.extract_array_items(json_content, "reasoning_steps")
                    if reasoning_steps:
                        self.parsed_fields["reasoning_steps"] = reasoning_steps
                    
                    remaining_steps = self.extract_array_items(json_content, "remaining_steps")
                    if remaining_steps:
                        self.parsed_fields["remaining_steps"] = remaining_steps
                    
                    # Extract function object
                    if '"function"' in json_content:
                        function_match = re.search(r'"function"\s*:\s*\{(.*?)\}', json_content, re.DOTALL)
                        if function_match:
                            function_content = "{" + function_match.group(1) + "}"
                            try:
                                function_obj = json.loads(function_content)
                                self.parsed_fields["function"] = function_obj
                            except:
                                tool_match = re.search(r'"tool"\s*:\s*"([^"]*)"', function_content)
                                if tool_match:
                                    self.parsed_fields["function"] = {"tool": tool_match.group(1)}
        
        except json.JSONDecodeError:
            pass
        except Exception:
            pass
        
        # Create table
        table = self.create_display_table(self.schema_type or "unknown", self.parsed_fields)
        
        # Extract questions for separate display
        questions = []
        if ("function" in self.parsed_fields and 
            "questions" in self.parsed_fields["function"] and 
            isinstance(self.parsed_fields["function"]["questions"], list)):
            questions = self.parsed_fields["function"]["questions"]
        
        return table, questions

def enhanced_streaming_display(stream, operation_name: str, console: Console):
    """
    Enhanced streaming visualization with Rich Live updates
    
    Args:
        stream: OpenAI streaming object
        operation_name: Name of the operation for display
        console: Rich console for output
    
    Returns:
        tuple: (final_response, accumulated_content, metrics)
    """
    
    parser = EnhancedSchemaParser(console)
    
    accumulated_content = ""
    chunk_count = 0
    start_time = time.time()
    last_update_time = start_time
    
    # Create layout for live updating
    layout = Layout()
    layout.split_column(
        Layout(Panel.fit("🚀 Starting...", title=f"📡 {operation_name}", border_style="cyan"), name="main"),
        Layout("", size=3, name="metrics")
    )
    
    with Live(layout, console=console, refresh_per_second=4) as live:
        try:
            # Process streaming chunks
            for chunk in stream:
                chunk_count += 1
                current_time = time.time()
                
                # Extract content from chunk
                content_delta = None
                
                if hasattr(chunk, 'type') and chunk.type == 'content.delta':
                    content_delta = chunk.delta
                elif hasattr(chunk, 'choices') and chunk.choices:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        content_delta = delta.content
                
                if content_delta:
                    accumulated_content += content_delta
                    
                    # Update every 0.2 seconds or on significant change
                    if (current_time - last_update_time > 0.2) or len(content_delta) > 10:
                        
                        # Create updated table and get questions
                        table, questions = parser.update_from_json(accumulated_content)
                        
                        # Create content with table and questions
                        content_parts = [table]
                        
                        if questions:
                            questions_table = Table(title="❔ Questions", show_header=False)
                            questions_table.add_column("Q", style="yellow", width=60)
                            for i, q in enumerate(questions, 1):
                                questions_table.add_row(f"{i}. {q}")
                            content_parts.append(questions_table)
                        
                        # Combine content
                        combined_content = Group(*content_parts)
                        
                        # Update main content
                        layout["main"].update(
                            Panel.fit(
                                combined_content, 
                                title=f"🤖 {operation_name} - Thinking...", 
                                border_style="cyan"
                            )
                        )
                        
                        # Update metrics
                        elapsed = current_time - start_time
                        speed = len(accumulated_content) / elapsed if elapsed > 0 else 0
                        metrics_text = Text()
                        metrics_text.append(f"⏱️ {elapsed:.1f}s", style="dim cyan")
                        metrics_text.append(" | ", style="dim")
                        metrics_text.append(f"📦 {chunk_count} chunks", style="dim green")
                        metrics_text.append(" | ", style="dim")
                        metrics_text.append(f"📝 {len(accumulated_content)} chars", style="dim blue")
                        metrics_text.append(" | ", style="dim")
                        metrics_text.append(f"⚡ {speed:.0f} ch/s", style="dim yellow")
                        
                        layout["metrics"].update(Panel.fit(metrics_text, border_style="dim"))
                        
                        last_update_time = current_time
            
            # Get final response
            final_response = stream.get_final_completion()
            total_time = time.time() - start_time
            
            # Final update
            final_table, final_questions = parser.update_from_json(accumulated_content)
            
            # Create final content with questions
            final_parts = [final_table]
            
            if final_questions:
                questions_table = Table(title="❔ Questions", show_header=False)
                questions_table.add_column("Q", style="yellow", width=60)
                for i, q in enumerate(final_questions, 1):
                    questions_table.add_row(f"{i}. {q}")
                final_parts.append(questions_table)
            
            final_combined = Group(*final_parts)
            
            layout["main"].update(
                Panel.fit(
                    final_combined, 
                    title=f"✅ {operation_name} Completed!", 
                    border_style="green"
                )
            )
            
            # Final metrics
            final_speed = len(accumulated_content) / total_time if total_time > 0 else 0
            final_metrics = Text()
            final_metrics.append(f"⏱️ Total: {total_time:.2f}s", style="bold green")
            final_metrics.append(" | ", style="dim")
            final_metrics.append(f"📦 {chunk_count} chunks", style="bold blue")
            final_metrics.append(" | ", style="dim")
            final_metrics.append(f"📝 {len(accumulated_content)} chars", style="bold cyan")
            final_metrics.append(" | ", style="dim")
            final_metrics.append(f"📊 {final_speed:.0f} chars/sec", style="bold yellow")
            
            layout["metrics"].update(Panel.fit(final_metrics, border_style="green"))
            
            # Show final result for 1 second
            time.sleep(1.0)
            
        except Exception as e:
            # Show error in live mode
            error_panel = Panel.fit(
                f"❌ Streaming error: {e}", 
                title="Error", 
                border_style="red"
            )
            layout["main"].update(error_panel)
            time.sleep(2.0)
            raise
    
    # After Live exit - show compact summary
    console.print(f"\n🎯 [bold green]{operation_name} completed successfully![/bold green]")
    
    metrics = {
        "total_time": total_time,
        "chunk_count": chunk_count,
        "content_size": len(accumulated_content),
        "chars_per_second": len(accumulated_content) / total_time if total_time > 0 else 0,
        "field_durations": parser.metrics.field_durations
    }
    
    return final_response, accumulated_content, metrics

class SpecializedDisplays:
    """Specialized display handlers for different schema types"""
    
    @staticmethod
    def display_clarification(data: Dict[str, Any], console: Console):
        """Display clarification request"""
        console.print(Panel(
            f"[yellow]Need clarification on: {', '.join(data.get('unclear_terms', []))}[/yellow]",
            title="❓ Clarification Needed",
            border_style="yellow"
        ))
    
    @staticmethod
    def display_plan(data: Dict[str, Any], console: Console):
        """Display research plan"""
        console.print(Panel(
            f"[cyan]Goal: {data.get('research_goal', 'N/A')}[/cyan]",
            title="📋 Research Plan",
            border_style="cyan"
        ))
    
    @staticmethod
    def display_search(data: Dict[str, Any], console: Console):
        """Display search information"""
        console.print(Panel(
            f"[blue]Searching: {data.get('query', 'N/A')}[/blue]",
            title="🔍 Web Search",
            border_style="blue"
        ))
    
    @staticmethod
    def display_report(data: Dict[str, Any], console: Console):
        """Display report creation"""
        console.print(Panel(
            f"[green]Report: {data.get('title', 'N/A')}[/green]",
            title="📝 Creating Report",
            border_style="green"
        ))