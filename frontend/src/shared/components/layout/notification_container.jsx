import use_app_store from '../../stores/use_app_store';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { 
  CheckCircleIcon, 
  ExclamationCircleIcon, 
  InformationCircleIcon,
  XCircleIcon 
} from '@heroicons/react/24/solid';

const NotificationContainer = () => {
  const { notifications, remove_notification } = use_app_store();

  const get_icon = (type) => {
    switch (type) {
      case 'success':
        return <CheckCircleIcon className="h-5 w-5 text-green-400" />;
      case 'error':
        return <XCircleIcon className="h-5 w-5 text-red-400" />;
      case 'warning':
        return <ExclamationCircleIcon className="h-5 w-5 text-yellow-400" />;
      default:
        return <InformationCircleIcon className="h-5 w-5 text-blue-400" />;
    }
  };

  const get_bg_color = (type) => {
    switch (type) {
      case 'success':
        return 'bg-green-50 border-green-200';
      case 'error':
        return 'bg-red-50 border-red-200';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200';
      default:
        return 'bg-blue-50 border-blue-200';
    }
  };

  return (
    <div className="fixed top-20 right-4 z-50 space-y-2">
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={`flex items-start p-4 rounded-lg shadow-lg border ${get_bg_color(notification.type)} 
            animate-slide-in max-w-sm`}
        >
          <div className="flex-shrink-0">
            {get_icon(notification.type)}
          </div>
          <div className="ml-3 flex-1">
            <p className="text-sm font-medium text-gray-900">
              {notification.message}
            </p>
          </div>
          <button
            onClick={() => remove_notification(notification.id)}
            className="ml-4 flex-shrink-0"
          >
            <XMarkIcon className="h-5 w-5 text-gray-400 hover:text-gray-500" />
          </button>
        </div>
      ))}
    </div>
  );
};

export default NotificationContainer;