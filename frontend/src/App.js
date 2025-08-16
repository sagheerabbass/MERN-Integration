// src/App.js
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import AdminDashboard from './AdminDashboard';
import LoginPage from './LoginPage';

// This component protects routes that require authentication.
const PrivateRoute = () => {
  // It checks for a token in the browser's local storage.
  const token = localStorage.getItem('token');
  // If a token exists, it renders the child route. Otherwise, it redirects to the login page.
  return token ? <Outlet /> : <Navigate to="/login" replace />;
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        {/* The PrivateRoute will now protect the AdminDashboard route. */}
        <Route path="/" element={<PrivateRoute />}>
          <Route path="dashboard" element={<AdminDashboard />} />
        </Route>
        {/* A catch-all route to redirect to the dashboard or login page. */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;