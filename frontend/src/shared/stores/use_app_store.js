import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

const use_app_store = create(
  devtools(
    persist(
      (set, get) => ({
        // State
        theme: 'light',
        sidebar_open: true,
        notifications: [],
        global_loading: false,

        // Actions
        set_theme: (theme) => {
          set({ theme });
          document.documentElement.classList.toggle('dark', theme === 'dark');
        },

        toggle_sidebar: () => set((state) => ({ 
          sidebar_open: !state.sidebar_open 
        })),

        add_notification: (notification) => {
          const id = Date.now();
          const new_notification = {
            id,
            ...notification,
            timestamp: new Date().toISOString()
          };
          
          set((state) => ({
            notifications: [...state.notifications, new_notification]
          }));

          // Auto-remove after 5 seconds
          setTimeout(() => {
            get().remove_notification(id);
          }, 5000);

          return id;
        },

        remove_notification: (id) => {
          set((state) => ({
            notifications: state.notifications.filter(n => n.id !== id)
          }));
        },

        clear_notifications: () => set({ notifications: [] }),

        set_global_loading: (loading) => set({ global_loading: loading })
      }),
      {
        name: 'app-storage',
        partialize: (state) => ({ 
          theme: state.theme,
          sidebar_open: state.sidebar_open 
        })
      }
    ),
    {
      name: 'AppStore'
    }
  )
);

export default use_app_store;