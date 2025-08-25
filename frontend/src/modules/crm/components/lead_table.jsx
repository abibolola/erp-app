import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import StatusBadge from './status_badge';
import { 
  PencilIcon, 
  TrashIcon, 
  EyeIcon,
  ArrowsUpDownIcon 
} from '@heroicons/react/24/outline';

const LeadTable = ({ 
  leads, 
  loading, 
  selected_leads, 
  on_selection_change, 
  on_delete,
  on_refresh 
}) => {
  const navigate = useNavigate();
  const [sort_field, set_sort_field] = useState('created_at');
  const [sort_order, set_sort_order] = useState('desc');

  const handle_select_all = (e) => {
    if (e.target.checked) {
      on_selection_change(leads.map(lead => lead.id));
    } else {
      on_selection_change([]);
    }
  };

  const handle_select_one = (lead_id) => {
    if (selected_leads.includes(lead_id)) {
      on_selection_change(selected_leads.filter(id => id !== lead_id));
    } else {
      on_selection_change([...selected_leads, lead_id]);
    }
  };

  const handle_sort = (field) => {
    if (sort_field === field) {
      set_sort_order(sort_order === 'asc' ? 'desc' : 'asc');
    } else {
      set_sort_field(field);
      set_sort_order('asc');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!leads || leads.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 dark:text-gray-400">No leads found</p>
        <button
          onClick={on_refresh}
          className="mt-4 text-blue-600 hover:text-blue-700"
        >
          Refresh
        </button>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead className="bg-gray-50 dark:bg-gray-700">
          <tr>
            <th className="px-6 py-3 text-left">
              <input
                type="checkbox"
                checked={selected_leads.length === leads.length}
                onChange={handle_select_all}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
            </th>
            <th 
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer"
              onClick={() => handle_sort('name')}
            >
              <div className="flex items-center">
                Name
                <ArrowsUpDownIcon className="ml-1 h-3 w-3" />
              </div>
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
              Email
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
              Phone
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
              Status
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
          {leads.map((lead) => (
            <tr 
              key={lead.id}
              className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              <td className="px-6 py-4 whitespace-nowrap">
                <input
                  type="checkbox"
                  checked={selected_leads.includes(lead.id)}
                  onChange={() => handle_select_one(lead.id)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm font-medium text-gray-900 dark:text-white">
                  {lead.name}
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  {lead.email}
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  {lead.phone || '-'}
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <StatusBadge status={lead.status} />
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div className="flex space-x-2">
                  <button
                    onClick={() => navigate(`/crm/leads/${lead.id}`)}
                    className="text-blue-600 hover:text-blue-900 dark:text-blue-400"
                    title="View"
                  >
                    <EyeIcon className="h-5 w-5" />
                  </button>
                  <button
                    onClick={() => navigate(`/crm/leads/${lead.id}/edit`)}
                    className="text-yellow-600 hover:text-yellow-900 dark:text-yellow-400"
                    title="Edit"
                  >
                    <PencilIcon className="h-5 w-5" />
                  </button>
                  <button
                    onClick={() => on_delete(lead.id)}
                    className="text-red-600 hover:text-red-900 dark:text-red-400"
                    title="Delete"
                  >
                    <TrashIcon className="h-5 w-5" />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default LeadTable;
