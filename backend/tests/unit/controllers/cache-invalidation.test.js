import Post from '../../../models/post.js';
import { createPostHandler, updatePostHandler, deletePostByIdHandler } from '../../../controllers/posts-controller.js';
import { deleteDataFromCache } from '../../../utils/cache-posts.js';
import { REDIS_KEYS } from '../../../utils/constants.js';
import { createPostObject } from '../../utils/helper-objects.js';

jest.mock('../../../models/post.js', () => ({ __esModule: true, default: jest.fn() }));
jest.mock('../../../utils/cache-posts.js', () => ({
  deleteDataFromCache: jest.fn().mockResolvedValue(undefined),
  storeDataInCache: jest.fn().mockResolvedValue(undefined),
}));

function response() { return { status: jest.fn().mockReturnThis(), json: jest.fn() }; }
function expectInvalidated() {
  expect(deleteDataFromCache.mock.calls.map(([key]) => key).sort()).toEqual(Object.values(REDIS_KEYS).sort());
}

test('create invalidates every list only after the database write succeeds', async () => {
  let finishWrite;
  const save = jest.fn(() => new Promise(resolve => { finishWrite = resolve; }));
  Post.mockImplementation(() => ({ save }));
  const res = response();
  const pending = createPostHandler({ body: createPostObject() }, res);
  expect(deleteDataFromCache).not.toHaveBeenCalled();
  finishWrite({ _id: 'new-post' });
  await pending;
  expectInvalidated();
  expect(res.status).toHaveBeenCalledWith(200);
});

test('update invalidates all list caches', async () => {
  Post.findByIdAndUpdate = jest.fn().mockResolvedValue({ _id: 'post', title: 'Updated' });
  await updatePostHandler({ params: { id: 'post' }, body: { title: 'Updated' } }, response());
  expectInvalidated();
});

test('delete invalidates all list caches', async () => {
  Post.findByIdAndDelete = jest.fn().mockResolvedValue({ _id: 'post' });
  await deletePostByIdHandler({ params: { id: 'post' } }, response());
  expectInvalidated();
});

test('missing post returns 404 without invalidating caches', async () => {
  Post.findByIdAndUpdate = jest.fn().mockResolvedValue(null);
  const res = response();
  await updatePostHandler({ params: { id: 'missing' }, body: {} }, res);
  expect(res.status).toHaveBeenCalledWith(404);
  expect(deleteDataFromCache).not.toHaveBeenCalled();
});

test('failed database write returns 500 without invalidating caches', async () => {
  Post.mockImplementation(() => ({ save: jest.fn().mockRejectedValue(new Error('Database unavailable')) }));
  const res = response();
  await createPostHandler({ body: createPostObject() }, res);
  expect(res.status).toHaveBeenCalledWith(500);
  expect(deleteDataFromCache).not.toHaveBeenCalled();
});
