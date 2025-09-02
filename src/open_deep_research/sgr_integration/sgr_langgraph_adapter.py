"""SGR LangGraph Adapter - мост между SGR streaming и LangGraph workflow"""

import asyncio
import json
from typing import Dict, Any, Optional, Literal, Union
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import Command

from open_deep_research.configuration import Configuration
from open_deep_research.state import AgentState
from open_deep_research.utils import get_today_str

# Импорты SGR компонентов (теперь доступны)
try:
    from ..sgr_streaming.enhanced_streaming import enhanced_streaming_display, EnhancedSchemaParser
    from ..sgr_streaming.sgr_visualizer import SGRLiveMonitor
    from ..sgr_streaming.sgr_streaming import SGRAgent, NextStep
    from rich.console import Console
    SGR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  SGR streaming components not found: {e}")
    SGR_AVAILABLE = False
    Console = None


class SGRStreamingNode:
    """LangGraph узел с SGR streaming поддержкой"""
    
    def __init__(self, config_dict: dict = None):
        self.config = config_dict or {}
        self.streaming_enabled = self.config.get("streaming_enabled", True)
        self.current_step = 0
        self.max_steps = self.config.get("max_reasoning_steps", 4)
        
        # Инициализируем SGR компоненты если доступны
        if SGR_AVAILABLE:
            self.console = Console()
            self.monitor = SGRLiveMonitor(self.console)
            self.parser = None
        else:
            self.console = None
            self.monitor = None
            self.parser = None
    
    async def __call__(self, state: AgentState, config: RunnableConfig) -> Command:
        """Выполняет SGR reasoning step с streaming отображением"""
        
        try:
            # Получаем конфигурацию
            configurable = Configuration.from_runnable_config(config)
            
            # Получаем последнее сообщение пользователя
            messages = state.get("messages", [])
            if not messages:
                return Command(goto="clarify_with_user")
            
            user_message = messages[-1].content if hasattr(messages[-1], 'content') else str(messages[-1])
            
            # Запускаем SGR reasoning с streaming
            if self.streaming_enabled and SGR_AVAILABLE:
                return await self._execute_with_streaming(user_message, state, configurable)
            else:
                return await self._execute_simple(user_message, state, configurable)
        
        except Exception as e:
            print(f"Error in SGR node: {e}")
            # Fallback к стандартному поведению
            return Command(goto="research_supervisor")
    
    async def _execute_with_streaming(self, user_message: str, state: AgentState, config: Configuration) -> Command:
        """Выполнение с SGR streaming отображением"""
        
        decision = await self._analyze_research_need(user_message, config)
        
        # Определяем следующий шаг на основе анализа
        if "clarification" in decision.lower():
            return Command(goto="clarify_with_user")
        elif "research" in decision.lower() or "search" in decision.lower():
            return Command(goto="research_supervisor") 
        elif "report" in decision.lower() or "complete" in decision.lower():
            return Command(goto="final_report_generation")
        else:
            return Command(goto="research_supervisor")
    
    async def _execute_simple(self, user_message: str, state: AgentState, config: Configuration) -> Command:
        """Простое выполнение без streaming"""
        
        print("🧠 SGR reasoning (simple mode)...")
        
        # Простая логика маршрутизации
        if len(user_message) < 10:
            return Command(goto="clarify_with_user")
        elif any(keyword in user_message.lower() for keyword in ["report", "summary", "conclude"]):
            return Command(goto="final_report_generation")
        else:
            return Command(goto="research_supervisor")
    
    async def _analyze_research_need(self, user_message: str, config: Configuration) -> str:
        """Анализ потребности в исследовании через LLM"""
        
        try:
            from langchain.chat_models import init_chat_model
            from open_deep_research.utils import get_api_key_for_model
            
            # Настраиваем модель
            model_config = {
                "model": config.research_model,
                "max_tokens": 200,
                "api_key": get_api_key_for_model(config.research_model, {"configurable": {}}),
                "tags": ["langsmith:nostream"]
            }
            
            model = init_chat_model(
                configurable_fields=("model", "max_tokens", "api_key"),
            ).with_config(model_config)
            
            # Промпт для анализа
            analysis_prompt = f"""
            Analyze this user request and determine the best next action:
            
            User request: "{user_message}"
            Date: {get_today_str()}
            
            Choose ONE of these actions:
            1. "clarification" - if the request is unclear or needs more details
            2. "research" - if we need to search for information
            3. "report" - if we have enough information to generate a report
            
            Respond with just the action name and brief reasoning.
            """
            
            response = await model.ainvoke([HumanMessage(content=analysis_prompt)])
            return response.content
            
        except Exception as e:
            print(f"Error in LLM analysis: {e}")
            return "research"  # Default fallback


class SGRDecisionRouter:
    """Роутер для принятия решений на основе SGR анализа"""
    
    @staticmethod
    def route_sgr_decision(state: AgentState) -> str:
        """Маршрутизация на основе SGR решения"""
        
        # Анализируем сообщения в состоянии
        messages = state.get("messages", [])
        
        if not messages:
            return "clarify"
        
        last_message = messages[-1]
        content = ""
        
        if hasattr(last_message, 'content'):
            content = last_message.content.lower()
        else:
            content = str(last_message).lower()
        
        # Простая логика маршрутизации
        if any(word in content for word in ["unclear", "clarify", "question", "what"]):
            return "clarify"
        elif any(word in content for word in ["search", "research", "find", "investigate"]):
            return "research"
        elif any(word in content for word in ["report", "summary", "complete", "finish"]):
            return "report"
        
        # Проверяем заполненность research_brief
        research_brief = state.get("research_brief", "")
        if not research_brief:
            return "research"
        
        # Проверяем наличие notes
        notes = state.get("notes", [])
        if len(notes) < 2:
            return "research"
        
        return "report"


class SGRStreamingConfig:
    """Конфигурация для SGR streaming интеграции"""
    
    def __init__(self, base_config: dict):
        self.base_config = base_config
        
    def get_streaming_config(self) -> dict:
        """Возвращает конфигурацию для SGR streaming"""
        return {
            "streaming_enabled": self.base_config.get("STREAMING_ENABLED", True),
            "display_type": self.base_config.get("STREAMING_DISPLAY_TYPE", "enhanced"),
            "update_interval": self.base_config.get("STREAMING_UPDATE_INTERVAL", 0.1),
            "animation_speed": self.base_config.get("STREAMING_ANIMATION_SPEED", 1.0),
            "schema_validation": self.base_config.get("SGR_SCHEMA_VALIDATION", True),
            "max_reasoning_steps": self.base_config.get("SGR_MAX_REASONING_STEPS", 4),
            "confidence_threshold": self.base_config.get("SGR_CONFIDENCE_THRESHOLD", 0.7),
            "enable_monitor": self.base_config.get("ENABLE_LIVE_MONITOR", True),
            "enable_tracker": self.base_config.get("ENABLE_STEP_TRACKER", True),
            "enable_progress": self.base_config.get("ENABLE_PROGRESS_BAR", True)
        }