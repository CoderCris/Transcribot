# W-002 — Motor de Transcripción

## Ficha de Oleada

- **ID**: W-002
- **Dependencias**: W-001
- **Entregable**: [chunker.py](http://chunker.py) segmenta audio por VAD, [transcriber.py](http://transcriber.py) transcribe cada chunk con faster-whisper.
- **Complejidad**: Media

---

## Prompt para Claude Code

```
---
OLEADA: W-002 — Motor de Transcripción
DEPENDENCIAS: W-001
CONTEXTO: CLI transcripción reuniones español con diarización. Pipeline secuencial.
STACK: Python 3.11+, faster-whisper 1.1.x, Silero VAD
---

INSTRUCCIONES:

1. Añadir faster-whisper>=1.1.0 a pyproject.toml

2. Implementar src/transcribot/chunker.py:
   - Dataclass AudioChunk(start: float, end: float, audio_path: Path)
   - segment_by_vad(wav_path, chunk_duration=600) -> list[AudioChunk]
   - Usar Silero VAD de faster-whisper para detectar habla
   - Agrupar en chunks sin exceder chunk_duration, cortando en silencios
   - Extraer fragmentos con pydub como WAV temporales
   - Retornar con timestamps globales

3. Implementar src/transcribot/transcriber.py:
   - Dataclass TranscriptionSegment(start: float, end: float, text: str)
   - Clase Transcriber con __init__(model_size, device, compute_type)
   - transcribe_chunk(chunk) -> list[TranscriptionSegment] con offset global
   - transcribe_all(chunks, progress_callback) -> list[TranscriptionSegment]

4. Actualizar hardware.py con torch.cuda y check_system_requirements()

5. Tests: test_chunker.py (WAV sintético), test_transcriber.py (marcados slow)

NO MODIFICAR: diarizer.py, aligner.py, formatter.py, cli.py

RESULTADO: Transcriber transcribe WAV, chunker segmenta audio largo
```

---

## Criterios de Validación

- [ ]  pip install -e . instala faster-whisper
- [ ]  from faster_whisper import WhisperModel funciona
- [ ]  pytest tests/test_[chunker.py](http://chunker.py) -v pasa
- [ ]  Transcriber con modelo tiny transcribe WAV corto correctamente