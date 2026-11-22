import { Component, computed, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { CurrencyPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { Subscription } from 'rxjs';
import { Products } from '../../services/products';
import { Product, StoreStatus } from '../../../models/products';

type SortOption = 'relevance' | 'price-asc' | 'price-desc' | 'discount';

const PAGE_SIZE = 20;

@Component({
  imports: [CurrencyPipe, FormsModule, RouterLink],
  selector: 'app-show-products',
  templateUrl: './show-products.html',
})
export class ShowProducts {
  private productsService = inject(Products);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private destroyRef = inject(DestroyRef);
  private request?: Subscription;

  // search bar on top of the grid
  searchText = '';

  query = signal('');
  page = signal(1);
  products = signal<Product[]>([]);
  stores = signal<StoreStatus[]>([]);
  loading = signal(false);
  loadingMore = signal(false);
  error = signal<string | null>(null);
  // true while at least one store returned a full page
  hasMore = signal(false);

  // filters ('' = every store)
  selectedStore = signal('');
  sort = signal<SortOption>('relevance');

  failedStores = computed(() => this.stores().filter((store) => !store.ok));

  storeNames = computed(() => {
    const names: Record<string, string> = {};
    for (const store of this.stores()) {
      names[store.id] = store.name;
    }
    return names;
  });

  visibleProducts = computed(() => {
    const store = this.selectedStore();
    let list = this.products().filter((product) => !store || product.store === store);

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
    // a new ?q= in the url = a new search
    this.route.queryParamMap.pipe(takeUntilDestroyed(this.destroyRef)).subscribe((params) => {
      const query = (params.get('q') ?? '').trim();
      this.searchText = query;
      this.query.set(query);
      this.selectedStore.set('');
      this.load(1);
    });
  }

  search() {
    const query = this.searchText.trim();
    if (query) {
      this.router.navigate(['products'], { queryParams: { q: query } });
    }
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
    }

    this.request = this.productsService.searchProducts(query, [], page, PAGE_SIZE).subscribe({
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
