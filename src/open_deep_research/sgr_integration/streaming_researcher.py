"""Streaming Researcher - обертки для researcher с SGR streaming поддержкой"""

import asyncio
from typing import Dict, Any, Optional
from langchain_core.runnables import RunnableConfig

from open_deep_research.deep_researcher import supervisor, supervisor_tools
from open_deep_research.state import SupervisorState, AgentState

# Попытка импорта SGR компонентов
try:
    from ..sgr_streaming.sgr_visualizer import SGRLiveMonitor
    from ..sgr_streaming.sgr_step_tracker import SGRStepTracker
    from rich.console import Console
    SGR_AVAILABLE = True
except ImportError:
    print("⚠️  SGR streaming components not available for streaming researcher")
    SGR_AVAILABLE = False
    Console = None


class StreamingResearcher:
    """Wrapper для researcher с SGR streaming отображением"""
    
    def __init__(self):
        self.monitor = None
        self.tracker = None
        
        if SGR_AVAILABLE:
            self.console = Console()
            self.monitor = SGRLiveMonitor(self.console)
            self.tracker = SGRStepTracker()
    
    async def streaming_supervisor_wrapper(self, state: AgentState, config: RunnableConfig):
        """Обертка для supervisor с streaming мониторингом"""
        
        if self.monitor and SGR_AVAILABLE:
            return await self._supervisor_with_monitoring(state, config)
        else:
            return await self._supervisor_simple(state, config)
    
    async def _supervisor_with_monitoring(self, state: AgentState, config: RunnableConfig):
        """Supervisor с полным SGR мониторингом"""
        
        try:
            with self.monitor.live_display():
                self.monitor.update_status("👨‍💼 Starting research supervision...")
                
                # Трекируем начало этапа
                if self.tracker:
                    self.tracker.start_step("supervisor_planning")
                
                # Создаем supervisor state из agent state
                supervisor_state = self._convert_to_supervisor_state(state)
                
                # Выполняем supervisor
                self.monitor.update_status("🧠 Analyzing research requirements...")
                result = await supervisor(supervisor_state, config)
                
                # Выполняем supervisor tools если есть tool calls
                if hasattr(result, 'update') and 'supervisor_messages' in result.update:
                    self.monitor.update_status("🔧 Executing supervisor tools...")
                    
                    # Обновляем состояние
                    for key, value in result.update.items():
                        supervisor_state[key] = value
                    
                    # Выполняем tools
                    tools_result = await supervisor_tools(supervisor_state, config)
                    
                    self.monitor.update_status("✅ Research supervision completed")
                    
                    if self.tracker:
                        self.tracker.complete_step("supervisor_planning")
                    
                    return tools_result
                
                return result
                
        except Exception as e:
            print(f"Error in streaming supervisor: {e}")
            # Fallback к простому режиму
            return await self._supervisor_simple(state, config)
    
    async def _supervisor_simple(self, state: AgentState, config: RunnableConfig):
        """Простой supervisor без streaming"""
        
        print("👨‍💼 Research supervision (simple mode)...")
        
        try:
            # Преобразуем state для supervisor
            supervisor_state = self._convert_to_supervisor_state(state)
            
            # Выполняем supervisor
            result = await supervisor(supervisor_state, config)
            
            print("✅ Research supervision completed")
            return result
            
        except Exception as e:
            print(f"Error in supervisor: {e}")
            # Возвращаем minimal успешный результат
            return {"supervisor_messages": [], "research_iterations": 1}
    
    def _convert_to_supervisor_state(self, agent_state: AgentState) -> SupervisorState:
        """Преобразует AgentState в SupervisorState"""
        
        supervisor_state = {
            "supervisor_messages": agent_state.get("supervisor_messages", []),
            "research_brief": agent_state.get("research_brief", ""),
            "notes": agent_state.get("notes", []),
            "research_iterations": 0,
            "raw_notes": agent_state.get("raw_notes", [])
        }
        
        return supervisor_state


class StreamingProgressTracker:
    """Трекер прогресса для streaming интерфейса"""
    
    def __init__(self):
        self.current_step = 0
        self.total_steps = 5  # Примерное количество шагов
        self.step_descriptions = [
            "🔍 Analyzing request",
            "📋 Planning research", 
            "🌐 Searching information",
            "📊 Processing results",
            "📝 Generating report"
        ]
        self.start_time = None
        
    def start_tracking(self):
        """Начать отслеживание прогресса"""
        import time
        self.start_time = time.time()
        self.current_step = 0
        
    def next_step(self, description: str = None):
        """Перейти к следующему шагу"""
        self.current_step += 1
        
        if description:
            # Обновляем описание текущего шага
            if self.current_step <= len(self.step_descriptions):
                self.step_descriptions[self.current_step - 1] = description
        
        self._update_display()
    
    def _update_display(self):
        """Обновить отображение прогресса"""
        if self.current_step <= len(self.step_descriptions):
            current_desc = self.step_descriptions[self.current_step - 1]
            progress = self.current_step / self.total_steps
            
            print(f"[{progress:.1%}] {current_desc}")
    
    def complete(self):
        """Завершить отслеживание"""
        import time
        if self.start_time:
            elapsed = time.time() - self.start_time
            print(f"✅ Research completed in {elapsed:.1f} seconds")


class SGRStreamingWrapper:
    """Общая обертка для добавления SGR streaming к любым функциям"""
    
    def __init__(self, enable_streaming: bool = True):
        self.enable_streaming = enable_streaming and SGR_AVAILABLE
        self.progress_tracker = StreamingProgressTracker()
    
    def wrap_function(self, func, description: str):
        """Оборачивает функцию в SGR streaming интерфейс"""
        
        async def wrapped(*args, **kwargs):
            if self.enable_streaming:
                self.progress_tracker.next_step(description)
            
            try:
                result = await func(*args, **kwargs)
                
                if self.enable_streaming:
                    print(f"✅ {description} completed")
                
                return result
                
            except Exception as e:
                if self.enable_streaming:
                    print(f"❌ {description} failed: {e}")
                raise e
        
        return wrapped
    
    def create_streaming_pipeline(self, functions_with_descriptions):
        """Создает pipeline из функций с streaming отображением"""
        
        wrapped_functions = []
        
        for func, description in functions_with_descriptions:
            wrapped_func = self.wrap_function(func, description)
            wrapped_functions.append(wrapped_func)
        
        return wrapped_functions


class SimpleStreamingMonitor:
    """Простой монитор без зависимостей от SGR компонентов"""
    
    def __init__(self):
        self.active = False
        self.current_status = "Ready"
    
    def start(self):
        """Начать мониторинг"""
        self.active = True
        print("🚀 Starting research monitoring...")
    
    def update_status(self, status: str):
        """Обновить статус"""
        self.current_status = status
        if self.active:
            print(f"📊 {status}")
    
    def stop(self):
        """Остановить мониторинг"""
        self.active = False
        print("🏁 Research monitoring stopped")
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()