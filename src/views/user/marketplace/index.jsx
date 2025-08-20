/* eslint-disable */
import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Flex,
  Text,
  useColorModeValue,
  SimpleGrid,
  keyframes,
  CircularProgress,
  Container,
  CircularProgressLabel,
  Skeleton,
  VStack,
  HStack,
  Icon,
  Avatar,
} from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { createColumnHelper } from '@tanstack/react-table';
import Banner from 'views/user/marketplace/components/Banner';
import HistoryItem from 'views/user/marketplace/components/HistoryItem';
import TableTopCreators from 'views/user/marketplace/components/TableTopCreators';
import Card from 'components/card/Card.js';
import { searchTickets, listReviews, getUserReservationHistory, getServiceProviders, getProviderTickets, getUserProfile } from 'services/api';
import { useToast } from '@chakra-ui/react';
import { useAuth } from '../../../useAuth';
import { FaTicketAlt, FaStar, FaCheckCircle, FaPlane, FaTrain, FaBus, FaMapMarkerAlt, FaDollarSign, FaHeart, FaCreditCard } from 'react-icons/fa';

const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
`;
const scaleHover = keyframes`
  from { transform: scale(1); }
  to { transform: scale(1.05); }
`;
const pulse = keyframes`
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
`;

const columnHelper = createColumnHelper();

export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [ticketCount, setTicketCount] = useState(0);
  const [reviewCount, setReviewCount] = useState(0);
  const [reservationStats, setReservationStats] = useState({
    total: 0,
    paid: 0,
    pending: 0,
    canceled: 0,
  });
  const [averageRating, setAverageRating] = useState(0);
  const [totalSpent, setTotalSpent] = useState(0);
  const [topDestinations, setTopDestinations] = useState([]);
  const [upcomingReservations, setUpcomingReservations] = useState([]);
  const [latestReservations, setLatestReservations] = useState([]);
  const [latestReview, setLatestReview] = useState(null);
  const [topTickets, setTopTickets] = useState([]);
  const [topProviders, setTopProviders] = useState([]);
  const [popularTransport, setPopularTransport] = useState('unknown');
  const [loyaltyStatus, setLoyaltyStatus] = useState('Traveler');
  const [recommendedTrips, setRecommendedTrips] = useState([]);
  const [latestPaymentStatus, setLatestPaymentStatus] = useState('N/A');
  const [userProfile, setUserProfile] = useState({ name: 'Traveler', avatar: 'https://via.placeholder.com/150' });
  const textColor = useColorModeValue('secondaryGray.900', 'white');
  const textColorBrand = useColorModeValue('brand.500', 'white');
  const bgColor = useColorModeValue('white', 'navy.700');
  const toast = useToast();
  const { user } = useAuth();
  const userId = user?.id;
  const navigate = useNavigate();

  const formatDateTime = (isoString) => {
    return isoString ? new Date(isoString).toLocaleString('en-US', { dateStyle: 'medium', timeStyle: 'short' }) : 'N/A';
  };

  useEffect(() => {
    const fetchDashboardData = async () => {
      if (!userId) {
        setError('User not authenticated');
        setLoading(false);
        toast({
          title: 'Error',
          description: 'Please log in to view your dashboard.',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
        navigate('/auth/sign-in');
        return;
      }
      setLoading(true);
      try {
        const [profileResponse, ticketsResponse, reviewsResponse, reservationsResponse, providersResponse] = await Promise.all([
          getUserProfile().catch(() => ({ first_name: 'Traveler', avatar: 'https://via.placeholder.com/150' })),
          searchTickets({ user_id: userId, limit: 5, skip: 0, status: 'available' }).catch(() => ({ data: [], total: 0 })),
          listReviews({ user_id: userId, limit: 1, skip: 0 }).catch(() => ({ data: [], total: 0 })),
          getUserReservationHistory(userId, { limit: 10, skip: 0 }).catch(() => ({ data: [], total: 0 })),
          getServiceProviders({ limit: 5, skip: 0 }).catch(() => ({ data: [], total: 0 })),
        ]);

        setUserProfile({
          name: profileResponse.first_name || 'Traveler',
          avatar: profileResponse.avatar || 'https://via.placeholder.com/150',
        });

        setTicketCount(ticketsResponse.total || ticketsResponse?.length || 0);
        const tickets = ticketsResponse.data || ticketsResponse;
        setTopTickets(tickets.map((ticket) => ({
          name: [ticket.departure_city + ' to ' + ticket.arrival_city, 'https://via.placeholder.com/30'],
          artworks: ticket.available_seats || 0,
          rating: Math.min(Number(ticket.price) / 1000000, 100) || 0,
          transport_type: ticket.transport_type || 'unknown',
          currency: ticket.currency || 'USD',
        })));

        setRecommendedTrips(tickets.slice(0, 3).map((ticket) => ({
          name: [ticket.departure_city + ' to ' + ticket.arrival_city, 'https://via.placeholder.com/30'],
          artworks: ticket.available_seats || 0,
          rating: Math.min(Number(ticket.price) / 1000000, 100) || 0,
          transport_type: ticket.transport_type || 'unknown',
          currency: ticket.currency || 'USD',
        })));

        const reviews = reviewsResponse.data || reviewsResponse;
        setReviewCount(reviewsResponse.total || reviews.length || 0);
        if (reviews.length > 0) {
          const totalRating = reviews.reduce((sum, review) => sum + (Number(review.rating) || 0), 0);
          setAverageRating((totalRating / reviews.length).toFixed(1));
          setLatestReview(reviews[0]);
        } else {
          setAverageRating(0);
          setLatestReview(null);
        }

        const reservations = reservationsResponse.data || reservationsResponse;
        const total = reservationsResponse.total || reservations.length || 0;
        const paid = reservations.filter((r) => r.status === 'paid').length;
        const pending = reservations.filter((r) => r.status === 'pending' || r.status === 'temporary').length;
        const canceled = reservations.filter((r) => r.status === 'canceled').length;
        setReservationStats({ total, paid, pending, canceled });

        const totalSpent = reservations.reduce((sum, r) => sum + (Number(r.price_paid) || 0), 0);
        setTotalSpent(totalSpent);

        const destinationCounts = reservations.reduce((acc, r) => {
          const city = r.ticket_details?.arrival_city || 'Unknown';
          acc[city] = (acc[city] || 0) + 1;
          return acc;
        }, {});
        const topDests = Object.entries(destinationCounts)
          .sort((a, b) => b[1] - a[1])
          .slice(0, 3)
          .map(([city, count]) => ({ city, count }));
        setTopDestinations(topDests);

        const upcoming = reservations
          .filter((r) => new Date(r.ticket_details?.departure_time) > new Date())
          .slice(0, 3);
        setUpcomingReservations(upcoming);

        setLatestReservations(reservations.slice(0, 5));

        const latestPayment = reservations
          .filter((r) => r.payment_details?.status)
          .sort((a, b) => new Date(b.payment_details?.payment_date) - new Date(a.payment_details?.payment_date))[0];
        setLatestPaymentStatus(latestPayment?.payment_details?.status || 'N/A');

        const transportCounts = reservations.reduce((acc, r) => {
          const type = r.ticket_details?.transport_type || 'unknown';
          acc[type] = (acc[type] || 0) + 1;
          return acc;
        }, {});
        const popular = Object.entries(transportCounts).reduce((a, b) => (a[1] > b[1] ? a : b), ['unknown', 0])[0];
        setPopularTransport(popular);

        setLoyaltyStatus(total >= 10 ? 'Gold Traveler' : total >= 5 ? 'Silver Traveler' : 'Traveler');

        const providers = providersResponse.data || providersResponse;
        const providerData = await Promise.all(
          providers.map(async (provider) => {
            try {
              const ticketCount = tickets.total || tickets?.length || 0;
              const avgPrice = tickets?.length
                ? (tickets.data.reduce((sum, t) => sum + (Number(t.price) || 0), 0) / tickets.length / 1000000).toFixed(2)
                : 0;
              return {
                name: [provider.name, provider.logo || 'https://via.placeholder.com/30'],
                artworks: ticketCount,
                rating: Number(avgPrice),
              };
            } catch (err) {
              console.error(`Failed to fetch tickets for provider ${provider.id}:`, err.message);
              return {
                name: [provider.name, provider.logo || 'https://via.placeholder.com/30'],
                artworks: 0,
                rating: 0,
              };
            }
          })
        );
        setTopProviders(providerData);
      } catch (err) {
        setError(err.response?.data?.detail || err.message || 'Failed to fetch dashboard data');
        toast({
          title: 'Error',
          description: err.response?.data?.detail || err.message || 'Failed to fetch dashboard data',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setLoading(false);
      }
    };
    fetchDashboardData();
  }, [userId, toast, navigate]);

  const tableColumnsTopProviders = [
    columnHelper.accessor('name', {
      id: 'name',
      header: () => (
        <Text justifyContent="space-between" align="center" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          PROVIDER
        </Text>
      ),
      cell: (info) => (
        <Flex align="center">
          <Avatar src={info.getValue()[1]} w="30px" h="30px" me="8px" />
          <Text color={textColor} fontSize="sm" fontWeight="600">
            {info.getValue()[0]}
          </Text>
        </Flex>
      ),
    }),
    columnHelper.accessor('artworks', {
      id: 'artworks',
      header: () => (
        <Text justifyContent="space-between" align="center" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          TICKETS
        </Text>
      ),
      cell: (info) => (
        <Text color={textColor} fontSize="sm" fontWeight="500">
          {info.getValue()}
        </Text>
      ),
    }),
    columnHelper.accessor('rating', {
      id: 'rating',
      header: () => (
        <Text justifyContent="space-between" align="center" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          AVG PRICE (MILLIONS)
        </Text>
      ),
      cell: (info) => (
        <Flex align="center">
          <CircularProgress value={Math.min(info.getValue() * 10, 100)} color="brand.500" size="50px">
            <CircularProgressLabel>{info.getValue()}</CircularProgressLabel>
          </CircularProgress>
        </Flex>
      ),
    }),
  ];

  const getTransportIcon = (transportType) => {
    switch (transportType?.toLowerCase()) {
      case 'plane':
      case 'flight':
        return FaPlane;
      case 'train':
        return FaTrain;
      case 'bus':
        return FaBus;
      default:
        return FaPlane;
    }
  };

  if (error) return <Text color="red.500">{error}</Text>;

  return (
    <Box pt={{ base: '100px', md: '100px', xl: '100px' }} minH="100vh">
      <Container maxW="container.xl">
        <VStack spacing={8} align="stretch" animation={`${fadeIn} 0.5s ease-out`}>
          <Banner
            banner="https://via.placeholder.com/1200x300/1e90ff/6a5acd?text=Badraghe+Travel"
            avatar={userProfile.avatar}
            name={userProfile.name}
            job={`Travel Enthusiast - ${loyaltyStatus}`}
            ticketCount={ticketCount}
            reviewCount={reviewCount}
            reservationCount={reservationStats.total}
          />
          <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} gap={6}>
            <Card p="20px" bg={bgColor} animation={`${fadeIn} 0.6s ease-out`} >
              {loading ? (
                <Skeleton height="100px" />
              ) : (
                <Flex direction="column" align="center">
                  <Icon as={FaTicketAlt} w={10} h={10} color="brand.500" mb={2} _hover={{ animation: `${pulse} 1s infinite` }} />
                  <Text color={textColor} fontSize="lg" fontWeight="600" mb="4px">
                    Total Tickets
                  </Text>
                  <Text color={textColor} fontSize="2xl" fontWeight="700">
                    {ticketCount}
                  </Text>
                  <Text color="gray.600" fontSize="sm">
                    Available for booking
                  </Text>
                </Flex>
              )}
            </Card>
            <Card p="20px" bg={bgColor} animation={`${fadeIn} 0.7s ease-out`} >
              {loading ? (
                <Skeleton height="100px" />
              ) : (
                <Flex direction="column" align="center">
                  <Icon as={FaStar} w={10} h={10} color="brand.500" mb={2} _hover={{ animation: `${pulse} 1s infinite` }} />
                  <Text color={textColor} fontSize="lg" fontWeight="600" mb="4px">
                    Total Reviews
                  </Text>
                  <Text color={textColor} fontSize="2xl" fontWeight="700">
                    {reviewCount}
                  </Text>
                  <Text color="gray.600" fontSize="sm">
                    Your submitted reviews
                  </Text>
                </Flex>
              )}
            </Card>
            <Card p="20px" bg={bgColor} animation={`${fadeIn} 0.8s ease-out`} >
              {loading ? (
                <Skeleton height="100px" />
              ) : (
                <Flex direction="column" align="center">
                  <Icon as={FaCheckCircle} w={10} h={10} color="brand.500" mb={2} _hover={{ animation: `${pulse} 1s infinite` }} />
                  <Text color={textColor} fontSize="lg" fontWeight="600" mb="4px">
                    Reservations
                  </Text>
                  <Text color={textColor} fontSize="2xl" fontWeight="700">
                    {reservationStats.total}
                  </Text>
                  <Text color="gray.600" fontSize="sm">
                    Paid: {reservationStats.paid}, Pending: {reservationStats.pending}, Canceled: {reservationStats.canceled}
                  </Text>
                </Flex>
              )}
            </Card>
            <Card p="20px" bg={bgColor} animation={`${fadeIn} 0.9s ease-out`} >
              {loading ? (
                <Skeleton height="100px" />
              ) : (
                <Flex direction="column" align="center">
                  <Icon as={FaDollarSign} w={10} h={10} color="brand.500" mb={2} _hover={{ animation: `${pulse} 1s infinite` }} />
                  <Text color={textColor} fontSize="lg" fontWeight="600" mb="4px">
                    Total Spent
                  </Text>
                  <Text color={textColor} fontSize="2xl" fontWeight="700">
                    {totalSpent.toLocaleString()} {topTickets[0]?.currency || 'USD'}
                  </Text>
                  <Text color="gray.600" fontSize="sm">
                    Across all reservations
                  </Text>
                </Flex>
              )}
            </Card>
            <Card p="20px" bg={bgColor}  animation={`${fadeIn} 1.0s ease-out`} >
              {loading ? (
                <Skeleton height="100px" />
              ) : (
                <Flex direction="column" align="center">
                  <Icon as={FaStar} w={10} h={10} color="brand.500" mb={2} _hover={{ animation: `${pulse} 1s infinite` }} />
                  <Text color={textColor} fontSize="lg" fontWeight="600" mb="4px">
                    Average Rating
                  </Text>
                  <Text color={textColor} fontSize="2xl" fontWeight="700">
                    {averageRating}
                  </Text>
                  <Text color="gray.600" fontSize="sm">
                    Based on your reviews
                  </Text>
                </Flex>
              )}
            </Card>
            <Card p="20px" bg={bgColor}  animation={`${fadeIn} 1.1s ease-out`} >
              {loading ? (
                <Skeleton height="100px" />
              ) : (
                <Flex direction="column" align="center">
                  <Icon as={getTransportIcon(popularTransport)} w={10} h={10} color="brand.500" mb={2} _hover={{ animation: `${pulse} 1s infinite` }} />
                  <Text color={textColor} fontSize="lg" fontWeight="600" mb="4px">
                    Popular Transport
                  </Text>
                  <Text color={textColor} fontSize="2xl" fontWeight="700">
                    {popularTransport.charAt(0).toUpperCase() + popularTransport.slice(1)}
                  </Text>
                  <Text color="gray.600" fontSize="sm">
                    Most booked transport type
                  </Text>
                </Flex>
              )}
            </Card>
            <Card p="20px" bg={bgColor}  animation={`${fadeIn} 1.2s ease-out`} >
              {loading ? (
                <Skeleton height="100px" />
              ) : (
                <Flex direction="column" align="center">
                  <Icon as={FaHeart} w={10} h={10} color="brand.500" mb={2} _hover={{ animation: `${pulse} 1s infinite` }} />
                  <Text color={textColor} fontSize="lg" fontWeight="600" mb="4px">
                    Loyalty Status
                  </Text>
                  <Text color={textColor} fontSize="2xl" fontWeight="700">
                    {loyaltyStatus}
                  </Text>
                  <Text color="gray.600" fontSize="sm">
                    Based on {reservationStats.total} reservations
                  </Text>
                </Flex>
              )}
            </Card>
            <Card p="20px" bg={bgColor}  animation={`${fadeIn} 1.3s ease-out`} >
              {loading ? (
                <Skeleton height="100px" />
              ) : (
                <Flex direction="column" align="center">
                  <Icon as={FaCreditCard} w={10} h={10} color="brand.500" mb={2} _hover={{ animation: `${pulse} 1s infinite` }} />
                  <Text color={textColor} fontSize="lg" fontWeight="600" mb="4px">
                    Latest Payment Status
                  </Text>
                  <Text color={textColor} fontSize="2xl" fontWeight="700">
                    {latestPaymentStatus}
                  </Text>
                  <Text color="gray.600" fontSize="sm">
                    Most recent payment
                  </Text>
                </Flex>
              )}
            </Card>
          </SimpleGrid>
          <Card p="0px" bg={bgColor}  animation={`${fadeIn} 0.8s ease-out`} >
            <Flex align="center" justify="space-between" w="100%" px="22px" py="18px">
              <Text color={textColor} fontSize="xl" fontWeight="600">
                Top Destinations
              </Text>
              <Button
                colorScheme="teal"
                bg="brand.500"
                color="white"
                rounded="full"
                onClick={() => navigate('/user/reservations')}
                _hover={{ animation: `${scaleHover} 0.3s`, bg: 'teal.600' }}
                transition="background 0.2s"
              >
                Explore More
              </Button>
            </Flex>
            {loading ? (
              <Skeleton height="100px" mx="22px" mb="20px" />
            ) : topDestinations.length > 0 ? (
              <SimpleGrid columns={{ base: 1, md: 3 }} gap={4} px="22px" pb="20px">
                {topDestinations.map((dest, index) => (
                  <Flex
                    key={index}
                    direction="column"
                    align="center"
                    p={4}
                    rounded="lg"
                    transition="transform 0.2s, box-shadow 0.2s"
                  >
                    <Icon as={FaMapMarkerAlt} w={6} h={6} color="brand.500" mb={2} _hover={{ animation: `${pulse} 1s infinite` }} />
                    <Text color={textColor} fontSize="md" fontWeight="600">
                      {dest.city}
                    </Text>
                    <Text color="gray.600" fontSize="sm">
                      Visited {dest.count} time{dest.count > 1 ? 's' : ''}
                    </Text>
                  </Flex>
                ))}
              </SimpleGrid>
            ) : (
              <Text color={textColor} px="22px" pb="20px">
                No destinations found.
              </Text>
            )}
          </Card>
          <Card p="0px" bg={bgColor}  animation={`${fadeIn} 0.9s ease-out`} >
            <Flex align="center" justify="space-between" w="100%" px="22px" py="18px">
              <Text color={textColor} fontSize="xl" fontWeight="600">
                Upcoming Trips
              </Text>
              <Button
                colorScheme="teal"
                bg="brand.500"
                color="white"
                rounded="full"
                onClick={() => navigate('/user/reservations')}
                _hover={{ animation: `${scaleHover} 0.3s`, bg: 'teal.600' }}
                transition="background 0.2s"
              >
                View All
              </Button>
            </Flex>
            {loading ? (
              <Skeleton height="100px" mx="22px" mb="20px" />
            ) : upcomingReservations.length > 0 ? (
              <VStack spacing="10px" px="22px" pb="20px" align="start">
                {upcomingReservations.map((reservation, index) => (
                  <HistoryItem
                    key={index}
                    name={`${reservation.ticket_details.departure_city || 'N/A'} to ${reservation.ticket_details.arrival_city || 'N/A'}`}
                    author={`Status: ${reservation.status} | ${reservation.ticket_details.transport_type ? reservation.ticket_details.transport_type.charAt(0).toUpperCase() + reservation.ticket_details.transport_type.slice(1) : 'N/A'}`}
                    date={formatDateTime(reservation.ticket_details.departure_time)}
                    price={`${reservation.ticket_details.price || 0} ${reservation.ticket_details.currency || 'USD'}`}
                    _hover={{ transform: 'scale(1.02)', boxShadow: '0px 10px 20px rgba(0, 0, 0, 0.2)' }}
                    transition="transform 0.2s, box-shadow 0.2s"
                  />
                ))}
              </VStack>
            ) : (
              <Text color={textColor} px="22px" pb="20px">
                No upcoming trips found.
              </Text>
            )}
          </Card>
         </VStack>
      </Container>
    </Box>
  );
}