from fastapi import Depends, FastAPI
from fastapi import HTTPException
from fastapi import Query
from fetcher import fetch_doctors, fetch_specialists
from schemas.doctor import Doctor
import httpx
from typing import Any

app = FastAPI(
    title="Doctors API",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

@app.get("/doctors", response_model=list[Doctor])
async def get_doctors_from_site(limit: int = Query(200, ge=1, le=350)) -> list[Doctor]:
    try:
        site_url = "https://interview.psyonclinic.ru/doctors"
        return await fetch_doctors(site_url, limit=limit)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Ошибка при загрузке каталога: {e}")


@app.get("/specialists")
async def get_specialists_from_api(page: int | None = Query(None, ge=1)) -> Any:
    params = {"page": page} if page else None
    try:
        return await fetch_specialists(params)
    except httpx.HTTPStatusError as e:
        # пробрасываем статус внешнего API (401, 404 и т.д.)
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Внешний API вернул ошибку: {e.response.text[:300]}",
        )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Внешний API не ответил вовремя")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Ошибка запроса к внешнему API: {e}")
    except ValueError:
        raise HTTPException(status_code=502, detail="Внешний API вернул не JSON")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)