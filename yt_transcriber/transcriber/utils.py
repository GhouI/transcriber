import os
import logging
from pytubefix import YouTube
from pydub import AudioSegment
import speech_recognition as sr
from celery import shared_task
from django.core.cache import cache
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_audio(url, output_path):
    try:
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        output_file = audio_stream.download(output_path=output_path)
        
        base, ext = os.path.splitext(output_file)
        new_file = base + '.wav'
        AudioSegment.from_file(output_file).export(new_file, format='wav')
        
        os.remove(output_file)
        return new_file
    except Exception as e:
        logger.error(f"Error downloading audio: {str(e)}")
        raise

@shared_task
def process_audio_chunk(chunk_file):
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(chunk_file) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio)
        os.remove(chunk_file)
        return text
    except sr.UnknownValueError:
        logger.warning(f"Speech recognition could not understand audio in {chunk_file}")
        return ""
    except sr.RequestError as e:
        logger.error(f"Could not request results from the speech recognition service; {e}")
        return ""
    except Exception as e:
        logger.error(f"Error processing audio chunk {chunk_file}: {str(e)}")
        return ""

def split_audio(file_path, max_size_mb=9):
    audio = AudioSegment.from_wav(file_path)
    max_size_bytes = max_size_mb * 1024 * 1024
    duration_ms = len(audio)
    chunk_length_ms = int((max_size_bytes / len(audio.raw_data)) * duration_ms)
    
    chunks = []
    for i in range(0, duration_ms, chunk_length_ms):
        chunk = audio[i:i+chunk_length_ms]
        chunk_file = f"{file_path[:-4]}_chunk_{i}.wav"
        chunk.export(chunk_file, format="wav")
        chunks.append(chunk_file)
    
    return chunks


    cache_key = f"transcription:{audio_file}"
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result

    try:
        chunks = split_audio(audio_file)
        total_chunks = len(chunks)
        
        results = []
        with ThreadPoolExecutor(max_workers=min(total_chunks, os.cpu_count() or 1)) as executor:
            future_to_chunk = {executor.submit(process_audio_chunk, chunk): chunk for chunk in chunks}
            for i, future in enumerate(as_completed(future_to_chunk)):
                results.append(future.result())
                self.update_state(state='PROGRESS', meta={'current': i + 1, 'total': total_chunks})
        
        full_text = " ".join(results).strip()
        cache.set(cache_key, full_text, timeout=86400)  # Cache for 24 hours
        
        os.remove(audio_file)
        return full_text
    except Exception as e:
        logger.error(f"Error in audio_to_text task: {str(e)}")
        raise
    # Check cache first
    cache_key = f"transcription:{audio_file}"
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result

    chunks = split_audio(audio_file)
    
    # Process chunks in parallel
    with ThreadPoolExecutor(max_workers=min(len(chunks), os.cpu_count() or 1)) as executor:
        future_to_chunk = {executor.submit(process_audio_chunk, chunk): chunk for chunk in chunks}
        results = []
        for future in as_completed(future_to_chunk):
            results.append(future.result())
    
    full_text = " ".join(results).strip()
    
    # Cache the result
    cache.set(cache_key, full_text, timeout=86400)  # Cache for 24 hours
    
    os.remove(audio_file)
    return full_text