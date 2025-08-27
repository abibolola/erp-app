import { useState } from 'react';
import axios from 'axios';

const TestConnection = () => {
  const [backend_status, set_backend_status] = useState(null);
  const [test_results, set_test_results] = useState({});

  const test_backend = async () => {
    const results = {};
    
    // Test 1: Basic connection
    try {
      const response = await fetch('http://localhost:8000/health');
      const data = await response.json();
      results.health = '✅ Connected: ' + data.message;
    } catch (error) {
      results.health = '❌ Failed: ' + error.message;
    }

    // Test 2: API root
    try {
      const response = await fetch('http://localhost:8000/');
      const data = await response.json();
      results.root = '✅ API Root: ' + data.message;
    } catch (error) {
      results.root = '❌ Failed';
    }

    // Test 3: Swagger docs
    try {
      const response = await fetch('http://localhost:8000/docs');
      results.swagger = response.ok ? '✅ Swagger UI Available' : '❌ Swagger Not Found';
    } catch (error) {
      results.swagger = '❌ Failed';
    }

    set_test_results(results);
  };

  const test_login = async () => {
    try {
      const response = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Client-Type': 'web'
        },
        credentials: 'include',
        body: JSON.stringify({
          email: 'admin@example.com',
          password: 'admin123'
        })
      });

      if (response.ok) {
        const data = await response.json();
        set_backend_status('✅ Login Successful! User: ' + data.user?.email);
      } else {
        set_backend_status('❌ Login Failed: ' + response.status);
      }
    } catch (error) {
      set_backend_status('❌ Connection Error: ' + error.message);
    }
  };

  return (
    <div className="min-h-screen p-8 bg-gray-100">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Frontend-Backend Connection Test</h1>
        
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Backend Status</h2>
          <button
            onClick={test_backend}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 mb-4"
          >
            Test Backend Connection
          </button>
          
          {Object.entries(test_results).map(([key, value]) => (
            <div key={key} className="mb-2">
              <strong>{key}:</strong> {value}
            </div>
          ))}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Authentication Test</h2>
          <button
            onClick={test_login}
            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 mb-4"
          >
            Test Login
          </button>
          
          {backend_status && (
            <div className="mt-4 p-4 bg-gray-100 rounded">
              {backend_status}
            </div>
          )}
        </div>

        <div className="mt-8 bg-yellow-50 border border-yellow-200 p-4 rounded">
          <h3 className="font-semibold">URLs to Check:</h3>
          <ul className="mt-2 space-y-1">
            <li>Backend API: <a href="http://localhost:8000" target="_blank" className="text-blue-500 underline">http://localhost:8000</a></li>
            <li>Swagger Docs: <a href="http://localhost:8000/docs" target="_blank" className="text-blue-500 underline">http://localhost:8000/docs</a></li>
            <li>Frontend: <a href="http://localhost:5173" target="_blank" className="text-blue-500 underline">http://localhost:5173</a></li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default TestConnection;