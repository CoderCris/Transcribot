"""Tests para transcribot.chunker.segment_by_vad."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydub import AudioSegment

from transcribot.chunker import AudioChunk, segment_by_vad


def test_segment_by_vad_returns_list_of_audiochunks(silent_wav_16k_mono: Path) -> None:
    chunks = segment_by_vad(silent_wav_16k_mono, chunk_duration=600)

    assert isinstance(chunks, list)
    assert all(isinstance(c, AudioChunk) for c in chunks)
    for c in chunks:
        assert c.audio_path.exists()
        assert c.audio_path.suffix == ".wav"
        assert c.end >= c.start


def test_segment_by_vad_silence_fallback(silent_wav_16k_mono: Path) -> None:
    """Sin habla, el chunker devuelve un único chunk cubriendo todo el audio."""
    chunks = segment_by_vad(silent_wav_16k_mono, chunk_duration=600)

    assert len(chunks) == 1
    total_ms = len(AudioSegment.from_file(silent_wav_16k_mono))
    assert chunks[0].start == 0.0
    assert chunks[0].end == pytest.approx(total_ms / 1000.0, abs=0.05)


def test_segment_by_vad_chunks_are_valid_wavs(silent_wav_16k_mono: Path) -> None:
    chunks = segment_by_vad(silent_wav_16k_mono, chunk_duration=600)

    for c in chunks:
        seg = AudioSegment.from_file(c.audio_path)
        assert seg.frame_rate == 16_000
        assert seg.channels == 1


def test_segment_by_vad_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        segment_by_vad(tmp_path / "nope.wav")
