import React, { createContext, useContext, useEffect, useState } from 'react';

const AuthContext = createContext({});

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [session, setSession] = useState(null);

  useEffect(() => {
    // Check for existing session
    const token = localStorage.getItem('pbt_token');
    if (token) {
      fetchUser(token);
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUser = async (token) => {
    try {
      const response = await fetch('/api/auth/user', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
        setSession({ access_token: token });
      } else {
        localStorage.removeItem('pbt_token');
      }
    } catch (error) {
      console.error('Error fetching user:', error);
      localStorage.removeItem('pbt_token');
    } finally {
      setLoading(false);
    }
  };

  const signIn = async (email, password) => {
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();

      if (data.success) {
        const token = data.session?.access_token;
        if (token) {
          localStorage.setItem('pbt_token', token);
          setUser(data.user);
          setSession(data.session);
        }
        return { data, error: null };
      } else {
        return { data: null, error: { message: 'Login failed' } };
      }
    } catch (error) {
      return { data: null, error };
    }
  };

  const signUp = async (email, password, fullName = '') => {
    try {
      const response = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          email, 
          password, 
          full_name: fullName 
        })
      });

      const data = await response.json();

      if (data.success) {
        return { data, error: null };
      } else {
        return { data: null, error: { message: 'Signup failed' } };
      }
    } catch (error) {
      return { data: null, error };
    }
  };

  const signOut = async () => {
    try {
      await fetch('/api/auth/logout', { method: 'POST' });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('pbt_token');
      setUser(null);
      setSession(null);
    }
  };

  const signInWithGitHub = async () => {
    try {
      const response = await fetch('/api/auth/github');
      const data = await response.json();
      
      if (data.auth_url) {
        window.location.href = data.auth_url;
      }
    } catch (error) {
      console.error('GitHub auth error:', error);
    }
  };

  const value = {
    user,
    session,
    loading,
    signIn,
    signUp,
    signOut,
    signInWithGitHub
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;