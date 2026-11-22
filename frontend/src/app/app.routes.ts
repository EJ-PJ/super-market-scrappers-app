import { Routes } from '@angular/router';
import { ShowProducts } from './components/show-products/show-products';
import { Search } from './components/search/search';

export const routes: Routes = [
  {path:'products', component:ShowProducts},
  {path:'', component:Search}
];
