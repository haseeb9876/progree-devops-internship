import { validCategories } from '../../utils/constants.js';

// Deliberate failure used only to demonstrate the deployment gate.
test('DEMO: an invalid category must not accidentally be accepted', () => {
  expect(validCategories).toContain('NotARealCategory');
});
