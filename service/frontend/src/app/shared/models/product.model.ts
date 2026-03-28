export interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  image: string;
  stock: number;
  category?: string;
  /** Present on /products/bestsellers response */
  sold_count?: number;
}
