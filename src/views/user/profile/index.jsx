/* eslint-disable */
import React, { useState, useEffect } from 'react';
import { Box, Grid, useToast } from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import Banner from 'views/user/profile/components/Banner';
import ProfileView from 'views/user/profile/components/ProfileView';
import ProfileEdit from 'views/user/profile/components/ProfileEdit';
import banner from 'assets/img/auth/banner.png';
import avatar from 'assets/img/avatars/avatar4.png';
import { getUserProfile } from 'services/api';

export default function Overview() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const toast = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProfile = async () => {
      setLoading(true);
      try {
        const response = await getUserProfile();
        setUser(response);
      } catch (err) {
        toast({
          title: 'Error',
          description: err.response?.data?.detail || 'Failed to fetch profile',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
        navigate('/auth/sign-in');
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, [toast, navigate]);

  if (loading) return <Box>Loading...</Box>;

  return (
    <Box pt={{ base: '130px', md: '80px', xl: '80px' }}>
      <Grid
        gap={{ base: '20px', xl: '20px' }}
      >
        <Banner
          gridArea="1 / 1 / 2 / 2"
          banner={banner}
          avatar={avatar}
          name={user?.first_name || 'User Name'}
          job={user?.role || 'User'}
          posts="0"
          followers="0"
          following="0"
        />
        
        <ProfileView gridArea={{ base: '2 / 1 / 3 / 2', lg: '1 / 2 / 2 / 4' }} />
      </Grid>
      <Grid
        my="40px"
      >
        <ProfileEdit gridArea={{ base: '1 / 1 / 2 / 2', lg: '1 / 1 / 2 / 3', '2xl': '1 / 2 / 2 / 3' }} />
      </Grid>
    </Box>
  );
}