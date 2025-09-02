"""SGR Configuration for LangGraph agent with custom model and API settings."""

import os
from pydantic import BaseModel
from typing import Optional


class SGRConfig(BaseModel):
    """Конфигурация для SGR-агента на LangGraph."""
    
    # API Keys (загружаются из переменных окружения)
    OPENROUTER_API_KEY: Optional[str] = None
    TAVILY_API_KEY: Optional[str] = None

    # Модели для разных ролей
    SUPERVISOR_MODEL_NAME: str = "google/gemini-2.0-flash-001"
    RESEARCHER_MODEL_NAME: str = "google/gemini-2.0-flash-001"
    WRITER_MODEL_NAME: str = "google/gemini-2.0-flash-001"
    CLARIFIER_MODEL_NAME: str = "google/gemini-2.0-flash-001"

    # Настройки процесса
    MAX_SUPERVISOR_ITERATIONS: int = 3
    MAX_SEARCH_RESULTS: int = 5
    MAX_RESEARCH_CALLS: int = 5

    # Дополнительные настройки для интеграции с существующей системой
    MAX_STRUCTURED_OUTPUT_RETRIES: int = 3
    ALLOW_CLARIFICATION: bool = True
    MAX_CONCURRENT_RESEARCH_UNITS: int = 5
    MAX_REACT_TOOL_CALLS: int = 10
    MAX_CONTENT_LENGTH: int = 50000
    
    # Настройки токенов для моделей
    SUMMARIZATION_MODEL_MAX_TOKENS: int = 8192
    RESEARCH_MODEL_MAX_TOKENS: int = 10000
    COMPRESSION_MODEL_MAX_TOKENS: int = 8192
    FINAL_REPORT_MODEL_MAX_TOKENS: int = 10000

    def __init__(self, **kwargs):
        """Инициализация с загрузкой API ключей из переменных окружения."""
        # Загружаем API ключи из переменных окружения
        kwargs.setdefault('OPENROUTER_API_KEY', os.getenv('OPENROUTER_API_KEY'))
        kwargs.setdefault('TAVILY_API_KEY', os.getenv('TAVILY_API_KEY'))
        super().__init__(**kwargs)
        
        # Проверяем наличие обязательных API ключей
        self._validate_api_keys()
    
    def _validate_api_keys(self):
        """Проверить наличие обязательных API ключей."""
        missing_keys = []
        
        if not self.OPENROUTER_API_KEY:
            missing_keys.append('OPENROUTER_API_KEY')
        if not self.TAVILY_API_KEY:
            missing_keys.append('TAVILY_API_KEY')
            
        if missing_keys:
            raise ValueError(
                f"Отсутствуют обязательные переменные окружения: {', '.join(missing_keys)}\n"
                "Создайте .env файл или установите переменные окружения."
            )

    def apply_environment_variables(self):
        """Применить настройки к переменным окружения."""
        if self.OPENROUTER_API_KEY:
            os.environ["OPENROUTER_API_KEY"] = self.OPENROUTER_API_KEY
        if self.TAVILY_API_KEY:
            os.environ["TAVILY_API_KEY"] = self.TAVILY_API_KEY
            
        os.environ["OPENROUTER_API_BASE"] = "https://openrouter.ai/api/v1"
        
        # Установить основные API ключи для совместимости
        if self.OPENROUTER_API_KEY:
            os.environ["OPENAI_API_KEY"] = self.OPENROUTER_API_KEY
            os.environ["ANTHROPIC_API_KEY"] = self.OPENROUTER_API_KEY
            os.environ["GOOGLE_API_KEY"] = self.OPENROUTER_API_KEY
        
        print("✅ Конфигурация настроена.")

    def get_openrouter_model_name(self, role: str) -> str:
        """Получить имя модели для OpenRouter с префиксом."""
        model_mapping = {
            "supervisor": self.SUPERVISOR_MODEL_NAME,
            "researcher": self.RESEARCHER_MODEL_NAME, 
            "writer": self.WRITER_MODEL_NAME,
            "clarifier": self.CLARIFIER_MODEL_NAME
        }
        
        model_name = model_mapping.get(role, self.RESEARCHER_MODEL_NAME)
        
        # Добавить префикс openai: для совместимости с init_chat_model
        if not model_name.startswith(("openai:", "anthropic:", "google:")):
            return f"openai:{model_name}"
        return model_name

    def to_configuration_dict(self) -> dict:
        """Преобразовать в словарь для использования с Configuration классом."""
        return {
            "max_structured_output_retries": self.MAX_STRUCTURED_OUTPUT_RETRIES,
            "allow_clarification": self.ALLOW_CLARIFICATION,
            "max_concurrent_research_units": self.MAX_CONCURRENT_RESEARCH_UNITS,
            "max_researcher_iterations": self.MAX_SUPERVISOR_ITERATIONS,
            "max_react_tool_calls": self.MAX_REACT_TOOL_CALLS,
            "search_api": "tavily",
            "summarization_model": self.get_openrouter_model_name("researcher"),
            "summarization_model_max_tokens": self.SUMMARIZATION_MODEL_MAX_TOKENS,
            "max_content_length": self.MAX_CONTENT_LENGTH,
            "research_model": self.get_openrouter_model_name("researcher"),
            "research_model_max_tokens": self.RESEARCH_MODEL_MAX_TOKENS,
            "compression_model": self.get_openrouter_model_name("researcher"),
            "compression_model_max_tokens": self.COMPRESSION_MODEL_MAX_TOKENS,
            "final_report_model": self.get_openrouter_model_name("writer"),
            "final_report_model_max_tokens": self.FINAL_REPORT_MODEL_MAX_TOKENS,
        }


# Создать экземпляр конфигурации
# Примечание: API ключи будут загружены из переменных окружения или .env файла
try:
    config = SGRConfig()
    # Применить настройки к окружению при импорте
    config.apply_environment_variables()
except ValueError as e:
    print(f"⚠️ Ошибка конфигурации: {e}")
    print("💡 Пример .env файла:")
    print("OPENROUTER_API_KEY=sk-or-v1-your-key-here")
    print("TAVILY_API_KEY=tvly-your-key-here")
    config = None