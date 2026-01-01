# AutoEQ - SoundCloud Likes EQ Dashboard

Dynamic music analysis and EQ preset generation for your SoundCloud likes using AI-powered clustering.

## Features

- **Daily Auto-Update**: Fetches new likes every day at 3 AM UTC
- **AI-Powered Clustering**: Uses Groq LLM (Llama 3.1 70B) for intelligent music categorization
- **Dynamic EQ Presets**: Generates optimal EQ settings for each music cluster
- **Copy-Paste Ready**: EqualizerAPO/Peace compatible preset format
- **Web Dashboard**: Beautiful visualization of your music taste

## Quick Start

### Local Development

```bash
# Clone and setup
git clone git@github.com:VitaNova/autoeq.git
cd autoeq

# Set environment
cp .env.example .env
# Edit .env with your GROQ_API_KEY

# Run locally
python3 -m http.server 8889
open http://localhost:8889
```

### Docker Deployment

```bash
# Build and run
docker-compose up -d

# Check logs
docker logs -f autoeq

# Access dashboard
open http://localhost:8890
```

### Production (ex63)

```bash
# Deploy to production
ssh ex63 "cd /root/autoeq && docker-compose pull && docker-compose up -d"
```

## Architecture

```
autoeq/
├── src/
│   ├── fetch_likes.py      # SoundCloud API scraper
│   ├── groq_cluster.py     # AI-powered clustering
│   ├── daily_update.py     # Cron job orchestrator
│   └── generate_eq_presets.py
├── data/
│   ├── soundcloud_likes.json
│   ├── track_clusters.json
│   └── eq_presets*.json
├── index.html              # Main dashboard
├── copy-presets.html       # Copy-paste EQ presets
├── Dockerfile
└── docker-compose.yml
```

## Multi-Repo Hot Availability

| Remote | URL | Purpose |
|--------|-----|---------|
| origin | Local Mac | Development |
| ex63 | ex63:/root/autoeq | Production deployment |
| github | github.com/VitaNova/autoeq | Public mirror |
| gitea | gitea.vitainfra.com/vitanova/autoeq | Private backup |

## API Endpoints

- `GET /` - Dashboard
- `GET /copy-presets.html` - Copy-paste EQ presets
- `GET /health` - Health check
- `GET /api/status` - Last update status
- `GET /data/*.json` - Raw data files

## License

MIT - VitaNova Infrastructure
