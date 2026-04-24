"""Tests para transcribot.audio.extract_audio."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydub import AudioSegment

from transcribot.audio import (
    TARGET_CHANNELS,
    TARGET_SAMPLE_RATE,
    extract_audio,
)


def test_extract_audio_returns_wav_16k_mono(silent_wav: Path, tmp_path: Path) -> None:
    out_dir = tmp_path / "out"
    result = extract_audio(silent_wav, output_dir=out_dir)

    assert result.exists()
    assert result.suffix == ".wav"

    produced = AudioSegment.from_file(result)
    assert produced.frame_rate == TARGET_SAMPLE_RATE
    assert produced.channels == TARGET_CHANNELS


def test_extract_audio_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        extract_audio(tmp_path / "does_not_exist.mp3")


def test_extract_audio_unsupported_extension_raises(tmp_path: Path) -> None:
    bogus = tmp_path / "file.xyz"
    bogus.write_bytes(b"not audio")
    with pytest.raises(ValueError):
        extract_audio(bogus)
