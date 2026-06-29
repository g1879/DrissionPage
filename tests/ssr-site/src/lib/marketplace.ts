export type MarketplaceCategory = 'fashion' | 'digital' | 'home' | 'beauty' | 'sports' | 'food';
export type MarketplaceSort = 'relevance' | 'sales-desc' | 'price-asc' | 'price-desc';

export interface MarketplaceItem {
  id: number;
  title: string;
  category: MarketplaceCategory;
  shop: string;
  location: string;
  price: number;
  originalPrice: number;
  sales: number;
  rating: number;
  coupon: number;
  tags: string[];
  services: string[];
  colors: string[];
  specs: string[];
  heroColor: string;
}

export interface MarketplaceAddress {
  id: string;
  label: string;
  receiver: string;
  detail: string;
  phone: string;
  eta: string;
}

export interface MarketplacePayment {
  id: string;
  label: string;
  summary: string;
}

export interface MarketplaceInvoice {
  id: string;
  label: string;
}

const categories: MarketplaceCategory[] = ['fashion', 'digital', 'home', 'beauty', 'sports', 'food'];
const categoryLabels: Record<MarketplaceCategory, string> = {
  fashion: '潮流服饰',
  digital: '数码电器',
  home: '品质家居',
  beauty: '美妆个护',
  sports: '运动户外',
  food: '食品生鲜',
};

const titles: Record<MarketplaceCategory, string[]> = {
  fashion: ['通勤风短外套', '轻量云感运动鞋', '松弛感针织开衫', '高腰垂感阔腿裤'],
  digital: ['降噪蓝牙耳机', '便携快充移动电源', '超清护眼显示器', '智能桌面氛围灯'],
  home: ['奶油风收纳边柜', '恒温鹅绒被', '人体工学办公椅', '无涂层不粘煎锅'],
  beauty: ['温和净透洁面乳', '持妆柔雾粉底液', '修护精华面霜', '香氛身体护理套装'],
  sports: ['城市骑行冲锋衣', '专业瑜伽训练垫', '轻量徒步双肩包', '筋膜放松按摩器'],
  food: ['低温烘焙坚果礼盒', '精品挂耳咖啡组合', '原切牛排家庭装', '鲜果酸奶早餐杯'],
};

const shops = ['造物旗舰店', '橙盒优选', '云上百货', '山海生活馆', '每日新鲜铺'];
const locations = ['杭州', '上海', '广州', '深圳', '成都'];
const colors = ['奶油白', '曜石黑', '薄荷绿', '日落橙'];
const specs = ['标准款', '升级款', '礼盒装'];
const heroColors = ['#ff6a00', '#f97316', '#fb7185', '#8b5cf6', '#06b6d4', '#22c55e'];

export const marketplaceAddresses: MarketplaceAddress[] = [
  {
    id: 'addr-hangzhou',
    label: '公司地址',
    receiver: '测试买家',
    detail: '杭州市西湖区确定性路 88 号 12 层',
    phone: '138****0001',
    eta: '预计明日 18:00 前送达',
  },
  {
    id: 'addr-shanghai',
    label: '家中地址',
    receiver: '自动化用户',
    detail: '上海市浦东新区 Fixture Avenue 99 号',
    phone: '138****0002',
    eta: '预计 48 小时内送达',
  },
];

export const marketplacePayments: MarketplacePayment[] = [
  { id: 'mock-alipay', label: '合成钱包', summary: '模拟第三方支付，不跳转外部站点' },
  { id: 'mock-card', label: '测试银行卡', summary: '本地支付确认，返回确定性订单号' },
];

export const marketplaceInvoices: MarketplaceInvoice[] = [
  { id: 'personal', label: '个人电子发票' },
  { id: 'company', label: '企业电子发票' },
  { id: 'none', label: '暂不开票' },
];

export function marketplaceSteps(itemId = 2, orderId = 'TBMOCK-000001') {
  return [
    { label: '首页浏览', href: '/scenarios/marketplace', testid: 'marketplace-step-home' },
    { label: '搜索筛选', href: '/scenarios/marketplace/search?query=耳机', testid: 'marketplace-step-search' },
    { label: '商品详情', href: `/scenarios/marketplace/item/${itemId}`, testid: 'marketplace-step-item' },
    { label: '购物车', href: '/scenarios/marketplace/cart', testid: 'marketplace-step-cart' },
    { label: '结算下单', href: '/scenarios/marketplace/checkout', testid: 'marketplace-step-checkout' },
    { label: '订单结果', href: `/scenarios/marketplace/order-result?order=${encodeURIComponent(orderId)}`, testid: 'marketplace-step-result' },
  ];
}

export function marketplaceSubtotal(item: MarketplaceItem, quantity: number): number {
  return Number((item.price * quantity).toFixed(2));
}

export function categoryLabel(category: MarketplaceCategory): string {
  return categoryLabels[category];
}

export function makeMarketplaceItem(id: number): MarketplaceItem {
  const category = categories[(id - 1) % categories.length];
  const names = titles[category];
  const titleIndex = Math.floor((id - 1) / categories.length) % names.length;
  const title = `${categoryLabels[category]} ${names[titleIndex]} ${String(id).padStart(3, '0')}`;
  const price = 39 + ((id * 23) % 420) + (category === 'digital' ? 260 : 0);
  return {
    id,
    title,
    category,
    shop: shops[id % shops.length],
    location: locations[id % locations.length],
    price,
    originalPrice: price + 30 + (id % 5) * 12,
    sales: 1200 + id * 137,
    rating: Number((4.2 + (id % 8) / 10).toFixed(1)),
    coupon: 5 + (id % 4) * 10,
    tags: id % 2 === 0 ? ['618同款', '券后好价'] : ['新品首发', '回购榜'],
    services: ['七天无理由', '极速退款', id % 3 === 0 ? '次日达' : '包邮'],
    colors,
    specs,
    heroColor: heroColors[(id - 1) % heroColors.length],
  };
}

export function makeMarketplaceItems(count: number, offset = 0): MarketplaceItem[] {
  return Array.from({ length: count }, (_, index) => makeMarketplaceItem(offset + index + 1));
}

export function searchMarketplaceItems({
  query = '',
  category = 'all',
  sort = 'relevance',
  count = 24,
  offset = 0,
}: {
  query?: string;
  category?: MarketplaceCategory | 'all';
  sort?: MarketplaceSort;
  count?: number;
  offset?: number;
}): MarketplaceItem[] {
  const normalized = query.trim().toLowerCase();
  let items = makeMarketplaceItems(180).filter((item) => {
    const text = `${item.title} ${item.shop} ${item.location} ${item.tags.join(' ')}`.toLowerCase();
    const matchQuery = !normalized || text.includes(normalized) || item.id === Number(normalized);
    const matchCategory = category === 'all' || item.category === category;
    return matchQuery && matchCategory;
  });

  if (sort === 'sales-desc') items = items.sort((a, b) => b.sales - a.sales);
  if (sort === 'price-asc') items = items.sort((a, b) => a.price - b.price);
  if (sort === 'price-desc') items = items.sort((a, b) => b.price - a.price);

  return items.slice(offset, offset + count);
}

export function marketplaceSummary(items = makeMarketplaceItems(180)) {
  return {
    total: items.length,
    fashion: items.filter((item) => item.category === 'fashion').length,
    digital: items.filter((item) => item.category === 'digital').length,
    home: items.filter((item) => item.category === 'home').length,
    averagePrice: Math.round(items.reduce((sum, item) => sum + item.price, 0) / items.length),
  };
}
