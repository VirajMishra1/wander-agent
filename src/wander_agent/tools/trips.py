"""Trip memory tools — save trips, track booking checklists across sessions."""

from __future__ import annotations

from ..utils import trip_store


async def save_trip(
    destination: str,
    depart_date: str | None = None,
    return_date: str | None = None,
    origin: str | None = None,
    travelers: int = 1,
    passport_country: str | None = None,
    purpose: str | None = None,
    notes: str | None = None,
) -> dict:
    trip = trip_store.create_trip(
        destination=destination,
        depart_date=depart_date,
        return_date=return_date,
        origin=origin,
        travelers=travelers,
        passport_country=passport_country,
        purpose=purpose,
        notes=notes,
    )
    return {
        "saved": True,
        "trip_id": trip["id"],
        "trip": trip,
        "progress": trip_store.checklist_progress(trip),
        "tip": "Reference this trip_id later to update its checklist or shortlist options.",
    }


async def list_my_trips(status: str | None = None) -> dict:
    trips = trip_store.list_trips(status=status)
    return {
        "count": len(trips),
        "status_filter": status or "all",
        "trips": [
            {
                "trip_id": t["id"],
                "destination": t["destination"],
                "depart_date": t.get("depart_date"),
                "return_date": t.get("return_date"),
                "status": t.get("status"),
                "progress": trip_store.checklist_progress(t),
            }
            for t in trips
        ],
    }


async def get_trip_status(trip_id: str | None = None, destination: str | None = None) -> dict:
    trip = None
    if trip_id:
        trip = trip_store.get_trip(trip_id)
    elif destination:
        trip = trip_store.find_trip_by_destination(destination)
    if not trip:
        return {"error": "Trip not found. Pass a valid trip_id or destination."}
    return {
        "trip": trip,
        "progress": trip_store.checklist_progress(trip),
    }


async def update_trip(
    trip_id: str,
    status: str | None = None,
    depart_date: str | None = None,
    return_date: str | None = None,
    notes: str | None = None,
    mark_done: str | None = None,
    mark_undone: str | None = None,
    checklist_note: str | None = None,
    shortlist_flight: dict | None = None,
    shortlist_hotel: dict | None = None,
) -> dict:
    trip = trip_store.get_trip(trip_id)
    if not trip:
        return {"error": f"No trip with id {trip_id}"}

    if any(v is not None for v in (status, depart_date, return_date, notes)):
        trip_store.update_trip(
            trip_id,
            status=status,
            depart_date=depart_date,
            return_date=return_date,
            notes=notes,
        )
    if mark_done:
        trip_store.set_checklist_item(trip_id, mark_done, True, checklist_note)
    if mark_undone:
        trip_store.set_checklist_item(trip_id, mark_undone, False, checklist_note)
    if shortlist_flight:
        trip_store.attach_option(trip_id, "flights", shortlist_flight)
    if shortlist_hotel:
        trip_store.attach_option(trip_id, "hotels", shortlist_hotel)

    trip = trip_store.get_trip(trip_id)
    return {
        "updated": True,
        "trip": trip,
        "progress": trip_store.checklist_progress(trip),
    }


async def delete_trip(trip_id: str) -> dict:
    ok = trip_store.delete_trip(trip_id)
    return {"deleted": ok, "trip_id": trip_id}
