"""Tests para transcribot.transcriber.Transcriber.

Marcados como `slow` porque descargan y cargan un modelo Whisper. Ejecutar con:
    pytest tests/test_transcriber.py --run-slow -v
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pydub import AudioSegment

from transcribot.chunker import AudioChunk
from transcribot.transcriber import Transcriber, TranscriptionSegment


@pytest.mark.slow
def test_transcriber_tiny_on_silent_wav(tmp_path: Path) -> None:
    """El modelo tiny debe manejar un WAV silencioso sin romper el pipeline."""
    wav_path = tmp_path / "silence.wav"
    AudioSegment.silent(duration=1000, frame_rate=16_000).set_channels(1).export(
        wav_path, format="wav"
    )
    chunk = AudioChunk(start=0.0, end=1.0, audio_path=wav_path)

    transcriber = Transcriber(
        model_size="tiny", device="cpu", compute_type="int8", language="es"
    )
    segments = transcriber.transcribe_chunk(chunk)

    assert isinstance(segments, list)
    assert all(isinstance(s, TranscriptionSegment) for s in segments)
    for s in segments:
        assert s.end >= s.start
        assert s.start >= chunk.start


@pytest.mark.slow
def test_transcriber_progress_callback(tmp_path: Path) -> None:
    wav_path = tmp_path / "silence.wav"
    AudioSegment.silent(duration=500, frame_rate=16_000).set_channels(1).export(
        wav_path, format="wav"
    )
    chunks = [
        AudioChunk(start=0.0, end=0.5, audio_path=wav_path),
        AudioChunk(start=0.5, end=1.0, audio_path=wav_path),
    ]

    transcriber = Transcriber(
        model_size="tiny", device="cpu", compute_type="int8", language="es"
    )
    calls: list[tuple[int, int]] = []
    transcriber.transcribe_all(chunks, progress_callback=lambda d, t: calls.append((d, t)))

    assert calls == [(1, 2), (2, 2)]
