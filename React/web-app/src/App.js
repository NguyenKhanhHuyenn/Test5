import React, { useState } from 'react';
import api from './api';

function App() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async () => {
    try {
      if (!username || !password) {
        setError('Username and password are required.');
        return;
      }

      const response = await api.post('/auth/token', {
        username: username,
        password: password,
        scope: '',
        grant_type: 'password',
        client_id: '',  // replace with your client_id if applicable
        client_secret: '',  // replace with your client_secret if applicable
      });

      const access_token = response.data.access_token;
      console.log('Access Token:', access_token);

      // Handle successful login, e.g., store the token in local storage
    } catch (error) {
      if (error.response) {
        console.error('Response Status:', error.response.status);
        console.error('Response Data:', error.response.data);

        // Check if there are validation errors and log them
        if (error.response.data.detail && Array.isArray(error.response.data.detail)) {
          error.response.data.detail.forEach(errorDetail => {
            console.error('Validation Error:', errorDetail);
          });
        }
      } else {
        console.error('No response received');
      }

      setError('Invalid credentials. Please try again.');
    }
  };

  return (
    <div>
      <h1>Login</h1>
      <div>
        <label>Username:</label>
        <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} />
      </div>
      <div>
        <label>Password:</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      </div>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <button onClick={handleLogin}>Login</button>
    </div>
  );
}

export default App;
