# W-003 — Diarización de Locutores

## Ficha de Oleada

- **ID**: W-003
- **Dependencias**: W-001
- **Entregable**: [diarizer.py](http://diarizer.py) identifica locutores con timestamps usando [pyannote.audio](http://pyannote.audio).
- **Complejidad**: Media

---

## Prompt para Claude Code

```
---
OLEADA: W-003 — Diarización de Locutores
DEPENDENCIAS: W-001
CONTEXTO: CLI transcripción reuniones español. Se necesita identificar quién habla sin conocer el número de participantes.
STACK: Python 3.11+, pyannote.audio 3.3.x, torch
---

INSTRUCCIONES:

1. Añadir pyannote.audio>=3.3.0 a pyproject.toml

2. Implementar src/transcribot/diarizer.py:
   - Dataclass: SpeakerSegment(start: float, end: float, speaker: str)
   - Clase: Diarizer
     - __init__(self, hf_token: str, device: str = "auto")
       - Cargar pipeline: Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=hf_token)
       - Si device es "auto", usar CUDA si disponible, sino CPU
       - Enviar pipeline al device: pipeline.to(torch.device(device))
     - diarize(self, wav_path: Path) -> list[SpeakerSegment]
       - Ejecutar pipeline(wav_path)
       - Iterar sobre el resultado (objeto Annotation de pyannote)
       - Para cada turn (track) extraer start, end, speaker label
       - Los labels de pyannote son tipo "SPEAKER_00", "SPEAKER_01", etc.
       - Renombrar a "Locutor 1", "Locutor 2", etc. (más legible)
       - Retornar lista ordenada por start
       - Logging: número de locutores detectados, duración total de habla por locutor

3. Manejar errores específicos:
   - Si HF_TOKEN no está configurado: error descriptivo con instrucciones
   - Si el modelo no está aceptado en HuggingFace: error con URL del modelo
   - Si VRAM insuficiente: fallback a CPU con warning

4. Añadir a config.py:
   - hf_token también se puede leer de variable de entorno HF_TOKEN si no está en YAML
   - Prioridad: CLI arg > YAML > env var

5. Tests tests/test_diarizer.py:
   - @pytest.mark.slow (requiere modelo descargado + HF token)
   - Test de contrato: diarize retorna list[SpeakerSegment]
   - Test unitario sin modelo: verificar que Diarizer lanza error claro sin HF_TOKEN

CONVENCIONES:
- Ejecución secuencial (después de transcripción en el pipeline final)
- Labels de locutor legibles para humanos
- Logging detallado de locutores detectados

ARCHIVOS A CREAR/MODIFICAR:
- pyproject.toml — añadir pyannote.audio
- src/transcribot/diarizer.py — COMPLETO
- src/transcribot/config.py — añadir lectura de HF_TOKEN desde env
- tests/test_diarizer.py — nuevo

NO MODIFICAR:
- chunker.py, transcriber.py (W-002)
- aligner.py, formatter.py (W-004)
- cli.py (W-005)

RESULTADO: Diarizer identifica locutores con timestamps en un WAV
```

---

## Criterios de Validación

- [ ]  pip install -e . instala [pyannote.audio](http://pyannote.audio)
- [ ]  python -c "from [pyannote.audio](http://pyannote.audio) import Pipeline; print('OK')" funciona
- [ ]  Con HF_TOKEN configurado: Diarizer().diarize(test.wav) retorna SpeakerSegments
- [ ]  Sin HF_TOKEN: error descriptivo con instrucciones
- [ ]  pytest tests/test_[diarizer.py](http://diarizer.py) -v -k "not slow" pasa