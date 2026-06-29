export type SocialChannel = 'recommend' | 'fashion' | 'beauty' | 'food' | 'travel' | 'home' | 'digital' | 'fitness';
export type SocialAction = 'like' | 'collect' | 'follow' | 'share';

export interface SocialNote {
  id: string;
  title: string;
  channel: SocialChannel;
  author: string;
  city: string;
  likes: number;
  collects: number;
  comments: number;
  isVideo: boolean;
  coverColor: string;
  coverLabel: string;
  excerpt: string;
  tags: string[];
  aspect: 'tall' | 'square' | 'wide';
}

export interface SocialComment {
  id: string;
  author: string;
  text: string;
  likes: number;
}

export const socialChannels: Array<{ id: SocialChannel; label: string }> = [
  { id: 'recommend', label: '推荐' },
  { id: 'fashion', label: '穿搭' },
  { id: 'beauty', label: '美妆' },
  { id: 'food', label: '美食' },
  { id: 'travel', label: '旅行' },
  { id: 'home', label: '居家' },
  { id: 'digital', label: '数码' },
  { id: 'fitness', label: '运动' },
];

const titles: Record<SocialChannel, string[]> = {
  recommend: ['周末松弛感生活记录', '通勤包里有什么', '新手也能完成的房间改造', '城市散步路线收藏'],
  fashion: ['早八通勤胶囊衣橱', '小个子显高公式', '雨天轻户外穿搭', '一衣多穿实验'],
  beauty: ['清透底妆步骤复盘', '敏感肌夜间护理', '空瓶精简护肤清单', '快速出门妆容'],
  food: ['十分钟早餐盘', '低卡便当备餐', '街角咖啡探店', '空气炸锅家常菜'],
  travel: ['两天一夜城市旅行', '海边日落机位', '博物馆路线笔记', '周边徒步补给'],
  home: ['小户型收纳动线', '桌面氛围灯布置', '厨房清洁清单', '租房软装改造'],
  digital: ['轻办公设备清单', '手机摄影参数记录', '桌面效率工具', '耳机通勤体验'],
  fitness: ['下班后拉伸流程', '新手力量训练计划', '晨跑装备清单', '瑜伽垫核心训练'],
};

const authors = ['南城记录员', '橙子实验室', '慢慢生活家', '半糖笔记', '山海同学', '晴天编辑部'];
const cities = ['上海', '杭州', '广州', '成都', '深圳', '南京'];
const colors = ['#fb7185', '#f97316', '#a855f7', '#06b6d4', '#22c55e', '#eab308', '#64748b', '#ec4899'];
const aspects: SocialNote['aspect'][] = ['tall', 'square', 'wide', 'tall'];

export function socialSteps(noteId = 'note-002') {
  return [
    { label: '移动首页', href: '/scenarios/social-notes', testid: 'social-step-home' },
    { label: '瀑布流筛选', href: '/scenarios/social-notes?channel=food', testid: 'social-step-feed' },
    { label: '笔记详情', href: `/scenarios/social-notes/note/${noteId}`, testid: 'social-step-detail' },
    { label: '评论互动', href: '/scenarios/social-notes#comments', testid: 'social-step-comments' },
    { label: '安全落地页', href: '/scenarios/social-notes/security-check?original=/explore/note-404', testid: 'social-step-security' },
  ];
}

export function channelLabel(channel: SocialChannel): string {
  return socialChannels.find((item) => item.id === channel)?.label || '推荐';
}

export function makeSocialNote(index: number): SocialNote {
  const channel = socialChannels[index % socialChannels.length].id;
  const titleList = titles[channel];
  const title = `${titleList[Math.floor(index / socialChannels.length) % titleList.length]} ${String(index + 1).padStart(3, '0')}`;
  return {
    id: `note-${String(index + 1).padStart(3, '0')}`,
    title,
    channel,
    author: authors[index % authors.length],
    city: cities[index % cities.length],
    likes: 80 + index * 17,
    collects: 20 + index * 7,
    comments: 3 + (index % 12),
    isVideo: index % 5 === 0,
    coverColor: colors[index % colors.length],
    coverLabel: channelLabel(channel),
    excerpt: `合成社区笔记内容 ${String(index + 1).padStart(3, '0')}，用于移动端瀑布流、详情弹层、点赞收藏和评论流程测试。`,
    tags: [`#${channelLabel(channel)}`, index % 2 === 0 ? '#新手友好' : '#真实体验', index % 3 === 0 ? '#清单' : '#记录'],
    aspect: aspects[index % aspects.length],
  };
}

export function makeSocialNotes(count: number, offset = 0): SocialNote[] {
  return Array.from({ length: count }, (_, index) => makeSocialNote(offset + index));
}

export function getSocialNote(id: string): SocialNote {
  const num = Math.max(Number(id.replace(/\D/g, '')) || 1, 1);
  return makeSocialNote(num - 1);
}

export function searchSocialNotes({
  query = '',
  channel = 'recommend',
  count = 20,
  offset = 0,
}: {
  query?: string;
  channel?: SocialChannel | 'all';
  count?: number;
  offset?: number;
}): SocialNote[] {
  const normalized = query.trim().toLowerCase();
  const all = makeSocialNotes(160);
  const filtered = all.filter((note) => {
    const text = `${note.title} ${note.author} ${note.city} ${note.tags.join(' ')}`.toLowerCase();
    const matchQuery = !normalized || text.includes(normalized) || note.id.toLowerCase().includes(normalized);
    const matchChannel = channel === 'recommend' || channel === 'all' || note.channel === channel;
    return matchQuery && matchChannel;
  });
  return filtered.slice(offset, offset + count);
}

export function makeSocialComments(noteId: string, count = 4): SocialComment[] {
  const seed = Math.max(Number(noteId.replace(/\D/g, '')) || 1, 1);
  return Array.from({ length: count }, (_, index) => ({
    id: `${noteId}-comment-${index + 1}`,
    author: authors[(seed + index) % authors.length],
    text: ['这个路线很实用', '收藏了，周末试试', '细节写得很清楚', '求一个完整清单'][index % 4],
    likes: seed + index * 3,
  }));
}
