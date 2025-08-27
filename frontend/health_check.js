/**
 * Comprehensive Health Check Script
 * Run this in browser console to verify all systems
 */

const health_check = async () => {
  console.log('🔍 Starting Comprehensive Health Check...\n');
  console.log('=' .repeat(50));
  
  const results = {
    api_connection: false,
    database: false,
    auth_store: false,
    cookies: {
      access_token: false,
      refresh_token: false,
      csrf_token: false
    },
    authentication: false,
    protected_routes: false
  };
  
  // 1. Check Basic API Connection
  console.log('\n📡 Checking API Connection...');
  try {
    const response = await fetch('http://localhost:8000/health', {
      credentials: 'include'
    });
    const data = await response.json();
    results.api_connection = true;
    console.log('✅ API Connection: OK');
    console.log(`   Version: ${data.version}`);
    console.log(`   Status: ${data.status}`);
  } catch (error) {
    console.log('❌ API Connection: FAILED');
    console.log(`   Error: ${error.message}`);
  }
  
  // 2. Check Database Connection
  console.log('\n💾 Checking Database...');
  try {
    const response = await fetch('http://localhost:8000/health/db', {
      credentials: 'include'
    });
    const data = await response.json();
    if (data.status === 'connected') {
      results.database = true;
      console.log('✅ Database: Connected');
      console.log('   Table Statistics:');
      Object.entries(data.table_statistics).forEach(([table, count]) => {
        console.log(`     - ${table}: ${count} records`);
      });
    } else {
      console.log('❌ Database: Not Connected');
      console.log(`   Error: ${data.error}`);
    }
  } catch (error) {
    console.log('❌ Database Check: FAILED');
    console.log(`   Error: ${error.message}`);
  }
  
  // 3. Check Readiness
  console.log('\n🚦 Checking Service Readiness...');
  try {
    const response = await fetch('http://localhost:8000/health/ready', {
      credentials: 'include'
    });
    const data = await response.json();
    console.log(`${data.status === 'ready' ? '✅' : '❌'} Service Status: ${data.status}`);
    Object.entries(data.checks).forEach(([check, status]) => {
      console.log(`   ${status ? '✅' : '❌'} ${check}`);
    });
    if (data.errors) {
      console.log('   Errors:');
      data.errors.forEach(error => console.log(`     - ${error}`));
    }
  } catch (error) {
    console.log('❌ Readiness Check: FAILED');
    console.log(`   Error: ${error.message}`);
  }
  
  // 4. Check Zustand Auth Store
  console.log('\n📦 Checking Auth Store (Zustand)...');
  try {
    const auth_storage = localStorage.getItem('auth-storage');
    if (auth_storage) {
      const data = JSON.parse(auth_storage);
      results.auth_store = true;
      console.log('✅ Auth Store: Found');
      if (data.state?.user) {
        console.log(`   User: ${data.state.user.email || data.state.user.username}`);
        console.log(`   Authenticated: ${data.state.is_authenticated}`);
      } else {
        console.log('   User: Not logged in');
      }
    } else {
      console.log('⚠️  Auth Store: Empty (user not logged in)');
    }
  } catch (error) {
    console.log('❌ Auth Store: Error reading');
    console.log(`   Error: ${error.message}`);
  }
  
  // 5. Check Cookies
  console.log('\n🍪 Checking Cookies...');
  const cookies = document.cookie.split(';').map(c => c.trim());
  const cookie_names = ['access_token', 'refresh_token', 'csrf_token'];
  
  cookie_names.forEach(name => {
    const exists = cookies.some(cookie => cookie.startsWith(`${name}=`));
    results.cookies[name] = exists;
    console.log(`   ${exists ? '✅' : '⚠️ '} ${name}: ${exists ? 'Set' : 'Not found'}`);
  });
  
  // 6. Test Authentication Endpoint
  console.log('\n🔐 Checking Authentication...');
  try {
    const response = await fetch('http://localhost:8000/api/auth/me', {
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (response.ok) {
      const user = await response.json();
      results.authentication = true;
      console.log('✅ Authentication: Valid');
      console.log(`   User: ${user.email}`);
      console.log(`   Username: ${user.username}`);
      console.log(`   Role: ${user.is_superuser ? 'Admin' : 'User'}`);
    } else if (response.status === 401) {
      console.log('⚠️  Authentication: Not logged in');
      console.log('   Run test_login() to test authentication');
    } else {
      console.log('❌ Authentication: Error');
      console.log(`   Status: ${response.status}`);
    }
  } catch (error) {
    console.log('❌ Authentication Check: FAILED');
    console.log(`   Error: ${error.message}`);
  }
  
  // 7. Test Protected Route
  console.log('\n🛡️  Checking Protected Routes...');
  try {
    const response = await fetch('http://localhost:8000/api/leads', {
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (response.ok) {
      const leads = await response.json();
      results.protected_routes = true;
      console.log('✅ Protected Routes: Accessible');
      console.log(`   Leads found: ${Array.isArray(leads) ? leads.length : 'N/A'}`);
    } else if (response.status === 401) {
      console.log('⚠️  Protected Routes: Authentication required');
    } else {
      console.log('❌ Protected Routes: Error');
      console.log(`   Status: ${response.status}`);
    }
  } catch (error) {
    console.log('❌ Protected Routes Check: FAILED');
    console.log(`   Error: ${error.message}`);
  }
  
  // Summary
  console.log('\n' + '=' .repeat(50));
  console.log('📊 HEALTH CHECK SUMMARY\n');
  
  const total_checks = 7;
  const passed_checks = Object.values(results).flat().filter(Boolean).length;
  const health_percentage = Math.round((passed_checks / total_checks) * 100);
  
  console.log(`Overall Health: ${health_percentage}%`);
  
  if (health_percentage === 100) {
    console.log('✅ All systems operational!');
  } else if (health_percentage >= 70) {
    console.log('⚠️  System operational with some issues');
  } else {
    console.log('❌ System has critical issues');
  }
  
  console.log('\n💡 Quick Actions:');
  if (!results.api_connection) {
    console.log('   1. Start backend: cd backend && uvicorn app.main:app --reload');
  }
  if (!results.database) {
    console.log('   2. Start PostgreSQL: docker-compose up -d postgres');
    console.log('   3. Run migrations: cd backend && alembic upgrade head');
  }
  if (!results.authentication) {
    console.log('   4. Login: Run test_login() or navigate to /auth/login');
  }
  
  console.log('\n✨ Health Check Complete!');
  return results;
};

// Test Login Function
const test_login = async (email = 'test@example.com', password = 'Test123!') => {
  console.log('\n🔐 Testing Login...');
  
  try {
    const response = await fetch('http://localhost:8000/api/auth/login', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-Client-Type': 'web'
      },
      body: JSON.stringify({ email, password })
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log('✅ Login successful!');
      console.log('   User:', data.email);
      console.log('   Cookies should now be set');
      console.log('   Run health_check() again to verify');
      return data;
    } else {
      const error = await response.json();
      console.log('❌ Login failed');
      console.log('   Error:', error.detail);
      return null;
    }
  } catch (error) {
    console.log('❌ Login request failed');
    console.log('   Error:', error.message);
    return null;
  }
};

// Test Registration Function
const test_register = async () => {
  console.log('\n📝 Testing Registration...');
  
  const test_user = {
    username: `testuser_${Date.now()}`,
    email: `test_${Date.now()}@example.com`,
    password: 'Test123!@#',
    full_name: 'Test User'
  };
  
  console.log(`   Creating user: ${test_user.email}`);
  
  try {
    const response = await fetch('http://localhost:8000/api/auth/register', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-Client-Type': 'web'
      },
      body: JSON.stringify(test_user)
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log('✅ Registration successful!');
      console.log('   User created:', data.email);
      console.log('   You can now login with these credentials');
      return { ...test_user, ...data };
    } else {
      const error = await response.json();
      console.log('❌ Registration failed');
      console.log('   Error:', error.detail);
      return null;
    }
  } catch (error) {
    console.log('❌ Registration request failed');
    console.log('   Error:', error.message);
    return null;
  }
};

// Full Integration Test
const test_full_flow = async () => {
  console.log('\n🧪 Starting Full Integration Test...\n');
  console.log('=' .repeat(50));
  
  const test_results = {
    registration: false,
    login: false,
    auth_check: false,
    protected_route: false,
    logout: false
  };
  
  // 1. Register new user
  console.log('\n1️⃣ Testing Registration...');
  const new_user = await test_register();
  if (new_user) {
    test_results.registration = true;
    
    // 2. Login with new user
    console.log('\n2️⃣ Testing Login...');
    const login_result = await test_login(new_user.email, new_user.password);
    test_results.login = !!login_result;
    
    // 3. Check authentication
    console.log('\n3️⃣ Testing Auth Check...');
    try {
      const response = await fetch('http://localhost:8000/api/auth/me', {
        credentials: 'include'
      });
      test_results.auth_check = response.ok;
      if (response.ok) {
        const user = await response.json();
        console.log('✅ Auth check passed:', user.email);
      }
    } catch (error) {
      console.log('❌ Auth check failed:', error.message);
    }
    
    // 4. Access protected route
    console.log('\n4️⃣ Testing Protected Route...');
    try {
      const response = await fetch('http://localhost:8000/api/leads', {
        credentials: 'include'
      });
      test_results.protected_route = response.ok;
      console.log(response.ok ? '✅ Protected route accessible' : '❌ Protected route blocked');
    } catch (error) {
      console.log('❌ Protected route error:', error.message);
    }
    
    // 5. Logout
    console.log('\n5️⃣ Testing Logout...');
    try {
      const response = await fetch('http://localhost:8000/api/auth/logout', {
        method: 'POST',
        credentials: 'include'
      });
      test_results.logout = response.ok;
      console.log(response.ok ? '✅ Logout successful' : '❌ Logout failed');
    } catch (error) {
      console.log('❌ Logout error:', error.message);
    }
  }
  
  // Summary
  console.log('\n' + '=' .repeat(50));
  console.log('📊 INTEGRATION TEST RESULTS\n');
  
  const total = Object.keys(test_results).length;
  const passed = Object.values(test_results).filter(Boolean).length;
  
  Object.entries(test_results).forEach(([test, passed]) => {
    console.log(`   ${passed ? '✅' : '❌'} ${test.replace('_', ' ').toUpperCase()}`);
  });
  
  console.log(`\n   Score: ${passed}/${total} tests passed (${Math.round(passed/total * 100)}%)`);
  
  if (passed === total) {
    console.log('\n🎉 All integration tests passed!');
  } else {
    console.log('\n⚠️  Some tests failed. Check the logs above.');
  }
  
  return test_results;
};

// Make functions available globally
window.health_check = health_check;
window.test_login = test_login;
window.test_register = test_register;
window.test_full_flow = test_full_flow;

// Auto-run health check on load
console.log('🏥 Health Check Script Loaded!');
console.log('Available commands:');
console.log('   health_check()    - Run full health check');
console.log('   test_login()      - Test login with default credentials');
console.log('   test_register()   - Register a new test user');
console.log('   test_full_flow()  - Run complete integration test');
console.log('\nRun health_check() to start...');