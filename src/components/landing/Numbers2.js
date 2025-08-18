import React, { useState, useEffect } from 'react';
import { Box, Container, Grid, Heading, Text, VStack, useColorModeValue, useToast } from '@chakra-ui/react';
import CountUp from 'react-countup';
import bgMastercard from 'assets/img/layout/cta2.jpg';
import { getFlightStatistics, getTrainStatistics, getBusStatistics, getReportStats } from 'services/api';
import { useAuth } from './../../useAuth';

export default function NumbersSection2() {
  const [stats, setStats] = useState([
    { value: 108, suffix: '+', label: 'Available Flights', decimals: 0, description: 'Number of flights you can book'},
    { value: 4.5, suffix: '', label: 'Average Train Rating', decimals: 1, description: 'Customer satisfaction score for trains'},
    { value: 73, suffix: '+', label: 'Available Buses', decimals: 0, description: 'Total buses ready for service' },
    { value: 41, suffix: '+', label: 'Resolved Reports', decimals: 0, description: 'Issues successfully addressed'},
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
        const [flightStats, trainStats, busStats, reportStats] = await Promise.all([
          getFlightStatistics({ airline: null, from_date: null, to_date: null }),
          getTrainStatistics({ min_rating: null, max_rating: null }),
          getBusStatistics({ bus_type: null }),
          getReportStats({ time_range: 'month' }),
        ]);

        setStats([
          { value: flightStats.by_transport_type?.plane || 108, suffix: '+', label: 'Available Flights', decimals: 0, description: 'Number of flights you can book'},
          { value: trainStats.avg_rating || 4.5, suffix: '', label: 'Average Train Rating', decimals: 1, description: 'Customer satisfaction score for trains'},
          { value: busStats.total_buses?.bus || 73, suffix: '+', label: 'Available Buses', decimals: 0, description: 'Total buses ready for service'},
          { value: reportStats.resolved || 41, suffix: '+', label: 'Resolved Reports', decimals: 0, description: 'Issues successfully addressed'},
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

    if (localStorage.getItem('authToken')) {
      fetchStats();
    } else {
      setLoading(false);
      toast({
        title: 'Authentication Required',
        description: 'Please log in to view statistics.',
        status: 'warning',
        duration: 5000,
        isClosable: true,
      });
    }
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
            <Box
              display={{ base: 'none', lg: 'block' }}
              rounded="xl"
              bgImage={bgMastercard}
              bgSize="cover"
              bgPosition="center"
              h="full"
              minH="600px"
            />
            <VStack align="stretch" spacing={16}>
              <VStack spacing={2} textAlign={{ base: 'center', lg: 'left' }}>
                <Heading
                  fontSize="3xl"
                  fontWeight="extrabold"
                  lineHeight="short"
                  color={headingColor}
                  fontFamily="DM Sans"
                >
                  Badraghe’s Specialized Reach
                </Heading>
                <Text
                  fontSize="md"
                  fontWeight="medium"
                  lineHeight="tall"
                  color={textColor}
                  fontFamily="DM Sans"
                >
                  Delivering tailored travel solutions across flights, trains, and buses.
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
          </Grid>
        )}
      </Container>
    </Box>
  );
}