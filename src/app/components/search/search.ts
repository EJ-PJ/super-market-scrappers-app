import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  imports: [FormsModule],
  selector: 'app-search',
  templateUrl: './search.html',
})
export class Search {
  product = ""
  empty_entry = false

  searchProduct(){
    if(this.product == ''){
      this.empty_entry = true
    } else {

    }
  }

}
