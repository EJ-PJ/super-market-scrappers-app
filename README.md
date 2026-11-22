# Supermarket Scrapper

A desktop app to **compare supermarket prices in Guatemala**. Search a product once and see the results of five supermarkets side by side, with the prices of the branches that deliver to your zone.

| Store | Website | Prices by location |
|---|---|---|
| Maxi Despensa | maxidespensa.com.gt | ✅ |
| Paiz | paiz.com.gt | ✅ |
| Walmart | walmart.com.gt | ✅ |
| La Torre | latorre.com.gt | ✅ (same prices in every branch, no addresses) |
| Super Fresh | misuperfresh.com.gt | ✅ (closest store, see [Super Fresh stores](#super-fresh-stores)) |

## Features

- **One search, five stores.** The stores are searched in parallel. If a store is down or has no branch in your zone, the other stores still show their results and that store shows a warning.
- **Prices by location.** Pick a department, municipality and zone (e.g. *Guatemala → Guatemala → Zona 10*). Each store returns the prices and products of the branch that covers that postal code. The location is remembered between sessions.
- **Branches used.** The left sidebar shows which branch of each store was used, with its address and distance to your zone.
- **Filters.** The right sidebar lets you show or hide stores and filter by department / category, with live counts.
- **Sorting.** By relevance, price (low to high, high to low) or biggest discount.
- **Product cards.** Image, store, brand, current price, regular price with the discount percentage, promotions (e.g. *2 x Q20*) and a link to the product in the store website.
- **Desktop app.** Electron app for Linux (AppImage) and Windows (installer). It includes the backend, so Python is not needed to use it.

## How it works

```
┌──────────────────── Electron (desktop/) ────────────────────┐
│  main.js: picks a free port → starts the backend → opens    │
│  the window with the Angular build → stops the backend      │
│  when the app closes                                        │
│                                                             │
│   Angular (frontend/)  ──HTTP──►  Flask API (backend/)      │
│   search, filters,               packaged with PyInstaller  │
│   location picker                                           │
└─────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
            Store websites (VTEX GraphQL / Super Fresh API)
```

The backend follows a layered design, with one file per supermarket in each layer:

| Layer | Folder | Responsibility |
|---|---|---|
| 1. Get information | `app/clients/` | HTTP requests to each store (search, postal code → branch, branch address). |
| 2. Extract information | `app/parser/`, `app/scrapper/` | Convert each store's response into the common product format (`app/models/product.py`). |
| 3. Services | `app/services/` | Search the selected stores in parallel and merge the results. |
| 4. Routes | `app/routes/` | REST API used by the frontend. |

**Location.** `app/postal_code/postal_code.json` maps every department / municipality / zone of Guatemala to its postal code.
- **Maxi Despensa, Paiz, Walmart and La Torre** run on VTEX. Their `regions` endpoint turns the postal code into a branch, which is sent in the `vtex_segment` cookie so the search returns that branch's prices. The branch address comes from the VTEX `pickup-points` endpoint.
- **Super Fresh** has no postal code lookup, so a precomputed table assigns the closest store to each postal code (see [Super Fresh stores](#super-fresh-stores)).

## Project structure

```
supermarket-scrapper-app/
├── backend/     Flask API + scrapers (Python)
├── frontend/    Angular web app (TypeScript + Tailwind CSS)
└── desktop/     Electron app and installer build scripts
```

## Requirements

- **Python** 3.12+ (tested with 3.13)
- **Node.js** 22+ and npm (tested with Node 24)
- Internet connection: prices are read live from the store websites.

## Installation

```bash
git clone <repository-url> supermarket-scrapper-app
cd supermarket-scrapper-app
```

### Backend

```bash
cd backend
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt     # Windows: .venv\Scripts\python -m pip ...
cd ..
```

Optional: `backend/app/.env` with `FLASK_KEY=<random string>`. The app works without it.

### Frontend

```bash
cd frontend
npm install
cd ..
```

### Desktop app

```bash
cd backend && .venv/bin/python -m pip install pyinstaller && cd ..   # only needed to build installers
cd desktop
npm install
```

## Running

### As a web app (development)

Two terminals:

```bash
# 1. API on http://127.0.0.1:5000
cd backend
.venv/bin/python main.py

# 2. Angular on http://localhost:4200
cd frontend
npx ng serve -o
```

### As a desktop app (development)

```bash
cd desktop
npm start          # builds the frontend and opens Electron (uses backend/.venv)
npm run start:fast # opens Electron without rebuilding the frontend
```

## Building the installers

```bash
cd desktop
npm run dist
```

This builds the Angular app, packages the backend with PyInstaller and creates the installer in `desktop/dist/`:

| Platform | Output |
|---|---|
| Linux | `Supermarket Scrapper-<version>.AppImage` |
| Windows | `Supermarket Scrapper Setup <version>.exe` |

PyInstaller can't cross-compile: **build the Windows installer on Windows** and the Linux one on Linux. On Windows, use the same steps with `.venv\Scripts\python` instead of `.venv/bin/python`.

Single steps: `npm run build:frontend` (→ `desktop/renderer/`) and `npm run build:backend` (→ `desktop/dist-backend/`).

### Running the AppImage

AppImages need FUSE 2. On recent Debian / Ubuntu:

```bash
sudo apt install libfuse2t64
chmod +x "Supermarket Scrapper-1.0.0.AppImage"
./"Supermarket Scrapper-1.0.0.AppImage"
```

Without FUSE: `./"Supermarket Scrapper-1.0.0.AppImage" --appimage-extract-and-run`.

## API

Base URL: `http://127.0.0.1:5000/api/v1` (development).

| Endpoint | Description |
|---|---|
| `GET /products?q=leche` | Search products. Optional: `stores=maxi_despensa,paiz` (default: all), `page` (default 1), `page_size` (1–50, default 20), `postal_code=1010`. |
| `GET /stores` | Supported stores (`id`, `name`). |
| `GET /locations` | Departments → municipalities → zones with their postal codes. |
| `GET /search-postal-code?department=Guatemala&municipality=Guatemala&area=Zona_10` | Postal code of one place. |

Example response of `/products`:

```json
{
  "query": "leche",
  "page": 1,
  "page_size": 20,
  "postal_code": "1010",
  "stores": [
    {
      "id": "paiz", "name": "Paiz", "ok": true, "count": 20, "error": null,
      "branch": { "name": "PAÍZ PRADERA", "address": "20 calle 25-85 zona 10, Guatemala", "distance_km": 3.0 }
    }
  ],
  "products": [
    {
      "id": "paiz:33866",
      "store": "paiz",
      "name": "Leche Entera Suli UHT - 1 L",
      "brand": "SULI",
      "price": 11.6,
      "regular_price": 12.9,
      "discount_percent": 10,
      "currency": "GTQ",
      "available": true,
      "promotions": [{ "type": "bundle", "label": "2 x Q20" }],
      "image": "https://...",
      "url": "https://www.paiz.com.gt/.../p",
      "category": { "department": "Lácteos", "category": "Leche", "subcategory": "Leche Entera" }
    }
  ]
}
```

`price` is what you pay today; `regular_price` is the price before discount.

## Super Fresh stores

`backend/app/postal_code/super_fresh_stores.json` assigns to every postal code the closest Super Fresh store within its coverage radius (15 km). It also stores the coordinates of every zone, which are used to find the VTEX branch addresses.

The table is generated by a script that downloads the Super Fresh stores and geocodes every place of `postal_code.json` with OpenStreetMap (Nominatim). Run it again when Super Fresh opens or closes stores:

```bash
cd backend
.venv/bin/python scripts/build_super_fresh_stores.py           # reuses saved coordinates
.venv/bin/python scripts/build_super_fresh_stores.py --refresh # looks every place up again (~10 min)
```

The `store` value of any postal code can be edited by hand.

## Adding a supermarket

1. **Client** in `backend/app/clients/`: `search_products(...)`, and `get_region` / `get_branch` if the store uses locations. For VTEX stores, copy `paiz_client.py` and change `host`, `sales_channel`, `seller_prefix` and the search variables taken from the store's browser request.
2. **Parser** in `backend/app/parser/`: return a list of `make_product(...)`.
3. **Scrapper** in `backend/app/scrapper/`: `search_products(query, page, page_size, postal_code)` and `get_branch(postal_code)`.
4. **Register it** in `STORES` (`backend/app/services/product_service.py`). The frontend picks it up automatically.

## Limitations

- The data comes from the stores' own website APIs, which are **not public or documented**. A change on a store website can break that store until its client or parser is updated; the other stores keep working.
- Prices and stock can differ from the physical store. The *Ver en tienda* button warns that the store website has its own location selector.
- La Torre doesn't publish its branch addresses.
- Distances are measured from the center of the zone / municipality, not from an exact address.
