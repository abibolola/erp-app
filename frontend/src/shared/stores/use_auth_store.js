import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import axios_instance from '../utils/axios';

const use_auth_store = create(
  devtools(
    persist(
      (set, get) => ({
        // State
        user: null,
        is_authenticated: false,
        loading: false,
        error: null,
        access_token: null,  // For mobile/API clients
        refresh_token: null, // For mobile/API clients
        client_type: 'web',  // Default to web

        // Actions
        set_client_type: (type) => set({ client_type: type }),

        login: async (email, password, client_type = 'web') => {
          set({ loading: true, error: null });
          try {
            const response = await axios_instance.post('/auth/login', 
              { email, password },
              { headers: { 'X-Client-Type': client_type } }
            );
            
            if (client_type === 'web') {
              // Web client - tokens are in cookies
              set({
                user: response.data.user,
                is_authenticated: true,
                loading: false,
                error: null,
                client_type: 'web'
              });
            } else {
              // Mobile/API client - tokens in response body
              set({
                user: response.data.user,
                access_token: response.data.access_token,
                refresh_token: response.data.refresh_token,
                is_authenticated: true,
                loading: false,
                error: null,
                client_type: client_type
              });
              
              // For mobile/API clients, set the token in axios defaults
              axios_instance.defaults.headers.common['Authorization'] = 
                `Bearer ${response.data.access_token}`;
            }
            
            return { success: true, data: response.data };
          } catch (error) {
            const error_message = error.response?.data?.detail || 'Login failed';
            set({
              user: null,
              is_authenticated: false,
              loading: false,
              error: error_message,
              access_token: null,
              refresh_token: null
            });
            return { success: false, error: error_message };
          }
        },

        register: async (user_data, client_type = 'web') => {
          set({ loading: true, error: null });
          try {
            const response = await axios_instance.post('/auth/register', 
              user_data,
              { headers: { 'X-Client-Type': client_type } }
            );
            
            if (client_type === 'web') {
              // Web client - tokens are in cookies
              set({
                user: response.data,
                is_authenticated: true,
                loading: false,
                error: null,
                client_type: 'web'
              });
            } else {
              // Mobile/API client - might return tokens
              // Adjust based on your register endpoint response
              set({
                user: response.data,
                is_authenticated: true,
                loading: false,
                error: null,
                client_type: client_type
              });
            }
            
            return { success: true, data: response.data };
          } catch (error) {
            const error_message = error.response?.data?.detail || 'Registration failed';
            set({
              loading: false,
              error: error_message
            });
            return { success: false, error: error_message };
          }
        },

        logout: async () => {
          const { client_type } = get();
          
          try {
            if (client_type === 'web') {
              // Web client - clear cookies on server
              await axios_instance.post('/auth/logout');
            } else {
              // Mobile/API client - just clear local tokens
              delete axios_instance.defaults.headers.common['Authorization'];
            }
          } catch (error) {
            console.error('Logout error:', error);
          } finally {
            set({
              user: null,
              is_authenticated: false,
              error: null,
              access_token: null,
              refresh_token: null
            });
            
            // Only redirect for web clients
            if (client_type === 'web') {
              window.location.href = '/auth/login';
            }
          }
        },

        check_auth: async () => {
          const { client_type, access_token } = get();
          set({ loading: true });
          
          try {
            // For mobile/API clients, set the token if we have it
            if (client_type !== 'web' && access_token) {
              axios_instance.defaults.headers.common['Authorization'] = 
                `Bearer ${access_token}`;
            }
            
            const response = await axios_instance.get('/auth/me');
            set({
              user: response.data,
              is_authenticated: true,
              loading: false
            });
            return true;
          } catch (error) {
            set({
              user: null,
              is_authenticated: false,
              loading: false
            });
            return false;
          }
        },

        refresh_access_token: async () => {
          const { client_type, refresh_token } = get();
          
          if (client_type === 'web') {
            // Web client - handled by cookies automatically
            return true;
          } else if (refresh_token) {
            // Mobile/API client - manual refresh
            try {
              const response = await axios_instance.post('/auth/refresh', {
                refresh_token: refresh_token
              });
              
              const new_access_token = response.data.access_token;
              
              set({ access_token: new_access_token });
              
              // Update axios defaults
              axios_instance.defaults.headers.common['Authorization'] = 
                `Bearer ${new_access_token}`;
              
              return true;
            } catch (error) {
              // Refresh failed, need to login again
              get().logout();
              return false;
            }
          }
          
          return false;
        },

        clear_error: () => set({ error: null })
      }),
      {
        name: 'auth-storage',
        // Persist different data based on client type
        partialize: (state) => ({ 
          user: state.user,
          is_authenticated: state.is_authenticated,
          client_type: state.client_type,
          // Only persist tokens for non-web clients
          ...(state.client_type !== 'web' && {
            access_token: state.access_token,
            refresh_token: state.refresh_token
          })
        })
      }
    ),
    {
      name: 'AuthStore'
    }
  )
);

export default use_auth_store;