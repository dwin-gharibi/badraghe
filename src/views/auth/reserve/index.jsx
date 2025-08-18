import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Flex,
  Heading,
  Text,
  Input,
  Select,
  VStack,
  HStack,
  Divider,
  Icon,
  useColorModeValue,
  Spinner,
  FormControl,
  FormLabel,
  FormErrorMessage,
} from '@chakra-ui/react';
import { AsyncSelect } from 'chakra-react-select';
import DefaultAuth from 'layouts/auth/Default';
import illustration from "assets/img/layout/banner.png";
import { FcGoogle } from 'react-icons/fc';
import { searchTickets, getCities, getPaymentMethods, createReservation, createPayment } from 'services/api';
import { useToast } from '@chakra-ui/react';

export default function TicketWizard() {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    from: null,
    to: null,
    departureDate: '',
    returnDate: '',
    passengers: 1,
    classType: 'Economy',
    name: '',
    email: '',
    paymentMethod: '',
    ticket_id: null,
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [availableTickets, setAvailableTickets] = useState([]);
  const textColor = useColorModeValue('navy.700', 'white');
  const textColorSecondary = 'gray.400';
  const textColorBrand = useColorModeValue('brand.500', 'white');
  const cardBg = useColorModeValue('white', 'gray.700');
  const googleBg = useColorModeValue('secondaryGray.300', 'whiteAlpha.200');
  const googleText = useColorModeValue('navy.700', 'white');
  const googleHover = useColorModeValue({ bg: 'gray.200' }, { bg: 'whiteAlpha.300' });
  const googleActive = useColorModeValue({ bg: 'secondaryGray.300' }, { bg: 'whiteAlpha.200' });
  const toast = useToast();

  useEffect(() => {
    const fetchPaymentMethods = async () => {
      try {
        const response = await getPaymentMethods();
        setPaymentMethods(response.data || response);
      } catch (err) {
        console.error('Fetch Payment Methods Error:', err);
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

  const validateStep = () => {
    const newErrors = {};
    if (step === 1) {
      if (!formData.from?.value) newErrors.from = 'Departure city is required';
      if (!formData.to?.value) newErrors.to = 'Arrival city is required';
      if (!formData.departureDate) newErrors.departureDate = 'Departure date is required';
      if (!formData.ticket_id) newErrors.ticket_id = 'Please select a ticket';
    } else if (step === 2) {
      if (!formData.name) newErrors.name = 'Full name is required';
      if (!formData.email || !/\S+@\S+\.\S+/.test(formData.email)) newErrors.email = 'Valid email is required';
    } else if (step === 3) {
      if (!formData.paymentMethod) newErrors.paymentMethod = 'Payment method is required';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const loadCityOptions = async (inputValue) => {
    try {
      const response = await getCities({ search: inputValue });
      const cities = response.data || response;
      return cities.map((city) => ({
        value: city.name,
        label: city.name,
      }));
    } catch (err) {
      console.error('Load Cities Error:', err);
      toast({
        title: 'Error',
        description: err.response?.data?.detail || err.message || 'Failed to load cities',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      return [];
    }
  };

  const fetchTickets = async () => {
    if (!formData.from?.value || !formData.to?.value || !formData.departureDate) return;
    setIsLoading(true);
    try {
      const response = await searchTickets({
        departure_city: formData.from.value,
        arrival_city: formData.to.value,
        travel_date: formData.departureDate,
        class_type: formData.classType,
      });
      setAvailableTickets(response.data || response);
      if (response.data?.length > 0) {
        setFormData((prev) => ({ ...prev, ticket_id: response.data[0].id }));
      } else {
        setErrors((prev) => ({ ...prev, ticket_id: 'No tickets available for this route' }));
      }
    } catch (err) {
      console.error('Search Tickets Error:', err);
      setErrors((prev) => ({
        ...prev,
        ticket_id: err.response?.data?.detail || err.message || 'Failed to fetch tickets',
      }));
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (name, value) => {
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (name === 'from' || name === 'to' || name === 'departureDate' || name === 'classType') {
      setFormData((prev) => ({ ...prev, ticket_id: null }));
      fetchTickets();
    }
  };

  const handleNext = () => {
    if (validateStep()) {
      setStep((prev) => prev + 1);
    } else {
      toast({
        title: 'Validation Error',
        description: 'Please fill in all required fields correctly',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const handleBack = () => setStep((prev) => prev - 1);

  const handleSubmit = async () => {
    if (!validateStep()) {
      toast({
        title: 'Validation Error',
        description: 'Please complete all steps correctly',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      return;
    }
    setIsLoading(true);
    try {
      const reservationData = {
        ticket_id: formData.ticket_id,
        user_id: 1,
        passengers: parseInt(formData.passengers),
      };
      const reservationResponse = await createReservation(reservationData);
      const reservationId = reservationResponse.id;

      const paymentData = {
        reservation_id: reservationId,
        user_id: 1,
        amount: availableTickets.find((ticket) => ticket.id === formData.ticket_id)?.price,
        currency: availableTickets.find((ticket) => ticket.id === formData.ticket_id)?.currency,
        payment_method_id: formData.paymentMethod,
      };
      await createPayment(paymentData);

      toast({
        title: 'Success',
        description: 'Reservation created successfully',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      setFormData({
        from: null,
        to: null,
        departureDate: '',
        returnDate: '',
        passengers: 1,
        classType: 'Economy',
        name: '',
        email: '',
        paymentMethod: '',
        ticket_id: null,
      });
      setStep(1);
    } catch (err) {
      console.error('Submit Error:', err);
      toast({
        title: 'Error',
        description: err.response?.data?.detail || err.message || 'Failed to create reservation',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <DefaultAuth illustrationBackground={illustration} image={illustration}>
      <Flex
        maxW={{ base: '100%', md: 'max-content' }}
        w="100%"
        mx={{ base: 'auto', lg: '0px' }}
        me="auto"
        h="100%"
        alignItems="start"
        justifyContent="center"
        mb={{ base: '30px', md: '60px' }}
        px={{ base: '25px', md: '0px' }}
        mt={{ base: '40px', md: '14vh' }}
        flexDirection="column"
      >
        <Box me="auto" mb="30px">
          <Heading color={textColor} fontSize="36px" mb="10px">
            Ticket Reservation
          </Heading>
          <Text mb="36px" ms="4px" color={textColorSecondary} fontWeight="400" fontSize="md">
            Fill in your flight and passenger details
          </Text>
        </Box>
        <Flex
          zIndex="2"
          direction="column"
          w={{ base: '100%', md: '420px' }}
          maxW="100%"
          background={cardBg}
          borderRadius="15px"
          p="30px"
          shadow="lg"
          mx={{ base: 'auto', lg: 'unset' }}
          me="auto"
          mb={{ base: '20px', md: 'auto' }}
        >
          <Button
            fontSize="sm"
            me="0px"
            mb="26px"
            py="15px"
            h="50px"
            borderRadius="16px"
            bg={googleBg}
            color={googleText}
            fontWeight="500"
            _hover={googleHover}
            _active={googleActive}
            _focus={googleActive}
          >
            <Icon as={FcGoogle} w="20px" h="20px" me="10px" />
            Book with Google
          </Button>

          {step === 1 && (
            <VStack spacing={4} align="stretch">
              <Text fontWeight="500" color={textColor}>
                Step 1: Flight Details
              </Text>
              <FormControl isInvalid={!!errors.from}>
                <FormLabel>From</FormLabel>
                <AsyncSelect
                  name="from"
                  value={formData.from}
                  onChange={(option) => handleChange('from', option)}
                  loadOptions={loadCityOptions}
                  placeholder="Select departure city"
                />
                <FormErrorMessage>{errors.from}</FormErrorMessage>
              </FormControl>
              <FormControl isInvalid={!!errors.to}>
                <FormLabel>To</FormLabel>
                <AsyncSelect
                  name="to"
                  value={formData.to}
                  onChange={(option) => handleChange('to', option)}
                  loadOptions={loadCityOptions}
                  placeholder="Select arrival city"
                />
                <FormErrorMessage>{errors.to}</FormErrorMessage>
              </FormControl>
              <FormControl isInvalid={!!errors.departureDate}>
                <FormLabel>Departure Date</FormLabel>
                <Input
                  type="date"
                  name="departureDate"
                  value={formData.departureDate}
                  onChange={(e) => handleChange('departureDate', e.target.value)}
                  variant="auth"
                />
                <FormErrorMessage>{errors.departureDate}</FormErrorMessage>
              </FormControl>
              <Input
                type="date"
                placeholder="Return Date"
                name="returnDate"
                value={formData.returnDate}
                onChange={(e) => handleChange('returnDate', e.target.value)}
                variant="auth"
              />
              <FormControl>
                <FormLabel>Passengers</FormLabel>
                <Select
                  name="passengers"
                  value={formData.passengers}
                  onChange={(e) => handleChange('passengers', e.target.value)}
                >
                  {[...Array(10).keys()].map((i) => (
                    <option key={i} value={i + 1}>
                      {i + 1} Passenger{i > 0 ? 's' : ''}
                    </option>
                  ))}
                </Select>
              </FormControl>
              <FormControl>
                <FormLabel>Class Type</FormLabel>
                <Select
                  name="classType"
                  value={formData.classType}
                  onChange={(e) => handleChange('classType', e.target.value)}
                >
                  <option>Economy</option>
                  <option>Business</option>
                  <option>First Class</option>
                </Select>
              </FormControl>
              {isLoading && <Spinner />}
              {availableTickets.length > 0 && (
                <FormControl isInvalid={!!errors.ticket_id}>
                  <FormLabel>Available Tickets</FormLabel>
                  <Select
                    name="ticket_id"
                    value={formData.ticket_id}
                    onChange={(e) => handleChange('ticket_id', e.target.value)}
                  >
                    {availableTickets.map((ticket) => (
                      <option key={ticket.id} value={ticket.id}>
                        {ticket.transport_type} - {ticket.price} {ticket.currency}
                      </option>
                    ))}
                  </Select>
                  <FormErrorMessage>{errors.ticket_id}</FormErrorMessage>
                </FormControl>
              )}
            </VStack>
          )}

          {step === 2 && (
            <VStack spacing={4} align="stretch">
              <Text fontWeight="500" color={textColor}>
                Step 2: Passenger Info
              </Text>
              <FormControl isInvalid={!!errors.name}>
                <FormLabel>Full Name</FormLabel>
                <Input
                  placeholder="Full Name"
                  name="name"
                  value={formData.name}
                  onChange={(e) => handleChange('name', e.target.value)}
                  variant="auth"
                />
                <FormErrorMessage>{errors.name}</FormErrorMessage>
              </FormControl>
              <FormControl isInvalid={!!errors.email}>
                <FormLabel>Email Address</FormLabel>
                <Input
                  type="email"
                  placeholder="Email Address"
                  name="email"
                  value={formData.email}
                  onChange={(e) => handleChange('email', e.target.value)}
                  variant="auth"
                />
                <FormErrorMessage>{errors.email}</FormErrorMessage>
              </FormControl>
            </VStack>
          )}

          {step === 3 && (
            <VStack spacing={4} align="stretch">
              <Text fontWeight="500" color={textColor}>
                Step 3: Payment
              </Text>
              <FormControl isInvalid={!!errors.paymentMethod}>
                <FormLabel>Payment Method</FormLabel>
                <Select
                  name="paymentMethod"
                  value={formData.paymentMethod}
                  onChange={(e) => handleChange('paymentMethod', e.target.value)}
                >
                  <option value="">Select Payment Method</option>
                  {paymentMethods.map((method) => (
                    <option key={method.id} value={method.id}>
                      {method.name || method.id}
                    </option>
                  ))}
                </Select>
                <FormErrorMessage>{errors.paymentMethod}</FormErrorMessage>
              </FormControl>
            </VStack>
          )}

          {step === 4 && (
            <VStack spacing={4} align="stretch">
              <Text fontWeight="500" color={textColor}>
                Step 4: Review & Confirm
              </Text>
              <Divider />
              <Text color={textColor}>From: {formData.from?.label}</Text>
              <Text color={textColor}>To: {formData.to?.label}</Text>
              <Text color={textColor}>Departure: {formData.departureDate}</Text>
              <Text color={textColor}>Return: {formData.returnDate || 'N/A'}</Text>
              <Text color={textColor}>Passengers: {formData.passengers}</Text>
              <Text color={textColor}>Class: {formData.classType}</Text>
              <Text color={textColor}>Ticket ID: {formData.ticket_id}</Text>
              <Text color={textColor}>Name: {formData.name}</Text>
              <Text color={textColor}>Email: {formData.email}</Text>
              <Text color={textColor}>
                Payment Method:{' '}
                {paymentMethods.find((m) => m.id === formData.paymentMethod)?.name || formData.paymentMethod}
              </Text>
            </VStack>
          )}

          <HStack mt={6} justify="space-between">
            {step > 1 && (
              <Button
                onClick={handleBack}
                fontSize="sm"
                variant="outline"
                w="48%"
                h="50px"
                borderRadius="16px"
                isDisabled={isLoading}
              >
                Back
              </Button>
            )}
            {step < 4 && (
              <Button
                onClick={handleNext}
                fontSize="sm"
                variant="brand"
                w="48%"
                h="50px"
                borderRadius="16px"
                isDisabled={isLoading}
              >
                Next
              </Button>
            )}
            {step === 4 && (
              <Button
                onClick={handleSubmit}
                fontSize="sm"
                variant="brand"
                w="100%"
                h="50px"
                borderRadius="16px"
                isLoading={isLoading}
              >
                Confirm Reservation
              </Button>
            )}
          </HStack>
        </Flex>
      </Flex>
    </DefaultAuth>
  );
}