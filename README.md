# 🎙️ Whisper Transcription API

API REST para transcrição de áudio usando [whisper.cpp](https://github.com/ggerganov/whisper.cpp) + FastAPI, containerizada com Docker.

---

## ✅ Pré-requisitos

- Docker e Docker Compose instalados
- whisper.cpp **compilado no host** (veja abaixo)

---

## 1. Instalar e compilar o whisper.cpp

```bash
# dependências (Ubuntu/Debian)
sudo apt update && sudo apt install -y git build-essential

# clona o repositório
git clone https://github.com/ggerganov/whisper.cpp.git /root/whisper.cpp
cd /root/whisper.cpp

# compila
cmake -B build
cmake --build build --config Release
```

> O binário gerado ficará em `/root/whisper.cpp/build/bin/whisper-cli`.

---

## 2. Baixar um modelo

Os modelos ficam em `/root/whisper.cpp/models/`. Baixe o que quiser:

```bash
cd /root/whisper.cpp
bash models/download-ggml-model.sh small   # recomendado para começar
bash models/download-ggml-model.sh medium
bash models/download-ggml-model.sh large-v3
```

| Modelo     | Tamanho | Qualidade     | RAM necessária |
|------------|---------|---------------|----------------|
| `tiny`     | ~75 MB  | Básica        | ~390 MB        |
| `base`     | ~142 MB | Razoável      | ~500 MB        |
| `small`    | ~466 MB | Boa ✅        | ~1 GB          |
| `medium`   | ~1.5 GB | Muito boa     | ~2.6 GB        |
| `large-v3` | ~3.1 GB | Excelente     | ~5.2 GB        |

---

## 3. Subir a API

```bash
git clone https://github.com/seu-usuario/whisper-api.git
cd whisper-api

docker compose up -d
```

A API ficará disponível em `http://localhost:8010`.

---

## 4. Uso

### Transcrever um arquivo

```bash
curl -X POST http://localhost:8010/transcribe \
  -F "file=@audio.mp3"
```

### Escolher modelo e idioma

```bash
curl -X POST http://localhost:8010/transcribe \
  -F "file=@audio.mp3" \
  -F "model=medium" \
  -F "language=pt"
```

### Parâmetros

| Parâmetro  | Tipo   | Padrão | Descrição                                              |
|------------|--------|--------|--------------------------------------------------------|
| `file`     | arquivo| —      | Arquivo de áudio/vídeo (obrigatório)                   |
| `model`    | string | `small`| Modelo whisper: `tiny`, `base`, `small`, `medium`, `large`, `large-v2`, `large-v3` |
| `language` | string | `auto` | Código do idioma: `pt`, `en`, `es`, `fr`, etc. ou `auto` |

### Formatos suportados

`.mp3` `.mp4` `.wav` `.ogg` `.flac` `.m4a` `.webm` `.mkv`

### Exemplo de resposta

```json
{
  "transcription": "Olá, este é um teste de transcrição.",
  "model": "small",
  "language": "pt",
  "filename": "audio.mp3"
}
```

---

## 5. Verificar saúde da API

```bash
curl http://localhost:8010/
```

---

## Estrutura do projeto

```
whisper-api/
├── app.py               # API FastAPI
├── Dockerfile           # Imagem Docker
├── docker-compose.yml   # Orquestração
├── requirements.txt     # Dependências Python
└── README.md
```

---

## Observações

- O whisper.cpp **não está dentro do container** — ele é montado como volume do host (`/root/whisper.cpp`). Isso mantém a imagem leve e permite atualizar modelos sem rebuild.
- Para mudar o caminho do whisper.cpp no host, edite o `docker-compose.yml`.

---

## Licença

MIT
