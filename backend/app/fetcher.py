import httpx
from schemas.doctor import Doctor
from parser import parse_doctors_list
from typing import Any
import dotenv
import os

dotenv.load_dotenv()

async def fetch_doctors(url: str, limit: int = 200, max_pages: int = 50) -> list[Doctor]:
    """Обходит страницы каталога и возвращает не более `limit` врачей."""
    result: list[Doctor] = []
    seen_ids: set[int] = set()

    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        for page in range(1, max_pages + 1):
            resp = await client.get(url, params={"page": page})
            resp.raise_for_status()

            doctors = parse_doctors_list(resp.text)
            if not doctors: # страницы кончились
                break

            for d in doctors:
                if d.id is not None:
                    if d.id in seen_ids: # защита от дублей между страницами
                        continue
                    seen_ids.add(d.id)
                result.append(d)
                if len(result) >= limit:
                    return result

    return result

API_TOKEN = os.getenv("PSYON_API_TOKEN")
API_URL = "https://interview.psyonclinic.ru/api/v1/specialists"

async def fetch_specialists(params: dict[str, Any] | None = None) -> Any:
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json",
    }
    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        resp = await client.get(API_URL, headers=headers, params=params)
        resp.raise_for_status()
        return resp.json()