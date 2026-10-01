export const posts = Array.from({ length: 10 }, (_, index) => ({
  _id: `post-${index}`,
  title: `Travel story ${index}`,
  authorName: 'Test Author',
  imageLink: 'https://example.com/travel.jpg',
  description: 'Deterministic travel story for component tests.',
  categories: index < 3 ? ['Nature'] : ['Travel'],
  isFeaturedPost: index < 5,
  timeOfPost: '2026-09-01T12:00:00.000Z',
}));

export function responseFor(url: string) {
  if (url.endsWith('/api/posts/featured')) return { data: posts.filter(p => p.isFeaturedPost) };
  if (url.endsWith('/api/posts/latest')) return { data: [...posts].reverse() };
  if (url.endsWith('/api/posts/categories/Nature')) return { data: posts.filter(p => p.categories.includes('Nature')) };
  if (url.endsWith('/api/posts')) return { data: posts };
  throw new Error(`Unexpected test request: ${url}`);
}
