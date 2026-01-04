import os
import asyncio
import json
import uuid
import shutil
import base64
import mimetypes
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from services.ai_client import AIClient

load_dotenv()

app = FastAPI()

# Directory Setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
IMAGE_DIR = os.path.join(OUTPUT_DIR, "images")
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# Shared AI Client (AI Builder Space)
ai_client = AIClient()

# In-memory storage for requirement analysis status (reset on restart)
# In production, this would be Redis/DB, but here we stay simple.
class RequirementStatus(BaseModel):
    id: str
    round: int
    status: str # "clarifying", "completed", "failed"
    updated_state: dict = {}
    document: Optional[dict] = None
    clarifications_needed: List[str] = []
    error: Optional[str] = None

active_tasks = {}

# Constants
MAX_IMAGE_COUNT = int(os.getenv("MAX_IMAGE_COUNT", "1000"))

# Models
class RequirementRequest(BaseModel):
    feedback: str
    state: dict # Global state passed from frontend (Requirement Genome)

# --- Helper Functions ---

async def retry_with_backoff(func, *args, max_retries=3, initial_delay=2, **kwargs):
    """Retries an async function with exponential backoff on 503 errors."""
    delay = initial_delay
    for i in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            err_str = str(e).lower()
            if "503" in err_str or "overloaded" in err_str or "unavailable" in err_str:
                if i == max_retries - 1:
                    raise e
                print(f"Model overloaded, retrying in {delay}s... (Attempt {i+1}/{max_retries})")
                await asyncio.sleep(delay)
                delay *= 2
            else:
                raise e

async def cleanup_images():
    """Removes oldest images if count exceeds MAX_IMAGE_COUNT."""
    files = [os.path.join(IMAGE_DIR, f) for f in os.listdir(IMAGE_DIR) if os.path.isfile(os.path.join(IMAGE_DIR, f))]
    if len(files) <= MAX_IMAGE_COUNT:
        return
    
    # Sort by creation time
    files.sort(key=os.path.getctime)
    num_to_delete = len(files) - MAX_IMAGE_COUNT
    for i in range(num_to_delete):
        try:
            os.remove(files[i])
        except Exception as e:
            print(f"Error deleting {files[i]}: {e}")

async def analyze_requirements_task(task_id: str, feedback: str, state: dict):
    """Analyze requirements and generate structured JSON document."""
    active_tasks[task_id]["status"] = "Analyzing requirements..."
    try:
        # Build prompt for requirement analysis
        current_round = state.get('round', 0)
        is_first_round = current_round == 0
        
        prompt = f"""
You are a 'Requirements Analysis Expert'. Your task is to understand user requirements, identify ambiguities, and generate structured requirement documents.

Current Requirement State: {json.dumps(state, indent=2, ensure_ascii=False)}
User Input: "{feedback}"

Task:
1. **Understand & Parse Requirements**:
   - Extract key functional requirements, user stories, and constraints from the user input
   - If this is NOT the first round, integrate new information with existing requirements
   - Identify any contradictions and resolve them (prioritize newer information)

2. **Identify Ambiguities**:
   - Determine if there are unclear points that need clarification
   - Generate specific clarification questions if needed
   - If requirements are clear enough, proceed to document generation

3. **Update Requirement Genome**:
   - Update 'features' list: Extract distinct functional features
   - Update 'user_stories' list: Create user stories in format "As a [role], I want [goal] so that [benefit]"
   - Update 'constraints' list: Identify technical, business, or other constraints
   - Update 'requirements_summary': Create a 2-3 sentence summary in Markdown
   - Ensure the genome reflects the FULL conversation history

4. **Generate Structured Document** (only if status="completed"):
   - If requirements are clear and complete, generate a full JSON requirement document
   - If clarifications are needed, set status="clarifying" and provide questions

Output Format: Respond ONLY with valid JSON.

Example Output (when clarifying):
{{
  "status": "clarifying",
  "updated_state": {{
    "round": {current_round + 1},
    "requirements_summary": "Summary of understood requirements so far...",
    "features": ["Feature 1", "Feature 2"],
    "user_stories": [
      {{"id": "US-1", "title": "User Story Title", "description": "As a... I want... so that..."}}
    ],
    "constraints": ["Constraint 1", "Constraint 2"],
    "clarifications_needed": ["Question 1", "Question 2"]
  }}
}}

Example Output (when completed):
{{
  "status": "completed",
  "updated_state": {{
    "round": {current_round + 1},
    "requirements_summary": "Complete summary of all requirements...",
    "features": ["Feature 1", "Feature 2"],
    "user_stories": [
      {{"id": "US-1", "title": "...", "description": "...", "acceptance_criteria": ["..."], "priority": "high"}}
    ],
    "constraints": ["Constraint 1"],
    "clarifications_needed": []
  }},
  "document": {{
    "project": {{
      "name": "Project Name",
      "description": "Project description"
    }},
    "user_stories": [
      {{
        "id": "US-1",
        "title": "User Story Title",
        "description": "As a [role], I want [goal] so that [benefit]",
        "acceptance_criteria": ["Criterion 1", "Criterion 2"],
        "priority": "high"
      }}
    ],
    "features": [
      {{
        "id": "F-1",
        "name": "Feature Name",
        "description": "Feature description",
        "related_user_stories": ["US-1"]
      }}
    ],
    "constraints": ["Constraint 1"],
    "technical_requirements": [],
    "non_functional_requirements": []
  }}
}}
"""
        
        # Use retry with backoff for requirement analysis
        analysis_data = await retry_with_backoff(
            ai_client.generate_plan,
            prompt=prompt,
            state=state
        )
        
        active_tasks[task_id]["status"] = analysis_data.get("status", "completed")
        active_tasks[task_id]["updated_state"] = analysis_data["updated_state"]
        active_tasks[task_id]["round"] = state.get("round", 0) + 1
        
        # If completed, include the document
        if analysis_data.get("status") == "completed":
            if "document" in analysis_data:
                active_tasks[task_id]["document"] = analysis_data["document"]
            active_tasks[task_id]["status"] = "completed"
        elif analysis_data.get("status") == "clarifying":
            active_tasks[task_id]["clarifications_needed"] = analysis_data["updated_state"].get("clarifications_needed", [])
            active_tasks[task_id]["status"] = "clarifying"

    except Exception as e:
        print(f"Error in requirement analysis task: {e}")
        import traceback
        traceback.print_exc()
        active_tasks[task_id]["status"] = "failed"
        active_tasks[task_id]["error"] = str(e)

# --- Endpoints ---

@app.post("/api/feedback")
async def handle_feedback(req: RequirementRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    active_tasks[task_id] = {
        "id": task_id,
        "round": req.state.get("round", 0),
        "status": "Analyzing requirements...",
        "updated_state": req.state,
        "document": None,
        "clarifications_needed": []
    }
    background_tasks.add_task(analyze_requirements_task, task_id, req.feedback, req.state)
    return {"task_id": task_id}

@app.get("/api/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return active_tasks[task_id]

@app.get("/api/images/{filename}")
async def get_image(filename: str):
    filepath = os.path.join(IMAGE_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(filepath)

@app.post("/api/transcribe")
async def transcribe_audio(audio_file: UploadFile = File(...)):
    """Transcribe audio using AI Builder Space API."""
    try:
        # Read audio file
        audio_data = await audio_file.read()
        
        # Call AI client to transcribe
        result = await ai_client.transcribe_audio(audio_data)
        
        return {
            "text": result.get("text", ""),
            "language": result.get("detected_language"),
            "confidence": result.get("confidence")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

# Serve Frontend (Must be after API routes)
if os.path.exists(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="frontend")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up AI client on shutdown."""
    await ai_client.close()

if __name__ == "__main__":
    import uvicorn
    # Use PORT from env or 8000
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
