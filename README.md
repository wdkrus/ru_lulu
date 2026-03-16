# ru_Lulu 🐕‍🦺

**Русскоязычный голосовой ИИ-чатбот для робоcобаки DOGZILLA Lite**
Perplexity AI + OpenAI Whisper/TTS + Keyword spotting + PiCamera

## Описание

Голосовой ассистент Lulu на базе Perplexity `sonar-pro` и OpenAI API.
**Активация**: Ключевое слово "LULU" + распознавание речи (Whisper ru).
**Ответ**: GPT-4o-mini TTS (голос shimmer) + эмоции и действия в реальном мире XGO + показ изображений DALL-E 3.

Поддерживает фото с PiCamera, физические действия робота, локальную историю чата.

Переиспользованы встроенные анимации Rider, необходимо переименовать все фреймы, сделав код двузначным, i.e. Angry1.png -> Angry01.png

## 🗂️ Структура файлов[^1][^2][^3][^4]

| Файл | Описание |
| :-- | :-- |
| `ru_lulu.py` [^1] | Главный цикл: keyword spotting → STT → LLM → TTS + XGO эмоции |
| `lulu_llm_integrations-5.py` [^2] | Perplexity/OpenAI: `ask_perplexity()`, Whisper, TTS, DALL-E 3 |
| `audio-3.py` [^3] | Keyword detection (lulu_v3.premium), запись/воспроизведение aplay |
| `libnyumaya-4.py` [^5] | Аудио-фильтры (FanNoise)я |
| `api_keys-2.py` [^6] | Ключи API (не коммитьте!) |
| `lulu_physical_actions-6.py` [^7] | Действия в реальном мире |
| `lulu_system_promt-7.txt` [^8] | Системный промпт Lulu |
| `perplexity-9.py` [^9] | `ask_perplexity()` с timeout=30s |
| `main-8.py` [^4] | Альтернативный main для собаки с быстрым доступом к RuLulu и Wi-Fi-приложению |

## 🔧 Ключевые фичи

### Keyword Spotting

- Модель: `lulu_v3.1.907.premium.p`
- Фильтр: FanNoise (RPi CM5)

### LLM Pipeline[^2][^9]

- Распознавание команды -> Генерация Python-кода на стороне Perplexity -> Исполнение кода + TTS

### Голос[^3]

- **STT**: `whisper_recognize(audio.wav, language='ru')`
- **TTS**: `text_to_speech(text, "lulu_tts.wav")` → `playfile()` (aplay + PID kill)


### Изображения

- PiCamera → tmpfiles.org → GPT Vision
- DALL-E 3: `generate_image(prompt)` → LCD 320x240


## ⚙️ Конфигурация

**`.env` или `api_keys.py`**:

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

**Автор**: Андрей Дьяков[^2]

***

*Гав-гав! Lulu слушает...* 🐶
