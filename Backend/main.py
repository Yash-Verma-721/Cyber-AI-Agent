from fastapi import FastAPI
from pydantic import BaseModel
from detector import rule_based_score
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
import os 
from dotenv import load_dotenv


load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

class Message(BaseModel):
    text: str
    language: str = "English"

@app.post("/analyze")
async def analyze(data: Message):
    text = data.text

    # Rule-based score
    rule_score, risk, attack_type, factors, explanation, actions = rule_based_score(text)

    # Try AI
    ai_used = False
    keywords = []
    should_block = (risk == "Dangerous")
    
    try:
        print("[DEBUG] Executing OpenAI/OpenRouter API call...")
        import json, re
        prompt = f"""You are an advanced Cybersecurity Detection Agent.

The system has already evaluated this message's risk as: {risk}

OUTPUT LANGUAGE: {data.language}

----------------------------------
Return STRICT JSON:

{{
  "risk": "{risk}",
  "summary": "Short conclusion (max 20 words)",
  "explanation": "Detailed analysis explaining WHY it is {risk} (max 40 words)",
  "intent": "Intent behind the message.",
  "risk_factors": ["list of important scam indicators"],
  "confidence": 0.95
}}

----------------------------------
Rules:
- Summary MUST be a short final verdict.
- Explanation MUST be detailed and explain WHY.
- Both MUST be in {data.language}.
- Do NOT mix languages.
- Keep technical terms in English if needed.
- Do NOT include formatting like **, bullets, markdown.
- Do NOT include extra text outside JSON.

Analyze this message:
{text}"""

        ai_response = client.chat.completions.create(
            model="google/gemma-3-4b-it:free",
            messages=[{"role": "user", "content": prompt}],
            extra_headers={
                "HTTP-Referer": "http://localhost",
                "X-Title": "Cyber AI Agent"
            }
        )
        ai_text = ai_response.choices[0].message.content
        print(f"[DEBUG] Raw API Response: {ai_text}")
        
        # Clean potential markdown formatting
        json_match = re.search(r'\{.*\}', ai_text, re.DOTALL)
        if json_match:
            ai_text = json_match.group(0)
            
        parsed_ai = json.loads(ai_text)
        
        risk = parsed_ai.get("risk", risk)
        summary_text = parsed_ai.get("summary", explanation)
        explanation_text = parsed_ai.get("explanation", "No detailed analysis provided.")
        keywords = parsed_ai.get("risk_factors", parsed_ai.get("keywords", keywords))
        should_block = (risk == "Dangerous")
        
        ai_used = True

    except Exception as e:
        # Fallback if API fails (key missing, quota exceeded, invalid JSON, etc.)
        print(f"[DEBUG] API Parse Failed! Fallback triggered. Reason: {e}")
        summary_text = f"This message appears to be related to {attack_type}." if attack_type != "None" else "No immediate threat patterns detected."
        explanation_text = explanation

    return {
        "risk": risk,
        "score": rule_score,
        "attack_type": attack_type,
        "ai_summary": summary_text,
        "ai_explanation": explanation_text,
        "risk_factors": factors,
        "detected_keywords": keywords,
        "recommended_actions": actions,
        "should_block": should_block,
        "ai_used": ai_used
    }

# Instead of hardcoding:

# import os

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Then in terminal:

# set OPENAI_API_KEY=sk-xxxxxxxxxxxx   # Windows

# 👉 This avoids leaking your key.