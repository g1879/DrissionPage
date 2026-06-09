export type ProductCategory = 'electronics' | 'apparel' | 'home' | 'outdoor';
export type StockState = 'in_stock' | 'low_stock' | 'sold_out';

export interface Product {
  id: number;
  sku: string;
  title: string;
  category: ProductCategory;
  price: number;
  rating: number;
  stock: StockState;
  variants: string[];
}

const categories: ProductCategory[] = ['electronics', 'apparel', 'home', 'outdoor'];
const variantMap: Record<ProductCategory, string[]> = {
  electronics: ['standard', 'pro', 'max'],
  apparel: ['s', 'm', 'l'],
  home: ['oak', 'walnut', 'white'],
  outdoor: ['trail', 'camp', 'expedition'],
};

export function makeProduct(id: number): Product {
  const category = categories[(id - 1) % categories.length];
  const stock: StockState = id % 11 === 0 ? 'sold_out' : id % 5 === 0 ? 'low_stock' : 'in_stock';
  const price = 19 + ((id * 17) % 280) + (category === 'electronics' ? 80 : 0);
  const rating = 3.5 + ((id % 15) / 10);
  return {
    id,
    sku: `SKU-${String(id).padStart(4, '0')}`,
    title: `Fixture Product ${String(id).padStart(3, '0')}`,
    category,
    price,
    rating: Number(rating.toFixed(1)),
    stock,
    variants: variantMap[category],
  };
}

export function makeProducts(count: number, offset = 0): Product[] {
  return Array.from({ length: count }, (_, index) => makeProduct(offset + index + 1));
}

export function summarizeProducts(items: Product[]) {
  return {
    total: items.length,
    inStock: items.filter((item) => item.stock !== 'sold_out').length,
    soldOut: items.filter((item) => item.stock === 'sold_out').length,
    electronics: items.filter((item) => item.category === 'electronics').length,
    apparel: items.filter((item) => item.category === 'apparel').length,
    home: items.filter((item) => item.category === 'home').length,
    outdoor: items.filter((item) => item.category === 'outdoor').length,
  };
}
