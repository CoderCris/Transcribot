"""Fixtures compartidas para la suite de tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydub import AudioSegment


@pytest.fixture()
def silent_wav(tmp_path: Path) -> Path:
    """Genera un WAV de 1 segundo de silencio (44.1 kHz estéreo) para pruebas."""
    wav_path = tmp_path / "silence.wav"
    AudioSegment.silent(duration=1000, frame_rate=44_100).set_channels(2).export(
        wav_path, format="wav"
    )
    return wav_path
