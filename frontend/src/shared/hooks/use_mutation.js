import { useMutation as use_react_mutation, useQueryClient } from '@tanstack/react-query';
import axios_instance from '../utils/axios';
import use_app_store from '../stores/use_app_store';

export const use_mutation = (options = {}) => {
  const query_client = useQueryClient();
  const { add_notification } = use_app_store();

  return use_react_mutation({
    mutationFn: async ({ method = 'post', url, data }) => {
      const response = await axios_instance[method](url, data);
      return response.data;
    },
    onSuccess: (data, variables) => {
      // Invalidate related queries
      if (options.invalidate_queries) {
        options.invalidate_queries.forEach(key => {
          query_client.invalidateQueries(key);
        });
      }

      // Show success notification
      if (options.success_message) {
        add_notification({
          type: 'success',
          message: options.success_message
        });
      }
    },
    onError: (error) => {
      const error_message = error.response?.data?.detail || 'Operation failed';
      add_notification({
        type: 'error',
        message: error_message
      });
    },
    ...options
  });
};