"""Fixtures y configuración compartidas para la suite de tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydub import AudioSegment


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="Ejecuta también los tests marcados como slow (descargan modelos).",
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    if config.getoption("--run-slow"):
        return
    skip_slow = pytest.mark.skip(reason="usa --run-slow para ejecutarlo")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


@pytest.fixture()
def silent_wav(tmp_path: Path) -> Path:
    """WAV de 1 s de silencio (44.1 kHz estéreo) para probar `extract_audio`."""
    wav_path = tmp_path / "silence.wav"
    AudioSegment.silent(duration=1000, frame_rate=44_100).set_channels(2).export(
        wav_path, format="wav"
    )
    return wav_path


@pytest.fixture()
def silent_wav_16k_mono(tmp_path: Path) -> Path:
    """WAV de 3 s de silencio, 16 kHz mono — formato que espera el chunker."""
    wav_path = tmp_path / "silence_16k.wav"
    AudioSegment.silent(duration=3000, frame_rate=16_000).set_channels(1).export(
        wav_path, format="wav"
    )
    return wav_path
