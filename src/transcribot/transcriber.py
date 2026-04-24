"""Motor de transcripción basado en faster-whisper."""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterable
from dataclasses import dataclass

from faster_whisper import WhisperModel

from transcribot.chunker import AudioChunk

logger = logging.getLogger(__name__)


@dataclass
class TranscriptionSegment:
    """Segmento transcrito con timestamps globales (segundos)."""

    start: float
    end: float
    text: str


class Transcriber:
    """Envoltorio sobre WhisperModel que transcribe AudioChunk a TranscriptionSegment.

    El modelo se carga una sola vez en el constructor y se reutiliza para todos los
    chunks de una misma sesión, para evitar recargas costosas entre llamadas.
    """

    def __init__(
        self,
        model_size: str = "medium",
        device: str = "cpu",
        compute_type: str = "int8",
        language: str | None = "es",
    ) -> None:
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.language = language
        logger.info(
            "Cargando WhisperModel: size=%s device=%s compute_type=%s",
            model_size,
            device,
            compute_type,
        )
        self.model = WhisperModel(
            model_size, device=device, compute_type=compute_type
        )

    def transcribe_chunk(self, chunk: AudioChunk) -> list[TranscriptionSegment]:
        """Transcribe un único chunk y ajusta los timestamps al eje global.

        Args:
            chunk: Fragmento producido por `chunker.segment_by_vad`.

        Returns:
            Lista de TranscriptionSegment con start/end en segundos globales.
        """
        segments_iter, _info = self.model.transcribe(
            str(chunk.audio_path),
            language=self.language,
            vad_filter=False,
        )
        results = [
            TranscriptionSegment(
                start=chunk.start + seg.start,
                end=chunk.start + seg.end,
                text=seg.text.strip(),
            )
            for seg in segments_iter
        ]
        logger.debug(
            "Chunk %s transcrito: %d segmentos", chunk.audio_path.name, len(results)
        )
        return results

    def transcribe_all(
        self,
        chunks: Iterable[AudioChunk],
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> list[TranscriptionSegment]:
        """Transcribe una secuencia de chunks preservando el orden temporal.

        Args:
            chunks: Iterable de AudioChunk (típicamente la salida de `segment_by_vad`).
            progress_callback: Callback opcional `fn(done, total)` invocado tras cada
                chunk completado — útil para barras de progreso en el CLI.

        Returns:
            Lista aplanada de TranscriptionSegment ordenada por timestamp global.
        """
        chunks_list = list(chunks)
        total = len(chunks_list)
        all_segments: list[TranscriptionSegment] = []
        for idx, chunk in enumerate(chunks_list, start=1):
            all_segments.extend(self.transcribe_chunk(chunk))
            if progress_callback is not None:
                progress_callback(idx, total)
        logger.info(
            "Transcripción completa: %d segmentos en %d chunks",
            len(all_segments),
            total,
        )
        return all_segments
