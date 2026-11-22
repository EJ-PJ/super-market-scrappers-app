import { HttpClient } from '@angular/common/http';
import { computed, inject, Service, signal } from '@angular/core';
import { API_URL } from './products';

// Same shape the backend returns in GET /api/v1/locations (app/postal_code/postal_code.py)
// "key" is the original key of postal_code.json, "name" is for display
export interface Area {
  key: string;
  name: string;
  postal_code: string;
}

export interface Municipality {
  key: string;
  name: string;
  postal_code: string | null; // null = split by zones, the codes are in areas
  areas: Area[];
}

export interface Department {
  key: string;
  name: string;
  municipalities: Municipality[];
}

// What the user picked, saved in localStorage
export interface SelectedLocation {
  departmentKey: string;
  municipalityKey: string;
  areaKey: string | null;
  label: string; // "Zona 10, Guatemala" / "Antigua Guatemala, Sacatepéquez"
  postalCode: string;
}

const STORAGE_KEY = 'location';

function readStored(): SelectedLocation | null {
  try {
    const value = localStorage.getItem(STORAGE_KEY);
    return value ? (JSON.parse(value) as SelectedLocation) : null;
  } catch {
    return null; // storage blocked or broken value = no location
  }
}

@Service()
export class Location {
  private http = inject(HttpClient);

  private _departments = signal<Department[]>([]);
  private _loading = signal(false);
  private _error = signal<string | null>(null);
  private _selected = signal<SelectedLocation | null>(readStored());

  departments = this._departments.asReadonly();
  loading = this._loading.asReadonly();
  error = this._error.asReadonly();
  selected = this._selected.asReadonly();

  // what the products search sends to the backend
  postalCode = computed(() => this._selected()?.postalCode ?? null);

  // the tree is the same for the whole app, load it only once
  load() {
    if (this._departments().length || this._loading()) {
      return;
    }
    this._loading.set(true);
    this._error.set(null);
    this.http.get<{ locations: Department[] }>(`${API_URL}/locations`).subscribe({
      next: (response) => {
        this._departments.set(response.locations);
        this._loading.set(false);
      },
      error: () => {
        this._error.set('No se pudieron cargar las ubicaciones');
        this._loading.set(false);
      },
    });
  }

  // null = no location (default prices of each store)
  select(location: SelectedLocation | null) {
    this._selected.set(location);
    try {
      if (location) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(location));
      } else {
        localStorage.removeItem(STORAGE_KEY);
      }
    } catch {
      // storage blocked: the location still works until the app is closed
    }
  }
}
