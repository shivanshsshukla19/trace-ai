import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from google import genai
from schemas import CodeAnalysisRequest, CodeAnalysisResponse

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is not set in the .env file")

client = genai.Client(api_key=api_key)
app = FastAPI(title="TraceAI - Code Complexity & Edge-Case Auditor")

app.mount("/static", StaticFiles(directory="static"), name="static")

FALLBACK_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-flash-latest",
    "gemini-3.5-flash",
    "gemini-flash-lite-latest",
]

SYSTEM_INSTRUCTION = """
You are an expert technical interviewer and systems performance engineer.
Analyze code concisely. Evaluate runtime bounds against 1-second online judge execution limits (~10^8 operations).
Provide only necessary idiomatic modern refactors (preferring STL like std::vector, std::unordered_set, std::span).
"""

@app.get("/")
def serve_home():
    return FileResponse("static/index.html")

@app.post("/analyze", response_model=CodeAnalysisResponse)
async def analyze_code(payload: CodeAnalysisRequest):
    constraint_text = f"Target Input Constraint: {payload.max_n}" if payload.max_n else "Target Input Constraint: Standard competitive programming upper bound (assume N <= 10^5 if unspecified)"

    prompt = f"""
    Analyze the following {payload.language} code:
    ```
    {payload.code}
    ```
    {constraint_text}

    1. Calculate time/space Big-O complexity.
    2. Evaluate whether it triggers a Time Limit Exceeded (TLE) under a standard 1-second (~10^8 operations) judge limit.
    3. Identify critical boundary edge cases.
    4. Provide an optimized, idiomatic refactored version.
    """

    last_error = None

    for model_name in FALLBACK_MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config={
                    "system_instruction": SYSTEM_INSTRUCTION,
                    "response_mime_type": "application/json",
                    "response_schema": CodeAnalysisResponse,
                    "max_output_tokens": 1200,
                },
            )
            return CodeAnalysisResponse.model_validate_json(response.text)

        except Exception as e:
            last_error = e
            print(f"[TraceAI Warning] {model_name} failed: {e}. Retrying next...")
            continue

    raise HTTPException(
        status_code=503,
        detail=f"All available Gemini models busy. Last error: {str(last_error)}"
    )