import axios from 'axios';
import { render, screen } from '@testing-library/react';
import App from '../App';
import { responseFor } from './fixtures';

jest.mock('axios');

it('renders the application and loads posts through the home route', async () => {
  jest.mocked(axios.get).mockImplementation((url: string) => Promise.resolve(responseFor(url)));
  render(<App />);
  expect(screen.getByRole('heading', { name: 'All Posts' })).toBeInTheDocument();
  expect(await screen.findAllByTestId('postcard')).toHaveLength(10);
});
