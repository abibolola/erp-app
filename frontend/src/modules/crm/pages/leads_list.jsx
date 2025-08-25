import { useState, useMemo } from 'react';
import { use_leads, use_delete_lead } from '../queries/use_leads';
import LeadTable from '../components/lead_table';
import SearchFilters from '../components/search_filters';
import LeadForm from '../components/lead_form';
import BulkActions from '../components/bulk_actions';
import { PlusIcon, ArrowDownTrayIcon } from '@heroicons/react/24/outline';
import use_app_store from '../../../shared/stores/use_app_store';

const LeadsList = () => {
  const [filters, set_filters] = useState({
    search: '',
    status: 'all',
    sort_by: 'created_at',
    sort_order: 'desc'
  });
  
  const [selected_leads, set_selected_leads] = useState([]);
  const [show_create_form, set_show_create_form] = useState(false);
  
  const { data: leads, isLoading: is_loading, error, refetch } = use_leads(filters);
  const delete_lead = use_delete_lead();
  const { add_notification } = use_app_store();

  // Filter and sort leads client-side for better UX
  const processed_leads = useMemo(() => {
    if (!leads) return [];
    
    let filtered = [...leads];
    
    // Search filter
    if (filters.search) {
      const search_lower = filters.search.toLowerCase();
      filtered = filtered.filter(lead => 
        lead.name.toLowerCase().includes(search_lower) ||
        lead.email.toLowerCase().includes(search_lower) ||
        lead.phone?.toLowerCase().includes(search_lower)
      );
    }
    
    // Status filter
    if (filters.status !== 'all') {
      filtered = filtered.filter(lead => lead.status === filters.status);
    }
    
    // Sorting
    filtered.sort((a, b) => {
      const a_val = a[filters.sort_by];
      const b_val = b[filters.sort_by];
      const order = filters.sort_order === 'asc' ? 1 : -1;
      
      if (a_val < b_val) return -order;
      if (a_val > b_val) return order;
      return 0;
    });
    
    return filtered;
  }, [leads, filters]);

  const handle_delete = async (lead_id) => {
    if (!window.confirm('Are you sure you want to delete this lead?')) return;
    
    try {
      await delete_lead.mutateAsync({
        method: 'delete',
        url: `/leads/${lead_id}`
      });
      set_selected_leads(prev => prev.filter(id => id !== lead_id));
    } catch (error) {
      console.error('Failed to delete lead:', error);
    }
  };

  const handle_bulk_delete = async () => {
    if (!window.confirm(`Delete ${selected_leads.length} selected leads?`)) return;
    
    try {
      await Promise.all(
        selected_leads.map(id => 
          delete_lead.mutateAsync({
            method: 'delete',
            url: `/leads/${id}`
          })
        )
      );
      set_selected_leads([]);
      add_notification({
        type: 'success',
        message: `${selected_leads.length} leads deleted successfully`
      });
    } catch (error) {
      console.error('Bulk delete failed:', error);
    }
  };

  const handle_export = () => {
    const csv = [
      ['Name', 'Email', 'Phone', 'Status', 'Notes'],
      ...processed_leads.map(lead => [
        lead.name,
        lead.email,
        lead.phone || '',
        lead.status,
        lead.notes || ''
      ])
    ].map(row => row.join(',')).join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `leads_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        Error loading leads: {error.message}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Leads Management
          </h1>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            {processed_leads.length} leads found
          </p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={handle_export}
            className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            <ArrowDownTrayIcon className="h-5 w-5 mr-2" />
            Export
          </button>
          <button
            onClick={() => set_show_create_form(true)}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Add Lead
          </button>
        </div>
      </div>

      {/* Filters */}
      <SearchFilters 
        filters={filters} 
        on_change={set_filters}
        result_count={processed_leads.length}
      />
      
      {/* Bulk Actions */}
      {selected_leads.length > 0 && (
        <BulkActions
          selected_count={selected_leads.length}
          on_delete={handle_bulk_delete}
          on_clear_selection={() => set_selected_leads([])}
        />
      )}
      
      {/* Table */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
        <LeadTable 
          leads={processed_leads}
          loading={is_loading}
          selected_leads={selected_leads}
          on_selection_change={set_selected_leads}
          on_delete={handle_delete}
          on_refresh={refetch}
        />
      </div>

      {/* Create Form Modal */}
      {show_create_form && (
        <LeadForm
          on_close={() => set_show_create_form(false)}
          on_success={() => {
            set_show_create_form(false);
            refetch();
          }}
        />
      )}
    </div>
  );
};

export default LeadsList;