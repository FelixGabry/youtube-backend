# YouTube Downloader Backend

Backend per il downloader YouTube creato con FastAPI e yt-dlp.

## Setup Locale

1. Installa Python 3.11+
2. Crea virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # oppure
   venv\Scripts\activate  # Windows
   ```
3. Installa dipendenze:
   ```bash
   pip install -r requirements.txt
   ```
4. Avvia il server:
   ```bash
   python main.py
   ```

Il server sarà disponibile su http://localhost:8000

## Deploy su Railway

1. Vai su https://railway.app
2. Crea un account e connetti GitHub
3. Carica questi file su un repository GitHub
4. Su Railway: "New Project" → "Deploy from GitHub repo"
5. Seleziona il repository
6. Railway farà il deploy automaticamente

## API Endpoints

- `POST /api/youtube/download` - Inizia download
- `GET /api/download/status/{id}` - Stato download
- `GET /api/file/{id}` - Scarica file
- `GET /` - Health check

## Struttura File

```
backend/
├── main.py           # Server FastAPI
├── requirements.txt  # Dipendenze Python
├── Dockerfile       # Container config
├── README.md        # Questa guida
└── downloads/       # Directory download (auto-creata)
```

## Note

- Il backend gestisce download reali da YouTube
- I file vengono salvati temporaneamente
- CORS configurato per domini Lovable
- Usa yt-dlp per download effettivi