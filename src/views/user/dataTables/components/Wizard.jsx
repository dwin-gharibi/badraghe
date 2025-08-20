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
  StepTitle,
  Stepper,
  Icon,
  Container,
} from '@chakra-ui/react';
import { FaPlane, FaMapMarkerAlt, FaCreditCard, FaCheckCircle, FaTimes, FaUsers, FaBuilding, FaBus, FaTrain, FaPlaneDeparture } from 'react-icons/fa';
import { useLocation, useNavigate } from 'react-router-dom';
import { createReservation, payForReservation, getPaymentMethods } from 'services/api';
import { useAuth } from '../../../../useAuth';

export default function TicketWizard() {
  const [step, setStep] = useState(1);
  const [ticket, setTicket] = useState({});
  const [passengers, setPassengers] = useState(1);
  const [paymentMethod, setPaymentMethod] = useState('');
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { user } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const toast = useToast();
  const textColor = useColorModeValue('secondaryGray.900', 'white');
  const bgColor = useColorModeValue('secondaryGray.300', 'navy.900');
  const buttonBg = useColorModeValue('brand.600', 'brand.700');
  const buttonColor = useColorModeValue('secondaryGray.100', 'whiteAlpha.900');

  useEffect(() => {
    const ticketData = location.state?.ticket;

    console.log(ticketData);

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

    let price = '';
    let currency = '';

    if (typeof ticketData.price === 'string') {
      const parts = ticketData.price.split(' ');
      price = parts[0] || '';
      currency = parts[1] || '';
    } else if (typeof ticketData.price === 'number') {
      price = ticketData.price;
      currency = ticketData.currency || '';
    }

    setTicket({
      id: ticketData.id || '',
      transport_type: ticketData.type || ticketData.transport_type || '',
      departure_city: ticketData.from || ticketData.departure_city || '',
      arrival_city: ticketData.to || ticketData.arrival_city || '',
      price,
      currency,
      departure_time: ticketData.departureTime || ticketData.departure_time || '',
      arrival_time: ticketData.arrivalTime || ticketData.arrival_time || '',
      company_name: ticketData.company || ticketData.company_name || 'N/A',
      class_type: ticketData.classType || ticketData.class_type || 'Economy',
      features: ticketData.features || [],
    });
  }, [location.state, navigate, toast]);

  useEffect(() => {
    const fetchPaymentMethods = async () => {
      try {
        const response = await getPaymentMethods();
        setPaymentMethods(response.data || response);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to fetch payment methods');
        toast({
          title: 'Error',
          description: err.response?.data?.detail || 'Failed to fetch payment methods',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
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
        amount: ticket.price,
        currency: ticket.currency,
        payment_method_id: paymentMethod,
      };
      console.log("data:", paymentData);
      await payForReservation(reservationId, paymentData);

      toast({
        title: 'Success',
        description: 'Reservation and payment created successfully',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      navigate('/reservations');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create reservation or payment');
      toast({
        title: 'Error',
        description: err.response?.data?.detail || 'Failed to create reservation or payment',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const steps = [
    { title: 'Ticket Details', description: 'Review your selected ticket', icon: FaPlane },
    { title: 'Passengers', description: 'Select number of passengers', icon: FaUsers },
    { title: 'Payment', description: 'Choose payment method', icon: FaCreditCard },
    { title: 'Confirm', description: 'Confirm your booking', icon: FaCheckCircle },
  ];

  if (error) {
    return <Text color="red.500">{error}</Text>;
  }

  return (
    <Box bg={bgColor} minH="100vh" py={{ base: 8, md: 12 }} px={{ base: 4, md: 8 }}>
      <Container maxW="container.md">
        <VStack spacing={6} align="stretch">
          <Heading color={textColor} textAlign="center" fontSize={{ base: '2xl', md: '3xl' }}>
            Reservation Wizard
          </Heading>
          <Stepper
            index={step - 1}
            colorScheme="brand"
            orientation="horizontal"
            gap={{ base: '4', md: '8' }}
            justifyContent="center"
            alignItems="center"
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
                      <Icon as={stepItem.icon} w={6} h={6} color="brand.500" />
                      <Text fontSize={{ base: 'sm', md: 'md' }}>{stepItem.title}</Text>
                    </HStack>
                  </StepTitle>
                  <StepDescription fontSize={{ base: 'xs', md: 'sm' }}>
                    {stepItem.description}
                  </StepDescription>
                </Box>
                <StepSeparator />
              </Step>
            ))}
          </Stepper>

          {step === 1 && (
            <VStack spacing={6} align="stretch" bg="white" p={6} rounded="lg" shadow="md">
              <HStack justify="center">
                <Icon as={FaPlane} w={8} h={8} color="brand.500" />
                <Text fontSize="lg" fontWeight="bold" color={textColor}>
                  Ticket Details
                </Text>
              </HStack>
              <FormControl>
                <FormLabel fontSize="sm" color={textColor}>Transport Type</FormLabel>
                <HStack>
                  <Icon
                    as={ticket.transport_type === 'flight' ? FaPlane : ticket.transport_type === 'train' ? FaTrain : FaBus}
                    color="brand.500"
                    w={5}
                    h={5}
                  />
                  <Input
                    value={ticket.transport_type}
                    isReadOnly
                    borderColor="brand.200"
                    size="md"
                    _focus={{ borderColor: 'brand.400' }}
                  />
                </HStack>
              </FormControl>
              <FormControl>
                <FormLabel fontSize="sm" color={textColor}>From</FormLabel>
                <HStack>
                  <Icon as={FaMapMarkerAlt} color="brand.500" w={5} h={5} />
                  <Input
                    value={ticket.departure_city}
                    isReadOnly
                    borderColor="brand.200"
                    size="md"
                    _focus={{ borderColor: 'brand.400' }}
                  />
                </HStack>
              </FormControl>
              <FormControl>
                <FormLabel fontSize="sm" color={textColor}>To</FormLabel>
                <HStack>
                  <Icon as={FaMapMarkerAlt} color="brand.500" w={5} h={5} />
                  <Input
                    value={ticket.arrival_city}
                    isReadOnly
                    borderColor="brand.200"
                    size="md"
                    _focus={{ borderColor: 'brand.400' }}
                  />
                </HStack>
              </FormControl>
              <FormControl>
                <FormLabel fontSize="sm" color={textColor}>Price</FormLabel>
                <HStack>
                  <Icon as={FaCreditCard} color="brand.500" w={5} h={5} />
                  <Input
                    value={`${ticket.price} ${ticket.currency}`}
                    isReadOnly
                    borderColor="brand.200"
                    size="md"
                    _focus={{ borderColor: 'brand.400' }}
                  />
                </HStack>
              </FormControl>
              <FormControl>
                <FormLabel fontSize="sm" color={textColor}>Departure Time</FormLabel>
                <HStack>
                  <Icon as={FaPlaneDeparture} color="brand.500" w={5} h={5} />
                  <Input
                    value={ticket.departure_time}
                    isReadOnly
                    borderColor="brand.200"
                    size="md"
                    _focus={{ borderColor: 'brand.400' }}
                  />
                </HStack>
              </FormControl>
              <FormControl>
                <FormLabel fontSize="sm" color={textColor}>Arrival Time</FormLabel>
                <HStack>
                  <Icon as={FaPlane} color="brand.500" w={5} h={5} />
                  <Input
                    value={ticket.arrival_time}
                    isReadOnly
                    borderColor="brand.200"
                    size="md"
                    _focus={{ borderColor: 'brand.400' }}
                  />
                </HStack>
              </FormControl>
              <FormControl>
                <FormLabel fontSize="sm" color={textColor}>Company</FormLabel>
                <HStack>
                  <Icon as={FaBuilding} color="brand.500" w={5} h={5} />
                  <Input
                    value={ticket.company_name}
                    isReadOnly
                    borderColor="brand.200"
                    size="md"
                    _focus={{ borderColor: 'brand.400' }}
                  />
                </HStack>
              </FormControl>
              <FormControl>
                <FormLabel fontSize="sm" color={textColor}>Class Type</FormLabel>
                <HStack>
                  <Icon as={FaCheckCircle} color="brand.500" w={5} h={5} />
                  <Input
                    value={ticket.class_type}
                    isReadOnly
                    borderColor="brand.200"
                    size="md"
                    _focus={{ borderColor: 'brand.400' }}
                  />
                </HStack>
              </FormControl>
              <FormControl>
                <FormLabel fontSize="sm" color={textColor}>Features</FormLabel>
                <HStack>
                  <Icon as={FaCheckCircle} color="brand.500" w={5} h={5} />
                  <Input
                    value={Array.isArray(ticket.features) ? ticket.features.join(', ') : ''}
                    isReadOnly
                    borderColor="brand.200"
                    size="md"
                    _focus={{ borderColor: 'brand.400' }}
                  />
                </HStack>
              </FormControl>
              <HStack justify="space-between" pt={4}>
                <Button
                  colorScheme="brand"
                  bg={buttonBg}
                  color={buttonColor}
                  onClick={() => navigate('/')}
                  isDisabled={loading}
                  leftIcon={<FaTimes />}
                  _hover={{ transform: 'scale(1.05)', transition: '0.3s' }}
                  size="md"
                >
                  Cancel
                </Button>
                <Button
                  colorScheme="brand"
                  bg={buttonBg}
                  color={buttonColor}
                  onClick={handleNext}
                  isDisabled={loading}
                  leftIcon={<FaCheckCircle />}
                  _hover={{ transform: 'scale(1.05)', transition: '0.3s' }}
                  size="md"
                >
                  Next
                </Button>
              </HStack>
            </VStack>
          )}

          {step === 2 && (
            <VStack spacing={6} align="stretch" bg="white" p={6} rounded="lg" shadow="md">
              <HStack justify="center">
                <Icon as={FaUsers} w={8} h={8} color="brand.500" />
                <Text fontSize="lg" fontWeight="bold" color={textColor}>
                  Select Passengers
                </Text>
              </HStack>
              <FormControl>
                <FormLabel fontSize="sm" color={textColor}>Number of Passengers</FormLabel>
                <HStack>
                  <Icon as={FaUsers} color="brand.500" w={5} h={5} />
                  <Select
                    value={passengers}
                    onChange={(e) => setPassengers(e.target.value)}
                    placeholder="Select number of passengers"
                    isDisabled={loading}
                    borderColor="brand.200"
                    size="md"
                    _focus={{ borderColor: 'brand.400' }}
                  >
                    {[...Array(10).keys()].map((i) => (
                      <option key={i} value={i + 1}>
                        {i + 1} Passenger{i > 0 ? 's' : ''}
                      </option>
                    ))}
                  </Select>
                </HStack>
              </FormControl>
              <HStack justify="space-between" pt={4}>
                <Button
                  colorScheme="brand"
                  bg={buttonBg}
                  color={buttonColor}
                  onClick={handleBack}
                  isDisabled={loading}
                  leftIcon={<FaTimes />}
                  _hover={{ transform: 'scale(1.05)', transition: '0.3s' }}
                  size="md"
                >
                  Back
                </Button>
                <Button
                  colorScheme="brand"
                  bg={buttonBg}
                  color={buttonColor}
                  onClick={handleNext}
                  isDisabled={loading}
                  leftIcon={<FaCheckCircle />}
                  _hover={{ transform: 'scale(1.05)', transition: '0.3s' }}
                  size="md"
                >
                  Next
                </Button>
              </HStack>
            </VStack>
          )}

          {step === 3 && (
            <VStack spacing={6} align="stretch" bg="white" p={6} rounded="lg" shadow="md">
              <HStack justify="center">
                <Icon as={FaCreditCard} w={8} h={8} color="brand.500" />
                <Text fontSize="lg" fontWeight="bold" color={textColor}>
                  Choose Payment Method
                </Text>
              </HStack>
              <FormControl>
                <FormLabel fontSize="sm" color={textColor}>Payment Method</FormLabel>
                <HStack>
                  <Icon as={FaCreditCard} color="brand.500" w={5} h={5} />
                  <Select
                    value={paymentMethod}
                    onChange={(e) => setPaymentMethod(e.target.value)}
                    placeholder="Select payment method"
                    isDisabled={loading}
                    borderColor="brand.200"
                    size="md"
                    _focus={{ borderColor: 'brand.400' }}
                  >
                    {paymentMethods.map((method) => (
                      <option key={method.id} value={method.id}>
                        {method.name || method.id}
                      </option>
                    ))}
                  </Select>
                </HStack>
              </FormControl>
              <HStack justify="space-between" pt={4}>
                <Button
                  colorScheme="brand"
                  bg={buttonBg}
                  color={buttonColor}
                  onClick={handleBack}
                  isDisabled={loading}
                  leftIcon={<FaTimes />}
                  _hover={{ transform: 'scale(1.05)', transition: '0.3s' }}
                  size="md"
                >
                  Back
                </Button>
                <Button
                  colorScheme="brand"
                  bg={buttonBg}
                  color={buttonColor}
                  onClick={handleNext}
                  isDisabled={loading}
                  leftIcon={<FaCheckCircle />}
                  _hover={{ transform: 'scale(1.05)', transition: '0.3s' }}
                  size="md"
                >
                  Next
                </Button>
              </HStack>
            </VStack>
          )}

          {step === 4 && (
            <VStack spacing={6} align="stretch" bg="white" p={6} rounded="lg" shadow="md">
              <HStack justify="center">
                <Icon as={FaCheckCircle} w={8} h={8} color="brand.500" />
                <Text fontSize="lg" fontWeight="bold" color={textColor}>
                  Confirm Booking
                </Text>
              </HStack>
              <Text color={textColor} fontSize="sm">Review your selections:</Text>
              <Text color={textColor} fontSize="sm">
                <strong>Ticket:</strong> {ticket.transport_type} from {ticket.departure_city} to {ticket.arrival_city}
              </Text>
              <Text color={textColor} fontSize="sm">
                <strong>Price:</strong> {ticket.price} {ticket.currency}
              </Text>
              <Text color={textColor} fontSize="sm">
                <strong>Passengers:</strong> {passengers}
              </Text>
              <Text color={textColor} fontSize="sm">
                <strong>Payment Method:</strong> {paymentMethods.find((m) => m.id === paymentMethod)?.name || 'N/A'}
              </Text>
              <HStack justify="space-between" pt={4}>
                <Button
                  colorScheme="brand"
                  bg={buttonBg}
                  color={buttonColor}
                  onClick={handleBack}
                  isDisabled={loading}
                  leftIcon={<FaTimes />}
                  _hover={{ transform: 'scale(1.05)', transition: '0.3s' }}
                  size="md"
                >
                  Back
                </Button>
                <Button
                  colorScheme="brand"
                  bg={buttonBg}
                  color={buttonColor}
                  onClick={handleBook}
                  isLoading={loading}
                  isDisabled={loading}
                  leftIcon={<FaCheckCircle />}
                  _hover={{ transform: 'scale(1.05)', transition: '0.3s' }}
                  size="md"
                >
                  Confirm Booking
                </Button>
              </HStack>
            </VStack>
          )}
        </VStack>
      </Container>
    </Box>
  );
}