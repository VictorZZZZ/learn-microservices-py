# recognize-service

Сервис распознавания текста (OCR) с техпаспортов автомобилей.

## Библиотека EasyOCR

[EasyOCR](https://github.com/JaidedAI/EasyOCR) — OCR-библиотека на PyTorch, поддерживает 80+ языков. Состоит из двух нейросетей:

- **Детектор** CRAFT (`craft_mlt_25k.pth`, ~80 МБ) — находит зоны с текстом на фото;
- **Распознаватель** CRNN — читает текст. Модель не на язык, а на алфавит: `cyrillic_g2.pth` (~14 МБ) покрывает ru/uk/be/bg и др., `latin_g2.pth` (~15 МБ) — en/de/pl и др.

Для `['ru', 'en']` скачивается ~110 МБ весов — один раз, в `~/.EasyOCR/` (при первом запуске).

## Ресурсы

| Что | Величина |
|---|---|
| Веса моделей (ru+en, диск) | ~110 МБ |
| RAM процесса при CPU-инференсе | ~600 МБ – 1,5 ГБ |
| Скорость на CPU | секунды–десятки секунд на фото |
| Скорость на GPU | ~0,3–1 сек на фото |

## Модели в сервисе (FastAPI)

`Reader` создаётся **один раз при старте** через lifespan и живёт в памяти постоянно — инициализация занимает 5–15 секунд, делать её на каждый запрос бессмысленно.

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
import easyocr

reader = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global reader
    reader = easyocr.Reader(['ru', 'en'], gpu=False)  # грузим один раз
    yield

app = FastAPI(lifespan=lifespan)
```

Особенности эксплуатации:

- **1 воркер = 1 копия моделей** (~1 ГБ RAM). Масштабировать репликами, а не воркерами.
- **Reader не потокобезопасен** — параллельные запросы сериализовать через lock или держать пул Reader'ов.
- **Не блокировать event loop** — эндпоинт объявлять `def` (Starlette унесёт в threadpool), а не `async def`.
- **Readiness-проба** должна ждать загрузки моделей.

## Запуск скрипта распознавания

```bash
python3 app/recognize/easyway.py
```

Скрипт проходит по всем фото в `files/` и печатает распознанный текст. Кириллические имена файлов читаются через `np.fromfile` + `cv2.imdecode` (`cv2.imread` на них спотыкается).
