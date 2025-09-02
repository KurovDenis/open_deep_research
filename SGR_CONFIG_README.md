# SGR Configuration Setup

Этот документ описывает как настроить безопасную конфигурацию для SGR-агента.

## Быстрый старт

### 1. Создайте .env файл

Скопируйте пример файла и заполните своими API ключами:

```bash
cp .env.sgr.example .env
```

Отредактируйте `.env` файл:

```env
OPENROUTER_API_KEY=sk-or-v1-ваш-реальный-ключ
TAVILY_API_KEY=tvly-ваш-реальный-ключ
```

### 2. Использование в коде

```python
from sgr_config import config

# Конфигурация автоматически загружается из переменных окружения
# Если config равен None, значит не хватает API ключей

if config:
    # Получить настройки для интеграции с Deep Research
    config_dict = config.to_configuration_dict()
    
    # Получить модели для разных ролей
    researcher_model = config.get_openrouter_model_name("researcher")
    writer_model = config.get_openrouter_model_name("writer")
else:
    print("❌ Конфигурация не загружена. Проверьте .env файл.")
```

## Получение API ключей

### OpenRouter
1. Зайдите на https://openrouter.ai/keys
2. Зарегистрируйтесь или войдите в аккаунт
3. Создайте новый API ключ
4. Скопируйте ключ (начинается с `sk-or-v1-`)

### Tavily
1. Зайдите на https://app.tavily.com/
2. Зарегистрируйтесь или войдите в аккаунт
3. Получите API ключ в дашборде
4. Скопируйте ключ (начинается с `tvly-`)

## Безопасность

✅ **Правильно:**
- Хранить API ключи в `.env` файле
- Добавить `.env` в `.gitignore` (уже сделано)
- Не коммитить секретные данные

❌ **Неправильно:**
- Хранить API ключи в коде
- Коммитить `.env` файл в репозиторий
- Использовать API ключи в открытом коде

## Структура конфигурации

```python
class SGRConfig(BaseModel):
    # API ключи (загружаются из переменных окружения)
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
    # ... другие настройки
```

## Интеграция с существующей системой

Конфигурация автоматически совместима с существующим классом `Configuration`:

```python
from sgr_config import config
from open_deep_research.configuration import Configuration

if config:
    # Преобразовать SGR конфигурацию в формат Deep Research
    config_dict = config.to_configuration_dict()
    
    # Использовать с существующей системой
    deep_research_config = Configuration(**config_dict)
```

## Устранение проблем

### Ошибка: "Отсутствуют обязательные переменные окружения"

```bash
# Проверьте содержимое .env файла
cat .env

# Убедитесь, что файл находится в корне проекта
ls -la .env

# Проверьте переменные окружения
echo $OPENROUTER_API_KEY
echo $TAVILY_API_KEY
```

### Ошибка импорта

```python
# Если возникают проблемы с импортом, попробуйте:
import os
from dotenv import load_dotenv

# Загрузить .env файл вручную
load_dotenv()

# Проверить переменные
print(os.getenv('OPENROUTER_API_KEY'))
print(os.getenv('TAVILY_API_KEY'))
```