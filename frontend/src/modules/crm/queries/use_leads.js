import { use_query } from '../../../shared/hooks/use_query';
import { use_mutation } from '../../../shared/hooks/use_mutation';

export const use_leads = (filters = {}) => {
  const query_key = ['leads', filters];
  
  return use_query(query_key, '/leads', {
    enabled: true,
    refetchOnWindowFocus: false
  });
};

export const use_create_lead = () => {
  return use_mutation({
    invalidate_queries: [['leads']],
    success_message: 'Lead created successfully'
  });
};

export const use_update_lead = () => {
  return use_mutation({
    invalidate_queries: [['leads']],
    success_message: 'Lead updated successfully'
  });
};

export const use_delete_lead = () => {
  return use_mutation({
    invalidate_queries: [['leads']],
    success_message: 'Lead deleted successfully'
  });
};