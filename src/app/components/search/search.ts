import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  imports: [FormsModule],
  selector: 'app-search',
  templateUrl: './search.html',
})

export class Search {
  product = ""
  empty_entry = false

  router = inject(Router)

  searchProduct(){
    const query = this.product.trim()

    if(query == ''){
      this.empty_entry = true
      return
    }

    this.empty_entry = false
    // the search term goes in the url: /products?q=leche
    this.router.navigate(['products'], { queryParams: { q: query } })
  }
}
