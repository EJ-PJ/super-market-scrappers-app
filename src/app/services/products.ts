import { HttpClient } from '@angular/common/http';
import { inject, Service } from '@angular/core';
import { map } from 'rxjs';
import { SearchResponse, Store } from '../../models/products';

// Full URL (not '/api/v1' + proxy): the proxy only exists in "ng serve",
// Electron loads the app from file:// and needs the real backend address
const API_URL = 'http://127.0.0.1:5000/api/v1';

@Service()
export class Products {
  private http = inject(HttpClient);

  // Without stores the backend searches in every supermarket
  searchProducts(query: string, stores: string[] = [], page = 1, pageSize = 20) {
    const params: Record<string, string> = {
      q: query,
      page: String(page),
      page_size: String(pageSize),
    };
    if (stores.length) {
      params['stores'] = stores.join(',');
    }
    return this.http.get<SearchResponse>(`${API_URL}/products`, { params });
  }

  getStores() {
    return this.http
      .get<{ stores: Store[] }>(`${API_URL}/stores`)
      .pipe(map((response) => response.stores));
  }
}
