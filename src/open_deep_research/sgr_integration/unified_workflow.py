"""Unified SGR Workflow - объединяет Open Deep Research с SGR Streaming"""

from typing import Literal
from langgraph.graph import StateGraph, END, START
from langgraph.types import Command

from open_deep_research.deep_researcher import (
    clarify_with_user, 
    write_research_brief, 
    final_report_generation,
    supervisor_subgraph,
    researcher_subgraph
)
from open_deep_research.configuration import Configuration
from open_deep_research.state import AgentState

from .sgr_langgraph_adapter import SGRStreamingNode, SGRDecisionRouter
from .streaming_researcher import StreamingResearcher


class UnifiedSGRWorkflow:
    """Объединенный workflow Open Deep Research + SGR Streaming"""
    
    def __init__(self, sgr_config):
        self.sgr_config = sgr_config
        self.sgr_node = SGRStreamingNode(sgr_config.get_sgr_streaming_config())
        self.streaming_researcher = StreamingResearcher()
        self.router = SGRDecisionRouter()
    
    def build_graph(self):
        """Создает объединенный LangGraph"""
        
        # Создаем граф с SGR интеграцией
        builder = StateGraph(AgentState, config_schema=Configuration)
        
        # Добавляем узлы
        builder.add_node("clarify_with_user", clarify_with_user)
        builder.add_node("write_research_brief", write_research_brief)
        builder.add_node("sgr_reasoning", self.sgr_node)
        builder.add_node("research_supervisor", self.streaming_researcher.streaming_supervisor_wrapper)
        builder.add_node("final_report_generation", final_report_generation)
        
        # Определяем основной flow
        builder.add_edge(START, "clarify_with_user")
        
        # SGR управляет переходами после clarification
        builder.add_conditional_edges(
            "clarify_with_user",
            self._route_after_clarification,
            {
                "brief": "write_research_brief",
                "end": END
            }
        )
        
        builder.add_edge("write_research_brief", "sgr_reasoning")
        
        # SGR принимает решения о следующих шагах
        builder.add_conditional_edges(
            "sgr_reasoning",
            self.router.route_sgr_decision,
            {
                "research": "research_supervisor",
                "report": "final_report_generation", 
                "clarify": "clarify_with_user",
                "end": END
            }
        )
        
        # После research supervisor снова возвращаемся к SGR для принятия решений
        builder.add_edge("research_supervisor", "sgr_reasoning")
        builder.add_edge("final_report_generation", END)
        
        return builder.compile()
    
    def _route_after_clarification(self, state: AgentState) -> str:
        """Маршрутизация после этапа уточнения"""
        
        messages = state.get("messages", [])
        if not messages:
            return "end"
        
        last_message = messages[-1]
        
        # Если последнее сообщение - от AI и содержит вопрос, значит нужно уточнение
        if hasattr(last_message, 'content'):
            content = last_message.content
            if "?" in content or "уточн" in content.lower() or "clarif" in content.lower():
                return "end"  # Ждем ответа пользователя
        
        return "brief"  # Переходим к созданию плана исследования


class SGREnhancedNodes:
    """SGR-улучшенные версии стандартных узлов"""
    
    def __init__(self, sgr_config):
        self.sgr_config = sgr_config
        self.streaming_enabled = sgr_config.get("streaming_enabled", True)
    
    async def enhanced_clarify_with_user(self, state: AgentState, config) -> Command:
        """Уточнение с SGR анализом"""
        
        if self.streaming_enabled:
            print("🤔 SGR Enhanced Clarification...")
            
        # Выполняем стандартное уточнение
        result = await clarify_with_user(state, config)
        
        if self.streaming_enabled:
            print("✅ Clarification completed")
            
        return result
    
    async def enhanced_write_research_brief(self, state: AgentState, config) -> Command:
        """Создание плана исследования с SGR анализом"""
        
        if self.streaming_enabled:
            print("📋 SGR Enhanced Research Planning...")
            
        # Выполняем стандартное создание плана
        result = await write_research_brief(state, config)
        
        if self.streaming_enabled:
            print("✅ Research plan created")
            
        return result
    
    async def enhanced_final_report_generation(self, state: AgentState, config):
        """Генерация отчета с SGR мониторингом"""
        
        if self.streaming_enabled:
            print("📝 SGR Enhanced Report Generation...")
            
        # Выполняем стандартную генерацию отчета
        result = await final_report_generation(state, config)
        
        if self.streaming_enabled:
            print("✅ Final report generated")
            
        return result


class SGRWorkflowBuilder:
    """Builder для создания различных конфигураций SGR workflow"""
    
    @staticmethod
    def build_simple_sgr_workflow(sgr_config):
        """Простой SGR workflow с базовой интеграцией"""
        
        workflow = UnifiedSGRWorkflow(sgr_config)
        return workflow.build_graph()
    
    @staticmethod  
    def build_enhanced_sgr_workflow(sgr_config):
        """Расширенный SGR workflow с дополнительными возможностями"""
        
        builder = StateGraph(AgentState, config_schema=Configuration)
        enhanced_nodes = SGREnhancedNodes(sgr_config)
        sgr_node = SGRStreamingNode(sgr_config.get_sgr_streaming_config())
        router = SGRDecisionRouter()
        
        # Добавляем enhanced узлы
        builder.add_node("clarify_with_user", enhanced_nodes.enhanced_clarify_with_user)
        builder.add_node("write_research_brief", enhanced_nodes.enhanced_write_research_brief)
        builder.add_node("sgr_reasoning", sgr_node)
        builder.add_node("research_supervisor", supervisor_subgraph)
        builder.add_node("final_report_generation", enhanced_nodes.enhanced_final_report_generation)
        
        # Настраиваем flow
        builder.add_edge(START, "clarify_with_user")
        builder.add_edge("clarify_with_user", "write_research_brief")
        builder.add_edge("write_research_brief", "sgr_reasoning")
        
        builder.add_conditional_edges(
            "sgr_reasoning",
            router.route_sgr_decision,
            {
                "research": "research_supervisor",
                "report": "final_report_generation",
                "clarify": "clarify_with_user", 
                "end": END
            }
        )
        
        builder.add_edge("research_supervisor", "sgr_reasoning")
        builder.add_edge("final_report_generation", END)
        
        return builder.compile()
    
    @staticmethod
    def build_streaming_focused_workflow(sgr_config):
        """SGR workflow с акцентом на streaming визуализацию"""
        
        # Этот вариант будет создавать workflow с максимальной SGR интеграцией
        # когда все SGR компоненты будут скопированы
        
        try:
            from ..sgr_streaming.sgr_streaming import SGRAgent
            
            # Создаем полноценный SGR agent
            sgr_agent = SGRAgent(sgr_config.get_sgr_streaming_config())
            
            # Здесь будет полная интеграция с SGR streaming
            # когда компоненты будут доступны
            
            workflow = UnifiedSGRWorkflow(sgr_config)
            return workflow.build_graph()
            
        except ImportError:
            print("⚠️  Full SGR streaming not available, using enhanced workflow")
            return SGRWorkflowBuilder.build_enhanced_sgr_workflow(sgr_config)