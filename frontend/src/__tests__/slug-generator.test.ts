import { createSlug } from '../utils/slug-generator';

test.each([
  ['A Trip To London', 'a-trip-to-london'],
  ['Nature & Adventure!', 'nature--adventure'],
  ['Mountain   Lake', 'mountain-lake'],
  ['Route 66', 'route-66'],
  ['', ''],
])('creates a stable post URL slug for %j', (title, expected) => {
  expect(createSlug(title)).toBe(expected);
});
