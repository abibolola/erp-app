import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import use_auth_store from '../../../shared/stores/use_auth_store';
import LoginForm from '../components/login_form';

const Login = () => {
  const navigate = useNavigate();
  const { login, loading, error } = use_auth_store();
  const [show_password, set_show_password] = useState(false);

  const handle_login = async (form_data) => {
    const result = await login(form_data.email, form_data.password);
    if (result.success) {
      navigate('/');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white">
            Sign in to your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
            Or{' '}
            <Link
              to="/auth/register"
              className="font-medium text-blue-600 hover:text-blue-500"
            >
              create a new account
            </Link>
          </p>
        </div>
        
        <LoginForm 
          on_submit={handle_login}
          loading={loading}
          error={error}
          show_password={show_password}
          on_toggle_password={() => set_show_password(!show_password)}
        />
      </div>
    </div>
  );
};

export default Login;