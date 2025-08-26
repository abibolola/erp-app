import { describe, it, expect, beforeEach } from 'vitest';
import use_auth_store from '../shared/stores/use_auth_store';

describe('Authentication Store', () => {
  beforeEach(() => {
    use_auth_store.setState({
      user: null,
      is_authenticated: false,
      error: null
    });
  });

  it('should handle successful login', async () => {
    // Mock the API call
    const result = await use_auth_store.getState().login(
      'test@example.com',
      'password',
      'web'
    );
    
    expect(result.success).toBe(true);
  });
});