"""LLM helper for bill extraction using Vertex AI Gemini."""
import json
import vertexai
from vertexai.generative_models import GenerativeModel

from shared.config import GCP_PROJECT

# Initialize Vertex AI
vertexai.init(project=GCP_PROJECT, location="us-central1")

model = GenerativeModel("gemini-2.0-flash-001")

EXTRACTION_PROMPT = """Extract the following information from this utility bill text and return ONLY valid JSON matching this schema:

{
  "billing_period_start": "YYYY-MM-DD",
  "billing_period_end": "YYYY-MM-DD", 
  "total_amount": <number>,
  "line_items": [
    {"name": "<charge name>", "amount": <number>}
  ]
}

Rules:
- Return ONLY the JSON, no other text
- For dates, use ISO format YYYY-MM-DD
- For amounts, use numbers (not strings)
- Include all line items/charges from the bill
"""


def extract_bill_data(bill_text: str, provider: str = None) -> dict:
    """Use LLM to extract structured data from bill text."""
    prompt = EXTRACTION_PROMPT
    
    if provider:
        prompt += f"\nProvider: {provider}\n"
    
    prompt += "\nBill text:\n" + bill_text
    
    response = model.generate_content(prompt)
    response_text = response.text.strip()
    
    # Clean up markdown code blocks
    if response_text.startswith("```"):
        response_text = response_text.split("```")[1]
        if response_text.startswith("json"):
            response_text = response_text[4:]
        response_text = response_text.strip()
    
    return json.loads(response_text)
