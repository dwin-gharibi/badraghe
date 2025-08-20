import React, { useState, useEffect } from 'react';
import { Box, Grid, useToast } from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import Banner from 'views/user/profile/components/Banner';
import ProfileView from 'views/user/profile/components/ProfileView';
import ProfileEdit from 'views/user/profile/components/ProfileEdit';
import banner from 'assets/img/auth/banner.png';
import avatar from 'assets/img/avatars/dwin.jpg';
import { getUserProfile, searchTickets, listReviews, getUserReservationHistory } from 'services/api';
import { useAuth } from '../../../useAuth';

export default function Overview() {
  const [user, setUser] = useState(null);
  const [counts, setCounts] = useState({ tickets: 0, reviews: 0, reservations: 0 });
  const [loading, setLoading] = useState(true);
  const toast = useToast();
  const navigate = useNavigate();
  const { user: authUser } = useAuth();
  const userId = authUser?.id;

  useEffect(() => {
    const fetchProfileAndCounts = async () => {
      if (!userId) {
        toast({
          title: 'Error',
          description: 'User not authenticated',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
        navigate('/auth/sign-in');
        return;
      }
      setLoading(true);
      try {
        const [profileResponse, ticketsResponse, reviewsResponse, reservationsResponse] = await Promise.all([
          getUserProfile(),
          searchTickets({ user_id: userId, limit: 1, skip: 0, status: 'available' }),
          listReviews({ user_id: userId, limit: 1, skip: 0 }),
          getUserReservationHistory(userId, { limit: 1, skip: 0 }),
        ]);

        setUser({
          id: profileResponse.id,
          first_name: profileResponse.first_name || 'User Name',
          avatar: profileResponse.avatar || avatar,
          role: profileResponse.role || 'Travel Enthusiast',
        });
        console.log(ticketsResponse);

        setCounts({
          tickets: ticketsResponse.total || ticketsResponse.data?.length || 0,
          reviews: reviewsResponse.total || reviewsResponse.data?.length || 0,
          reservations: reservationsResponse.total || reservationsResponse.data?.length || 0,
        });
      } catch (err) {
        toast({
          title: 'Error',
          description: err.response?.data?.detail || 'Failed to fetch profile or counts',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
        navigate('/auth/sign-in');
      } finally {
        setLoading(false);
      }
    };
    fetchProfileAndCounts();
  }, [userId, toast, navigate]);

  if (loading) return <Box>Loading...</Box>;

  return (
    <Box pt={{ base: '130px', md: '80px', xl: '80px' }}>
      <Grid gap={{ base: '20px', xl: '20px' }}>
        <Banner
          gridArea="1 / 1 / 2 / 2"
          banner={banner}
          avatar={user?.avatar}
          name={user?.first_name}
          job={user?.role}
        />
        <ProfileView gridArea={{ base: '2 / 1 / 3 / 2', lg: '1 / 2 / 2 / 4' }} />
      </Grid>
      <Grid my="40px">
        <ProfileEdit gridArea={{ base: '1 / 1 / 2 / 2', lg: '1 / 1 / 2 / 3', '2xl': '1 / 2 / 2 / 3' }} />
      </Grid>
    </Box>
  );
}