import { Component, computed, inject, output } from '@angular/core';
import { CurrencyPipe } from '@angular/common';
import { Compare } from '../../services/compare';
import { Product } from '../../../models/products';

// Side by side table of the products picked with "Comparar"
@Component({
  imports: [CurrencyPipe],
  selector: 'app-product-compare',
  templateUrl: './product-compare.html',
  host: { '(document:keydown.escape)': 'compare.open.set(false)' },
})
export class ProductCompare {
  compare = inject(Compare);

  // "Ver en tienda": the parent shows the location warning first
  visit = output<Product>();

  private priced = computed(() =>
    this.compare
      .items()
      .map((item) => item.product)
      .filter((product) => product.available && product.price != null),
  );

  // lowest price of the available products (null if fewer than 2 have a price)
  bestPrice = computed(() => {
    const prices = this.priced().map((product) => product.price!);
    return prices.length > 1 ? Math.min(...prices) : null;
  });

  isBest(product: Product) {
    return product.available && product.price != null && product.price === this.bestPrice();
  }

  // how much more than the cheapest one
  difference(product: Product) {
    const best = this.bestPrice();
    if (best == null || !product.available || product.price == null) {
      return null;
    }
    return product.price - best;
  }

  savings(product: Product) {
    if (product.price == null || !product.regular_price || product.regular_price <= product.price) {
      return null;
    }
    return product.regular_price - product.price;
  }

  categoryPath(product: Product) {
    const { department, category, subcategory } = product.category;
    return [department, category, subcategory].filter(Boolean).join(' › ') || null;
  }
}
