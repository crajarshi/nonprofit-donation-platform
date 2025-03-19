import React, { useState, useEffect, createContext, useContext, ReactNode } from 'react';
import { useRouter } from 'next/router';
import api from '../api/axios';

export type User = {
  id: string;
  email: string;
  full_name: string;
  is_nonprofit: boolean;
  created_at: string;
};

type SignupData = {
  email: string;
  password: string;
  fullName: string;
  isNonprofit: boolean;
};

type AuthContextType = {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (data: SignupData) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isLoading: boolean;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('token');
      if (token) {
        const response = await api.get('/auth/me');
        setUser(response.data);
      }
    } catch (error) {
      localStorage.removeItem('token');
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      const response = await api.post('/auth/login', {
        username: email,  // FastAPI OAuth2 expects 'username'
        password,
      });
      const { access_token } = response.data;
      localStorage.setItem('token', access_token);
      await checkAuth();  // Fetch user data after login
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to login');
      }
      throw error;
    }
  };

  const signup = async (data: SignupData) => {
    try {
      const response = await api.post('/auth/signup', {
        email: data.email,
        password: data.password,
        full_name: data.fullName,
        is_nonprofit: data.isNonprofit,
      });
      const { access_token } = response.data;
      localStorage.setItem('token', access_token);
      await checkAuth();  // Fetch user data after signup
    } catch (error) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to create account');
      }
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    router.push('/');
  };

  const value = {
    user,
    login,
    signup,
    logout,
    isAuthenticated: !!user,
    isLoading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
} 