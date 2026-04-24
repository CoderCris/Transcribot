# W-004 — Alineación + Output

## Ficha de Oleada

- **ID**: W-004
- **Dependencias**: W-002, W-003
- **Entregable**: [aligner.py](http://aligner.py) fusiona transcripción con diarización. [formatter.py](http://formatter.py) genera texto plano con etiquetas de locutor.
- **Complejidad**: Media

---

## Prompt para Claude Code

```
---
OLEADA: W-004 — Alineación + Output
DEPENDENCIAS: W-002 (transcriber), W-003 (diarizer)
CONTEXTO: Fusionar segmentos de transcripción (texto+timestamps) con segmentos de diarización (locutor+timestamps) para producir texto con identificación de hablante.
STACK: Python 3.11+, dataclasses existentes de oleadas previas
---

INSTRUCCIONES:

1. Implementar src/transcribot/aligner.py:
   - Dataclass: AlignedSegment(start: float, end: float, speaker: str, text: str)
   - Función: align(transcription: list[TranscriptionSegment], speakers: list[SpeakerSegment]) -> list[AlignedSegment]
   - Algoritmo de alineación por overlap:
     a) Para cada TranscriptionSegment, calcular qué SpeakerSegment tiene mayor overlap temporal
     b) Asignar el speaker de mayor overlap al segmento de transcripción
     c) Si no hay overlap con ningún speaker (silencio), asignar "Desconocido"
     d) Fórmula de overlap: max(0, min(t_end, s_end) - max(t_start, s_start))
   - Función: merge_consecutive(segments: list[AlignedSegment]) -> list[AlignedSegment]
     - Fusionar segmentos consecutivos del mismo locutor en uno solo
     - Concatenar textos con espacio
     - start = primer segmento, end = último segmento
   - Retornar merge_consecutive(aligned)

2. Implementar src/transcribot/formatter.py:
   - Función: format_as_text(segments: list[AlignedSegment], include_timestamps: bool = False) -> str
   - Formato SIN timestamps:
```

[Locutor 1]

Texto del locutor 1...

[Locutor 2]

Texto del locutor 2...

[Locutor 1]

Texto del locutor 1 de nuevo...

```
- Formato CON timestamps:
```

[00:00:15 - 00:01:23] [Locutor 1]

Texto del locutor 1...

[00:01:24 - 00:02:45] [Locutor 2]

Texto del locutor 2...

```
   - Función auxiliar: format_time(seconds: float) -> str que convierte 90.5 a "00:01:30"
   - Añadir header con metadata: fecha, archivo original, duración, número de locutores

3. Implementar src/transcribot/pipeline.py:
   - Función: run(input_path: Path, output_path: Path, config: TranscribotConfig, progress_callback=None) -> None
   - Orquestar el flujo completo:
     a) extract_audio(input_path) -> wav_path
     b) segment_by_vad(wav_path, config.chunk_duration) -> chunks
     c) Transcriber(config).transcribe_all(chunks) -> transcription
     d) Diarizer(config.hf_token, config.device).diarize(wav_path) -> speakers
     e) align(transcription, speakers) -> aligned
     f) format_as_text(aligned, include_timestamps=config tiene flag) -> text
     g) Escribir text a output_path
     h) Limpiar archivos temporales (WAV, chunks)
   - Timing: medir y logear tiempo de cada paso
   - Manejar excepciones y limpiar temporales en finally

4. Tests:
   - tests/test_aligner.py:
     - Test con segmentos sintéticos: 3 TranscriptionSegments + 2 SpeakerSegments con overlap conocido
     - Verificar asignación correcta de speakers
     - Test merge_consecutive: segmentos consecutivos del mismo speaker se fusionan
     - Test sin overlap: asigna "Desconocido"
   - tests/test_formatter.py:
     - Test format_as_text con y sin timestamps
     - Test format_time: 0->00:00:00, 90.5->00:01:30, 3661->01:01:01

ARCHIVOS A CREAR/MODIFICAR:
- src/transcribot/aligner.py — COMPLETO
- src/transcribot/formatter.py — COMPLETO
- src/transcribot/pipeline.py — COMPLETO
- tests/test_aligner.py — nuevo
- tests/test_formatter.py — nuevo

NO MODIFICAR:
- audio.py, chunker.py, transcriber.py, diarizer.py (oleadas previas)
- cli.py (W-005)

RESULTADO: pipeline.run() ejecuta el flujo completo y genera archivo de texto con locutores
```

---

## Criterios de Validación

- [ ]  pytest tests/test_[aligner.py](http://aligner.py) -v pasa
- [ ]  pytest tests/test_[formatter.py](http://formatter.py) -v pasa
- [ ]  Probar manualmente: from transcribot.pipeline import run; run("[test.mp](http://test.mp)4", "out.txt", config) genera output correcto
- [ ]  El output tiene formato [Locutor N] seguido de texto
- [ ]  Los temporales se limpian al terminar