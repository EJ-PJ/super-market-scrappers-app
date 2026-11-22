// Same shape the Flask backend returns in GET /api/v1/products
// (backend: app/models/product.py and app/services/product_service.py)

export interface ProductCategory {
  department: string | null;
  category: string | null;
  subcategory: string | null;
}

export interface Promotion {
  // bundle: "2 x Q20", combo: "Combina 3 x Q30", badge: "Precio bajo exclusivo en línea"
  type: 'bundle' | 'combo' | 'badge' | string;
  label: string;
  [key: string]: unknown;
}

export interface Product {
  id: string; // "<store>:<product id>"
  store: string; // store id, e.g. "maxi_despensa"
  name: string | null;
  brand: string | null;
  price: number | null; // what you pay today (with discount)
  regular_price: number | null; // price before discount
  discount_percent: number;
  currency: string;
  available: boolean; // false = out of stock or without price
  promotions: Promotion[];
  image: string | null;
  url: string | null;
  category: ProductCategory;
}

// Store (branch) used for the chosen postal code
export interface Branch {
  name: string | null;
  address: string | null; // La Torre doesn't publish addresses
  distance_km: number | null; // from the chosen zone
}

export interface StoreStatus {
  id: string;
  name: string;
  ok: boolean; // false = the store failed, the others still return products
  count: number;
  error: string | null;
  branch: Branch | null; // null = no location chosen (default prices) or the store failed
}

export interface SearchResponse {
  query: string;
  page: number;
  page_size: number;
  stores: StoreStatus[];
  products: Product[];
}

export interface Store {
  id: string;
  name: string;
}
