import os
import resend
from datetime import date


RECIPIENT = "divyansh_misra@yahoo.com"
SENDER = "Build Spark <onboarding@resend.dev>"


def _difficulty_color(level: str) -> str:
    return {"Beginner": "#22c55e", "Intermediate": "#f59e0b", "Advanced": "#ef4444"}.get(
        level, "#6b7280"
    )


def _source_badge(url: str) -> str:
    if "reddit.com" in url:
        return '<span style="background:#ff4500;color:#fff;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;">Reddit</span>'
    if "youtube.com" in url:
        return '<span style="background:#ff0000;color:#fff;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;">YouTube</span>'
    return ""


def _render_idea(idx: int, idea: dict) -> str:
    difficulty_color = _difficulty_color(idea.get("difficulty", "Beginner"))
    badge = _source_badge(idea.get("source_url", ""))
    return f"""
    <div style="background:#ffffff;border:1px solid #e5e7eb;border-radius:12px;padding:24px;margin-bottom:20px;">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
        <span style="background:#f3f4f6;color:#374151;width:28px;height:28px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;">{idx}</span>
        {badge}
        <span style="background:{difficulty_color}22;color:{difficulty_color};padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;">{idea.get("difficulty", "Beginner")}</span>
      </div>
      <h2 style="margin:0 0 10px;font-size:18px;color:#111827;line-height:1.4;">{idea["title"]}</h2>
      <p style="margin:0 0 12px;color:#4b5563;font-size:14px;line-height:1.6;">{idea["why"]}</p>
      <div style="background:#f9fafb;border-left:3px solid #6366f1;padding:12px 16px;border-radius:0 8px 8px 0;margin-bottom:14px;">
        <p style="margin:0;font-size:13px;color:#374151;"><strong>How to start:</strong> {idea["how_to_start"]}</p>
      </div>
      <a href="{idea["source_url"]}" style="font-size:12px;color:#6366f1;text-decoration:none;">
        View source: {idea["source_title"][:80]}{"..." if len(idea["source_title"]) > 80 else ""}
      </a>
    </div>"""


def send_email(ideas: list[dict]) -> None:
    resend.api_key = os.environ["RESEND_API_KEY"]

    today = date.today().strftime("%B %d, %Y")
    ideas_html = "".join(_render_idea(i + 1, idea) for i, idea in enumerate(ideas))

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f3f4f6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <div style="max-width:620px;margin:40px auto;padding:0 16px;">

    <div style="background:#6366f1;border-radius:12px 12px 0 0;padding:32px 32px 24px;">
      <p style="margin:0 0 4px;color:#c7d2fe;font-size:13px;font-weight:500;letter-spacing:0.05em;">BUILD SPARK</p>
      <h1 style="margin:0;color:#ffffff;font-size:26px;font-weight:700;">Your AI build ideas</h1>
      <p style="margin:8px 0 0;color:#a5b4fc;font-size:14px;">{today} · {len(ideas)} ideas curated for you</p>
    </div>

    <div style="background:#f9fafb;padding:24px 32px 8px;">
      <p style="margin:0 0 20px;color:#6b7280;font-size:13px;">
        Sourced from Reddit and YouTube · curated by Claude for beginner AI builders
      </p>
      {ideas_html}
    </div>

    <div style="background:#f3f4f6;border-radius:0 0 12px 12px;padding:20px 32px;text-align:center;">
      <p style="margin:0;color:#9ca3af;font-size:12px;">
        You'll receive the next digest in 3 days.<br>
        Built with Claude API + GitHub Actions.
      </p>
    </div>

  </div>
</body>
</html>"""

    resend.Emails.send({
        "from": SENDER,
        "to": [RECIPIENT],
        "subject": f"Your AI build ideas — {today}",
        "html": html,
    })

    print(f"Email sent to {RECIPIENT} with {len(ideas)} ideas.")
