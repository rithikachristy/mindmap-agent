"""
AI Mind-Map Agent — FastAPI backend for Vercel deployment.
Stateless by design (no persistent storage between invocations).
"""

import os
import sys
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(__file__))

from lib import llm
from lib.prompts import INTAKE_PROMPT, ARCHITECT_PROMPT, CRITIQUE_PROMPT
from lib import patch

app = FastAPI()


# ============================================================
# Request/Response Models
# ============================================================

class Turn(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class IntakeRequest(BaseModel):
    conversation: list[Turn]


class DraftRequest(BaseModel):
    brief: dict


class CritiqueRequest(BaseModel):
    outline: str


class RefineRequest(BaseModel):
    outline: str
    branch: str
    question: str | None = None
    answer: str


class EditRequest(BaseModel):
    outline: str
    branch: str
    action: str = "edit"  # "edit" or "delete"
    requested_change: str | None = None
    override: bool = False


# ============================================================
# API Routes
# ============================================================

@app.post("/api/intake")
def api_intake(req: IntakeRequest):
    """One turn of Intake conversation."""
    messages = [{"role": t.role, "content": t.content} for t in req.conversation]
    text = llm.complete(INTAKE_PROMPT, messages)
    try:
        import json
        brief = json.loads(text)
        return {"type": "brief", "brief": brief}
    except Exception:
        return {"type": "question", "question": text.strip()}


@app.post("/api/draft")
def api_draft(req: DraftRequest):
    """Architect MODE 1 — first draft."""
    import json
    outline = llm.complete(ARCHITECT_PROMPT, [{"role": "user", "content": json.dumps(req.brief)}])
    is_valid, err = patch.validate_outline(outline)
    if not is_valid:
        return {"error": f"validation failed: {err}", "outline": outline}
    return {"outline": outline}


@app.post("/api/critique")
def api_critique(req: CritiqueRequest):
    """Critique MODE 1 — research and validate."""
    try:
        result = llm.complete_json(CRITIQUE_PROMPT, [{"role": "user", "content": req.outline}], use_web_search=True)
        return result
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/refine")
def api_refine(req: RefineRequest):
    """Architect MODE 2 — targeted refine."""
    import json
    payload = {"branch": req.branch, "question": req.question, "answer": req.answer}
    refined = llm.complete(ARCHITECT_PROMPT, [{"role": "user", "content": json.dumps(payload)}])

    try:
        pushback = json.loads(refined)
        if isinstance(pushback, dict) and pushback.get("push_back"):
            return {"pushback": pushback.get("reason", "Declined"), "outline": req.outline}
    except Exception:
        pass

    try:
        new_outline = patch.splice_branch(req.outline, req.branch, refined)
        return {"outline": new_outline}
    except ValueError as e:
        return {"pushback": str(e), "outline": req.outline}


@app.post("/api/edit")
def api_edit(req: EditRequest):
    """User-initiated edit/delete."""
    import json
    try:
        if req.action == "delete":
            new_outline = patch.delete_branch(req.outline, req.branch)
            return {"applied": True, "outline": new_outline}
        else:
            refined = llm.complete(ARCHITECT_PROMPT, [
                {"role": "user", "content": json.dumps({
                    "branch": req.branch,
                    "question": None,
                    "answer": req.requested_change or ""
                })}
            ])
            new_outline = patch.splice_branch(req.outline, req.branch, refined)
            return {"applied": True, "outline": new_outline}
    except ValueError as e:
        return {"applied": False, "error": str(e), "outline": req.outline}


@app.get("/api/health")
def health():
    """Health check."""
    return {
        "ok": True,
        "provider": llm.PROVIDER,
        "model": llm.MODEL,
    }


# ============================================================
# Static Frontend
# ============================================================

_public_dir = os.path.join(os.path.dirname(__file__), "public")
if os.path.isdir(_public_dir):
    app.mount("/", StaticFiles(directory=_public_dir, html=True), name="static")
