#!/usr/bin/env python3
"""
Пример использования SGR streaming интеграции с Open Deep Research
"""

import asyncio
import sys
from pathlib import Path

# Добавляем путь к модулям проекта
project_root = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(project_root))

from open_deep_research.sgr_config import config
from open_deep_research.sgr_integration.unified_workflow import (
    UnifiedSGRWorkflow, 
    SGRWorkflowBuilder
)


async def simple_sgr_example():
    """Simple example using SGR streaming"""
    
    print("🚀 SGR Streaming Integration Example")
    print("=" * 50)
    
    # Check configuration
    if config is None:
        print("❌ SGR configuration not loaded. Check .env file.")
        print("💡 Copy .env.sgr.example to .env and add your API keys")
        return
    
    print("✅ SGR configuration loaded")
    print(f"📊 Streaming enabled: {config.STREAMING_ENABLED}")
    print(f"🎯 Display type: {config.STREAMING_DISPLAY_TYPE}")
    
    # Test SGR agent creation
    try:
        from open_deep_research.sgr_streaming.sgr_streaming import SGRAgent
        
        # Create config dictionary for SGR agent
        sgr_config_dict = {
            'openai_api_key': config.OPENROUTER_API_KEY,
            'openai_base_url': 'https://openrouter.ai/api/v1',
            'openai_model': config.RESEARCHER_MODEL_NAME,
            'max_tokens': 8000,
            'temperature': 0.4
        }
        
        agent = SGRAgent(sgr_config_dict)
        print("✅ SGR Agent created successfully")
        
        # Test conversation log creation
        test_query = "Research current trends in artificial intelligence"
        conversation_log = agent.get_conversation_log(test_query)
        print(f"✅ Conversation log created with {len(conversation_log)} messages")
        
        # Start research session (demonstration)
        agent.start_research_session(test_query)
        
        print("✅ SGR streaming integration test completed!")
        print("📝 The agent is ready for integration with Open Deep Research")
        
    except Exception as e:
        print(f"❌ Error creating SGR agent: {e}")
        import traceback
        traceback.print_exc()
        return


async def enhanced_sgr_example():
    """Расширенный пример с использованием enhanced workflow"""
    
    print("🚀 Enhanced SGR Streaming Example")
    print("=" * 50)
    
    if config is None:
        print("❌ SGR конфигурация не загружена")
        return
    
    # Создаем enhanced workflow
    try:
        enhanced_graph = SGRWorkflowBuilder.build_enhanced_sgr_workflow(config)
        print("✅ Enhanced SGR workflow создан")
        
    except Exception as e:
        print(f"❌ Ошибка создания enhanced workflow: {e}")
        return
    
    # Демонстрируем возможности
    query = "Проанализируй влияние блокчейн технологий на финансовую индустрию"
    
    print(f"\n🔍 Исследуем: {query}")
    
    try:
        # Показываем SGR конфигурацию
        sgr_config = config.get_sgr_streaming_config()
        print("\n📊 SGR Streaming конфигурация:")
        for key, value in sgr_config.items():
            print(f"  {key}: {value}")
        
        # Запускаем enhanced исследование
        print("\n🚀 Запуск enhanced исследования...")
        
        result = await enhanced_graph.ainvoke({
            "messages": [{"role": "user", "content": query}]
        })
        
        print("\n✅ Enhanced исследование завершено!")
        
        # Анализируем результат
        if "final_report" in result:
            print(f"📝 Финальный отчет готов ({len(result['final_report'])} символов)")
        
        if "notes" in result:
            print(f"📚 Собрано заметок: {len(result.get('notes', []))}")
        
        if "research_brief" in result:
            print(f"📋 План исследования: {result.get('research_brief', 'N/A')[:100]}...")
            
    except Exception as e:
        print(f"❌ Ошибка в enhanced исследовании: {e}")


async def streaming_focused_example():
    """Пример с акцентом на streaming визуализацию"""
    
    print("🎬 Streaming-Focused SGR Example")
    print("=" * 50)
    
    if config is None:
        print("❌ SGR конфигурация не загружена")
        return
    
    # Пытаемся создать streaming-focused workflow
    try:
        streaming_graph = SGRWorkflowBuilder.build_streaming_focused_workflow(config)
        print("✅ Streaming-focused workflow создан")
        
    except Exception as e:
        print(f"⚠️  Используем fallback workflow: {e}")
        streaming_graph = SGRWorkflowBuilder.build_simple_sgr_workflow(config)
    
    # Демонстрируем streaming возможности
    query = "Research the future of renewable energy technologies"
    
    print(f"\n🎯 Streaming research: {query}")
    
    try:
        # Настраиваем streaming конфигурацию
        config.STREAMING_ENABLED = True
        config.STREAMING_DISPLAY_TYPE = "enhanced"
        config.STREAMING_UPDATE_INTERVAL = 0.1
        
        print(f"🎮 Streaming настройки:")
        print(f"  Enabled: {config.STREAMING_ENABLED}")
        print(f"  Display: {config.STREAMING_DISPLAY_TYPE}")
        print(f"  Interval: {config.STREAMING_UPDATE_INTERVAL}s")
        
        # Запускаем с streaming мониторингом
        print("\n🎬 Запуск streaming исследования...")
        
        result = await streaming_graph.ainvoke({
            "messages": [{"role": "user", "content": query}]
        })
        
        print("\n🎉 Streaming исследование завершено!")
        
        # Показываем статистику
        if result:
            print("📊 Результаты:")
            for key, value in result.items():
                if isinstance(value, str):
                    print(f"  {key}: {len(value)} символов")
                elif isinstance(value, list):
                    print(f"  {key}: {len(value)} элементов")
                else:
                    print(f"  {key}: {type(value).__name__}")
                    
    except Exception as e:
        print(f"❌ Ошибка в streaming исследовании: {e}")


async def interactive_sgr_demo():
    """Интерактивная демонстрация SGR"""
    
    print("🎮 Interactive SGR Demo")
    print("=" * 50)
    
    if config is None:
        print("❌ SGR конфигурация не загружена")
        return
    
    # Создаем workflow
    workflow = UnifiedSGRWorkflow(config)
    graph = workflow.build_graph()
    
    print("✅ SGR система готова к работе")
    print("💡 Введите ваш исследовательский запрос (или 'quit' для выхода):")
    
    while True:
        try:
            # Получаем запрос от пользователя
            user_input = input("\n🔍 Ваш запрос: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 До свидания!")
                break
            
            if not user_input:
                print("⚠️  Пустой запрос. Попробуйте еще раз.")
                continue
            
            print(f"\n🚀 Исследуем: {user_input}")
            
            # Запускаем исследование
            result = await graph.ainvoke({
                "messages": [{"role": "user", "content": user_input}]
            })
            
            # Показываем результат
            if "final_report" in result and result["final_report"]:
                print("\n📋 Результат исследования:")
                print("-" * 40)
                print(result["final_report"])
                print("-" * 40)
            else:
                print("\n⚠️  Исследование завершено, но отчет не создан")
            
        except KeyboardInterrupt:
            print("\n👋 Прервано пользователем")
            break
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
            continue


async def main():
    """Главная функция с выбором примера"""
    
    print("🎯 SGR Streaming Integration Examples")
    print("=" * 50)
    
    examples = {
        "1": ("Simple SGR Example", simple_sgr_example),
        "2": ("Enhanced SGR Example", enhanced_sgr_example), 
        "3": ("Streaming-Focused Example", streaming_focused_example),
        "4": ("Interactive Demo", interactive_sgr_demo)
    }
    
    print("Выберите пример для запуска:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    
    try:
        choice = input("\nВаш выбор (1-4): ").strip()
        
        if choice in examples:
            name, func = examples[choice]
            print(f"\n🚀 Запуск: {name}")
            await func()
        else:
            print("❌ Неверный выбор")
            
    except KeyboardInterrupt:
        print("\n👋 Программа прервана")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main())