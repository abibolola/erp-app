const health_check = async () => {
  console.log('🔍 Starting Health Check...\n');
  
  // 1. Check API connection
  try {
    const response = await fetch('http://localhost:8000/health');
    console.log('✅ API Connection: OK');
  } catch (error) {
    console.log('❌ API Connection: FAILED');
  }
  
  // 2. Check authentication
  const auth_store = localStorage.getItem('auth-storage');
  if (auth_store) {
    const data = JSON.parse(auth_store);
    console.log('✅ Auth Store: Found');
    console.log(`   User: ${data.state?.user?.email || 'None'}`);
  } else {
    console.log('⚠️ Auth Store: Empty');
  }
  
  // 3. Check cookies
  console.log('\n🍪 Cookies:');
  console.log(`   CSRF Token: ${document.cookie.includes('csrf_token') ? '✅' : '❌'}`);
  
  console.log('\n✨ Health Check Complete!');
};

// Run in browser console
health_check();