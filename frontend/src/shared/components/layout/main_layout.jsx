import { Outlet } from 'react-router-dom';
import Navbar from './navbar';
import Sidebar from './sidebar';
import NotificationContainer from './notification_container';
import use_app_store from '../../stores/use_app_store';

const MainLayout = () => {
  const { sidebar_open } = use_app_store();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <div className="flex">
        <Sidebar />
        <main className={`flex-1 transition-all duration-300 ${
          sidebar_open ? 'ml-64' : 'ml-16'
        }`}>
          <div className="p-6">
            <Outlet />
          </div>
        </main>
      </div>
      <NotificationContainer />
    </div>
  );
};

export default MainLayout;