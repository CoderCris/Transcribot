# Plan de Oleadas

## Estrategia de desarrollo

El proyecto se divide en **5 oleadas** siguiendo un enfoque **bottom-up por capas**, luego integración vertical:

| ID | Nombre | Dependencias | Complejidad | Entregable |
| --- | --- | --- | --- | --- |
| W-001 | Scaffolding + Extracción de Audio | — | Baja | Proyecto inicializado, ffmpeg extrae audio de cualquier formato |
| W-002 | Motor de Transcripción | W-001 | Media | faster-whisper transcribe chunks con VAD, auto-detección GPU/CPU |
| W-003 | Diarización de Locutores | W-001 | Media | pyannote identifica locutores con timestamps |
| W-004 | Alineación + Output | W-002, W-003 | Media | Merge transcripción+diarización, output formateado |
| W-005 | CLI, Config y Hardening | W-004 | Baja | CLI completa, config YAML, logging, README, tests |

## Nota sobre HuggingFace

Antes de ejecutar W-003, el usuario debe:

1. Crear cuenta en [huggingface.co](http://huggingface.co)
2. Aceptar las condiciones de `pyannote/speaker-diarization-3.1` y `pyannote/segmentation-3.0`
3. Crear un token de acceso (read) y guardarlo como variable de entorno `HF_TOKEN`

[W-001 — Scaffolding + Extracción de Audio](Plan%20de%20Oleadas/W-001%20%E2%80%94%20Scaffolding%20+%20Extracci%C3%B3n%20de%20Audio%20335c9238bd0f817fa049f888ba014e39.md)

[W-002 — Motor de Transcripción](Plan%20de%20Oleadas/W-002%20%E2%80%94%20Motor%20de%20Transcripci%C3%B3n%20335c9238bd0f81848dbbd9dcedcd886c.md)

[W-003 — Diarización de Locutores](Plan%20de%20Oleadas/W-003%20%E2%80%94%20Diarizaci%C3%B3n%20de%20Locutores%20335c9238bd0f81f987f6f73ba6a2dd05.md)

[W-004 — Alineación + Output](Plan%20de%20Oleadas/W-004%20%E2%80%94%20Alineaci%C3%B3n%20+%20Output%20335c9238bd0f8194b34dcadf467da1d2.md)

[W-005 — CLI, Config y Hardening](Plan%20de%20Oleadas/W-005%20%E2%80%94%20CLI,%20Config%20y%20Hardening%20335c9238bd0f81a390e2cbee5f2622a3.md)