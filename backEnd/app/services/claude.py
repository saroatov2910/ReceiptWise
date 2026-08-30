import json
import anthropic
from app.core.config import settings

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def parse_receipt_with_claude(raw_text: str) -> dict:
    prompt = f"""
אתה מערכת לניתוח קבלות עסקיות.
להלן טקסט גולמי שחולץ מקבלה באמצעות OCR:

---
{raw_text}
---

חלץ את הפרטים הבאים והחזר JSON בלבד (ללא הסברים):
{{
  "vendor": "שם הספק / העסק",
  "amount": 0.00,
  "currency": "ILS",
  "date": "YYYY-MM-DD",
  "category": "food | transport | office | utilities | entertainment | health | other",
  "description": "תיאור קצר של ההוצאה"
}}

אם פרט מסוים לא קיים בטקסט, השתמש ב-null.
"""

    message = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )

    text = message.content[0].text.strip()

    # נקה את התגובה אם יש markdown
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]

    return json.loads(text)
