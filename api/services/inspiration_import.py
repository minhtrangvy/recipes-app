import json
import os
from typing import Any

import requests
from bs4 import BeautifulSoup
from openai import OpenAI

from api.constants import AMOUNT_TYPES

AMOUNT_TYPE_SET = set(AMOUNT_TYPES)


def import_recipe_from_url(inspiration_url: str) -> dict[str, Any]:
    page_text = fetch_page_text(inspiration_url)
    client = OpenAI(api_key=get_openai_api_key())

    response = client.responses.create(
        model=os.environ.get("OPENAI_MODEL", "gpt-5.5"),
        input=[
            {
                "role": "system",
                "content": (
                    "Extract recipe data from the provided page text. "
                    "Return only valid JSON with this shape: "
                    '{"ingredients":[{"name":"string","amount":1,"amount_type":"cup|teaspoon|tablespoon|dash|weight_g"}],'
                    '"instructions":[{"title":"string","steps":["string"]}]}. '
                    "Do not include markdown fences or commentary. "
                    "If the page is ambiguous, make the best structured extraction you can."
                ),
            },
            {
                "role": "user",
                "content": f"Source URL: {inspiration_url}\n\nPage text:\n{page_text}",
            },
        ],
    )

    parsed = json.loads(extract_json(response.output_text))
    return normalize_import_payload(parsed)


def fetch_page_text(url: str) -> str:
    response = requests.get(
        url,
        timeout=20,
        headers={
            "User-Agent": "recipes-app/1.0",
        },
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines()]
    filtered_lines = [line for line in lines if line]
    text = "\n".join(filtered_lines[:1500])
    return text[:20000]


def get_openai_api_key() -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for inspiration imports")
    return api_key


def normalize_import_payload(payload: dict[str, Any]) -> dict[str, Any]:
    ingredients = []
    for ingredient in payload.get("ingredients", []):
        name = str(ingredient.get("name", "")).strip()
        amount = ingredient.get("amount")
        amount_type = ingredient.get("amount_type")

        if not name:
            continue

        if not isinstance(amount, int) or amount <= 0:
            amount = 1

        if amount_type not in AMOUNT_TYPE_SET:
            amount_type = "dash"

        ingredients.append(
            {
                "name": name,
                "amount": amount,
                "amount_type": amount_type,
            }
        )

    instructions = []
    for instruction in payload.get("instructions", []):
        title = str(instruction.get("title", "")).strip() or "Instruction"
        raw_steps = instruction.get("steps", [])
        steps = [str(step).strip() for step in raw_steps if str(step).strip()]
        instructions.append(
            {
                "title": title,
                "steps": steps,
            }
        )

    return {
        "ingredients": ingredients,
        "instructions": instructions,
    }


def extract_json(output_text: str) -> str:
    stripped = output_text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return stripped
