# W-001 — Scaffolding + Extracción de Audio

## Ficha de Oleada

- **ID**: W-001
- **Dependencias**: Ninguna
- **Entregable**: Proyecto Python inicializado con estructura de carpetas, dependencias base, y módulo `audio.py` que extrae audio WAV 16kHz mono de cualquier formato soportado.
- **Complejidad**: Baja

---

## Prompt para Claude Code

```
---
OLEADA: W-001 — Scaffolding + Extracción de Audio
DEPENDENCIAS: Ninguna
CONTEXTO DEL PROYECTO: CLI local para transcripción de audio/video con diarización. Python, faster-whisper, pyannote.audio. Uso personal en Windows.
STACK RELEVANTE: Python 3.11+, pyproject.toml con uv, ffmpeg, pydub, Click, pytest
---

INSTRUCCIONES:

1. Crear la estructura de carpetas del proyecto:
   transcribot/
   ├── pyproject.toml
   ├── README.md
   ├── config/
   │   └── default.yaml
   ├── src/
   │   └── transcribot/
   │       ├── __init__.py
   │       ├── cli.py
   │       ├── config.py
   │       ├── pipeline.py
   │       ├── audio.py
   │       ├── chunker.py
   │       ├── transcriber.py
   │       ├── diarizer.py
   │       ├── aligner.py
   │       ├── formatter.py
   │       ├── hardware.py
   │       └── logger.py
   └── tests/
       ├── conftest.py
       └── test_audio.py

2. Configurar pyproject.toml:
   - name: transcribot
   - version: 0.1.0
   - requires-python: ">=3.11"
   - Dependencias SOLO de esta oleada: pydub, click, pyyaml, pytest (dev)
   - NO incluir aún faster-whisper ni pyannote (se añaden en sus oleadas)
   - Entry point: transcribot = "transcribot.cli:main"
   - Build backend: hatchling

3. Implementar src/transcribot/audio.py:
   - Función: extract_audio(input_path: Path, output_dir: Path | None = None) -> Path
   - Usa pydub (que requiere ffmpeg) para:
     a) Cargar cualquier formato soportado por ffmpeg
     b) Convertir a WAV 16kHz mono (16-bit PCM)
     c) Guardar en output_dir (o directorio temporal si None)
   - Validar que el archivo de entrada existe y tiene extensión reconocida
   - Extensiones soportadas: .mp3, .mp4, .wav, .m4a, .ogg, .mkv, .webm, .flac, .wma, .aac
   - Lanzar excepciones claras: FileNotFoundError, ValueError para formato no soportado, RuntimeError si ffmpeg falla
   - Logging: log el path de entrada, duración detectada, y path de salida

4. Implementar src/transcribot/hardware.py:
   - Función: detect_device() -> dict con keys:
     - "device": "cuda" | "cpu"
     - "compute_type": "float16" | "int8"
     - "model_size": "large-v3" | "medium"
     - "gpu_name": str | None
     - "vram_gb": float | None
   - Detectar CUDA vía torch.cuda.is_available() (try/except si torch no instalado aún)
   - Si no hay torch, intentar detectar vía ctranslate2 (también try/except)
   - Fallback final: asumir CPU
   - Logging: log la configuración detectada

5. Implementar src/transcribot/config.py:
   - Dataclass TranscribotConfig con campos:
     - model_size: str = "auto" (auto = usar detección de hardware)
     - language: str = "es"
     - chunk_duration: int = 600 (segundos)
     - compute_type: str = "auto"
     - device: str = "auto"
     - hf_token: str | None = None
     - output_format: str = "txt"
     - log_level: str = "INFO"
     - log_file: str | None = None
   - Función: load_config(config_path: Path | None = None, **overrides) -> TranscribotConfig
     - Carga config/default.yaml como base
     - Aplica overrides de argumentos CLI
     - Resuelve "auto" usando hardware.detect_device()

6. Crear config/default.yaml:
   model_size: auto
   language: es
   chunk_duration: 600
   compute_type: auto
   device: auto
   hf_token: null
   output_format: txt
   log_level: INFO
   log_file: null

7. Implementar src/transcribot/logger.py:
   - Función: setup_logging(level: str, log_file: str | None) -> None
   - Configurar logging estándar de Python
   - Formato: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
   - Si log_file: añadir FileHandler además de StreamHandler
   - StreamHandler: solo WARNING+ para no ensuciar stdout
   - FileHandler: nivel configurable (default INFO)

8. Implementar src/transcribot/cli.py (esqueleto):
   - Grupo principal Click: @click.group()
   - Comando `transcribe`: recibe input_path (argumento), --output/-o (opción), --config/-c (opción)
   - Comando `info`: muestra hardware detectado, config activa, versión
   - En esta oleada, `transcribe` solo ejecuta extract_audio y muestra el resultado
   - `info` muestra el output de detect_device() formateado

9. Implementar stubs vacíos (solo docstring + raise NotImplementedError) para:
   - pipeline.py: run()
   - chunker.py: segment_by_vad()
   - transcriber.py: transcribe()
   - diarizer.py: diarize()
   - aligner.py: align()
   - formatter.py: format_output()

10. Escribir tests/test_audio.py:
    - Test que genera un WAV sintético (1s de silencio con pydub) y verifica extract_audio:
      - Output es WAV
      - Sample rate es 16000
      - Canales es 1
    - Test que lanza FileNotFoundError para archivo inexistente
    - Test que lanza ValueError para extensión no soportada (.xyz)

11. Crear README.md básico:
    - Nombre y descripción de una línea
    - Requisitos: Python 3.11+, ffmpeg instalado en PATH
    - Instalación: pip install -e .
    - Uso básico: transcribot transcribe input.mp4 -o output.txt
    - Nota: "En desarrollo — oleadas restantes por implementar"

CONVENCIONES:
- Tipado estricto con type hints en todas las funciones
- Docstrings en formato Google style
- Logging con logger = logging.getLogger(__name__) en cada módulo
- Excepciones con mensajes descriptivos para el usuario
- Imports absolutos: from transcribot.audio import extract_audio

ARCHIVOS A CREAR:
- pyproject.toml — metadata y dependencias
- README.md — documentación básica
- config/default.yaml — configuración por defecto
- src/transcribot/__init__.py — __version__ = "0.1.0"
- src/transcribot/cli.py — entry point Click
- src/transcribot/config.py — carga de configuración
- src/transcribot/audio.py — extracción de audio (IMPLEMENTACIÓN COMPLETA)
- src/transcribot/hardware.py — detección de hardware (IMPLEMENTACIÓN COMPLETA)
- src/transcribot/logger.py — setup de logging (IMPLEMENTACIÓN COMPLETA)
- src/transcribot/pipeline.py — stub
- src/transcribot/chunker.py — stub
- src/transcribot/transcriber.py — stub
- src/transcribot/diarizer.py — stub
- src/transcribot/aligner.py — stub
- src/transcribot/formatter.py — stub
- tests/conftest.py — fixtures
- tests/test_audio.py — tests de extracción

NO MODIFICAR: N/A (proyecto nuevo)

RESULTADO ESPERADO:
- `pip install -e .` completa sin errores
- `transcribot info` muestra la detección de hardware
- `transcribot transcribe test.mp3 -o out.txt` extrae el audio (transcripción aún no implementada)
- `pytest tests/test_audio.py` pasa todos los tests
```

---

## Criterios de Validación

- [ ]  `pip install -e .` completa sin errores
- [ ]  `transcribot --help` muestra los comandos disponibles
- [ ]  `transcribot info` muestra device (cuda/cpu), modelo seleccionado, y versión
- [ ]  `transcribot transcribe <cualquier_audio> -o test.txt` genera un WAV temporal 16kHz mono (verificar con `ffprobe`)
- [ ]  `pytest tests/test_audio.py -v` — todos los tests pasan
- [ ]  Existe `config/default.yaml` con los valores por defecto
- [ ]  Los stubs de módulos futuros existen y lanzan `NotImplementedError`