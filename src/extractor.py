import json
import logging

from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .config import GROQ_API_KEY, GROQ_MODEL
from .models import ExtractionResult, Opportunity

logger = logging.getLogger(__name__)

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are an expert recruitment opportunity extraction engine.

You will receive:
1. YouTube video title
2. YouTube video description
3. YouTube transcript

Your task is to identify every internship, full-time job, apprenticeship, graduate program, fellowship, off-campus drive, hiring opportunity, and recruitment announcement mentioned in the video.

Important:
- Application links usually exist in the description.
- Eligibility information usually exists in the transcript.
- Combine both sources.

For every opportunity extract:
- job_title
- company
- eligible_batches
- application_link
- confidence

Rules:
- Extract ALL opportunities.
- Do not summarize the video.
- Do not explain.
- Do not add markdown.
- Return JSON only.
- Ignore social links.
- Ignore sponsor links.
- Ignore affiliate links.
- Ignore unrelated URLs.

Return valid JSON matching the schema exactly."""


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def _call_llm(content: str) -> dict:
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": content},
        ],
        temperature=0.1,
        max_tokens=4096,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


def extract_opportunities(title: str, description: str, transcript: str) -> list[Opportunity]:
    content = f"Video Title: {title}\n\nDescription: {description[:3000]}\n\nTranscript: {transcript[:5000]}"

    try:
        result = _call_llm(content)
        extraction = ExtractionResult(**result)
        return [
            opp
            for opp in extraction.opportunities
            if opp.job_title and opp.company
        ]

    except json.JSONDecodeError as e:
        logger.error("Failed to parse LLM response as JSON: %s", e)
        return []

    except Exception as e:
        logger.error("Extraction error: %s", e)
        return []
