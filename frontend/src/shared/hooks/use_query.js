import { useQuery as use_react_query } from '@tanstack/react-query';
import axios_instance from '../utils/axios';
import use_app_store from '../stores/use_app_store';

export const use_query = (key, url, options = {}) => {
  const { add_notification } = use_app_store();

  return use_react_query({
    queryKey: Array.isArray(key) ? key : [key],
    queryFn: async () => {
      try {
        const response = await axios_instance.get(url);
        return response.data;
      } catch (error) {
        const error_message = error.response?.data?.detail || 'Failed to fetch data';
        add_notification({
          type: 'error',
          message: error_message
        });
        throw error;
      }
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
    retry: 3,
    retryDelay: attempt_index => Math.min(1000 * 2 ** attempt_index, 30000),
    ...options
  });
};