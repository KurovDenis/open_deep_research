#!/usr/bin/env python3
"""
SGR Step Tracker - Track and visualize SGR reasoning steps
Simplified version for Open Deep Research integration
"""

import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

@dataclass
class SGRStep:
    """Represents a single SGR reasoning step"""
    name: str
    description: str
    start_time: float
    end_time: Optional[float] = None
    status: str = "running"  # running, completed, failed
    result: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration(self) -> float:
        """Get step duration"""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time
    
    @property
    def is_completed(self) -> bool:
        """Check if step is completed"""
        return self.status == "completed"

class SGRStepTracker:
    """Track SGR reasoning steps with detailed metrics"""
    
    def __init__(self):
        self.steps: List[SGRStep] = []
        self.current_step: Optional[SGRStep] = None
        self.session_start: float = time.time()
        self.field_durations: Dict[str, float] = {}
        
        # Step type emojis
        self.step_emojis = {
            "clarification": "❓",
            "generate_plan": "📋",
            "web_search": "🔍",
            "adapt_plan": "🔄",
            "create_report": "📝",
            "next_step": "🧠",
            "analysis": "📊",
            "completion": "✅"
        }
    
    def start_step(self, step_name: str, description: str = "", metadata: Dict[str, Any] = None) -> SGRStep:
        """Start tracking a new step"""
        # Complete previous step if not completed
        if self.current_step and not self.current_step.is_completed:
            self.complete_step("Auto-completed")
        
        step = SGRStep(
            name=step_name,
            description=description,
            start_time=time.time(),
            metadata=metadata or {}
        )
        
        self.current_step = step
        return step
    
    def complete_step(self, result: str = "", status: str = "completed") -> Optional[SGRStep]:
        """Complete the current step"""
        if not self.current_step:
            return None
        
        self.current_step.end_time = time.time()
        self.current_step.result = result
        self.current_step.status = status
        
        # Archive the step
        self.steps.append(self.current_step)
        completed_step = self.current_step
        self.current_step = None
        
        return completed_step
    
    def fail_step(self, error: str) -> Optional[SGRStep]:
        """Mark current step as failed"""
        return self.complete_step(error, "failed")
    
    def update_field_durations(self, field_durations: Dict[str, float]):
        """Update field completion durations from streaming"""
        self.field_durations.update(field_durations)
    
    def get_step_emoji(self, step_name: str) -> str:
        """Get emoji for step type"""
        for key, emoji in self.step_emojis.items():
            if key in step_name.lower():
                return emoji
        return "📋"
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get complete session summary"""
        total_time = time.time() - self.session_start
        completed_steps = [s for s in self.steps if s.is_completed]
        failed_steps = [s for s in self.steps if s.status == "failed"]
        
        return {
            "total_time": total_time,
            "total_steps": len(self.steps),
            "completed_steps": len(completed_steps),
            "failed_steps": len(failed_steps),
            "current_step": self.current_step.name if self.current_step else None,
            "average_step_duration": sum(s.duration for s in completed_steps) / len(completed_steps) if completed_steps else 0,
            "field_durations": self.field_durations
        }
    
    def create_summary_table(self) -> Table:
        """Create a summary table of all steps"""
        table = Table(title="📊 SGR Step Summary", show_header=True)
        table.add_column("Step", style="cyan", width=15)
        table.add_column("Status", style="white", width=8)
        table.add_column("Duration", style="yellow", width=8)
        table.add_column("Result", style="green", width=30)
        
        for step in self.steps:
            # Status with emoji
            if step.status == "completed":
                status = "✅ Done"
            elif step.status == "failed":
                status = "❌ Failed"
            else:
                status = "🔄 Running"
            
            # Format duration
            duration = f"{step.duration:.2f}s"
            
            # Truncate result
            result = step.result[:30] + "..." if len(step.result) > 30 else step.result
            
            # Add emoji to step name
            step_emoji = self.get_step_emoji(step.name)
            step_display = f"{step_emoji} {step.name}"
            
            table.add_row(step_display, status, duration, result)
        
        # Add current step if running
        if self.current_step:
            step_emoji = self.get_step_emoji(self.current_step.name)
            step_display = f"{step_emoji} {self.current_step.name}"
            duration = f"{self.current_step.duration:.2f}s"
            table.add_row(step_display, "🔄 Running", duration, "In progress...")
        
        return table
    
    def create_progress_panel(self) -> Panel:
        """Create a progress panel for current status"""
        summary = self.get_session_summary()
        
        progress_table = Table(show_header=False, box=None)
        progress_table.add_column("", style="cyan", width=12)
        progress_table.add_column("", style="white")
        
        # Session info
        progress_table.add_row("⏱️ Session:", f"{summary['total_time']:.1f}s")
        progress_table.add_row("📋 Steps:", f"{summary['completed_steps']}/{summary['total_steps']}")
        
        if summary['failed_steps'] > 0:
            progress_table.add_row("❌ Failed:", str(summary['failed_steps']))
        
        if summary['current_step']:
            progress_table.add_row("🔄 Current:", summary['current_step'])
        
        if summary['average_step_duration'] > 0:
            progress_table.add_row("⏱️ Avg Step:", f"{summary['average_step_duration']:.2f}s")
        
        return Panel(
            progress_table,
            title="🔍 SGR Progress",
            border_style="cyan"
        )
    
    def display_summary(self, console: Console):
        """Display complete summary"""
        console.print(self.create_summary_table())
        console.print()
        console.print(self.create_progress_panel())
    
    def display_progress(self, console: Console):
        """Display current progress only"""
        console.print(self.create_progress_panel())
    
    def reset(self):
        """Reset tracker for new session"""
        self.steps.clear()
        self.current_step = None
        self.session_start = time.time()
        self.field_durations.clear()