import subprocess
import os
from datasets import load_dataset

OUTPUT_DIR = "musiccaps_audio"
os.makedirs(OUTPUT_DIR, exist_ok=True)

dataset = load_dataset("google/MusicCaps", split="train")

def get_audio_stream_url(youtube_url):
    """
    Получает прямую ссылку на аудиопоток через yt-dlp
    """
    cmd = [
        "yt-dlp",
        "-f", "bestaudio",
        "-g",                # вывести прямой URL потока
        youtube_url,
        "--cookies", "cookies.txt"  # если нужно, укажите путь к файлу с куки для доступа к контенту
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()

def download_clip(stream_url, start_time, out_file):
    """
    Скачивает 10 секунд аудио напрямую через ffmpeg
    """
    cmd = [
        "ffmpeg",
        "-ss", str(start_time),
        "-i", stream_url,
        "-t", "10",
        "-ac", "1",
        "-ar", "16000",
        "-vn",
        "-y",
        out_file
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def already_downloaded(path):
    """
    Проверяем что файл существует и не пустой
    """
    return os.path.exists(path) and os.path.getsize(path) > 10_000

for item in dataset:
    ytid = item["ytid"]
    start_s = item["start_s"]

    youtube_url = f"https://www.youtube.com/watch?v={ytid}"
    out_file = os.path.join(OUTPUT_DIR, f"{ytid}_{start_s}.wav")

    if already_downloaded(out_file):
        print("Skip:", out_file)
        continue
    
    try:
        stream_url = get_audio_stream_url(youtube_url)
        print(stream_url)
        download_clip(stream_url, start_s, out_file)
        print("Downloaded:", out_file)
    except Exception as e:
        print("Error:", youtube_url, e)