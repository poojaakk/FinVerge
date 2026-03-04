import os
import google.generativeai as genai
from ..config import settings

# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

def call_gemini(prompt: str) -> str:
    """Call Gemini API with the given prompt"""
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error calling Gemini API: {str(e)}"

def explain(discrepancies, po, invoice):
    prompt = f"""
    Explain the following procurement discrepancies clearly:
    {discrepancies}
    """
    return call_gemini(prompt)

def explain_with_rag(discrepancy, context):
    context_text = "\n".join([c["text"] for c in context])

    prompt = f"""
You are a procurement compliance assistant.

Discrepancy detected:
- Item: {discrepancy['item']}
- Type: {discrepancy['type']}

Relevant procurement rules and contracts:
{context_text}

Task:
Decide whether this discrepancy is:
- ACCEPTABLE
- NEEDS_REVIEW
- REJECTED

Give:
1. Decision
2. Short explanation (2–3 lines)
"""

    return call_gemini(prompt)

def parse_llm_response(response: str):
    decision = "NEEDS_REVIEW"

    if "ACCEPTABLE" in response:
        decision = "ACCEPTABLE"
    elif "REJECT" in response:
        decision = "REJECTED"

    return decision, response.strip()
