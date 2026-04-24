# ADRs — Decisiones de Arquitectura

## ADR-001: faster-whisper sobre openai-whisper

**Contexto**: Se necesita un motor de transcripción local que soporte GPU NVIDIA y fallback a CPU, con buen rendimiento en audios largos.

**Decisión**: Usar `faster-whisper` (backend CTranslate2).

**Alternativas descartadas**:

- `openai-whisper`: 4x más lento, mayor consumo VRAM (~2x), misma precisión.
- `whisper.cpp`: Rápido pero integración con pyannote compleja (C++ vs Python).
- `whisperX`: Añade alineación forzada (wav2vec2) innecesaria para texto plano. Más dependencias.

**Consecuencias**: Dependencia de CTranslate2. Requiere AVX2 en CPU (hardware post-2013). El API de faster-whisper es ligeramente distinto al original.

---

## ADR-002: Segmentación VAD con reset de contexto

**Contexto**: Whisper pierde precisión en audios >30 min por *context drift* — el contexto de decodificación previo contamina segmentos posteriores.

**Decisión**: Segmentar el audio por VAD (Silero, integrado en faster-whisper) en chunks de ~10 min (configurable), agrupando segmentos de habla adyacentes. Cada chunk se transcribe independientemente (contexto limpio).

**Alternativas descartadas**:

- Corte fijo por tiempo (5/10 min): Puede cortar mid-sentence.
- Procesamiento monolítico: Calidad degradada en archivos largos.

**Consecuencias**: Posible pérdida de contexto inter-chunk (una frase que cruza el límite). Mitigado al cortar en silencios detectados por VAD.

---

## ADR-003: [pyannote.audio](http://pyannote.audio) para diarización

**Contexto**: Se requiere identificar locutores distintos sin conocer previamente el número de participantes.

**Decisión**: Usar `pyannote/speaker-diarization-3.1` pipeline.

**Alternativas descartadas**:

- Diarización basada en energía/silencios: Muy imprecisa.
- NeMo Speaker Diarization: Bueno, pero ecosistema más pesado (NVIDIA NeMo framework completo).
- Clustering manual de embeddings: Requiere más código y tuning.

**Consecuencias**: Requiere token de HuggingFace y aceptar la licencia del modelo (gratuito pero requiere registro). Añade ~2-3 GB VRAM. Se ejecuta secuencialmente tras la transcripción para no competir por VRAM.

---

## ADR-004: Ejecución secuencial (no paralela) del pipeline

**Contexto**: Transcripción y diarización son ambas GPU-intensivas.

**Decisión**: Pipeline secuencial: primero transcripción, luego diarización. No paralelismo.

**Alternativas descartadas**:

- Ejecución paralela: Pico de VRAM ~9-10 GB, la RTX 4060 tiene 8 GB. Imposible.
- Transcripción en GPU + diarización en CPU: Posible pero añade complejidad y la diarización en CPU es muy lenta.

**Consecuencias**: Tiempo total = transcripción + diarización (no overlap). Aceptable para uso personal/batch.

---

## ADR-005: Auto-detección de hardware con fallback

**Contexto**: La herramienta debe funcionar en máquinas con y sin GPU NVIDIA.

**Decisión**: Al arrancar, detectar CUDA. Si disponible: `large-v3` + `float16`. Si no: `medium` + `int8` en CPU. Warning al usuario sobre la diferencia de calidad/velocidad.

**Alternativas descartadas**:

- Solo GPU: Excluye el caso de uso secundario.
- Mismo modelo en ambos: `large-v3` en CPU es inviablemente lento (~20x realtime).

**Consecuencias**: Output no será idéntico entre GPU y CPU (modelo distinto). Documentado como limitación conocida.