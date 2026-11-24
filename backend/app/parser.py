import re
from typing import Optional

from bs4 import BeautifulSoup, Tag
from schemas.doctor import Doctor

def _text(node: Optional[Tag]) -> Optional[str]:
    """Текст элемента без лишних пробелов (включая неразрывные)."""
    if node is None:
        return None
    return " ".join(node.get_text(" ", strip=True).replace("\xa0", " ").split()) or None


def _first_int(value: Optional[str]) -> Optional[int]:
    """Достаёт первое число из строки, учитывая пробелы-разделители тысяч: '3 550 ₽' -> 3550."""
    if not value:
        return None
    digits = re.sub(r"[^\d]", "", value)
    return int(digits) if digits else None


def _parse_card(card: Tag) -> Doctor:
    """Разбор одного тега article.doctor-card (тело прежней parse_doctor_card)."""
    link = card.select_one("h3 a")
    name = _text(link) or _text(card.select_one("h3"))
    if not name:
        raise ValueError("Не удалось определить имя врача")
    profile_url = link.get("href") if link else None

    slug, doctor_id = None, None
    if profile_url:
        slug = profile_url.rstrip("/").rsplit("/", 1)[-1]
        m = re.search(r"-(\d+)$", slug)
        doctor_id = int(m.group(1)) if m else None

    img = card.select_one("img")
    photo_url = img.get("src") if img else None

    specialty = _text(card.select_one("h3 + p"))

    experience_years = None
    for p in card.select("p"):
        t = _text(p) or ""
        if t.lower().startswith("стаж"):
            experience_years = _first_int(t)
            break

    rating = None
    rating_node = card.select_one("strong")
    if rating_node and rating_node.find_previous_sibling("span", class_="text-amber-500"):
        try:
            rating = float((_text(rating_node) or "").replace(",", "."))
        except ValueError:
            rating = None

    reviews_count = None
    for span in card.select("span"):
        t = _text(span) or ""
        if "отзыв" in t:
            reviews_count = _first_int(t)
            break

    clinic = _text(card.select_one("p.truncate"))

    price_from = None
    for strong in card.select("strong"):
        t = _text(strong) or ""
        if "₽" in t or t.lower().startswith("от"):
            price_from = _first_int(t)
            break

    return Doctor(
        id=doctor_id, name=name, slug=slug, specialty=specialty,
        experience_years=experience_years, rating=rating,
        reviews_count=reviews_count, clinic=clinic, price_from=price_from,
        photo_url=photo_url, profile_url=profile_url,
    )


def parse_doctor_card(html: str) -> Doctor:
    card = BeautifulSoup(html, "html.parser").select_one("article.doctor-card")
    if card is None:
        raise ValueError("Элемент article.doctor-card не найден")
    return _parse_card(card)


def parse_doctors_list(html: str) -> list[Doctor]:
    """Все карточки врачей на одной странице каталога."""
    soup = BeautifulSoup(html, "html.parser")
    doctors = []
    for card in soup.select("article.doctor-card"):
        try:
            doctors.append(_parse_card(card))
        except ValueError:
            continue  # битую карточку пропускаем, остальные не теряем
    return doctors