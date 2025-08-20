import React, { useEffect, useState } from 'react';
import { Avatar, Box, Flex, Text, useColorModeValue, Skeleton } from '@chakra-ui/react';
import Card from 'components/card/Card.js';
import { useAuth } from '../../../../useAuth';
import { useToast } from '@chakra-ui/react';
import { searchTickets, listReviews, getUserReservationHistory } from 'services/api';

export default function Banner(props) {
  const { banner, avatar, name, job } = props;
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [ticketCount, setTicketCount] = useState(0);
  const [reviewCount, setReviewCount] = useState(0);
  const [reservationCount, setReservationCount] = useState(0);
  const textColorPrimary = useColorModeValue('secondaryGray.900', 'white');
  const textColorSecondary = useColorModeValue('gray.400', 'gray.400');
  const borderColor = useColorModeValue('white !important', '#111C44 !important');
  const { user } = useAuth();
  const userId = user?.id;
  const toast = useToast();

  useEffect(() => {
    const fetchMetrics = async () => {
      if (!userId) {
        setError('User not authenticated');
        setLoading(false);
        return;
      }
      setLoading(true);
      try {
        const [ticketsResponse, reviewsResponse, reservationsResponse] = await Promise.all([
          searchTickets({ user_id: userId, limit: 1000, skip: 0 }),
          listReviews({ user_id: userId, limit: 1000, skip: 0 }),
          getUserReservationHistory(userId, { limit: 100, skip: 0 }),
        ]);

        setTicketCount(ticketsResponse.total || ticketsResponse?.length || 0);
        setReviewCount(reviewsResponse.total || reviewsResponse?.length || 0);
        setReservationCount(reservationsResponse.total || reservationsResponse?.length || 0);
      } catch (err) {
        setError(err.response?.data?.detail || err.message || 'Failed to fetch metrics');
        toast({
          title: 'Error',
          description: err.response?.data?.detail || err.message || 'Failed to fetch metrics',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setLoading(false);
      }
    };
    fetchMetrics();
  }, [userId, toast]);

  if (error) return <Text color="red.500">{error}</Text>;

  return (
    <Card mb={{ base: '0px', lg: '20px' }} align="center">
      <Box
        bg={`url(${banner})`}
        bgSize="cover"
        borderRadius="16px"
        h="131px"
        w="100%"
      />
      <Avatar
        mx="auto"
        src={avatar}
        h="87px"
        w="87px"
        mt="-43px"
        border="4px solid"
        borderColor={borderColor}
      />
      <Text color={textColorPrimary} fontWeight="bold" fontSize="xl" mt="10px">
        {name}
      </Text>
      <Text color={textColorSecondary} fontSize="sm">
        {job}
      </Text>
      <Flex w="max-content" mx="auto" mt="26px">
        <Flex mx="auto" me="60px" align="center" direction="column">
          {loading ? (
            <Skeleton height="20px" width="50px" />
          ) : (
            <Text color={textColorPrimary} fontSize="2xl" fontWeight="700">
              {reservationCount}
            </Text>
          )}
          <Text color={textColorSecondary} fontSize="sm" fontWeight="400">
            Reservations
          </Text>
        </Flex>
        <Flex mx="auto" me="60px" align="center" direction="column">
          {loading ? (
            <Skeleton height="20px" width="50px" />
          ) : (
            <Text color={textColorPrimary} fontSize="2xl" fontWeight="700">
              {reviewCount}
            </Text>
          )}
          <Text color={textColorSecondary} fontSize="sm" fontWeight="400">
            Reviews
          </Text>
        </Flex>
        <Flex mx="auto" align="center" direction="column">
          {loading ? (
            <Skeleton height="20px" width="50px" />
          ) : (
            <Text color={textColorPrimary} fontSize="2xl" fontWeight="700">
              {ticketCount}
            </Text>
          )}
          <Text color={textColorSecondary} fontSize="sm" fontWeight="400">
            Tickets
          </Text>
        </Flex>
      </Flex>
    </Card>
  );
}