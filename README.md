# ru_Lulu 🐕‍🦺

**Русскоязычный голосовой ИИ-чатбот для робоcобаки DOGZILLA Lite**
Perplexity AI + OpenAI Whisper/TTS + Keyword spotting + PiCamera

## Описание

Голосовой ассистент Lulu на базе Perplexity `sonar-pro` и OpenAI API.
**Активация**: Ключевое слово "LULU" + распознавание речи (Whisper ru).
**Ответ**: GPT-4o-mini TTS (голос shimmer) + эмоции и действия в реальном мире XGO + показ изображений DALL-E 3.

Поддерживает фото с PiCamera, физические действия робота, локальную историю чата.

Переиспользованы встроенные анимации Rider, необходимо переименовать все фреймы, сделав код двузначным, i.e. Angry1.png -> Angry01.png

## 🗂️ Структура файлов

| Файл | Описание |
| :-- | :-- |
| `ru_lulu.py` | Главный цикл: keyword spotting → STT → LLM → TTS + XGO эмоции |
| `lulu_llm_integrations-5.py` | Perplexity/OpenAI: `ask_perplexity()`, Whisper, TTS, DALL-E 3 |
| `audio-3.py` | Keyword detection (lulu_v3.premium), запись/воспроизведение aplay |
| `libnyumaya-4.py` | Аудио-фильтры (FanNoise) |
| `api_keys-2.py` | Ключи API (не коммитьте!) |
| `lulu_physical_actions-6.py` | Действия в реальном мире |
| `lulu_system_promt-7.txt` | Системный промпт Lulu |
| `perplexity-9.py` | `ask_perplexity()` с timeout=30s |
| `main-8.py` | Альтернативный main для собаки с быстрым доступом к RuLulu и Wi-Fi-приложению |

## 🔧 Ключевые фичи

### Keyword Spotting

- Модель: `lulu_v3.1.907.premium.p`
- Фильтр: FanNoise (RPi CM5)

### LLM Pipeline

- Распознавание команды -> Генерация Python-кода на стороне Perplexity -> Исполнение кода + TTS

### Голос

- **STT**: `whisper_recognize(audio.wav, language='ru')`
- **TTS**: `text_to_speech(text, "lulu_tts.wav")` → `playfile()` (aplay + PID kill)


### Изображения

- PiCamera → tmpfiles.org → GPT Vision
- DALL-E 3: `generate_image(prompt)` → LCD 320x240


## ⚙️ Конфигурация

**`api_keys.py`**:

```
OPENAI_KEY=sk-proj-...
PERPLEXITY_KEY=pxl-...
```

**Логи**: `lulu.log`

## 📱 Управление

- **Кнопка B**: Выход
- **Голос**: "LULU" → запись → ответ
- **LCD**: Анимации эмоций + текст + waveform

## 🤝 Разработка

**Автор**: Андрей Дьяков

***

*Гав-гав! Lulu слушает...* 🐶
