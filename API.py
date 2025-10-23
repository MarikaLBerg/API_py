Установка необходимых библиотек
bash

pip install fastapi uvicorn pydub python-multipart
Код API
python

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydub import AudioSegment
import uuid
import os

app = FastAPI()

# Папка для хранения загруженных файлов
UPLOAD_DIRECTORY = "uploaded_songs"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# Внутренний словарь для хранения информации о проигранных песнях
songs = {}

@app.post("/upload/")
async def upload_song(file: UploadFile = File(...)):
    # Проверка расширения файла
    filename = file.filename
    if not filename.lower().endswith(('.mp3', '.wav', '.ogg', '.flac')):
        raise HTTPException(status_code=400, detail="Поддерживаются только аудиофайлы: mp3, wav, ogg, flac")
    
    # Создаем уникальное имя файла
    song_id = str(uuid.uuid4())
    filepath = os.path.join(UPLOAD_DIRECTORY, f"{song_id}_{filename}")
    
    # Чтение и сохранение файла
    with open(filepath, "wb") as buffer:
        buffer.write(await file.read())
    
    # Загружаем аудиофайл для получения информации
    audio = AudioSegment.from_file(filepath)
    duration_sec = len(audio) / 1000  # Длина в секундах
    
    # Сохраняем информацию о песне
    songs[song_id] = {
        "filename": filename,
        "filepath": filepath,
        "duration_sec": duration_sec
    }
    
    return {
        "song_id": song_id,
        "filename": filename,
        "duration_sec": duration_sec
    }

@app.get("/play/{song_id}")
async def play_song(song_id: str):
    if song_id not in songs:
        raise HTTPException(status_code=404, detail="Песня не найдена")
    
    song = songs[song_id]
    filepath = song["filepath"]
    filename = song["filename"]
    
    return {
        "filename": filename,
        "file_url": f"/download/{song_id}"
    }

@app.get("/download/{song_id}")
async def download_song(song_id: str):
    if song_id not in songs:
        raise HTTPException(status_code=404, detail="Песня не найдена")
    filepath = songs[song_id]["filepath"]
    filename = songs[song_id]["filename"]
    return await fastapi.responses.FileResponse(filepath, filename=filename)

# Запуск сервера: команда в терминале
# uvicorn main:app --reload
