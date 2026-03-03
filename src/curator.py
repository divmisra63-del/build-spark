import os
import json
import anthropic


SYSTEM_PROMPT = """You are a helpful assistant that curates build ideas for a beginner developer
interested in AI and LLM tools. You receive a list of Reddit posts and YouTube videos scraped
from the internet, and your job is to extract the 3 to 5 most interesting, actionable project ideas.

Guidelines:
- The developer is a beginner — ideas should be achievable in a weekend with clear starting points
- Focus on ideas involving AI APIs (Claude, OpenAI), LLMs, chatbots, automation, or AI-powered tools
- Avoid ideas that are purely theoretical, memes, or unrelated to building something
- Each idea should be concrete enough to start immediately

Return ONLY a valid JSON array. No markdown, no explanation. Format:
[
  {
    "title": "Short catchy project title",
    "why": "One sentence on why this is a fun or useful thing to build",
    "how_to_start": "One concrete first step to begin this project today",
    "difficulty": "Beginner",
    "source_title": "Title of the Reddit post or YouTube video that inspired this",
    "source_url": "URL of the source"
  }
]"""


def curate(raw_items: list[dict]) -> list[dict]:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    formatted = "\n\n".join(
        f"[{i+1}] {item['type'].upper()} — {item['source']}\n"
        f"Title: {item['title']}\n"
        f"URL: {item['url']}\n"
        f"Snippet: {item['snippet'] or '(no description)'}"
        for i, item in enumerate(raw_items)
    )

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1500,
        messages=[
            {
                "role": "user",
                "content": f"Here are the scraped posts and videos from the last few days:\n\n{formatted}\n\nExtract 3–5 beginner-friendly AI build ideas as a JSON array.",
            }
        ],
        system=SYSTEM_PROMPT,
    )

    text = message.content[0].text.strip()
    # Strip markdown code fences if the model wraps the JSON
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    return json.loads(text)
