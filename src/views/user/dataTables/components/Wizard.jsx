import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Heading,
  Text,
  Button,
  Select,
  Input,
  useColorModeValue,
  useToast,
  FormControl,
  FormLabel,
  Step,
  StepDescription,
  StepIcon,
  StepIndicator,
  StepNumber,
  StepSeparator,
  StepStatus,
  Skeleton,
  StepTitle,
  Stepper,
  Icon,
  Container,
  keyframes,
  SimpleGrid,
} from '@chakra-ui/react';
import { FaPlane, FaMapMarkerAlt, FaCreditCard, FaCheckCircle, FaTimes, FaUsers, FaBuilding, FaBus, FaTrain, FaPlaneDeparture } from 'react-icons/fa';
import { useLocation, useNavigate } from 'react-router-dom';
import { createReservation, payForReservation, getPaymentMethods } from 'services/api';
import { useAuth } from '../../../../useAuth';

const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
`;
const scaleHover = keyframes`
  from { transform: scale(1); }
  to { transform: scale(1.1); }
`;

export default function TicketWizard() {
  const [step, setStep] = useState(1);
  const [ticket, setTicket] = useState({});
  const [passengers, setPassengers] = useState(1);
  const [paymentMethod, setPaymentMethod] = useState('');
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [paymentMethodsLoading, setPaymentMethodsLoading] = useState(false);
  const [paymentMethodsError, setPaymentMethodsError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { user } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const toast = useToast();
  const textColor = useColorModeValue('black.900', 'white');
  const buttonBgPrimary = useColorModeValue('brand.500', 'brand.500');
  const buttonBgCancel = useColorModeValue('red.500', 'red.600');
  const buttonColor = useColorModeValue('white', 'whiblackpha.900');

  useEffect(() => {
    const ticketData = location.state?.ticket;
    if (!ticketData || !ticketData.id) {
      toast({
        title: 'No Ticket Selected',
        description: 'Please search and select a ticket to proceed with booking.',
        status: 'warning',
        duration: 5000,
        isClosable: true,
      });
      navigate('/');
      return;
    }
    setTicket({
      id: ticketData.id || '',
      transport_type: ticketData.transport_type || ticketData.type || 'unknown',
      departure_city: ticketData.from || ticketData.departure_city || 'N/A',
      arrival_city: ticketData.to || ticketData.arrival_city || 'N/A',
      price: Number(ticketData.price) || 0,
      currency: ticketData.currency || 'IRR',
      departure_time: ticketData.departureTime || ticketData.departure_time || 'N/A',
      arrival_time: ticketData.arrivalTime || ticketData.arrival_time || 'N/A',
      company_name: ticketData.company || ticketData.company_name || 'N/A',
      class_type: ticketData.classType || ticketData.class_type || 'Economy',
      features: ticketData.features || [],
    });
  }, [location.state, navigate, toast]);

  useEffect(() => {
    const fetchPaymentMethods = async () => {
      setPaymentMethodsLoading(true);
      try {
        const response = await getPaymentMethods();
        setPaymentMethods(response.data || response);
      } catch (err) {
        setPaymentMethodsError(err.response?.data?.detail || 'Failed to fetch payment methods');
        toast({
          title: 'Error',
          description: err.response?.data?.detail || 'Failed to fetch payment methods',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setPaymentMethodsLoading(false);
      }
    };
    fetchPaymentMethods();
  }, [toast]);

  const handleNext = () => {
    if (step === 2 && !passengers) {
      toast({
        title: 'Error',
        description: 'Please select the number of passengers',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      return;
    }
    if (step === 3 && !paymentMethod) {
      toast({
        title: 'Error',
        description: 'Please select a payment method',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      return;
    }
    setStep(step + 1);
  };

  const handleBack = () => {
    setStep(step - 1);
  };

  const handleBook = async () => {
    if (!user) {
      toast({
        title: 'Error',
        description: 'User not authenticated. Please log in.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      navigate('/auth/sign-in');
      return;
    }
    setLoading(true);
    try {
      const reservationData = {
        ticket_id: ticket.id,
        user_id: user.id,
        passengers: parseInt(passengers),
      };
      const reservationResponse = await createReservation(reservationData);
      const reservationId = reservationResponse.id;
      const paymentData = {
        payment_method_id: Number(paymentMethod),
        amount: Number(ticket.price),
        currency: ticket.currency,
      };
      const paymentResponse = await payForReservation(reservationId, paymentData);
      toast({
        title: 'Redirecting to Payment',
        description: 'You will be redirected to the payment gateway to complete your transaction.',
        status: 'info',
        duration: 5000,
        isClosable: true,
      });
      window.location.href = paymentResponse.payment_url;
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create reservation or initiate payment');
      toast({
        title: 'Error',
        description: err.response?.data?.detail || 'Failed to create reservation or initiate payment',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const steps = [
    { title: 'Ticket Details', description: 'Review your ticket', icon: FaPlane },
    { title: 'Passengers', description: 'Select passengers', icon: FaUsers },
    { title: 'Payment', description: 'Choose payment method', icon: FaCreditCard },
    { title: 'Confirm', description: 'Confirm booking', icon: FaCheckCircle },
  ];

  if (error) {
    return <Text color="red.500">{error}</Text>;
  }

  const getTransportIcon = () => {
    switch (ticket.transport_type?.toLowerCase()) {
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

  return (
    <Box minH="100vh" py={{ base: 8, md: 12 }} px={{ base: 4, md: 8 }}>
      <Container maxW="container.xl">
        <VStack spacing={8} align="stretch" animation={`${fadeIn} 0.5s ease-out`}>
          <Heading color={textColor} textAlign="center" fontSize={{ base: '2xl', md: '4xl' }} fontWeight="extrabold">
            Reservation Wizard
          </Heading>
          <Stepper
            index={step - 1}
            colorScheme="brand.500"
            orientation="horizontal"
            gap={{ base: '4', md: '8' }}
            justifyContent="center"
            alignItems="center"
            bg="white"
            p={6}
            rounded="2xl"
          >
            {steps.map((stepItem, index) => (
              <Step key={index}>
                <StepIndicator>
                  <StepStatus
                    complete={<StepIcon />}
                    incomplete={<StepNumber />}
                    active={<StepNumber />}
                  />
                </StepIndicator>
                <Box flexShrink="0" textAlign="center">
                  <StepTitle>
                    <HStack justify="center">
                      <Icon as={stepItem.icon} w={10} h={10} color="brand.500" _hover={{ transform: 'scale(1.2)', transition: '0.3s' }} />
                      <Text fontSize={{ base: 'md', md: 'lg' }} fontWeight="extrabold" color={textColor}>{stepItem.title}</Text>
                    </HStack>
                  </StepTitle>
                  <StepDescription fontSize={{ base: 'xs', md: 'sm' }} color="gray.600">
                    {stepItem.description}
                  </StepDescription>
                </Box>
                <StepSeparator />
              </Step>
            ))}
          </Stepper>
          {step === 1 && (
            <Box
              bg="white"
              p={{ base: 4, md: 6 }}
              rounded="2xl"
              animation={`${fadeIn} 0.5s ease-out`}
            >
              <VStack spacing={4} align="stretch">
                <HStack justify="center" mb={4}>
                  <Icon as={getTransportIcon()} w={12} h={12} color="brand.500" _hover={{ transform: 'rotate(5deg)', transition: '0.3s' }} />
                  <Text fontSize={{ base: 'xl', md: '2xl' }} fontWeight="bold" color={textColor}>
                    Ticket Details
                  </Text>
                </HStack>
                <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
                  <FormControl>
                    <FormLabel fontSize="sm" color={textColor}>Transport Type</FormLabel>
                    <HStack>
                      <Icon as={getTransportIcon()} color="brand.500" w={5} h={5} />
                      <Input
                        value={ticket.transport_type ? ticket.transport_type.charAt(0).toUpperCase() + ticket.transport_type.slice(1) : 'N/A'}
                        isReadOnly
                        bg="black.50"
                        size="md"
                        _hover={{ borderColor: 'black.400', bg: 'black.100' }}
                        _focus={{ borderColor: 'black.400' }}
                      />
                    </HStack>
                  </FormControl>
                  <FormControl>
                    <FormLabel fontSize="sm" color={textColor}>From</FormLabel>
                    <HStack>
                      <Icon as={FaMapMarkerAlt} color="green.500" w={5} h={5} />
                      <Input
                        value={ticket.departure_city || 'N/A'}
                        isReadOnly
                        bg="black.50"
                        size="md"
                        _hover={{ borderColor: 'black.400', bg: 'black.100' }}
                        _focus={{ borderColor: 'black.400' }}
                      />
                    </HStack>
                  </FormControl>
                  <FormControl>
                    <FormLabel fontSize="sm" color={textColor}>To</FormLabel>
                    <HStack>
                      <Icon as={FaMapMarkerAlt} color="orange.500" w={5} h={5} />
                      <Input
                        value={ticket.arrival_city || 'N/A'}
                        isReadOnly
                        bg="black.50"
                        size="md"
                        _hover={{ borderColor: 'black.400', bg: 'black.100' }}
                        _focus={{ borderColor: 'black.400' }}
                      />
                    </HStack>
                  </FormControl>
                  <FormControl>
                    <FormLabel fontSize="sm" color={textColor}>Price</FormLabel>
                    <HStack>
                      <Icon as={FaCreditCard} color="cyan.500" w={5} h={5} />
                      <Input
                        value={`${ticket.price || 0} ${ticket.currency || 'N/A'}`}
                        isReadOnly
                        bg="black.50"
                        size="md"
                        _hover={{ borderColor: 'black.400', bg: 'black.100' }}
                        _focus={{ borderColor: 'black.400' }}
                      />
                    </HStack>
                  </FormControl>
                  <FormControl>
                    <FormLabel fontSize="sm" color={textColor}>Departure Time</FormLabel>
                    <HStack>
                      <Icon as={FaPlaneDeparture} color="purple.500" w={5} h={5} />
                      <Input
                        value={ticket.departure_time || 'N/A'}
                        isReadOnly
                        bg="black.50"
                        size="md"
                        _hover={{ borderColor: 'black.400', bg: 'black.100' }}
                        _focus={{ borderColor: 'black.400' }}
                      />
                    </HStack>
                  </FormControl>
                  <FormControl>
                    <FormLabel fontSize="sm" color={textColor}>Arrival Time</FormLabel>
                    <HStack>
                      <Icon as={getTransportIcon()} color="pink.500" w={5} h={5} />
                      <Input
                        value={ticket.arrival_time || 'N/A'}
                        isReadOnly
                        bg="black.50"
                        size="md"
                        _hover={{ borderColor: 'black.400', bg: 'black.100' }}
                        _focus={{ borderColor: 'black.400' }}
                      />
                    </HStack>
                  </FormControl>
                  <FormControl>
                    <FormLabel fontSize="sm" color={textColor}>Company</FormLabel>
                    <HStack>
                      <Icon as={FaBuilding} color="yellow.500" w={5} h={5} />
                      <Input
                        value={ticket.company_name || 'N/A'}
                        isReadOnly
                        bg="black.50"
                        size="md"
                        _hover={{ borderColor: 'black.400', bg: 'black.100' }}
                        _focus={{ borderColor: 'black.400' }}
                      />
                    </HStack>
                  </FormControl>
                  <FormControl>
                    <FormLabel fontSize="sm" color={textColor}>Class Type</FormLabel>
                    <HStack>
                      <Icon as={FaCheckCircle} color="navy.500" w={5} h={5} />
                      <Input
                        value={ticket.class_type || 'N/A'}
                        isReadOnly
                        bg="black.50"
                        size="md"
                        _hover={{ borderColor: 'black.400', bg: 'black.100' }}
                        _focus={{ borderColor: 'black.400' }}
                      />
                    </HStack>
                  </FormControl>
                  <FormControl>
                    <FormLabel fontSize="sm" color={textColor}>Features</FormLabel>
                    <HStack>
                      <Icon as={FaCheckCircle} color="green.400" w={5} h={5} />
                      <Input
                        value={Array.isArray(ticket.features) ? ticket.features.join(', ') : 'N/A'}
                        isReadOnly
                        bg="black.50"
                        size="md"
                        _hover={{ borderColor: 'black.400', bg: 'black.100' }}
                        _focus={{ borderColor: 'black.400' }}
                      />
                    </HStack>
                  </FormControl>
                </SimpleGrid>
                <HStack justify="space-between" pt={4}>
                  <Button
                    colorScheme="red"
                    bg={buttonBgCancel}
                    color={buttonColor}
                    onClick={() => navigate('/')}
                    rounded="full"
                    isDisabled={loading}
                    leftIcon={<FaTimes />}
                    _hover={{ animation: `${scaleHover} 0.3s`, bg: 'red.600' }}
                    size="md"
                  >
                    Cancel
                  </Button>
                  <Button
                    colorScheme="black"
                    bg={buttonBgPrimary}
                    color={buttonColor}
                    onClick={handleNext}
                    rounded="full"
                    isDisabled={loading}
                    leftIcon={<FaCheckCircle />}
                    _hover={{ animation: `${scaleHover} 0.3s`, bg: 'black.600' }}
                    size="md"
                  >
                    Next
                  </Button>
                </HStack>
              </VStack>
            </Box>
          )}
          {step === 2 && (
            <Box
              bg="white"
              p={{ base: 4, md: 6 }}
              rounded="2xl"
              animation={`${fadeIn} 0.5s ease-out`}
            >
              <VStack spacing={4} align="stretch">
                <HStack justify="center" mb={4}>
                  <Icon as={FaUsers} w={12} h={12} color="brand.500" _hover={{ transform: 'rotate(5deg)', transition: '0.3s' }} />
                  <Text fontSize={{ base: 'xl', md: '2xl' }} fontWeight="bold" color={textColor}>
                    Select Passengers
                  </Text>
                </HStack>
                <HStack justify="center">
                  <FormControl maxW={{ base: '100%', md: '400px' }}>
                    <FormLabel fontSize="sm" color={textColor}>Number of Passengers</FormLabel>
                    <HStack>
                      <Icon as={FaUsers} color="black.500" w={5} h={5} />
                      <Select
                        value={passengers}
                        onChange={(e) => setPassengers(e.target.value)}
                        placeholder="Select number of passengers"
                        isDisabled={loading}
                        bg="black.50"
                        size="md"
                        _hover={{ borderColor: 'black.400', bg: 'black.100' }}
                        _focus={{ borderColor: 'black.400' }}
                      >
                        {[...Array(10).keys()].map((i) => (
                          <option key={i} value={i + 1}>
                            {i + 1} Passenger{i > 0 ? 's' : ''}
                          </option>
                        ))}
                      </Select>
                    </HStack>
                  </FormControl>
                </HStack>
                <HStack justify="space-between" pt={4}>
                  <Button
                    colorScheme="red"
                    bg={buttonBgCancel}
                    color={buttonColor}
                    onClick={handleBack}
                    rounded="full"
                    isDisabled={loading}
                    leftIcon={<FaTimes />}
                    _hover={{ animation: `${scaleHover} 0.3s`, bg: 'red.600' }}
                    size="md"
                  >
                    Back
                  </Button>
                  <Button
                    colorScheme="black"
                    bg={buttonBgPrimary}
                    color={buttonColor}
                    onClick={handleNext}
                    rounded="full"
                    isDisabled={loading}
                    leftIcon={<FaCheckCircle />}
                    _hover={{ animation: `${scaleHover} 0.3s`, bg: 'black.600' }}
                    size="md"
                  >
                    Next
                  </Button>
                </HStack>
              </VStack>
            </Box>
          )}
          {step === 3 && (
            <Box
              bg="white"
              p={{ base: 4, md: 6 }}
              rounded="2xl"
              animation={`${fadeIn} 0.5s ease-out`}
            >
              <VStack spacing={4} align="stretch">
                <HStack justify="center" mb={4}>
                  <Icon as={FaCreditCard} w={12} h={12} color="brand.500" _hover={{ transform: 'rotate(5deg)', transition: '0.3s' }} />
                  <Text fontSize={{ base: 'xl', md: '2xl' }} fontWeight="bold" color={textColor}>
                    Choose Payment Method
                  </Text>
                </HStack>
                {paymentMethodsError ? (
                  <Text color="red.500" textAlign="center">{paymentMethodsError}</Text>
                ) : (
                  <HStack justify="center">
                    <FormControl maxW={{ base: '100%', md: '400px' }}>
                      <FormLabel fontSize="sm" color={textColor}>Payment Method</FormLabel>
                      <HStack>
                        <Icon as={FaCreditCard} color="black.500" w={5} h={5} />
                        {paymentMethodsLoading ? (
                          <Skeleton height="40px" width="100%" />
                        ) : (
                          <Select
                            value={paymentMethod}
                            onChange={(e) => setPaymentMethod(e.target.value)}
                            placeholder="Select payment method"
                            isDisabled={loading || paymentMethods.length === 0}
                            bg="black.50"
                            size="md"
                            _hover={{ borderColor: 'black.400', bg: 'black.100' }}
                            _focus={{ borderColor: 'black.400' }}
                          >
                            {paymentMethods.map((method) => (
                              <option key={method.id} value={method.id}>
                                {method.name || method.id}
                              </option>
                            ))}
                          </Select>
                        )}
                      </HStack>
                    </FormControl>
                  </HStack>
                )}
                <HStack justify="space-between" pt={4}>
                  <Button
                    colorScheme="red"
                    bg={buttonBgCancel}
                    color={buttonColor}
                    onClick={handleBack}
                    rounded="full"
                    isDisabled={loading}
                    leftIcon={<FaTimes />}
                    _hover={{ animation: `${scaleHover} 0.3s`, bg: 'red.600' }}
                    size="md"
                  >
                    Back
                  </Button>
                  <Button
                    colorScheme="black"
                    bg={buttonBgPrimary}
                    color={buttonColor}
                    onClick={handleNext}
                    rounded="full"
                    isDisabled={loading || paymentMethodsLoading || paymentMethodsError}
                    leftIcon={<FaCheckCircle />}
                    _hover={{ animation: `${scaleHover} 0.3s`, bg: 'black.600' }}
                    size="md"
                  >
                    Next
                  </Button>
                </HStack>
              </VStack>
            </Box>
          )}
          {step === 4 && (
            <Box
              bg="white"
              p={{ base: 4, md: 6 }}
              rounded="2xl"
              animation={`${fadeIn} 0.5s ease-out`}
            >
              <VStack spacing={4} align="stretch">
                <HStack justify="center" mb={4}>
                  <Icon as={FaCheckCircle} w={12} h={12} color="brand.500" _hover={{ transform: 'rotate(5deg)', transition: '0.3s' }} />
                  <Text fontSize={{ base: 'xl', md: '2xl' }} fontWeight="bold" color={textColor}>
                    Confirm Booking
                  </Text>
                </HStack>
                <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={4}>
                  <HStack>
                    <Icon as={getTransportIcon()} color="black.500" w={5} h={5} />
                    <Text color={textColor} fontSize="sm">
                      <strong>Ticket:</strong> {ticket.transport_type ? ticket.transport_type.charAt(0).toUpperCase() + ticket.transport_type.slice(1) : 'N/A'} from {ticket.departure_city || 'N/A'} to {ticket.arrival_city || 'N/A'}
                    </Text>
                  </HStack>
                  <HStack>
                    <Icon as={FaCreditCard} color="black.500" w={5} h={5} />
                    <Text color={textColor} fontSize="sm">
                      <strong>Price:</strong> {ticket.price || 0} {ticket.currency || 'N/A'}
                    </Text>
                  </HStack>
                  <HStack>
                    <Icon as={FaUsers} color="black.500" w={5} h={5} />
                    <Text color={textColor} fontSize="sm">
                      <strong>Passengers:</strong> {passengers}
                    </Text>
                  </HStack>
                  <HStack>
                    <Icon as={FaCreditCard} color="black.500" w={5} h={5} />
                    <Text color={textColor} fontSize="sm">
                      <strong>Payment Method:</strong> {paymentMethods.find((m) => m.id === Number(paymentMethod))?.name || 'N/A'}
                    </Text>
                  </HStack>
                </SimpleGrid>
                <HStack justify="space-between" pt={4}>
                  <Button
                    colorScheme="red"
                    bg={buttonBgCancel}
                    color={buttonColor}
                    onClick={handleBack}
                    rounded="full"
                    isDisabled={loading}
                    leftIcon={<FaTimes />}
                    _hover={{ animation: `${scaleHover} 0.3s`, bg: 'red.600' }}
                    size="md"
                  >
                    Back
                  </Button>
                  <Button
                    colorScheme="black"
                    bg={buttonBgPrimary}
                    color={buttonColor}
                    onClick={handleBook}
                    rounded="full"
                    isLoading={loading}
                    isDisabled={loading}
                    leftIcon={<FaCheckCircle />}
                    _hover={{ animation: `${scaleHover} 0.3s`, bg: 'black.600' }}
                    size="md"
                  >
                    Confirm Booking
                  </Button>
                </HStack>
              </VStack>
            </Box>
          )}
        </VStack>
      </Container>
    </Box>
  );
}