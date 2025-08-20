import React, { useEffect, useState } from 'react';
import { SimpleGrid, Text, useColorModeValue, Button, Flex, Icon } from '@chakra-ui/react';
import Card from 'components/card/Card';
import Information from 'views/user/profile/components/Information';
import { getUserProfile, getUnreadNotificationCount } from 'services/api';
import { useToast } from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { FaUser } from 'react-icons/fa';

export default function ProfileView() {
  const [profile, setProfile] = useState({});
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const textColorPrimary = useColorModeValue('secondaryGray.900', 'white');
  const textColorSecondary = 'gray.400';
  const cardShadow = useColorModeValue('0px 18px 40px rgba(112, 144, 176, 0.12)', 'unset');
  const toast = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProfile = async () => {
      setLoading(true);
      try {
        const profileResponse = await getUserProfile();
        const unreadResponse = await getUnreadNotificationCount();
        setProfile(profileResponse);
        setUnreadCount(unreadResponse.count || 0);
      } catch (err) {
        setError(err.message || 'Failed to fetch profile or notifications');
        toast({
          title: 'Error',
          description: err.message || 'Failed to fetch profile or notifications',
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

  if (loading) return <Text>Loading...</Text>;
  if (error) return <Text color="red.500">{error}</Text>;

  return (
    <Card mb={{ base: '0px', '2xl': '20px' }}>
      <Flex justifyContent="space-between" align="center" mb="20px">
        <Text color={textColorPrimary} fontWeight="bold" fontSize="2xl" mt="10px">
          <Icon as={FaUser} color="brand.500" w={5} h={5} mx={2}/> Profile Information
        </Text>
      </Flex>
      <Text color={textColorSecondary} fontSize="md" me="26px" mb="40px" mx={2}>
        View your personal details and account information below.
      </Text>
      <SimpleGrid columns={{ sm: 1, md: 2 }} gap="20px">
        <Information
          boxShadow="none"
          title="First Name"
          value={profile.first_name || 'N/A'}
        />
        <Information
          boxShadow="none"

          title="Last Name"
          value={profile.last_name || 'N/A'}
        />
        <Information
          boxShadow="none"

          title="Email"
          value={profile.email || 'N/A'}
        />
        <Information
          boxShadow="none"

          title="Phone"
          value={profile.phone || 'N/A'}
        />
        <Information
          boxShadow="none"

          title="Balance"
          value={`${profile.balance} IRR`}
        />
        <Information
          boxShadow="none"

          title="Country"
          value={profile.country || 'N/A'}
        />
        <Information
          boxShadow="none"

          title="City"
          value={profile.city || 'N/A'}
        />
        <Information
          boxShadow="none"
          title="Date of Birth"
          value={profile.date_of_birth || 'N/A'}
        />
      </SimpleGrid>
    </Card>
  );
}