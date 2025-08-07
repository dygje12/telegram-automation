import React, { useState, useEffect, createContext, useContext } from 'react';
import { api } from '../api/client';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [authStep, setAuthStep] = useState('login'); // 'login', 'code', '2fa', 'authenticated'
  const [tempData, setTempData] = useState(null);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        setIsLoading(false);
        return;
      }

      const response = await api.auth.getStatus();
      if (response.data.authenticated) {
        const userResponse = await api.auth.getMe();
        setUser(userResponse.data);
        setIsAuthenticated(true);
        setAuthStep('authenticated');
      } else {
        // Token exists but not authenticated, clear it
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_data');
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_data');
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (credentials) => {
    try {
      setIsLoading(true);
      const response = await api.auth.login(credentials);
      
      if (response.data.success) {
        setTempData({ phone_number: credentials.phone_number });
        setAuthStep('code');
        return { success: true, message: response.data.message };
      }
      
      return { success: false, message: 'Login failed' };
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.detail || 'Login failed' 
      };
    } finally {
      setIsLoading(false);
    }
  };

  const verifyCode = async (code) => {
    try {
      setIsLoading(true);
      const response = await api.auth.verifyCode({
        phone_number: tempData.phone_number,
        code: code
      });

      if (response.data.requires_2fa) {
        setAuthStep('2fa');
        return { success: true, requires2FA: true, message: response.data.message };
      } else if (response.data.access_token) {
        // Authentication successful
        localStorage.setItem('auth_token', response.data.access_token);
        localStorage.setItem('user_data', JSON.stringify(response.data.user));
        
        setUser(response.data.user);
        setIsAuthenticated(true);
        setAuthStep('authenticated');
        setTempData(null);
        
        return { success: true, requires2FA: false };
      }
      
      return { success: false, message: 'Code verification failed' };
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.detail || 'Code verification failed' 
      };
    } finally {
      setIsLoading(false);
    }
  };

  const verify2FA = async (password) => {
    try {
      setIsLoading(true);
      const response = await api.auth.verify2FA({
        phone_number: tempData.phone_number,
        password: password
      });

      if (response.data.access_token) {
        localStorage.setItem('auth_token', response.data.access_token);
        localStorage.setItem('user_data', JSON.stringify(response.data.user));
        
        setUser(response.data.user);
        setIsAuthenticated(true);
        setAuthStep('authenticated');
        setTempData(null);
        
        return { success: true };
      }
      
      return { success: false, message: '2FA verification failed' };
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.detail || '2FA verification failed' 
      };
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_data');
      setUser(null);
      setIsAuthenticated(false);
      setAuthStep('login');
      setTempData(null);
    }
  };

  const resetAuth = () => {
    setAuthStep('login');
    setTempData(null);
  };

  const value = {
    user,
    isAuthenticated,
    isLoading,
    authStep,
    tempData,
    login,
    verifyCode,
    verify2FA,
    logout,
    resetAuth,
    checkAuthStatus
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

