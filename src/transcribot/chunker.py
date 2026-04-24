"""Segmentación de audio por VAD (Silero vía faster-whisper)."""

from __future__ import annotations

import logging
import tempfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from faster_whisper.vad import VadOptions, get_speech_timestamps
from pydub import AudioSegment

logger = logging.getLogger(__name__)

VAD_SAMPLING_RATE = 16_000


@dataclass
class AudioChunk:
    """Fragmento de audio con timestamps globales respecto al WAV original."""

    start: float
    end: float
    audio_path: Path


def _audio_segment_to_float32(audio: AudioSegment) -> np.ndarray:
    """Convierte un AudioSegment (mono, 16 kHz) a numpy float32 en [-1, 1]."""
    samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
    max_val = float(1 << (8 * audio.sample_width - 1))
    return samples / max_val


def segment_by_vad(wav_path: Path, chunk_duration: int = 600) -> list[AudioChunk]:
    """Detecta regiones de habla y las agrupa en chunks cortados en silencios.

    Args:
        wav_path: Ruta a un WAV (se normaliza a 16 kHz mono si no lo está).
        chunk_duration: Duración máxima deseada por chunk, en segundos.

    Returns:
        Lista de AudioChunk. Si Silero no detecta habla, se devuelve un único chunk
        que cubre todo el audio (fallback) para no bloquear el pipeline.

    Raises:
        FileNotFoundError: Si `wav_path` no existe.
    """
    wav_path = Path(wav_path)
    if not wav_path.exists():
        raise FileNotFoundError(f"WAV no encontrado: {wav_path}")

    audio = AudioSegment.from_file(wav_path)
    if audio.frame_rate != VAD_SAMPLING_RATE:
        audio = audio.set_frame_rate(VAD_SAMPLING_RATE)
    if audio.channels != 1:
        audio = audio.set_channels(1)

    samples = _audio_segment_to_float32(audio)

    opts = VadOptions(max_speech_duration_s=float(chunk_duration))
    timestamps = get_speech_timestamps(
        samples, vad_options=opts, sampling_rate=VAD_SAMPLING_RATE
    )

    out_dir = Path(tempfile.mkdtemp(prefix="transcribot_chunks_"))

    if not timestamps:
        total_sec = len(audio) / 1000.0
        logger.warning(
            "VAD no detectó habla en %s (%.2fs); devolviendo audio completo como chunk.",
            wav_path,
            total_sec,
        )
        out_path = out_dir / f"{wav_path.stem}_chunk_0000.wav"
        audio.export(out_path, format="wav")
        return [AudioChunk(start=0.0, end=total_sec, audio_path=out_path)]

    groups: list[tuple[float, float]] = []
    group_start: float | None = None
    group_end: float | None = None

    for ts in timestamps:
        start_s = ts["start"] / VAD_SAMPLING_RATE
        end_s = ts["end"] / VAD_SAMPLING_RATE
        if group_start is None:
            group_start, group_end = start_s, end_s
            continue
        if (end_s - group_start) > chunk_duration:
            groups.append((group_start, group_end))  # type: ignore[arg-type]
            group_start, group_end = start_s, end_s
        else:
            group_end = end_s

    if group_start is not None:
        groups.append((group_start, group_end))  # type: ignore[arg-type]

    chunks: list[AudioChunk] = []
    for i, (g_start, g_end) in enumerate(groups):
        seg = audio[int(g_start * 1000) : int(g_end * 1000)]
        out_path = out_dir / f"{wav_path.stem}_chunk_{i:04d}.wav"
        seg.export(out_path, format="wav")
        chunks.append(AudioChunk(start=g_start, end=g_end, audio_path=out_path))

    logger.info(
        "VAD produjo %d chunks (chunk_duration=%ds) a partir de %s",
        len(chunks),
        chunk_duration,
        wav_path,
    )
    return chunks
