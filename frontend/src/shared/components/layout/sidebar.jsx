import { NavLink } from 'react-router-dom';
import use_app_store from '../../stores/use_app_store';
import {
  HomeIcon,
  UsersIcon,
  ChartBarIcon,
  CogIcon,
  DocumentTextIcon,
  CurrencyDollarIcon,
  BuildingOfficeIcon
} from '@heroicons/react/24/outline';

const Sidebar = () => {
  const { sidebar_open } = use_app_store();

  const navigation = [
    { name: 'Dashboard', href: '/', icon: HomeIcon },
    { name: 'Leads', href: '/crm/leads', icon: UsersIcon },
    { name: 'HR', href: '/hr', icon: DocumentTextIcon },
    { name: 'Finance', href: '/finance', icon: CurrencyDollarIcon },
    { name: 'Inventory', href: '/inventory', icon: BuildingOfficeIcon },
    { name: 'Reports', href: '/reports', icon: ChartBarIcon },
    { name: 'Settings', href: '/settings', icon: CogIcon },
  ];

  return (
    <aside className={`fixed left-0 top-16 h-full bg-gray-900 text-white transition-all duration-300 z-30 ${
      sidebar_open ? 'w-64' : 'w-16'
    }`}>
      <nav className="mt-8">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              `flex items-center px-4 py-3 hover:bg-gray-800 transition-colors ${
                isActive ? 'bg-gray-800 border-l-4 border-blue-500' : ''
              }`
            }
          >
            <item.icon className="h-6 w-6" />
            {sidebar_open && <span className="ml-3">{item.name}</span>}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;