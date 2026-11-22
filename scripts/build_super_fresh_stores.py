"""
Builds app/postal_code/super_fresh_stores.json: postal code -> closest Super Fresh store.

Super Fresh doesn't pick the store by postal code (the VTEX stores do), it only
gives its stores with coordinates and a coverage radius. So this script:
  1. Downloads the Super Fresh stores (POST /api/stores).
  2. Gets the coordinates of every municipality / zone of postal_code.json
     from OpenStreetMap (Nominatim). Only place names are sent.
  3. Picks the closest store inside its coverage radius (15 km) for each postal code.

Run it only when Super Fresh opens / closes stores (it takes ~10 minutes the first
time because Nominatim allows 1 request per second). Coordinates already in the
output file are reused, use --refresh to look them up again.

    cd supermarket-scrapper-backend
    .venv/bin/python scripts/build_super_fresh_stores.py

The output file can be edited by hand to fix a store assignment.
"""

import argparse
import json
import math
import sys
import time
import unicodedata
from datetime import date
from pathlib import Path

import requests

BACKEND_DIR = Path(__file__).resolve().parent.parent
POSTAL_CODE_FILE = BACKEND_DIR / "app" / "postal_code" / "postal_code.json"
OUTPUT_FILE = BACKEND_DIR / "app" / "postal_code" / "super_fresh_stores.json"

STORES_URL = "https://msf-api.gta.com.gt/api/stores"
STORES_HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://www.misuperfresh.com.gt",
    "Referer": "https://www.misuperfresh.com.gt/",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:154.0) Gecko/20100101 Firefox/154.0",
}

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
# Nominatim policy: identify the app and max 1 request per second
NOMINATIM_HEADERS = {"User-Agent": "supermarket-price-compare-geocoder/1.0"}
NOMINATIM_DELAY = 1.1

# store used when the user didn't pick a location (same as before)
DEFAULT_STORE = 2
# used if a store doesn't send coverage.distance
DEFAULT_COVERAGE_KM = 15


def display_name(key: str) -> str:
    return key.replace("_", " ")


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    return "".join(c for c in text if unicodedata.category(c) != "Mn").casefold()


def distance_km(lat1, lon1, lat2, lon2) -> float:
    # haversine: straight line distance on the earth
    lat1, lon1, lat2, lon2 = map(math.radians, (lat1, lon1, lat2, lon2))
    a = (math.sin((lat2 - lat1) / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
    return 6371 * 2 * math.asin(math.sqrt(a))


def fetch_stores() -> dict:
    response = requests.post(
        STORES_URL,
        json={"version": "5.1.6", "channel": "web", "type": 0},
        headers=STORES_HEADERS,
        timeout=30,
    )
    response.raise_for_status()

    stores = {}
    for store in response.json().get("store") or []:
        coords = (store.get("address") or {}).get("coords") or {}
        if coords.get("latitude") is None or coords.get("longitude") is None:
            continue
        stores[str(store["code"])] = {
            "name": store.get("name"),
            "address": (store.get("address") or {}).get("address"),
            "latitude": coords["latitude"],
            "longitude": coords["longitude"],
            "coverage_km": (store.get("coverage") or {}).get("distance") or DEFAULT_COVERAGE_KM,
        }
    return stores


class Geocoder:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(NOMINATIM_HEADERS)
        self.cache = {}

    def search(self, **params):
        key = json.dumps(params, sort_keys=True)
        if key in self.cache:
            return self.cache[key]

        time.sleep(NOMINATIM_DELAY)
        response = self.session.get(
            NOMINATIM_URL,
            params={**params, "format": "jsonv2", "limit": 1, "countrycodes": "gt"},
            timeout=30,
        )
        response.raise_for_status()
        results = response.json()
        result = results[0] if results else None
        self.cache[key] = result
        return result

    def municipality(self, department: str, municipality: str):
        result = (self.search(city=municipality, state=department, country="Guatemala")
                  or self.search(q=f"{municipality}, {department}, Guatemala"))
        return to_coords(result)

    def area(self, municipality: str, area: str):
        # Guatemala City zones are "Zona 10, Ciudad de Guatemala" in OpenStreetMap
        city = "Ciudad de Guatemala" if normalize(municipality) == "guatemala" else municipality
        result = self.search(q=f"{area}, {city}, Guatemala")
        # make sure it's the zone of this municipality and not one with the same name
        if result and normalize(municipality) in normalize(result.get("display_name", "")):
            return to_coords(result)
        return None


def to_coords(result):
    if not result:
        return None
    return {"latitude": float(result["lat"]), "longitude": float(result["lon"])}


def places(postal_codes: dict):
    # (postal_code, department, municipality, area or None)
    for department_key, municipalities in postal_codes.items():
        for municipality_key, value in municipalities.items():
            if isinstance(value, dict):
                for area_key, code in value.items():
                    # Villa Nueva has a code for the whole municipality under its own name
                    area = None if area_key == municipality_key else display_name(area_key)
                    yield str(code), display_name(department_key), display_name(municipality_key), area
            else:
                yield str(value), display_name(department_key), display_name(municipality_key), None


def closest_store(coords, stores):
    best = None
    for code, store in stores.items():
        km = distance_km(coords["latitude"], coords["longitude"], store["latitude"], store["longitude"])
        if km <= store["coverage_km"] and (best is None or km < best[1]):
            best = (code, km)
    return best


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--refresh", action="store_true", help="look up every coordinate again")
    args = parser.parse_args()

    postal_codes = json.loads(POSTAL_CODE_FILE.read_text(encoding="utf-8"))

    previous = {}
    if OUTPUT_FILE.exists() and not args.refresh:
        previous = json.loads(OUTPUT_FILE.read_text(encoding="utf-8")).get("postal_codes", {})

    print("Downloading Super Fresh stores...")
    stores = fetch_stores()
    print(f"  {len(stores)} stores")

    geocoder = Geocoder()
    municipality_coords = {}
    result = {}
    all_places = list(places(postal_codes))

    for index, (code, department, municipality, area) in enumerate(all_places, 1):
        place = ", ".join(p for p in (area, municipality, department) if p)
        old = previous.get(code)

        if old and old.get("place") == place and old.get("latitude") is not None:
            coords = {"latitude": old["latitude"], "longitude": old["longitude"]}
            approximate = old.get("approximate", False)
        else:
            coords, approximate = None, False
            if area:
                coords = geocoder.area(municipality, area)
            if coords is None:
                # zone not found: use the municipality center
                key = (department, municipality)
                if key not in municipality_coords:
                    municipality_coords[key] = geocoder.municipality(department, municipality)
                coords = municipality_coords[key]
                approximate = bool(area) and coords is not None

        entry = {
            "place": place,
            "latitude": coords["latitude"] if coords else None,
            "longitude": coords["longitude"] if coords else None,
            # true = zone not found, the municipality center was used
            "approximate": approximate,
            "store": None,
            "distance_km": None,
        }
        if coords:
            best = closest_store(coords, stores)
            if best:
                entry["store"] = int(best[0])
                entry["distance_km"] = round(best[1], 1)
        result[code] = entry

        store_text = f"-> {stores[str(entry['store'])]['name']} ({entry['distance_km']} km)" if entry["store"] else ""
        print(f"[{index}/{len(all_places)}] {code} {place} {'(no coords)' if not coords else ''}{store_text}")

    output = {
        "_comment": "Generated by scripts/build_super_fresh_stores.py. 'store' can be edited by hand.",
        "generated_at": date.today().isoformat(),
        "default_store": DEFAULT_STORE,
        "stores": stores,
        "postal_codes": result,
    }
    OUTPUT_FILE.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    with_store = sum(1 for e in result.values() if e["store"])
    without_coords = sum(1 for e in result.values() if e["latitude"] is None)
    print(f"\nSaved {OUTPUT_FILE.relative_to(BACKEND_DIR)}")
    print(f"  {len(result)} postal codes, {with_store} with a Super Fresh store, {without_coords} without coordinates")


if __name__ == "__main__":
    sys.exit(main())
