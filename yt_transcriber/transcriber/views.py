import os
import logging
from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
from .forms import YouTubeURLForm
from .utils import download_audio
from .tasks import audio_to_text
from celery.result import AsyncResult

logger = logging.getLogger(__name__)

def transcribe_video(request):
    if request.method == 'POST':
        form = YouTubeURLForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            output_path = os.path.join(settings.MEDIA_ROOT, 'audio')
            os.makedirs(output_path, exist_ok=True)
            
            try:
                audio_file = download_audio(url, output_path)
                task = audio_to_text.delay(audio_file)
                return redirect(reverse('transcription_status', kwargs={'task_id': task.id}))
            except Exception as e:
                logger.error(f"Error in transcribe_video view: {str(e)}")
                error_message = f"An error occurred: {str(e)}"
                return render(request, 'transcriber/error.html', {'error': error_message})
    else:
        form = YouTubeURLForm()
    
    return render(request, 'transcriber/transcribe.html', {'form': form})

def transcription_status(request, task_id):
    task = AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {'state': task.state, 'status': 'Pending...'}
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': task.info.get('status', '') if isinstance(task.info, dict) else '',
            'current': task.info.get('current', 0) if isinstance(task.info, dict) else 0,
            'total': task.info.get('total', 1) if isinstance(task.info, dict) else 1,
            'percent': int(task.info.get('current', 0) / task.info.get('total', 1) * 100) if isinstance(task.info, dict) else 0,
        }
        if task.state == 'SUCCESS':
            response['result'] = task.result
    else:
        response = {
            'state': task.state,
            'status': str(task.info),
        }
    return render(request, 'transcriber/status.html', {'task_id': task_id, 'response': response})