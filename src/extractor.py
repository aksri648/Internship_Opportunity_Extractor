import json
from groq import Groq
from .config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are an AI assistant that extracts job/internship opportunities from YouTube video content about placements, jobs, and internships.

From the given video title, description, and transcript, extract ALL job/internship opportunities mentioned. For each opportunity, extract:
- job_title: The exact job/internship title (e.g., "Software Engineer Intern", "SDE Intern", "AI/ML Intern")
- company: The company name (e.g., "Microsoft", "Google", "Amazon")
- eligible_batches: List of eligible batch years (e.g., ["2026", "2027"])
- application_link: The application URL if mentioned, otherwise use "Not mentioned"
- location: Job location if mentioned, otherwise "Not specified"
- stipend: Stipend/salary if mentioned, otherwise "Not specified"
- deadline: Application deadline if mentioned, otherwise "Not specified"

Return ONLY a valid JSON object with this exact structure:
{
  "opportunities": [
    {
      "job_title": "string",
      "company": "string",
      "eligible_batches": ["string"],
      "application_link": "string",
      "location": "string",
      "stipend": "string",
      "deadline": "string"
    }
  ]
}

If no opportunities are found, return {"opportunities": []}. Do not include any text outside the JSON."""


def extract_opportunities(title: str, description: str, transcript: str) -> list[dict]:
    content = f"Video Title: {title}\n\nDescription: {description[:3000]}\n\nTranscript: {transcript[:5000]}"

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": content},
            ],
            temperature=0.1,
            max_tokens=4096,
            response_format={"type": "json_object"},
        )

        result = json.loads(response.choices[0].message.content)
        opportunities = result.get("opportunities", [])
        return [opp for opp in opportunities if opp.get("job_title") and opp.get("company")]
    except Exception as e:
        print(f"Extraction error: {e}")
        return []
