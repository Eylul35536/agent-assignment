from __future__ import annotations
import random
from datetime import date, timedelta
from typing import Any

_BOOKINGS: dict = {}
_REMINDERS: list = []

_CATALOGUE = [
    {"id": "dent-001", "category": "dentist", "city": "Warsaw", "name": "Smile Dental Clinic", "address": "ul. Marszalkowska 12", "price_pln": 150, "rating": 4.8},
    {"id": "dent-002", "category": "dentist", "city": "Warsaw", "name": "DentaCare Centre", "address": "ul. Nowy Swiat 45", "price_pln": 120, "rating": 4.5},
    {"id": "dent-003", "category": "dentist", "city": "Warsaw", "name": "PerfectSmile", "address": "ul. Pulawska 78", "price_pln": 100, "rating": 4.2},
    {"id": "cow-001", "category": "coworking", "city": "Warsaw", "name": "Brain Embassy", "address": "ul. Konstruktorska 11", "price_usd_day": 18, "rating": 4.7},
    {"id": "cow-002", "category": "coworking", "city": "Warsaw", "name": "The Refinery", "address": "ul. Woloska 9", "price_usd_day": 15, "rating": 4.4},
    {"id": "cow-003", "category": "coworking", "city": "Warsaw", "name": "CitySpace", "address": "ul. Emilii Plater 53", "price_usd_day": 20, "rating": 4.6},
    {"id": "cow-004", "category": "coworking", "city": "Warsaw", "name": "Deskimo Hub", "address": "ul. Zlota 59", "price_usd_day": 12, "rating": 4.1},
    {"id": "hot-001", "category": "hotel", "city": "Prague", "name": "Old Town Hotel", "address": "Stare Mesto, Prague", "price_eur_night": 65, "rating": 4.5},
    {"id": "hot-002", "category": "hotel", "city": "Prague", "name": "Prague Hostel Hub", "address": "Zizkov, Prague", "price_eur_night": 20, "rating": 4.2},
    {"id": "hot-003", "category": "hotel", "city": "Prague", "name": "Apartman Vltava", "address": "Mala Strana, Prague", "price_eur_night": 55, "rating": 4.7},
    {"id": "trn-001", "category": "transport", "city": "Warsaw-Prague", "name": "RegioJet bus Warsaw-Prague", "price_eur": 25, "rating": 4.3},
    {"id": "trn-002", "category": "transport", "city": "Warsaw-Prague", "name": "FlixBus Warsaw-Prague", "price_eur": 18, "rating": 4.0},
]

def calendar_check(start_date: str, end_date: str) -> dict:
    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except ValueError as exc:
        return {"ok": False, "error": f"Invalid date: {exc}"}
    free, busy = [], []
    current = start
    while current <= end:
        if current.weekday() < 5:
            busy_hours = set(random.sample(range(9, 20), k=random.randint(2, 5)))
            for h in range(9, 20):
                slot = f"{current.isoformat()} {h:02d}:00"
                (busy if h in busy_hours else free).append(slot)
        current += timedelta(days=1)
    return {"ok": True, "free_slots": free[:15], "busy_slots": busy[:10]}

def search_service(query: str, category: str = None, city: str = None, max_price: float = None) -> dict:
    results = list(_CATALOGUE)
    if category:
        results = [r for r in results if r["category"].lower() == category.lower()]
    if city:
        results = [r for r in results if city.lower() in r["city"].lower()]
    if max_price is not None:
        filtered = []
        for r in results:
            price = r.get("price_usd_day") or r.get("price_eur_night") or r.get("price_eur") or r.get("price_pln", 9999)
            if price <= max_price:
                filtered.append(r)
        results = filtered
    if not results and query:
        kw = query.lower()
        results = [r for r in _CATALOGUE if kw in r["name"].lower() or kw in r.get("city","").lower() or kw in r["category"].lower()]
    if not results:
        return {"ok": True, "results": [], "total": 0, "note": "No results. Try broader filters."}
    return {"ok": True, "results": results[:5], "total": len(results)}

def booking_service(option_id: str, when: str = None, notes: str = None) -> dict:
    option = next((r for r in _CATALOGUE if r["id"] == option_id), None)
    if option is None:
        return {"ok": False, "error": f"Unknown option_id '{option_id}'. Call search_service first."}
    if random.random() < 0.10:
        return {"ok": False, "error": "Booking service temporarily unavailable. Please retry."}
    conf_id = f"BK-{random.randint(10000000, 99999999)}"
    _BOOKINGS[conf_id] = {"option": option, "when": when}
    return {"ok": True, "confirmation_id": conf_id, "message": f"Booked '{option['name']}'" + (f" for {when}" if when else "") + f". Confirmation: {conf_id}"}

def reminder_create(title: str, when: str, notes: str = None) -> dict:
    if not title or not when:
        return {"ok": False, "error": "title and when are required."}
    rem_id = f"REM-{random.randint(10000, 99999)}"
    _REMINDERS.append({"id": rem_id, "title": title, "when": when})
    return {"ok": True, "reminder_id": rem_id, "message": f"Reminder '{title}' set for {when}. ID: {rem_id}"}

TOOL_FUNCTIONS = {
    "calendar_check": calendar_check,
    "search_service": search_service,
    "booking_service": booking_service,
    "reminder_create": reminder_create,
}

TOOL_SCHEMAS = [
    {"name": "calendar_check", "description": "List free and busy time slots for a date range.", "input_schema": {"type": "object", "properties": {"start_date": {"type": "string", "description": "ISO date e.g. 2025-06-10"}, "end_date": {"type": "string", "description": "ISO date e.g. 2025-06-14"}}, "required": ["start_date", "end_date"]}},
    {"name": "search_service", "description": "Search for dentists, coworking spaces, hotels, or transport. Returns option_ids for booking.", "input_schema": {"type": "object", "properties": {"query": {"type": "string"}, "category": {"type": "string", "description": "dentist | coworking | hotel | transport"}, "city": {"type": "string"}, "max_price": {"type": "number"}}, "required": ["query"]}},
    {"name": "booking_service", "description": "Book an option from search_service using its option_id.", "input_schema": {"type": "object", "properties": {"option_id": {"type": "string"}, "when": {"type": "string"}, "notes": {"type": "string"}}, "required": ["option_id"]}},
    {"name": "reminder_create", "description": "Create a reminder for the user.", "input_schema": {"type": "object", "properties": {"title": {"type": "string"}, "when": {"type": "string"}, "notes": {"type": "string"}}, "required": ["title", "when"]}},
    {"name": "ask_user", "description": "Ask the user ONE clarifying question when you cannot proceed without their input.", "input_schema": {"type": "object", "properties": {"question": {"type": "string"}}, "required": ["question"]}},
]