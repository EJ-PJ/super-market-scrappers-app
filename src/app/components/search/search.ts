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
    if(this.product == ''){
      this.empty_entry = true
      console.log('this is empty');

    } else {
      console.log('this was press ');
      this.router.navigate(['products'])
    }
    this.product = ""
  }
}
