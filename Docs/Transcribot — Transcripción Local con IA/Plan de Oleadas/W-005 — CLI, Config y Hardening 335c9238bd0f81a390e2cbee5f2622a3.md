# W-005 — CLI, Config y Hardening

## Ficha de Oleada

- **ID**: W-005
- **Dependencias**: W-004
- **Entregable**: CLI completa con barra de progreso, configuración robusta, manejo de errores, README final, tests de integración.
- **Complejidad**: Baja

---

## Prompt para Claude Code

```
---
OLEADA: W-005 — CLI, Config y Hardening
DEPENDENCIAS: W-004 (pipeline completo)
CONTEXTO: Finalizar la herramienta CLI. Todo el pipeline funciona. Falta la interfaz de usuario, robustez y documentación.
STACK: Python 3.11+, Click 8.x, PyYAML
---

INSTRUCCIONES:

1. Implementar src/transcribot/cli.py completo:
   - Grupo Click principal con --version
   - Comando `transcribe`:
     - Argumento: INPUT_PATH (click.Path, must_exist=True)
     - Opciones:
       --output / -o: ruta de salida (default: mismo nombre que input con .txt)
       --config / -c: ruta a YAML de config (default: config/default.yaml)
       --model: override de modelo (tiny/small/medium/large-v3)
       --device: override de device (auto/cuda/cpu)
       --chunk-duration: override de duración de chunk en segundos
       --timestamps / -t: incluir timestamps en output (flag)
       --log-file: ruta para log detallado
       --verbose / -v: nivel de log en consola (INFO en vez de WARNING)
     - Barra de progreso con click.progressbar:
       - Paso 1: "Extrayendo audio..."
       - Paso 2: "Segmentando por VAD..."
       - Paso 3: "Transcribiendo (chunk X/N)..."
       - Paso 4: "Identificando locutores..."
       - Paso 5: "Generando output..."
     - Al finalizar: imprimir resumen (duración audio, locutores, tiempo total, ruta output)
     - Manejar KeyboardInterrupt: limpiar temporales y salir
   - Comando `info`:
     - Mostrar versión, hardware detectado, config activa, check de requisitos
     - Verificar ffmpeg, modelo descargado, HF_TOKEN

2. Mejorar manejo de errores en pipeline.py:
   - Envolver cada paso en try/except con mensajes de usuario claros
   - Exit codes estandarizados:
     - 0: OK
     - 1: Archivo no encontrado
     - 2: ffmpeg no disponible
     - 3: Error de extracción de audio
     - 4: HF_TOKEN no configurado
     - 5: Error de modelo/VRAM
     - 99: Error inesperado
   - Siempre limpiar temporales en finally

3. Actualizar config.py:
   - Resolver ruta de default.yaml relativa al package (pkg_resources o importlib.resources)
   - Validar configuración: model_size debe ser uno de los permitidos, chunk_duration > 0, etc.

4. Actualizar README.md completo:
   - Descripción del proyecto
   - Requisitos: Python 3.11+, ffmpeg, GPU NVIDIA (opcional)
   - Instalación paso a paso (incluido HuggingFace token)
   - Uso: ejemplos de comandos comunes
   - Configuración: documentar cada parámetro del YAML
   - Limitaciones conocidas:
     - Modelo diferente en GPU vs CPU
     - Diarización no perfecta con muchos locutores simultáneos
     - Primera ejecución descarga modelos (~3 GB)
   - Troubleshooting: errores comunes y soluciones

5. Tests de integración tests/test_integration.py:
   - @pytest.mark.integration
   - Test del pipeline completo con audio sintético corto (5s)
   - Verificar que genera archivo de output con contenido
   - Test del CLI con subprocess: transcribot info retorna exit code 0
   - Test del CLI: transcribot transcribe con archivo inexistente retorna exit code 1

6. Añadir .gitignore:
   - __pycache__, *.pyc, .venv, dist, *.egg-info, *.wav (temporales), .env

ARCHIVOS A CREAR/MODIFICAR:
- src/transcribot/cli.py — COMPLETO (reemplazar esqueleto)
- src/transcribot/config.py — actualizar resolución de rutas y validación
- src/transcribot/pipeline.py — añadir manejo de errores y exit codes
- README.md — reescribir completo
- tests/test_integration.py — nuevo
- .gitignore — nuevo

NO MODIFICAR:
- audio.py, chunker.py, transcriber.py, diarizer.py, aligner.py, formatter.py

RESULTADO:
- transcribot transcribe video.mp4 funciona end-to-end con barra de progreso
- transcribot info muestra estado del sistema
- Errores muestran mensajes claros al usuario
- README documenta todo
```

---

## Criterios de Validación

- [ ]  transcribot transcribe <audio> -o output.txt completa end-to-end
- [ ]  Barra de progreso muestra cada paso
- [ ]  transcribot info muestra hardware, config, y check de requisitos
- [ ]  transcribot transcribe archivo_[inexistente.mp](http://inexistente.mp)4 muestra error claro y exit code 1
- [ ]  Ctrl+C durante ejecución limpia temporales
- [ ]  pytest tests/ -v --ignore=tests/test_[transcriber.py](http://transcriber.py) pasa (excluir tests lentos)
- [ ]  [README.md](http://README.md) contiene instrucciones completas de setup
- [ ]  .gitignore existe y excluye archivos apropiados