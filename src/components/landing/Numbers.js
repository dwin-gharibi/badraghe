import React, { useState, useEffect } from 'react';
import { Box, Container, Grid, Heading, Text, VStack, useColorModeValue, useToast } from '@chakra-ui/react';
import CountUp from 'react-countup';
import bgMastercard from 'assets/img/layout/cta.jpg';
import { getReservationStats, getTicketStats } from 'services/api';

export default function NumbersSection() {
  const [stats, setStats] = useState([
    { value: 1188, suffix: '+', label: 'Total Reservations', decimals: 0, description: 'All reservations made through the platform'},
    { value: 2.5, suffix: '+', label: 'Paid Reservations', decimals: 0, description: 'Reservations that have been fully paid'},
    { value: 1000, suffix: '+', label: 'Available Tickets', decimals: 0, description: 'Tickets currently available for booking'},
    { value: 924, suffix: '+', label: 'Total Tickets', decimals: 0, description: 'All tickets issued so far'},
  ]);
  const [loading, setLoading] = useState(true);
  const toast = useToast();
  const headingColor = useColorModeValue('gray.900', 'white');
  const textColor = useColorModeValue('gray.600', 'gray.300');
  const bgColor = useColorModeValue('white', 'white');

  useEffect(() => {
    const fetchStats = async () => {
      setLoading(true);
      try {
        const [reservationStats, ticketStats] = await Promise.all([
          getReservationStats({ transport_type: null, start_date: null, end_date: null }),
          getTicketStats({ transport_type: null, class_type: null }),
        ]);

        setStats([
          { value: reservationStats.total_reservations || 1188, suffix: '+', label: 'Total Reservations', decimals: 0 , description: 'All reservations made through the platform'},
          { value: reservationStats.paid || 2.5, suffix: '+', label: 'Paid Reservations', decimals: 0, description: 'Reservations that have been fully paid'},
          { value: ticketStats.available || 1000, suffix: '+', label: 'Available Tickets', decimals: 0, description: 'Tickets currently available for booking'},
          { value: ticketStats.total_tickets || 924, suffix: '+', label: 'Total Tickets', decimals: 0, description: 'All tickets issued so far'},
        ]);
      } catch (err) {
        console.error('Fetch Stats Error:', err);
        toast({
          title: 'Error',
          description: err.response?.data?.detail || 'Failed to fetch statistics',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setLoading(false);
      }
    };
    
    fetchStats();
  }, [toast]);

  return (
    <Box w="full" py={{ base: 10, lg: 10 }} bg={bgColor}>
      <Container maxW="container.xl">
        {loading ? (
          <Text textAlign="center" color={textColor}>Loading statistics...</Text>
        ) : (
          <Grid
            templateColumns={{ base: '1fr', lg: '1fr 1fr' }}
            gap={{ base: 16, lg: 32 }}
            alignItems="center"
          >
            <VStack align="stretch" spacing={16}>
              <VStack spacing={2} textAlign={{ base: 'center', lg: 'left' }}>
                <Heading
                  fontSize="3xl"
                  fontWeight="extrabold"
                  lineHeight="short"
                  color={headingColor}
                  fontFamily="DM Sans"
                >
                  Discover Badraghe’s Impact
                </Heading>
                <Text
                  fontSize="md"
                  fontWeight="medium"
                  lineHeight="tall"
                  color={textColor}
                  fontFamily="DM Sans"
                >
                  Connecting travelers worldwide with seamless booking experiences.
                </Text>
              </VStack>
              <Grid templateColumns={{ base: '1fr', md: '1fr 1fr' }} gapX={10} gapY={16}>
                {stats.map((stat, index) => (
                  <VStack key={index} align="flex-start" spacing={1}>
                    <Heading
                      fontSize="4xl"
                      fontWeight="extrabold"
                      lineHeight="tight"
                      color={headingColor}
                      fontFamily="DM Sans"
                    >
                      {stat.prefix && stat.prefix}
                      <CountUp end={stat.value} duration={2} decimals={stat.decimals || 0} />
                      {stat.suffix}
                    </Heading>
                    <Heading
                      fontSize="md"
                      fontWeight="bold"
                      lineHeight="tight"
                      color={headingColor}
                      fontFamily="DM Sans"
                    >
                      {stat.label}
                    </Heading>
                    <Text
                      fontSize="md"
                      fontWeight="medium"
                      lineHeight="tall"
                      color={textColor}
                      fontFamily="DM Sans"
                    >
                      {stat.description}
                    </Text>
                  </VStack>
                ))}
              </Grid>
            </VStack>
            <Box
              display={{ base: 'none', lg: 'block' }}
              rounded="xl"
              bgImage={bgMastercard}
              bgSize="cover"
              bgPosition="center"
              h="full"
              minH="600px"
            />
          </Grid>
        )}
      </Container>
    </Box>
  );
}