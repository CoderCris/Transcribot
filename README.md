# Transcribot

CLI local para transcripción de audio/video con diarización (Whisper + pyannote).

## Requisitos

- Python 3.11+
- `ffmpeg` instalado y disponible en el `PATH`

### Instalar ffmpeg

**Windows** (elige una opción):

```powershell
winget install Gyan.FFmpeg     # recomendado
choco install ffmpeg           # alternativa con Chocolatey
scoop install ffmpeg           # alternativa con Scoop
```

Tras instalar, abre una terminal nueva y verifica con `ffmpeg -version`.

**Linux (Debian/Ubuntu):**

```bash
sudo apt install ffmpeg
```

**macOS:**

```bash
brew install ffmpeg
```

## Instalación

```bash
pip install -e .
```

## Uso básico

```bash
transcribot info                          # hardware detectado y config activa
transcribot transcribe input.mp4 -o output.txt
```

> **Nota:** proyecto en desarrollo — oleadas restantes por implementar (transcripción,
> diarización, alineación y formateo se añaden en W-002…W-005).
