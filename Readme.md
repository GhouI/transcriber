# Audio Transcription Service

### Overview

This repository contains a Django-based service for downloading, processing, and transcribing audio files. The service utilizes several libraries including `pytube`, `pydub`, `speech_recognition`, and `celery` to provide a seamless and efficient audio transcription process. Audio files are downloaded from YouTube, converted to WAV format, split into manageable chunks, and then transcribed using Google's speech recognition service. The results are cached to improve performance for repeated requests.

### Features

- **Download Audio**: Download audio from YouTube and convert it to WAV format.
- **Audio Splitting**: Split large audio files into smaller chunks.
- **Speech Recognition**: Transcribe audio chunks using Google's speech recognition service.
- **Parallel Processing**: Process audio chunks in parallel to speed up transcription.
- **Caching**: Cache transcription results to improve performance for repeated requests.

### Prerequisites

- Python 3.6+
- Django
- Celery
- Redis (for caching and Celery backend)
- FFMpeg (for audio processing with `pydub`)

### Installation

1. **Clone the repository:**

    ```sh
    git clone https://github.com/yourusername/audio-transcription-service.git
    cd audio-transcription-service
    ```

2. **Install the required packages:**

    ```sh
    pip install -r requirements.txt
    ```

3. **Set up the Django project:**

    ```sh
    # Update your settings.py with appropriate configurations for database, cache, etc.
    python manage.py migrate
    ```

4. **Run Redis:**
   
   Make sure you have Redis installed and running on your system. You can start it with:

   ```sh
   redis-server
   ```

5. **Run Celery worker:**

    ```sh
    celery -A your_project_name worker --loglevel=info
    ```

### Usage

1. **Add the following to your Django settings:**

    ```python
    # settings.py

    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    ```

2. **Use the transcription service:**

   Call the `audio_to_text` task with the URL of the YouTube video:

   ```python
   from .tasks import audio_to_text

   result = audio_to_text.delay(your_audio_file_url)
   ```

### Code Walkthrough

- **Downloading Audio:**

    ```python
    def download_audio(url, output_path):
        ...
    ```

    Downloads audio from a given URL and converts it to WAV format.

- **Processing Audio Chunks:**

    ```python
    @shared_task
    def process_audio_chunk(chunk_file):
        ...
    ```

    Uses Google's speech recognition service to transcribe audio chunks.

- **Splitting Audio:**

    ```python
    def split_audio(file_path, max_size_mb=9):
        ...
    ```

    Splits large audio files into smaller chunks for easy processing.

- **Transcription Task:**

    ```python
    @shared_task(bind=True)
    def audio_to_text(self, audio_file):
        ...
    ```

    Manages the entire process of downloading, splitting, processing, and caching the transcription of an audio file.

### Error Handling

Extensive error handling is utilized throughout the code to ensure robustness. Errors are logged appropriately, and operations that fail do not affect the overall process.

```python
except Exception as e:
    logger.error(f"Error in audio_to_text task: {str(e)}")
    raise
```

### Contributing

Contributions are welcome! Please create a pull request or open an issue to discuss any improvements or fixes.

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

By following these guidelines and the provided code structure, you should be able to set up and use the audio transcription service effectively. Happy coding!
