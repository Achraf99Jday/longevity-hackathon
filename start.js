const { spawn } = require('child_process');
const path = require('path');

console.log('🚀 Starting Longevity R&D Map Platform...\n');

// Start API server
console.log('📡 Starting API server on http://localhost:8000...');
const api = spawn('python', ['scripts/run_api.py'], {
  cwd: __dirname,
  stdio: 'inherit',
  shell: true
});

// Wait a bit for API to start
setTimeout(() => {
  // Start web server
  console.log('🌐 Starting web server on http://localhost:3000...');
  const web = spawn('python', ['-m', 'http.server', '3000'], {
    cwd: path.join(__dirname, 'public'),
    stdio: 'inherit',
    shell: true
  });

  console.log('\n✅ Both servers are running!');
  console.log('   API: http://localhost:8000');
  console.log('   Web: http://localhost:3000');
  console.log('\nPress Ctrl+C to stop both servers\n');

  // Handle cleanup
  process.on('SIGINT', () => {
    console.log('\n\n🛑 Stopping servers...');
    api.kill();
    web.kill();
    process.exit();
  });
}, 3000);

// Handle API errors
api.on('error', (err) => {
  console.error('❌ API server error:', err);
  process.exit(1);
});


