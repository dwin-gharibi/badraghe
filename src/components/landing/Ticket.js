import React, { useState } from 'react';
import {
  Box,
  Flex,
  VStack,
  HStack,
  Text,
  Badge,
  Icon,
  Divider,
  SimpleGrid,
  Button,
  useColorModeValue,
} from '@chakra-ui/react';
import { FaPlane, FaTimes, FaTicketAlt, FaInfoCircle, FaTrain, FaBus, FaPlaneDeparture, FaPlaneArrival, FaClock, FaRoute, FaHashtag } from 'react-icons/fa';
import { motion, AnimatePresence } from 'framer-motion';
import { useInView } from 'react-intersection-observer';

const MotionBox = motion(Box);

const typeColors = {
  plane: 'blue.400',
  bus: 'orange.400',
  train: 'teal.400',
};

const typeIcons = {
  plane: FaPlane,
  bus: FaBus,
  train: FaTrain,
};

const sanitizeTicket = (ticket) => ({
  id: ticket.id || `ticket-${Date.now()}-${Math.random()}`,
  type: typeof ticket.transport_type === 'string' ? ticket.transport_type : 'unknown',
  company: typeof ticket.company_name === 'string' ? ticket.company_name : 'N/A',
  price: typeof ticket.price === 'string' || typeof ticket.price === 'number' ? `${ticket.price} ${ticket.currency || ''}` : 'N/A',
  classType: typeof ticket.class_type === 'string' ? ticket.class_type : 'Economy',
  from: typeof ticket.departure_city === 'string' ? ticket.departure_city : 'Unknown',
  to: typeof ticket.arrival_city === 'string' ? ticket.arrival_city : 'Unknown',
  departureTime: typeof ticket.departure_time === 'string' ? ticket.departure_time : 'N/A',
  arrivalTime: typeof ticket.arrival_time === 'string' ? ticket.arrival_time : 'N/A',
  features: Array.isArray(ticket.features) 
    ? ticket.features.map(feat => typeof feat === 'object' && feat.name ? feat.name : typeof feat === 'string' ? feat : 'Unknown Feature')
    : [],
  airline_name: typeof ticket.airline_name === 'string' ? ticket.airline_name : undefined,
  bus_company: typeof ticket.bus_company === 'string' ? ticket.bus_company : undefined,
  flight_class: typeof ticket.flight_class === 'string' ? ticket.flight_class : undefined,
  train_star_rating: typeof ticket.train_star_rating === 'string' || typeof ticket.train_star_rating === 'number' ? ticket.train_star_rating : undefined,
  seats_per_row: typeof ticket.seats_per_row === 'string' || typeof ticket.seats_per_row === 'number' ? ticket.seats_per_row : undefined,
  departure_airport: typeof ticket.departure_airport === 'string' ? ticket.departure_airport : undefined,
  arrival_airport: typeof ticket.arrival_airport === 'string' ? ticket.arrival_airport : undefined,
  flight_number: typeof ticket.flight_number === 'string' ? ticket.flight_number : undefined,
  private_cabin: typeof ticket.private_cabin === 'string' || typeof ticket.private_cabin === 'boolean' ? ticket.private_cabin : undefined,
  bus_type: typeof ticket.bus_type === 'string' ? ticket.bus_type : undefined,
  stops: typeof ticket.stops === 'string' || typeof ticket.stops === 'number' ? ticket.stops : 'N/A',
  created_at: typeof ticket.created_at === 'string' ? ticket.created_at : undefined,
  updated_at: typeof ticket.updated_at === 'string' ? ticket.updated_at : undefined,
});

function TicketCard({ type, company, price, classType, from, to, departureTime, arrivalTime, features, onExpand, onReserve }) {
  const cardBg = useColorModeValue('white', 'gray.700');
  const textColor = useColorModeValue('secondaryGray.900', 'white');
  const { ref, inView } = useInView({
    triggerOnce: true,
    threshold: 0.1,
  });

  return (
    <MotionBox
      ref={ref}
      bg={cardBg}
      borderRadius="2xl"
      shadow="lg"
      overflow="hidden"
      p={6}
      initial={{ opacity: 0, y: 50 }}
      animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 50 }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
    >
      <Flex justify="space-between" align="center" mb={4}>
        <Text fontWeight="bold" fontSize="xl" color="teal.600">
          {company}
        </Text>
        <Badge colorScheme="pink" fontSize="lg" px={3} py={1}>
          {price}
        </Badge>
      </Flex>
      <Flex align="center" justify="space-between" mb={4}>
        <VStack spacing={1} align="flex-start">
          <Text fontWeight="bold" fontSize="2xl" color={textColor}>{from}</Text>
          <Text fontSize="sm" color="gray.500">{departureTime}</Text>
        </VStack>
        <Icon as={typeIcons[type] || FaRoute} w={12} h={12} color={typeColors[type] || 'gray.400'} />
        <VStack spacing={1} align="flex-end">
          <Text fontWeight="bold" fontSize="2xl" color={textColor}>{to}</Text>
          <Text fontSize="sm" color="gray.500">{arrivalTime}</Text>
        </VStack>
      </Flex>
      <Divider mb={4} />
      <Flex justify="space-between" align="center" wrap="wrap" gap={2}>
        <Badge colorScheme="green" fontSize="sm" px={3} py={1}>
          {classType}
        </Badge>
        <HStack spacing={2} wrap="wrap">
          {features.slice(0, 3).map((feat, idx) => (
            <Badge key={idx} colorScheme="blue" fontSize="sm" px={2} py={1}>
              {feat}
            </Badge>
          ))}
        </HStack>
      </Flex>
      <Divider my={4} />
      <Button
        mt="3"
        colorScheme="teal"
        leftIcon={<FaInfoCircle />}
        size="sm"
        width="full"
        onClick={onExpand}
      >
        Show More
      </Button>
      <Button
        mt="3"
        colorScheme="brand"
        leftIcon={<FaTicketAlt />}
        size="sm"
        width="full"
        onClick={onReserve}
      >
        Reserve Ticket
      </Button>
    </MotionBox>
  );
}

function ExpandedTicket({ ticket, onClose, onReserve }) {
  const cardBg = useColorModeValue('white', 'gray.700');
  const textColor = useColorModeValue('secondaryGray.900', 'white');
  const labelColor = useColorModeValue("gray.600", "gray.400");

  let companyField, classField, depField, arrField, numberField, stopsField, DepIcon, ArrIcon;
  switch (ticket.type) {
    case 'plane':
      companyField = ticket.airline_name || ticket.company || 'N/A';
      classField = ticket.flight_class?.replace("_", " ") || ticket.classType || 'Economy';
      depField = ticket.departure_airport || ticket.from || 'Unknown';
      arrField = ticket.arrival_airport || ticket.to || 'Unknown';
      numberField = ticket.flight_number || '';
      stopsField = typeof ticket.stops === 'string' || typeof ticket.stops === 'number' ? ticket.stops : 'N/A';
      DepIcon = FaPlaneDeparture;
      ArrIcon = FaPlaneArrival;
      break;
    case 'train':
      companyField = ticket.railway_company || ticket.company || 'N/A';
      classField = ticket.train_class?.replace("_", " ") || ticket.classType || 'Standard';
      depField = ticket.departure_station || ticket.from || 'Unknown';
      arrField = ticket.arrival_station || ticket.to || 'Unknown';
      numberField = ticket.train_number || '';
      stopsField = typeof ticket.stops === 'string' || typeof ticket.stops === 'number' ? ticket.stops : 'N/A';
      DepIcon = FaTrain;
      ArrIcon = FaTrain;
      break;
    case 'bus':
      companyField = ticket.bus_company || ticket.company || 'N/A';
      classField = ticket.bus_class?.replace("_", " ") || ticket.classType || 'Standard';
      depField = ticket.departure_terminal || ticket.from || 'Unknown';
      arrField = ticket.arrival_terminal || ticket.to || 'Unknown';
      numberField = ticket.bus_number || '';
      stopsField = typeof ticket.stops === 'string' || typeof ticket.stops === 'number' ? ticket.stops : 'N/A';
      DepIcon = FaBus;
      ArrIcon = FaBus;
      break;
    default:
      companyField = ticket.company || 'N/A';
      classField = ticket.classType || 'N/A';
      depField = ticket.from || 'Unknown';
      arrField = ticket.to || 'Unknown';
      numberField = '';
      stopsField = 'N/A';
      DepIcon = FaRoute;
      ArrIcon = FaRoute;
  }

  return (
    <MotionBox
      bg={cardBg}
      borderRadius="2xl"
      shadow="2xl"
      p={10}
      maxW="4xl"
      mx="auto"
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.8 }}
      transition={{ duration: 0.3 }}
      position="relative"
    >
      <Flex justify="space-between" align="center" mb={8}>
        <Text fontWeight="bold" fontSize="2xl" color="teal.600">{companyField}</Text>
        <Badge colorScheme="pink" fontSize="2xl" px={5} py={2}>
          {ticket.price}
        </Badge>
      </Flex>
      <Flex align="center" justify="space-between" mb={6}>
        <VStack spacing={1} align="flex-start">
          <Text fontWeight="bold" fontSize="4xl" color={textColor}>{ticket.from}</Text>
          <Text fontSize="lg" color="gray.500">{ticket.departureTime}</Text>
        </VStack>
        <Icon as={typeIcons[ticket.type] || FaRoute} w={12} h={12} color={typeColors[ticket.type] || 'gray.400'} />
        <VStack spacing={1} align="flex-end">
          <Text fontWeight="bold" fontSize="4xl" color={textColor}>{ticket.to}</Text>
          <Text fontSize="lg" color="gray.500">{ticket.arrivalTime}</Text>
        </VStack>
      </Flex>
      <Divider mb={6} />
      <Flex justify="space-between" align="center" mb={6}>
        <Text fontWeight="bold" fontSize="2xl" color="teal.600">{companyField}</Text>
        <Badge colorScheme="pink" fontSize="lg" px={4} py={2} borderRadius="md">{classField}</Badge>
      </Flex>
      <Flex align="center" justify="space-between" mb={6}>
        <VStack spacing={1} align="flex-start">
          <HStack>
            <Icon as={DepIcon} color="teal.500" />
            <Text fontSize="lg" fontWeight="bold" color={textColor}>{depField}</Text>
          </HStack>
          <Text fontSize="sm" color={labelColor}>Departure</Text>
        </VStack>
        <Icon as={FaRoute} w={10} h={10} color="gray.400" />
        <VStack spacing={1} align="flex-end">
          <HStack>
            <Icon as={ArrIcon} color="orange.500" />
            <Text fontSize="lg" fontWeight="bold" color={textColor}>{arrField}</Text>
          </HStack>
          <Text fontSize="sm" color={labelColor}>Arrival</Text>
        </VStack>
      </Flex>
      <Divider mb={6} />
      <VStack spacing={4} align="stretch">
        {numberField && (
          <HStack justify="space-between">
            <HStack>
              <Icon as={FaHashtag} color="blue.500" />
              <Text color={labelColor}>{ticket.type.charAt(0).toUpperCase() + ticket.type.slice(1)} Number:</Text>
            </HStack>
            <Text fontWeight="bold">{numberField}</Text>
          </HStack>
        )}
        {ticket.created_at && (
          <HStack justify="space-between">
            <HStack>
              <Icon as={FaClock} color="purple.500" />
              <Text color={labelColor}>Created:</Text>
            </HStack>
            <Text>{new Date(ticket.created_at).toLocaleString()}</Text>
          </HStack>
        )}
        {ticket.updated_at && (
          <HStack justify="space-between">
            <HStack>
              <Icon as={FaClock} color="green.500" />
              <Text color={labelColor}>Updated:</Text>
            </HStack>
            <Text>{new Date(ticket.updated_at).toLocaleString()}</Text>
          </HStack>
        )}
        {stopsField !== 'N/A' && (
          <HStack justify="space-between">
            <HStack>
              <Icon as={FaInfoCircle} color="red.400" />
              <Text color={labelColor}>Stops:</Text>
            </HStack>
            <Text fontWeight="bold">{stopsField}</Text>
          </HStack>
        )}
      </VStack>
      <VStack spacing={4} align="stretch" mt={3}>
        <Badge colorScheme="green" fontSize="lg" px={6} py={3}>{classField}</Badge>
        <Flex wrap="wrap" gap={3}>
          {ticket.features.map((feat, idx) => (
            <Badge key={idx} colorScheme="blue" fontSize="lg" px={4} py={2}>
              {feat}
            </Badge>
          ))}
        </Flex>
      </VStack>
      <Button
        mt={6}
        colorScheme="brand"
        size="lg"
        leftIcon={<FaTicketAlt />}
        width="full"
        onClick={onReserve}
      >
        Reserve
      </Button>
      <Button
        mt={6}
        colorScheme="red"
        size="lg"
        width="full"
        onClick={onClose}
        leftIcon={<FaTimes />}
      >
        Close
      </Button>
    </MotionBox>
  );
}

export default function TicketGrid({ tickets, onViewDetails, onReserve, loading }) {
  const [expandedIndex, setExpandedIndex] = useState(null);
  const mappedTickets = tickets.map((ticket) => sanitizeTicket(ticket));

  return (
    <Box py={12} px={{ base: 4, md: 8 }}>
      <AnimatePresence>
        {expandedIndex !== null ? (
          <ExpandedTicket
            ticket={mappedTickets[expandedIndex]}
            onClose={() => setExpandedIndex(null)}
            onReserve={() => onReserve(mappedTickets[expandedIndex])}
          />
        ) : (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={8}>
            {mappedTickets.map((ticket, idx) => (
              <TicketCard
                key={ticket.id}
                {...ticket}
                onExpand={() => {
                  setExpandedIndex(idx);
                  onViewDetails(ticket.id, ticket.type);
                }}
                onReserve={() => onReserve(ticket)}
              />
            ))}
          </SimpleGrid>
        )}
      </AnimatePresence>
    </Box>
  );
}