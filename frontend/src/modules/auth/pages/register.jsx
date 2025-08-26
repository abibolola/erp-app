import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import use_auth_store from '../../../shared/stores/use_auth_store';

const Register = () => {
  const navigate = useNavigate();
  const { register, loading, error } = use_auth_store();
  const [form_data, set_form_data] = useState({
    username: '',
    email: '',
    password: '',
    confirm_password: ''
  });

  const handle_submit = async (e) => {
    e.preventDefault();
    
    if (form_data.password !== form_data.confirm_password) {
      alert('Passwords do not match');
      return;
    }

    const result = await register({
      username: form_data.username,
      email: form_data.email,
      password: form_data.password,
      org_id: 1,  // Default org for now
      role_id: 1  // Default role for now
    });

    if (result.success) {
      navigate('/');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handle_submit}>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
              {error}
            </div>
          )}
          
          <div className="space-y-4">
            <input
              type="text"
              required
              placeholder="Username"
              value={form_data.username}
              onChange={(e) => set_form_data({...form_data, username: e.target.value})}
              className="w-full px-3 py-2 border rounded-md"
            />
            
            <input
              type="email"
              required
              placeholder="Email"
              value={form_data.email}
              onChange={(e) => set_form_data({...form_data, email: e.target.value})}
              className="w-full px-3 py-2 border rounded-md"
            />
            
            <input
              type="password"
              required
              placeholder="Password"
              value={form_data.password}
              onChange={(e) => set_form_data({...form_data, password: e.target.value})}
              className="w-full px-3 py-2 border rounded-md"
            />
            
            <input
              type="password"
              required
              placeholder="Confirm Password"
              value={form_data.confirm_password}
              onChange={(e) => set_form_data({...form_data, confirm_password: e.target.value})}
              className="w-full px-3 py-2 border rounded-md"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Creating account...' : 'Sign up'}
          </button>

          <p className="text-center text-sm">
            Already have an account?{' '}
            <Link to="/auth/login" className="text-blue-600 hover:text-blue-500">
              Sign in
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
};

export default Register;