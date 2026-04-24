# Transcribot — Transcripción Local con IA

## Visión del Proyecto

Herramienta CLI local para transcribir audios y vídeos de reuniones (30 min – 2 h) en español, con **diarización de locutores** y salida en texto plano. Diseñada para funcionar con GPU NVIDIA (RTX 4060) o en modo CPU-only como fallback.

El output se usará como input para procesamiento posterior por otra IA (síntesis de información de negocio, procesos, etc.).

## Requisitos clave

- Transcripción local con `faster-whisper` (CTranslate2) — no cloud, no API keys
- Diarización con `pyannote.audio` — identificar quién habla
- Chunking inteligente por VAD para mantener calidad en audios largos
- Soporte de formatos comunes: mp3, mp4, wav, m4a, ogg, mkv, webm, flac
- Auto-detección GPU/CPU: modelo `large-v3` con CUDA, `medium` en CPU
- Interfaz CLI minimalista: input → output transparente
- Español como idioma fijo (optimizable)

---

## Stack Técnico

| Capa | Tecnología | Versión | Justificación |
| --- | --- | --- | --- |
| Lenguaje | Python | 3.11+ | Ecosistema ML maduro, bindings nativos para Whisper y pyannote |
| Transcripción | faster-whisper | 1.1.x | 4x más rápido que openai-whisper, menor consumo de VRAM, VAD integrado (Silero) |
| Diarización | [pyannote.audio](http://pyannote.audio) | 3.3.x | Estado del arte en speaker diarization, pipeline pre-entrenado |
| Audio I/O | ffmpeg + pydub | system / 0.25.x | Decodificación universal de formatos, normalización a WAV 16kHz mono |
| CLI | Click | 8.x | Ligero, decoradores declarativos, buen soporte de progreso |
| Configuración | PyYAML + dataclasses | — | Config externalizada, defaults sensatos, override por CLI |
| Packaging | pyproject.toml + uv | — | Estándar moderno, resolución rápida de dependencias |
| Testing | pytest | 8.x | Estándar de facto |

---

## Panel de Expertos — Síntesis

### Experto 1 — Ingeniera de Speech/NLP

> El riesgo #1 en transcripciones largas es el *context drift*: Whisper procesa en ventanas de 30s y arrastra contexto previo que degrada la precisión. La mitigación correcta es **segmentar por VAD en chunks de ~5–10 min con reset de contexto**, no confiar en el procesamiento monolítico. Además, para español, el modelo `large-v3` es significativamente mejor que `medium` — la degradación en CPU es un trade-off real que hay que documentar. Recomiendo exponer la opción de modelo y chunk size como configuración.
> 

### Experto 2 — Arquitecto de Sistemas CLI

> La herramienta debe ser *fire-and-forget*: un comando, un output, sin interactividad. El pipeline debe manejar errores de forma silenciosa pero trazable (logs a archivo). El diseño debe ser pipeline lineal, no over-engineered — no hay necesidad de hexagonal ni plugins en una CLI personal. La barra de progreso es esencial porque 2h de audio toma tiempo real. Y ojo: pyannote requiere aceptar licencia en HuggingFace y un token — esto debe documentarse claramente en el setup.
> 

### Experto 3 — ML Ops / Edge Deployment

> La dualidad GPU/CPU necesita una estrategia de fallback explícita: detectar CUDA al inicio, seleccionar modelo y `compute_type` automáticamente. En CPU sin AVX2 (máquinas viejas), CTranslate2 no funciona — hay que validar esto en el arranque. La diarización con pyannote consume ~2-3 GB VRAM adicionales; si la GPU no tiene suficiente, se debe ejecutar en CPU independientemente de la transcripción. Recomiendo ejecutar transcripción y diarización secuencialmente para evitar picos de VRAM.
> 

### Síntesis de consenso

**Acuerdo**: Segmentación VAD con reset de contexto es obligatoria. Pipeline secuencial (no paralelo) para economizar VRAM. Click CLI sin interactividad. Logging a archivo.

**Tensión**: Modelo grande (calidad) vs. modelo medio (portabilidad CPU). Resolución: auto-selección por hardware con override manual.

**Recomendación final**: Pipeline secuencial `ffmpeg → VAD chunking → faster-whisper → pyannote → alignment → output`. Auto-detección de hardware con defaults conservadores. Chunk size configurable (default 600s). Ejecución secuencial de transcripción y diarización para minimizar VRAM.

[Arquitectura](Transcribot%20%E2%80%94%20Transcripci%C3%B3n%20Local%20con%20IA/Arquitectura%20335c9238bd0f8173bebcc2be7f149044.md)

[ADRs — Decisiones de Arquitectura](Transcribot%20%E2%80%94%20Transcripci%C3%B3n%20Local%20con%20IA/ADRs%20%E2%80%94%20Decisiones%20de%20Arquitectura%20335c9238bd0f8109a29de7c6d2445f5b.md)

[Plan de Oleadas](Transcribot%20%E2%80%94%20Transcripci%C3%B3n%20Local%20con%20IA/Plan%20de%20Oleadas%20335c9238bd0f814eb7d8c362dff860f7.md)