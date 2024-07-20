import os
import logging
from celery import shared_task
from django.core.cache import cache
from concurrent.futures import ThreadPoolExecutor, as_completed
from .utils import split_audio, process_audio_chunk

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def audio_to_text(self, audio_file):
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