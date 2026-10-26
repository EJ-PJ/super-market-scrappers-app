export interface Subcategory {
  name: string;
}

export interface Category {
  department: string;
  name: string;
  subcategory: Subcategory;
}

export interface Products {
  ListPrice: number;
  Price: number;
  brand: string;
  category: Category;
  description: string;
  img: string;
  offerHighlight: unknown[][];
  price: string;
  url: string;
}

export interface MaxiDespensa {
  products: Products[];
}

export interface Subcategory2 {
  name: string;
}

export interface Category2 {
  name: string;
  subcategory: Subcategory2;
}

export interface Products2 {
  category: Category2;
  description: string;
  img: string;
  offerHighlight: unknown[];
  price: number;
  price_offer: unknown;
  url: string;
}

export interface SuperFresh {
  products: Products2[];
}

export interface Data {
  maxi_despensa: MaxiDespensa;
  super_fresh: SuperFresh;
}

export interface Root {
  data: Data;
}
