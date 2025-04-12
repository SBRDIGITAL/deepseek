# Ollama CPU-Only Deployment (4 Cores)

Минималистичная конфигурация для работы Ollama с моделями LLM исключительно на CPU с жестким ограничением в 4 ядра.

## Требования
- Docker 20.10+
- 8 GB+ свободной RAM
- Поддержка AVX2/AVX512 инструкций

## Быстрый старт
1. **Создайте конфигурационный файл** `docker-compose.yml`:
```yaml
services:
  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_NUM_PARALLEL=4    # Ограничение потоков CPU
      - OLLAMA_GPU_LAYERS=0      # Полное отключение GPU
      # - OLLAMA_DEBUG=false
      # - OLLAMA_DISABLE_GPU_INFO=true  # новая опция в версии 0.6.5+
    deploy:
      resources:
        reservations:
          cpus: '4'             # Жесткое ограничение ядер
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434"]
      interval: 10s
      timeout: 5s
      retries: 3

volumes:
  ollama_data:
```

2. **Запустите сервис**:
```bash
docker-compose up -d
```

3. **Загрузите модель** (выполнить один раз):
```bash
docker-compose exec ollama ollama pull deepseek-coder:6.7b
```

## Проверка установки
Просмотр доступных моделей:
```bash
docker-compose exec ollama ollama list
```

Ожидаемый вывод:
```
NAME                ID          SIZE    MODIFIED
deepseek-coder:6.7b 7ba89a...    4.1 GB 2 minutes ago
```

## Использование API

### Генерация текста

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "deepseek-coder:6.7b",
  "prompt": "Реализуй быструю сортировку на Python",
  "stream": false,
  "options": {
    "temperature": 0.8,
    "num_predict": 300
  }
}'
```

### Получение эмбеддингов

```bash
curl http://localhost:11434/api/embeddings -d '{
  "model": "deepseek-coder:6.7b",
  "prompt": "Нейронные сети и машинное обучение"
}'
```

## Управление сервисом

Остановка с очисткой данных:
```bash
docker-compose down -v
```

Перезагрузка конфигурации:
```bash
docker-compose restart ollama
```

## Технические характеристики

| Параметр               | Значение               |
|------------------------|------------------------|
| Макс. использование RAM | ~7.5 GB               |
| Скорость генерации     | 2-3 токена/сек        |
| Поддержка контекста    | До 4096 токенов       |
| Требуемые инструкции   | AVX2/AVX512           |
| Поддержка GPU          | Отключена             |

## Оптимизационные настройки

Для тонкой настройки запросов используйте:
- `temperature`: 0.1 (точность) — 2.0 (креативность)
- `top_p`: 0.5 (фокус) — 1.0 (разнообразие)
- `num_predict`: 1-4096 (ограничение длины ответа)

## Особенности реализации

1. Автоматическое определение оптимальных CPU-инструкций
2. Изоляция данных через Docker volume
3. Встроенный healthcheck для мониторинга
4. Жесткое ограничение ресурсов через cgroups
5. Поддержка только CPU-расчетов

Для работы с другими моделями просто замените `deepseek-coder:6.7b` в примерах на нужное имя модели.