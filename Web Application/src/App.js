import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './App.css';
import Dashboard from './Components/Dashboard/dashboard';
import LoginPage from './Components/Login/login'; // Assuming LoginPage is in the 'Test' directory

class App extends React.Component {
  render() {
    return (
      <div className="App">
        <BrowserRouter>
          <Routes>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/" element={<LoginPage />} /> {/* Default route to LoginPage */}
          </Routes>
        </BrowserRouter>
      </div>
    );
  }
}

export default App;
