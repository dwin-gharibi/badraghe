import {
  Box
} from "@chakra-ui/react";

import React, { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { useToast } from '@chakra-ui/react';
import { getUserProfile } from 'services/api';

const PrivateRoute = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(null);
  const toast = useToast();

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('authToken');
      if (!token) {
        setIsAuthenticated(false);
        return;
      }

      const expiry = localStorage.getItem('tokenExpiry');
      if (expiry && Date.now() > Number(expiry)) {
        localStorage.removeItem('authToken');
        localStorage.removeItem('tokenExpiry');
        setIsAuthenticated(false);
        toast({
          title: 'Session Expired',
          description: 'Your session has expired. Please log in again.',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
        return;
      }

      try {
        await getUserProfile();
        setIsAuthenticated(true);
      } catch (err) {
        console.error('Auth Check Error:', err);
        localStorage.removeItem('authToken');
        localStorage.removeItem('tokenExpiry');
        setIsAuthenticated(false);
        toast({
          title: 'Authentication Error',
          description: 'Invalid token. Please log in again.',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      }
    };
    checkAuth();
  }, [toast]);

  if (isAuthenticated === null) {
    return <Box>Loading...</Box>;
  }

  return isAuthenticated ? children : <Navigate to="/auth/sign-in" replace />;
};

export default PrivateRoute;