# AI Mind-Map Agent

A three-agent AI system (Intake, Architect, Research & Critique) that generates and iteratively refines mind maps through research and user feedback.

**Live Demo**: https://mindmap-agent-web.vercel.app/

## Quick Start

### Local Development

1. **Clone and install**:
   ```bash
   git clone <your-repo-url>
   cd mindmap-agent
   pip install -r requirements.txt
   ```

2. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run locally**:
   ```bash
   uvicorn app:app --reload
   ```
   
   Open http://localhost:8000

### Deploy to Vercel

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Initial commit: AI Mind-Map Agent"
   git push origin main
   ```

2. **Import into Vercel**:
   - Go to https://vercel.com/new
   - Select "Import Git Repository"
   - Choose this repo
   - Click "Deploy"

3. **Set Environment Variables** in Vercel Dashboard:
   - `MINDMAP_PROVIDER` = `openrouter`
   - `MINDMAP_MODEL` = `openai/gpt-4-turbo` (or your choice)
   - `OPENROUTER_API_KEY` = your OpenRouter key (get from https://openrouter.ai/keys)

4. **Done!** Vercel auto-deploys on each push.

## Architecture

**Three-Agent Pipeline**:

1. **Intake Agent** — Extracts topic, audience, and depth preference through natural conversation
2. **Architect Agent** — Builds MECE (mutually exclusive, collectively exhaustive) structures; refines targeted branches
3. **Research & Critique Agent** — Researches alternatives, validates assumptions, asks probing questions

## API Endpoints

- `POST /api/intake` — One turn of clarifying conversation
- `POST /api/draft` — Generate first-draft mind map
- `POST /api/critique` — Research and validate branches
- `POST /api/refine` — Deepen a specific branch
- `POST /api/edit` — User-initiated edit or delete
- `GET /api/health` — Health check

## File Structure

```
mindmap-agent/
├── public/
│   └── index.html          # Polished UI (mind map visualization)
├── lib/
│   ├── __init__.py
│   ├── prompts.py          # Embedded agent system prompts
│   ├── llm.py              # LLM provider abstraction
│   └── patch.py            # Mind map patching utilities
├── app.py                  # FastAPI main app
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── vercel.json            # Vercel config
└── README.md              # This file
```

## Configuration

**Supported Providers**:
- OpenRouter (recommended for cost efficiency)
- Anthropic API

**Environment Variables**:
```
MINDMAP_PROVIDER=openrouter          # or "anthropic"
MINDMAP_MODEL=openai/gpt-4-turbo     # Model name
OPENROUTER_API_KEY=sk-or-v1-...      # Your OpenRouter key
```

## Design Principles

- **Stateless** — No persistent storage between API calls (Vercel Functions compatible)
- **User-centric** — Real-time agent activity visualization with explanations
- **Iterative** — Multi-agent collaboration with human-in-the-loop refinement
- **Research-driven** — Critique agent validates with web search

## Next Steps

- Week 2: Add persistent storage (Vercel KV or database)
- Week 2: Expand test cases and refinement loops
- Week 3: Multi-modal export (PDF, Markmap HTML, PNG)

## Support

For issues or questions, check the GitHub issues or contact the team.
