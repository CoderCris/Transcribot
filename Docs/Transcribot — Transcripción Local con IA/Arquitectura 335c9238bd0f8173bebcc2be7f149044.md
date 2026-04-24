# Arquitectura

## Diagrama de Contexto (C4 - Nivel 1)

```mermaid
graph TB
    User["Usuario / Operador"] -->|"CLI: transcribot input.mp4"| Transcribot["Transcribot\nCLI local"]
    Transcribot -->|"Lee archivos"| FS[("Sistema de archivos\nAudios/Videos")]
    Transcribot -->|"Escribe"| Output[("Archivo de texto\nTranscripción con locutores")]
    Transcribot -.->|"Descarga modelos\n(primera ejecución)"| HF["HuggingFace Hub"]
```

## Diagrama de Contenedores (C4 - Nivel 2)

```mermaid
graph TB
    subgraph Transcribot["Transcribot CLI"]
        CLI["cli.py\nPunto de entrada Click"] --> Pipeline["pipeline.py\nOrquestador"]
        Pipeline --> Audio["audio.py\nExtracción ffmpeg"]
        Pipeline --> Chunker["chunker.py\nVAD + segmentación"]
        Pipeline --> Transcriber["transcriber.py\nfaster-whisper"]
        Pipeline --> Diarizer["diarizer.py\npyannote.audio"]
        Pipeline --> Aligner["aligner.py\nMerge timestamps"]
        Pipeline --> Formatter["formatter.py\nOutput texto"]
        Config["config.py\nYAML + CLI overrides"] --> Pipeline
    end
    Audio -->|"WAV 16kHz mono"| Chunker
    Chunker -->|"Segmentos con timestamps"| Transcriber
    Audio -->|"WAV completo"| Diarizer
    Transcriber -->|"Segmentos transcritos"| Aligner
    Diarizer -->|"Segmentos de locutor"| Aligner
    Aligner -->|"Texto con locutores"| Formatter
```

## Diagrama de Secuencia — Flujo Principal

```mermaid
sequenceDiagram
    participant U as Usuario
    participant CLI as cli.py
    participant P as pipeline.py
    participant A as audio.py
    participant C as chunker.py
    participant T as transcriber.py
    participant D as diarizer.py
    participant AL as aligner.py
    participant F as formatter.py

    U->>CLI: transcribot transcribe input.mp4 -o output.txt
    CLI->>P: run(input, output, config)
    P->>A: extract_audio(input) → wav_path
    A-->>P: /tmp/audio_16khz.wav
    
    par Transcripción
        P->>C: segment_by_vad(wav_path) → chunks[]
        C-->>P: chunks con timestamps
        loop Por cada chunk
            P->>T: transcribe(chunk) → segments[]
        end
        T-->>P: transcription_segments[]
    and Diarización
        Note over P,D: Secuencial en práctica\n(para economizar VRAM)
    end
    
    P->>D: diarize(wav_path) → speaker_segments[]
    D-->>P: speaker_segments[]
    P->>AL: align(transcription, speakers) → aligned[]
    AL-->>P: aligned_segments[]
    P->>F: format_output(aligned) → text
    F-->>P: formatted_text
    P-->>CLI: write(output.txt)
    CLI-->>U: Transcripción completada → output.txt
```

## Estructura de Carpetas

```
transcribot/
├── pyproject.toml              # Metadata, dependencias, entry points
├── README.md                   # Setup, uso, requisitos de HF token
├── config/
│   └── default.yaml            # Defaults: modelo, chunk_size, idioma, compute_type
├── src/
│   └── transcribot/
│       ├── __init__.py         # Versión
│       ├── cli.py              # Comandos Click (transcribe, info)
│       ├── config.py           # Carga YAML + merge con CLI args
│       ├── pipeline.py         # Orquestador principal del flujo
│       ├── audio.py            # Extracción de audio con ffmpeg/pydub
│       ├── chunker.py          # VAD segmentation + agrupación en chunks
│       ├── transcriber.py      # Wrapper de faster-whisper
│       ├── diarizer.py         # Wrapper de pyannote.audio
│       ├── aligner.py          # Merge transcripción + diarización por timestamps
│       ├── formatter.py        # Genera output texto con etiquetas de locutor
│       ├── hardware.py         # Detección GPU/CPU, selección de modelo
│       └── logger.py           # Configuración de logging
└── tests/
    ├── conftest.py             # Fixtures (audio de prueba sintético)
    ├── test_audio.py           # Tests de extracción
    ├── test_chunker.py         # Tests de segmentación VAD
    ├── test_aligner.py         # Tests de alineación
    └── test_formatter.py       # Tests de formato de salida
```

## Diagrama de Flujo de Errores

```mermaid
flowchart TD
    A[Inicio] --> B{Archivo existe?}
    B -->|No| E1["ERROR: Archivo no encontrado\nExit code 1"]
    B -->|Sí| C{ffmpeg disponible?}
    C -->|No| E2["ERROR: ffmpeg no instalado\nExit code 2"]
    C -->|Sí| D[Extraer audio]
    D --> F{Audio válido?}
    F -->|No| E3["ERROR: No se pudo extraer audio\nExit code 3"]
    F -->|Sí| G{GPU disponible?}
    G -->|Sí| H["Modelo large-v3 + CUDA"]
    G -->|No| I["Modelo medium + CPU\n(warning al usuario)"]
    H --> J[Transcribir chunks]
    I --> J
    J --> K{HF token válido?}
    K -->|No| E4["ERROR: Token HuggingFace requerido\npara diarización. Exit code 4"]
    K -->|Sí| L[Diarizar]
    L --> M[Alinear + formatear]
    M --> N["Output → archivo.txt\nExit code 0"]
```