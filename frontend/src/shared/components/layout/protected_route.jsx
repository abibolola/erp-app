import { Navigate, Outlet } from 'react-router-dom';
import use_auth_store from '../../stores/use_auth_store';
import { useEffect } from 'react';

const ProtectedRoute = () => {
  const { is_authenticated, loading, check_auth } = use_auth_store();

  useEffect(() => {
    // Check auth status on mount
    check_auth();
  }, [check_auth]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return is_authenticated ? <Outlet /> : <Navigate to="/auth/login" replace />;
};

export default ProtectedRoute;