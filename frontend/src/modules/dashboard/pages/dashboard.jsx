const Dashboard = () => {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm">Total Leads</h3>
          <p className="text-2xl font-bold mt-2">0</p>
        </div>
        
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm">Active Users</h3>
          <p className="text-2xl font-bold mt-2">0</p>
        </div>
        
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm">Revenue</h3>
          <p className="text-2xl font-bold mt-2">$0</p>
        </div>
        
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h3 className="text-gray-500 text-sm">Pending Tasks</h3>
          <p className="text-2xl font-bold mt-2">0</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;