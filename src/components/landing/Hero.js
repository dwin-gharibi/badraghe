import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Flex,
  VStack,
  HStack,
  Heading,
  Text,
  Icon,
  Textarea,
  Button,
  Select,
  Checkbox,
  useColorModeValue,
  useToast,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
} from '@chakra-ui/react';
import { FaRocket, FaPlane, FaSearch, FaMagic, FaComments, FaInfoCircle, FaTicketAlt, FaTags } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';
import TravelSearch from './Search';
import ReactMarkdown from 'react-markdown';
import { sendAIQuery, createReservation, payForReservation, getPaymentMethods, getTrainDetails, getBusDetails, getFlightDetails, checkTicketExists } from 'services/api';

export default function SexyHeroWithSearch() {
  const bg = useColorModeValue(
    'linear-gradient(135deg, #6B73FF 0%, #000DFF 100%)',
    'linear-gradient(135deg, #1A202C 0%, #2D3748 100%)'
  );
  const borderColor = useColorModeValue('gray.300', 'gray.600');
  const bgInput = useColorModeValue('transparent', 'transparent');
  const textColor = 'white';
  const subTextColor = 'whiteAlpha.800';
  const [aiQuery, setAiQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [recommendation, setRecommendation] = useState('');
  const [tickets, setTickets] = useState([]);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [passengers, setPassengers] = useState(1);
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [paymentMethod, setPaymentMethod] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [autoReserve, setAutoReserve] = useState(false);
  const toast = useToast();
  const navigate = useNavigate();
  let selected;

  useEffect(() => {
    const fetchPaymentMethods = async () => {
      try {
        const response = await getPaymentMethods();
        setPaymentMethods(response.data || response);
      } catch (err) {
        toast({
          title: 'Error',
          description: err.response?.data?.detail || err.message || 'Failed to fetch payment methods',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      }
    };
    fetchPaymentMethods();
  }, [toast]);

  const handleAIQuerySubmit = async () => {
    if (!aiQuery.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter a query',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      return;
    }
    setLoading(true);
    try {
      const response = await sendAIQuery(aiQuery);
      if (response.reservation) {
        toast({
          title: 'Success',
          description: 'Reservation created successfully via AI',
          status: 'success',
          duration: 5000,
          isClosable: true,
        });
        navigate('/reservations');
      } else {
        setRecommendation(response.recommendation || '');
        setTickets(response.tickets || []);
        if (response.tickets?.length > 0) {
          const firstTicket = response.tickets[0];
          console.log('First Ticket:', firstTicket);
          console.log("iddddd", firstTicket.id)
          let firstTicketId;
          if (firstTicket && typeof firstTicket.id === 'number') {
            firstTicketId = firstTicket.id;
          } else if (firstTicket && typeof firstTicket.id === 'string') {
            firstTicketId = parseInt(firstTicket.id, 10);
          } else {
            console.error('Invalid ticket ID structure:', firstTicket);
            toast({
              title: 'Error',
              description: 'Invalid ticket ID in response',
              status: 'error',
              duration: 5000,
              isClosable: true,
            });
            setIsModalOpen(true);
            return;
          }
          if (isNaN(firstTicketId) || firstTicketId <= 0) {
            console.error('Parsed ticket ID is invalid:', firstTicket.id);
            toast({
              title: 'Error',
              description: 'Invalid ticket ID: not a valid number',
              status: 'error',
              duration: 5000,
              isClosable: true,
            });
            setIsModalOpen(true);
            return;
          }
          console.log("iddddd", firstTicket.id)
          setSelectedTicket(firstTicket.id);
          selected = firstTicket.id;
          setIsModalOpen(true);
          console.log(response.tickets);
          if (autoReserve) {
            const ticketAvailable = await checkTicketExists(firstTicket.id);
            if (ticketAvailable) {
              await handleBookTicket(firstTicket.id);
            } else {
              toast({
                title: 'Error',
                description: 'Selected ticket is not available or sold out',
                status: 'error',
                duration: 5000,
                isClosable: true,
              });
            }
          }
        } else {
          toast({
            title: 'Nothing Found',
            description: 'No tickets found for your query',
            status: 'warning',
            duration: 5000,
            isClosable: true,
          });
        }
      }
      setAiQuery('');
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || error.message || 'Failed to process AI query',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleViewDetails = async (ticketId, transportType) => {
    setLoading(true);
    console.log("tempppp", ticketId);
    try {
      let response;
      switch (transportType) {
        case 'plane':
          response = await getFlightDetails(ticketId);
          break;
        case 'train':
          response = await getTrainDetails(ticketId);
          break;
        case 'bus':
          response = await getBusDetails(ticketId);
          break;
        default:
          throw new Error('Invalid transport type');
      }
      toast({
        title: 'Now you can see ticket details',
        description: response.summary,
        status: 'info',
        duration: 10000,
        isClosable: true,
      });
    } catch (err) {
      toast({
        title: 'Error',
        description: err.response?.data?.detail || err.message || 'Failed to fetch ticket details',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleBookTicket = async (ticketId = selectedTicket) => {
    console.log("tempppp", ticketId);
    if (!ticketId || !passengers || !paymentMethod) {
      toast({
        title: 'Error',
        description: 'Please select a ticket, number of passengers, and payment method',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      return;
    }
    setLoading(true);
    try {
      const ticketAvailable = await checkTicketExists(ticketId);
      if (!ticketAvailable) {
        toast({
          title: 'Error',
          description: 'Selected ticket is not available or sold out',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
        return;
      }
      const reservationData = {
        ticket_id: ticketId,
        user_id: 1,
        passengers: parseInt(passengers),
      };
      const reservationResponse = await createReservation(reservationData);
  
      const reservationId = reservationResponse.id;

      const paymentData = {
        amount: tickets.find((ticket) => ticket.id === ticketId)?.price,
        currency: tickets.find((ticket) => ticket.id === ticketId)?.currency,
        payment_method_id: paymentMethod,
      };
      await payForReservation(reservationId, paymentData);

      toast({
        title: 'Success',
        description: 'Reservation and payment created successfully',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      setIsModalOpen(false);
      navigate('/reservations');
    } catch (err) {
      toast({
        title: 'Error',
        description: err.response?.data?.detail || err.message || 'Failed to create reservation or payment',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Box bgGradient={bg} position="relative" overflow="hidden" pb={{ base: 40, md: 44 }}>
        <Container maxW="container.xl" pt={{ base: 32, md: 40 }}>
          <Flex
            direction={{ base: 'column', lg: 'row' }}
            align="center"
            gap={{ base: 8, lg: 16 }}
          >
            <VStack
              align={{ base: 'center', lg: 'flex-start' }}
              spacing={6}
              textAlign={{ base: 'center', lg: 'left' }}
              flex="1"
            >
              <HStack
                spacing={1}
                bg="rgba(255,255,255,0.15)"
                px={4}
                py={1}
                rounded="full"
                backdropFilter="blur(12px)"
              >
                <Text
                  fontSize="sm"
                  fontWeight="bold"
                  letterSpacing="wide"
                  color="whiteAlpha.900"
                >
                  EXPLORE WITH AI
                </Text>
              </HStack>
              <Heading
                as="h1"
                size="3xl"
                fontWeight="extrabold"
                lineHeight="short"
                color={textColor}
                maxW="lg"
              >
                Plan Your Perfect Trip with Badraghe
              </Heading>
              <Text fontSize="md" color={subTextColor} maxW="lg">
                Discover the easiest way to book flights, trains, and buses. Let our AI assist you in finding the best travel options tailored to your needs.
              </Text>
            </VStack>
            <Box flex="1" display={{ base: 'none', lg: 'block' }} position="relative">
              <Box py={8} px={{ base: 4, md: 0 }} bg="white" shadow="xl" rounded="2xl">
                <VStack spacing={2} align="stretch">
                  <Text fontSize="lg" fontWeight="bold" color="black" ml={3} pl={4}>
                    Ask Our AI Travel Assistant
                  </Text>
                  <HStack
                    align="start"
                    border={`1px solid ${borderColor}`}
                    rounded="xl"
                    p={4}
                    spacing={3}
                    bg={bgInput}
                  >
                    <Icon as={FaComments} color="blue.400" mt={3} ml={3}/>
                    <Textarea
                      value={aiQuery}
                      onChange={(e) => setAiQuery(e.target.value)}
                      placeholder="Tell us your travel plans or ask for recommendations (e.g., 'Find a cheap flight from Tehran to Shiraz')"
                      resize="vertical"
                      border="none"
                      _focus={{ boxShadow: 'none' }}
                      rows={6}
                      isDisabled={loading}
                    />
                  </HStack>
                  <Text fontSize="md" fontWeight="normal" color="gray" ml={3} pl={6}>
                    By using this service you will accept Badraghe data privacy rules.
                  </Text>
                  <HStack justify="space-between" align="center">
                    <Checkbox
                      isChecked={autoReserve}
                      onChange={(e) => setAutoReserve(e.target.checked)}
                      colorScheme="brand"
                      ml={8}
                      isDisabled={loading}
                    >
                      Auto-reserve best ticket
                    </Checkbox>
                    <Button
                      leftIcon={<Icon as={FaMagic} />}
                      colorScheme="blue"
                      onClick={handleAIQuerySubmit}
                      rounded="full"
                      isLoading={loading}
                      size="lg"
                      alignSelf={{ base: 'stretch', md: 'flex-end' }}
                      px={8}
                      mt={2}
                      mr={4}
                    >
                      AI Magic
                    </Button>
                  </HStack>
                </VStack>
              </Box>
            </Box>
          </Flex>
        </Container>
      </Box>

      <Box position="relative" zIndex={10} mt={-200} px={{ base: 4, md: 0 }}>
        <Box rounded="2xl" p={8} bg="none" shadow="none">
          <VStack spacing={4} align="stretch">
          </VStack>
        </Box>
      </Box>

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} size="5xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader><Icon as={FaMagic} /> AI Search Results</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4} align="stretch">
              {recommendation && (
                <Box>
                  <Text fontSize="md" color="gray.600" mx={10}>
                    <ReactMarkdown>{recommendation}</ReactMarkdown>
                  </Text>
                </Box>
              )}
              {tickets.length > 0 ? (
                <Box>
                  <Text fontSize="lg" fontWeight="bold" color="black" mb={2} p={2}>
                    <Icon as={FaTicketAlt}/> Available Tickets
                  </Text>
                  <VStack spacing={4} align="stretch">
                    {tickets.map((ticket) => (
                      <Box
                        key={ticket.id}
                        border="1px solid"
                        borderColor={borderColor}
                        rounded="lg"
                        p={4}
                      >
                        <Text fontWeight="semibold">
                          {ticket.transport_type} - {ticket.departure_city} to {ticket.arrival_city}
                        </Text>
                        <Text>Price: {(ticket.price / 1000000).toFixed(2)} {ticket.currency}</Text>
                        <Text>Departure: {ticket.departure_time}</Text>
                        <Text>Arrival: {ticket.arrival_time}</Text>
                        <Text>Company: {ticket.company_name || 'N/A'}</Text>
                        <Text>Features: {ticket.features?.join(', ') || 'None'}</Text>
                        {ticket.details && (
                          <Box mt={2}>
                            <Text fontWeight="medium">Details:</Text>
                            {ticket.transport_type === 'plane' && (
                              <>
                                <Text>Airline: {ticket.details.airline_name}</Text>
                                <Text>Flight Number: {ticket.details.flight_number}</Text>
                                <Text>Stops: {ticket.details.stops}</Text>
                              </>
                            )}
                            {ticket.transport_type === 'train' && (
                              <>
                                <Text>Star Rating: {ticket.details.train_star_rating}</Text>
                                <Text>Private Cabin: {ticket.details.private_cabin ? 'Yes' : 'No'}</Text>
                              </>
                            )}
                            {ticket.transport_type === 'bus' && (
                              <>
                                <Text>Bus Company: {ticket.details.bus_company}</Text>
                                <Text>Seats per Row: {ticket.details.seats_per_row}</Text>
                              </>
                            )}
                          </Box>
                        )}
                        <HStack mt={2} spacing={2}>
                          <Button
                            colorScheme={selectedTicket === ticket.id ? 'blue' : 'gray'}
                            size="sm"
                            onClick={() => setSelectedTicket(ticket.id)}
                            isDisabled={loading}
                          >
                            {selectedTicket === ticket.id ? 'Selected' : 'Select'}
                          </Button>
                          <Button
                            leftIcon={<Icon as={FaInfoCircle} />}
                            colorScheme="teal"
                            size="sm"
                            onClick={() => handleViewDetails(ticket.id, ticket.transport_type)}
                            isLoading={loading}
                          >
                            View Details
                          </Button>
                        </HStack>
                      </Box>
                    ))}
                  </VStack>
                  {selectedTicket && (
                    <Box mt={6}>
                      <Text fontSize="lg" fontWeight="bold" color="black" mb={2} p={2}>
                        <Icon as={FaTags}/> Book Ticket
                      </Text>
                      <VStack spacing={4} align="stretch" p={2}>
                        <HStack>
                          <Text fontSize="sm" fontWeight="medium">Passengers</Text>
                          <Select
                            value={passengers}
                            onChange={(e) => setPassengers(e.target.value)}
                            size="sm"
                            width="150px"
                            isDisabled={loading}
                          >
                            {[...Array(10).keys()].map((i) => (
                              <option key={i} value={i + 1}>
                                {i + 1} Passenger{i > 0 ? 's' : ''}
                              </option>
                            ))}
                          </Select>
                        </HStack>
                        <HStack>
                          <Text fontSize="sm" fontWeight="medium">Payment Method</Text>
                          <Select
                            value={paymentMethod}
                            onChange={(e) => setPaymentMethod(e.target.value)}
                            size="sm"
                            width="150px"
                            placeholder="Select Payment Method"
                            isDisabled={loading}
                          >
                            {paymentMethods.map((method) => (
                              <option key={method.id} value={method.id}>
                                {method.name || method.id}
                              </option>
                            ))}
                          </Select>
                        </HStack>
                      </VStack>
                    </Box>
                  )}
                </Box>
              ) : (
                <Text fontSize="md" color="gray.600" textAlign="center">
                  Nothing Found
                </Text>
              )}
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button
              colorScheme="blue"
              onClick={() => handleBookTicket(selectedTicket)}
              rounded="full"
              isLoading={loading}
              mr={3}
              isDisabled={!selectedTicket || !passengers || !paymentMethod || autoReserve}
            >
              Book Now
            </Button>
            <Button variant="ghost" rounded="full" onClick={() => setIsModalOpen(false)} isDisabled={loading}>
              Close
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
}