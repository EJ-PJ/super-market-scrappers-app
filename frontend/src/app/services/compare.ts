import { computed, Service, signal } from '@angular/core';
import { Branch, Product } from '../../models/products';

// A product picked for the comparator. The store name and branch are copied when
// it is picked so it can still be shown after a new search (other stores / zone).
export interface CompareItem {
  product: Product;
  storeName: string;
  branch: Branch | null;
}

export const MAX_COMPARE = 4;

@Service()
export class Compare {
  readonly items = signal<CompareItem[]>([]);
  readonly ids = computed(() => this.items().map((item) => item.product.id));
  readonly full = computed(() => this.items().length >= MAX_COMPARE);
  // comparison table open / closed
  readonly open = signal(false);

  has(productId: string) {
    return this.ids().includes(productId);
  }

  toggle(item: CompareItem) {
    if (this.has(item.product.id)) {
      this.remove(item.product.id);
    } else if (!this.full()) {
      this.items.update((items) => [...items, item]);
    }
  }

  remove(productId: string) {
    this.items.update((items) => items.filter((item) => item.product.id !== productId));
    // nothing left to compare
    if (this.items().length < 2) {
      this.open.set(false);
    }
  }

  clear() {
    this.items.set([]);
    this.open.set(false);
  }
}
