import React, { useEffect } from 'react';
import { useToast } from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';

function Logout() {
  const navigate = useNavigate();
  const toast = useToast();

  useEffect(() => {
    localStorage.removeItem('authToken');

    toast({
      title: 'Logged Out',
      description: 'You have been logged out successfully.',
      status: 'success',
      duration: 5000,
      isClosable: true,
    });

    navigate('/auth/sign-in');
  }, [navigate, toast]);

  return null;
}

export default Logout;
