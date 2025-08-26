import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import use_auth_store from '../../stores/use_auth_store';
import use_app_store from '../../stores/use_app_store';
import { 
  Bars3Icon, 
  UserCircleIcon,
  MoonIcon,
  SunIcon,
  ArrowRightOnRectangleIcon 
} from '@heroicons/react/24/outline';

const Navbar = () => {
  const navigate = useNavigate();
  const { user, logout } = use_auth_store();
  const { theme, set_theme, toggle_sidebar } = use_app_store();
  const [show_dropdown, set_show_dropdown] = useState(false);

  const handle_logout = async () => {
    await logout();
    navigate('/auth/login');
  };

  const toggle_theme = () => {
    set_theme(theme === 'light' ? 'dark' : 'light');
  };

  return (
    <nav className="bg-white dark:bg-gray-800 shadow-lg fixed top-0 left-0 right-0 z-40">
      <div className="px-4 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={toggle_sidebar}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <Bars3Icon className="h-6 w-6 text-gray-600 dark:text-gray-300" />
          </button>
          <h1 className="text-xl font-bold text-gray-800 dark:text-white">
            ERP System
          </h1>
        </div>

        <div className="flex items-center space-x-4">
          <button
            onClick={toggle_theme}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            {theme === 'light' ? (
              <MoonIcon className="h-5 w-5 text-gray-600" />
            ) : (
              <SunIcon className="h-5 w-5 text-gray-300" />
            )}
          </button>

          <div className="relative">
            <button
              onClick={() => set_show_dropdown(!show_dropdown)}
              className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              <UserCircleIcon className="h-6 w-6 text-gray-600 dark:text-gray-300" />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                {user?.username || user?.email}
              </span>
            </button>

            {show_dropdown && (
              <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg py-2">
                <button
                  onClick={handle_logout}
                  className="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
                >
                  <ArrowRightOnRectangleIcon className="h-4 w-4 mr-2" />
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;