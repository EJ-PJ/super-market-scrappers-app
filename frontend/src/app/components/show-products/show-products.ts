import { Component, computed, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed, toObservable } from '@angular/core/rxjs-interop';
import { CurrencyPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { combineLatest, Subscription } from 'rxjs';
import { Products } from '../../services/products';
import { Location } from '../../services/location';
import { LocationPicker } from '../location-picker/location-picker';
import { ProductCompare } from '../product-compare/product-compare';
import { Compare, MAX_COMPARE } from '../../services/compare';
import { Product, StoreStatus } from '../../../models/products';

type SortOption = 'relevance' | 'price-asc' | 'price-desc' | 'discount';

// department -> category used by the sidebar
interface ProductGroup {
  department: string;
  category: string | null;
}

interface CategoryCount {
  name: string;
  count: number;
}

interface DepartmentCount {
  name: string;
  count: number;
  categories: CategoryCount[];
}

const OTHER = 'Otros';

// Super Fresh has no department, its "category" is the top level
function productGroup(product: Product): ProductGroup {
  const { department, category, subcategory } = product.category;
  if (department) {
    return { department, category: category ?? null };
  }
  if (category) {
    return { department: category, category: subcategory ?? null };
  }
  return { department: OTHER, category: null };
}

const PAGE_SIZE = 20;

@Component({
  imports: [CurrencyPipe, FormsModule, LocationPicker, ProductCompare],
  selector: 'app-show-products',
  templateUrl: './show-products.html',
})
export class ShowProducts {
  private productsService = inject(Products);
  location = inject(Location);
  compare = inject(Compare);
  readonly maxCompare = MAX_COMPARE;
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private destroyRef = inject(DestroyRef);
  private request?: Subscription;

  // search bar on top of the grid
  searchText = '';
  // location panel open / closed
  showLocation = signal(false);
  // product whose "Ver en tienda" was pressed, shows the location warning
  storeWarning = signal<Product | null>(null);

  query = signal('');
  page = signal(1);
  products = signal<Product[]>([]);
  stores = signal<StoreStatus[]>([]);
  loading = signal(false);
  loadingMore = signal(false);
  error = signal<string | null>(null);
  // true while at least one store returned a full page
  hasMore = signal(false);

  // sidebar filters: stores unchecked by the user, and the department / category clicked
  hiddenStores = signal<string[]>([]);
  selectedGroup = signal<ProductGroup | null>(null);
  sort = signal<SortOption>('relevance');

  // store warnings closed with the X (they come back on a new search)
  dismissedWarnings = signal<string[]>([]);

  failedStores = computed(() =>
    this.stores().filter((store) => !store.ok && !this.dismissedWarnings().includes(store.id)),
  );

  storeNames = computed(() => {
    const names: Record<string, string> = {};
    for (const store of this.stores()) {
      names[store.id] = store.name;
    }
    return names;
  });

  // products of the checked stores (used for the category counts)
  private storeFiltered = computed(() => {
    const hidden = this.hiddenStores();
    return this.products().filter((product) => !hidden.includes(product.store));
  });

  // products of the selected category (used for the store counts)
  private groupFiltered = computed(() => {
    const selected = this.selectedGroup();
    if (!selected) {
      return this.products();
    }
    return this.products().filter((product) => {
      const group = productGroup(product);
      return (
        group.department === selected.department &&
        (selected.category === null || group.category === selected.category)
      );
    });
  });

  // stores in the sidebar with how many products they have in the current category
  storeCounts = computed(() => {
    const counts: Record<string, number> = {};
    for (const product of this.groupFiltered()) {
      counts[product.store] = (counts[product.store] ?? 0) + 1;
    }
    return this.stores().map((store) => ({ ...store, shown: counts[store.id] ?? 0 }));
  });

  // departments -> categories of the checked stores, the biggest first
  departments = computed<DepartmentCount[]>(() => {
    const tree = new Map<string, { count: number; categories: Map<string, number> }>();
    for (const product of this.storeFiltered()) {
      const group = productGroup(product);
      const department = tree.get(group.department) ?? { count: 0, categories: new Map() };
      department.count++;
      if (group.category) {
        department.categories.set(group.category, (department.categories.get(group.category) ?? 0) + 1);
      }
      tree.set(group.department, department);
    }

    const byCount = (a: { count: number }, b: { count: number }) => b.count - a.count;
    return [...tree.entries()]
      .map(([name, value]) => ({
        name,
        count: value.count,
        categories: [...value.categories.entries()]
          .map(([category, count]) => ({ name: category, count }))
          .sort(byCount),
      }))
      .sort(byCount);
  });

  visibleProducts = computed(() => {
    const hidden = this.hiddenStores();
    let list = this.groupFiltered().filter((product) => !hidden.includes(product.store));

    const sort = this.sort();
    if (sort === 'relevance') {
      return list;
    }

    list = [...list];
    // products without price / out of stock always go at the end
    const noPrice = (p: Product) => (p.available && p.price != null ? 0 : 1);
    list.sort((a, b) => {
      if (noPrice(a) !== noPrice(b)) {
        return noPrice(a) - noPrice(b);
      }
      if (sort === 'price-asc') {
        return (a.price ?? 0) - (b.price ?? 0);
      }
      if (sort === 'price-desc') {
        return (b.price ?? 0) - (a.price ?? 0);
      }
      return b.discount_percent - a.discount_percent;
    });
    return list;
  });

  constructor() {
    // a new ?q= in the url or a new location = a new search
    combineLatest([this.route.queryParamMap, toObservable(this.location.postalCode)])
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(([params]) => {
        const query = (params.get('q') ?? '').trim();
        this.searchText = query;
        this.query.set(query);
        this.clearFilters();
        this.load(1);
      });
  }

  search() {
    const query = this.searchText.trim();
    if (query) {
      this.router.navigate(['products'], { queryParams: { q: query } });
    }
  }

  openStore(product: Product) {
    this.storeWarning.set(null);
    if (product.url) {
      window.open(product.url, '_blank', 'noopener');
    }
  }

  // "Comparar" checkbox of a product card
  toggleCompare(product: Product) {
    const store = this.stores().find((s) => s.id === product.store);
    this.compare.toggle({
      product,
      storeName: store?.name ?? product.store,
      branch: store?.branch ?? null,
    });
  }

  // empty slots of the compare bar
  compareSlots = computed(() =>
    Array.from({ length: MAX_COMPARE - this.compare.items().length }, (_, i) => i),
  );

  toggleStore(storeId: string) {
    this.hiddenStores.update((ids) =>
      ids.includes(storeId) ? ids.filter((id) => id !== storeId) : [...ids, storeId],
    );
  }

  // click the selected department / category again to remove the filter
  selectGroup(department: string, category: string | null = null) {
    const current = this.selectedGroup();
    const same = current?.department === department && current?.category === category;
    this.selectedGroup.set(same ? null : { department, category });
  }

  isDepartmentOpen(department: string) {
    return this.selectedGroup()?.department === department;
  }

  clearFilters() {
    this.hiddenStores.set([]);
    this.selectedGroup.set(null);
  }

  dismissWarning(storeId: string) {
    this.dismissedWarnings.update((ids) => [...ids, storeId]);
  }

  loadMore() {
    this.load(this.page() + 1);
  }

  private load(page: number) {
    // cancel a search that is still running (e.g. the user searched again)
    this.request?.unsubscribe();

    const query = this.query();
    if (!query) {
      this.products.set([]);
      this.stores.set([]);
      this.hasMore.set(false);
      return;
    }

    const firstPage = page === 1;
    this.loading.set(firstPage);
    this.loadingMore.set(!firstPage);
    this.error.set(null);
    if (firstPage) {
      this.products.set([]);
      this.stores.set([]);
      this.dismissedWarnings.set([]);
    }

    this.request = this.productsService
      .searchProducts(query, [], page, PAGE_SIZE, this.location.postalCode())
      .subscribe({
        next: (response) => {
          this.page.set(page);
          this.products.update((current) =>
            firstPage ? response.products : [...current, ...response.products],
          );
          // keep the store status of the first page if the next ones fail differently
          if (firstPage) {
            this.stores.set(response.stores);
          }
          this.hasMore.set(response.stores.some((store) => store.ok && store.count === PAGE_SIZE));
          this.loading.set(false);
          this.loadingMore.set(false);
        },
        error: (err) => {
          this.error.set(
            err.status === 0
              ? 'No se pudo conectar con el servidor. ¿Está corriendo el backend?'
              : err.error?.error || 'Ocurrió un error al buscar los productos',
          );
          this.loading.set(false);
          this.loadingMore.set(false);
        },
      });
  }
}
