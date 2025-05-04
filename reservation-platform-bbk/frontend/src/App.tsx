import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { AuthProvider } from './context/contexts/AuthContext';
import SignupForm from './components/components/SignupForm';
import LoginForm from './components/components/LoginForm';

import Layout from './components/components/Layout';
import HomePage from './pages/pages/HomePage';
import RestaurantPage from './pages/pages/RestaurantPage';
import LoginPage from './pages/pages/LoginPage';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Layout>
          <ToastContainer
            position="top-right"
            autoClose={2000}
            hideProgressBar={false}
            newestOnTop
            closeOnClick
            pauseOnHover
            draggable
            theme="light"
          />
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/restaurant/:id" element={<RestaurantPage />} />
            <Route path="/signup" element={<SignupForm />} />
            <Route path="/login" element={<LoginForm />} />
          </Routes>
        </Layout>
      </Router>
    </AuthProvider>
  );
}

export default App;
