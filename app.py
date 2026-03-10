from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import subprocess
import uuid
import os

app = FastAPI(title="Whisper Transcription API")

WHISPER_BIN = "/whisper/build/bin/whisper-cli"
WHISPER_MODELS_DIR = "/whisper/models"
TMP_DIR = "/tmp"

ALLOWED_EXTENSIONS = {".mp3", ".mp4", ".wav", ".ogg", ".flac", ".m4a", ".webm", ".mkv"}

AVAILABLE_MODELS = ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"]


@app.get("/")
def root():
    return {
        "service": "Whisper Transcription API",
        "usage": "POST /transcribe with form-data: file, model (optional), language (optional)",
        "models": AVAILABLE_MODELS,
    }


@app.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    model: str = Form(default="small"),
    language: str = Form(default="auto"),
):
    # valida modelo
    if model not in AVAILABLE_MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"Modelo inválido: '{model}'. Disponíveis: {AVAILABLE_MODELS}",
        )

    # valida extensão do arquivo
    extension = os.path.splitext(file.filename)[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de arquivo não suportado: '{extension}'. Permitidos: {sorted(ALLOWED_EXTENSIONS)}",
        )

    # verifica se o modelo existe no disco
    model_path = f"{WHISPER_MODELS_DIR}/ggml-{model}.bin"
    if not os.path.exists(model_path):
        raise HTTPException(
            status_code=404,
            detail=f"Modelo '{model}' não encontrado em {WHISPER_MODELS_DIR}. Baixe com: bash models/download-ggml-model.sh {model}",
        )

    tmp_audio_path = f"{TMP_DIR}/{uuid.uuid4()}{extension}"
    tmp_output_path = f"{TMP_DIR}/{uuid.uuid4()}"

    # salva arquivo recebido
    with open(tmp_audio_path, "wb") as f:
        f.write(await file.read())

    # monta comando whisper
    cmd = [
        WHISPER_BIN,
        "-m", model_path,
        "-f", tmp_audio_path,
        "-otxt",
        "-of", tmp_output_path,
    ]

    if language != "auto":
        cmd += ["-l", language]

    # executa whisper
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        _cleanup(tmp_audio_path)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao transcrever: {e.stderr}",
        )
    finally:
        _cleanup(tmp_audio_path)

    # lê o arquivo de texto gerado
    result_file = tmp_output_path + ".txt"
    try:
        with open(result_file, "r") as f:
            text = f.read().strip()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Arquivo de saída não encontrado.")
    finally:
        _cleanup(result_file)

    return {
        "transcription": text,
        "model": model,
        "language": language,
        "filename": file.filename,
    }


def _cleanup(*paths):
    for path in paths:
        try:
            if path and os.path.exists(path):
                os.remove(path)
        except Exception:
            pass
