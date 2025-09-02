#!/usr/bin/env python3
"""
SGR Live Monitor - Real-time monitoring and visualization
Simplified version for Open Deep Research integration
"""

import time
from typing import Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.layout import Layout

class SGRStepTracker:
    """Track SGR reasoning steps and timing"""
    
    def __init__(self):
        self.steps = []
        self.current_step = None
        self.step_timings = {}
        
    def start_step(self, step_name: str, description: str = ""):
        """Start tracking a new step"""
        self.current_step = {
            "name": step_name,
            "description": description,
            "start_time": time.time(),
            "status": "running"
        }
        
    def complete_step(self, result: str = ""):
        """Complete the current step"""
        if self.current_step:
            self.current_step["end_time"] = time.time()
            self.current_step["duration"] = self.current_step["end_time"] - self.current_step["start_time"]
            self.current_step["result"] = result
            self.current_step["status"] = "completed"
            self.steps.append(self.current_step)
            self.current_step = None
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all steps"""
        total_time = sum(step.get("duration", 0) for step in self.steps)
        return {
            "total_steps": len(self.steps),
            "total_time": total_time,
            "completed_steps": len([s for s in self.steps if s["status"] == "completed"]),
            "current_step": self.current_step["name"] if self.current_step else None
        }
    
    def update_field_durations(self, field_durations: Dict[str, float]):
        """Update field completion durations"""
        self.step_timings.update(field_durations)

class SGRLiveMonitor:
    """Live monitoring system for SGR processes"""
    
    def __init__(self, console: Console, step_tracker: Optional[SGRStepTracker] = None):
        self.console = console
        self.step_tracker = step_tracker or SGRStepTracker()
        self.is_monitoring = False
        self.context = {}
        self.start_time = None
        
    def start_monitoring(self):
        """Start the monitoring session"""
        self.is_monitoring = True
        self.start_time = time.time()
        self.console.print("[bold green]🔍 SGR Monitoring Started[/bold green]")
        
    def stop_monitoring(self):
        """Stop the monitoring session"""
        self.is_monitoring = False
        if self.start_time:
            total_time = time.time() - self.start_time
            self.console.print(f"[bold green]✅ SGR Monitoring Completed ({total_time:.2f}s)[/bold green]")
    
    def update_context(self, context: Dict[str, Any]):
        """Update monitoring context"""
        self.context.update(context)
    
    def create_status_panel(self) -> Panel:
        """Create status monitoring panel"""
        table = Table(show_header=False, box=None)
        table.add_column("", style="cyan", width=12)
        table.add_column("", style="white")
        
        # Basic status
        if self.start_time:
            elapsed = time.time() - self.start_time
            table.add_row("⏱️ Runtime:", f"{elapsed:.1f}s")
        
        # Current task
        if "task" in self.context:
            task = self.context["task"][:50] + "..." if len(self.context["task"]) > 50 else self.context["task"]
            table.add_row("🎯 Task:", task)
        
        # Research progress
        if "searches" in self.context:
            search_count = len(self.context["searches"])
            table.add_row("🔍 Searches:", str(search_count))
        
        if "sources" in self.context:
            source_count = len(self.context["sources"])
            table.add_row("📚 Sources:", str(source_count))
        
        # Current step
        step_summary = self.step_tracker.get_summary()
        if step_summary["current_step"]:
            table.add_row("📋 Step:", step_summary["current_step"])
        
        return Panel(
            table,
            title="🔍 SGR Monitor",
            border_style="cyan"
        )
    
    def show_progress_summary(self):
        """Show a summary of progress"""
        if not self.is_monitoring:
            return
            
        summary_panel = self.create_status_panel()
        self.console.print(summary_panel)
    
    def log_event(self, event_type: str, message: str):
        """Log an event with timestamp"""
        if self.is_monitoring:
            timestamp = time.strftime("%H:%M:%S")
            self.console.print(f"[dim]{timestamp}[/dim] [bold]{event_type}:[/bold] {message}")
    
    def display_live_progress(self, duration: float = 5.0):
        """Display live progress for a specified duration"""
        if not self.is_monitoring:
            return
        
        with Live(self.create_status_panel(), console=self.console, refresh_per_second=2) as live:
            end_time = time.time() + duration
            while time.time() < end_time:
                live.update(self.create_status_panel())
                time.sleep(0.5)

# Пример использования
def demo_sgr_visualization():
    """Демонстрация SGR визуализации"""
    console = Console()
    monitor = SGRLiveMonitor(console)
    
    try:
        # Запускаем мониторинг
        monitor.start_monitoring()
        
        # Обновляем контекст
        monitor.update_context({
            "task": "Исследование цен на BMW X6 2025 года в России",
            "plan": {
                "research_goal": "Найти актуальные цены на BMW X6",
                "planned_steps": ["Поиск официальных данных", "Анализ дилеров", "Сравнение цен"]
            },
            "searches": [],
            "sources": {}
        })
        
        # Симулируем этапы SGR
        steps = [
            ("generate_plan", "Создание плана исследования"),
            ("web_search", "Поиск информации о ценах"),
            ("web_search", "Дополнительный поиск по дилерам"),
            ("create_report", "Составление итогового отчета"),
            ("report_completion", "Завершение задачи")
        ]
        
        for i, (step_name, details) in enumerate(steps):
            monitor.step_tracker.start_step(step_name, details)
            time.sleep(2)  # Симуляция работы
            
            # Симулируем результат
            result = f"Результат этапа {i+1}: {step_name}"
            monitor.step_tracker.complete_step(result)
            
            # Обновляем контекст
            if step_name == "web_search":
                current_searches = monitor.context.get("searches", [])
                current_searches.append({"query": f"BMW X6 prices search {len(current_searches)+1}"})
                monitor.update_context({"searches": current_searches})
            
            # Показываем обновленный статус
            monitor.show_progress_summary()
            time.sleep(1)
        
        # Показываем финальное состояние
        time.sleep(1)
        
    finally:
        monitor.stop_monitoring()

if __name__ == "__main__":
    demo_sgr_visualization()
