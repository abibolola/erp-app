import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useEffect } from 'react';

// Layouts
import MainLayout from './shared/components/layout/main_layout';
import ProtectedRoute from './shared/components/layout/protected_route';

// Pages
import Login from './modules/auth/pages/login';
import Register from './modules/auth/pages/register';
import Dashboard from './modules/dashboard/pages/dashboard';
import LeadsList from './modules/crm/pages/leads_list';
import TestConnection from './modules/auth/pages/test_connection';

// Stores
import use_auth_store from './shared/stores/use_auth_store';
import use_app_store from './shared/stores/use_app_store';

// Create a client
const query_client = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      cacheTime: 10 * 60 * 1000,
      retry: 3,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  const { check_auth } = use_auth_store();
  const { set_theme, theme } = use_app_store();

  useEffect(() => {
    // Check authentication on app mount
    check_auth();
    
    // Apply saved theme
    document.documentElement.classList.toggle('dark', theme === 'dark');
  }, [check_auth, theme]);

  return (
    <QueryClientProvider client={query_client}>
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/test" element={<TestConnection />} />
          <Route path="/auth/login" element={<Login />} />
          <Route path="/auth/register" element={<Register />} />
          
          {/* Protected routes */}
          <Route element={<ProtectedRoute />}>
            <Route element={<MainLayout />}>
              <Route path="/" element={<Dashboard />} />
              <Route path="/crm/leads" element={<LeadsList />} />
              {/* Add more routes here */}
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

export default App;