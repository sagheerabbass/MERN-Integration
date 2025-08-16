import logo from './logo.svg';
import './App.css';
import ReactDOM from 'react-dom/client';
import AdminDashboard from './AdminDashboard'
import React from 'react';

function App() {
  return (
    <div className="App">
       <React.StrictMode>
                   <AdminDashboard />
       </React.StrictMode>,
    </div>
  );
}

export default App;
