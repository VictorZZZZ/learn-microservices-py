import os

import cv2
import easyocr
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_DIR = os.path.join(BASE_DIR, '..', '..', 'files')

# Инициализируем reader для русского и английского языков (английский нужен для VIN и госномера)
reader = easyocr.Reader(['ru', 'en'], gpu=False) # Если есть видеокарта, поставьте gpu=True

image_names = sorted(
    name for name in os.listdir(FILES_DIR)
    if name.lower().endswith(('.jpg', '.jpeg', '.png'))
)

for name in image_names:
    # cv2.imread не читает кириллические имена файлов, читаем через буфер
    data = np.fromfile(os.path.join(FILES_DIR, name), dtype=np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_COLOR)

    print(f'\n=== {name} ===')
    # Распознаем весь текст на фото
    results = reader.readtext(image)
    # Выводим найденный текст
    for (bbox, text, prob) in results:
        print(f"Текст: {text} (Уверенность: {prob:.2f})")
