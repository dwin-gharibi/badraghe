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
import { FaPlane, FaTimes, FaTicketAlt, FaInfoCircle, FaTrain, FaBus } from 'react-icons/fa';
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
        <Icon as={typeIcons[type]} w={12} h={12} color={typeColors[type]} />
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
          {features.map((feat, idx) => (
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
        <Text fontWeight="bold" fontSize="2xl" color="teal.600">{ticket.company}</Text>
        <Badge colorScheme="pink" fontSize="2xl" px={5} py={2}>
          {ticket.price}
        </Badge>
      </Flex>
      <Flex align="center" justify="space-between" mb={6}>
        <VStack spacing={1} align="flex-start">
          <Text fontWeight="bold" fontSize="4xl" color={textColor}>{ticket.from}</Text>
          <Text fontSize="lg" color="gray.500">{ticket.departureTime}</Text>
        </VStack>
        <Icon as={typeIcons[ticket.type]} w={12} h={12} color={typeColors[ticket.type]} />
        <VStack spacing={1} align="flex-end">
          <Text fontWeight="bold" fontSize="4xl" color={textColor}>{ticket.to}</Text>
          <Text fontSize="lg" color="gray.500">{ticket.arrivalTime}</Text>
        </VStack>
      </Flex>
      <Divider mb={6} />
      <VStack spacing={4} align="stretch">
        <Badge colorScheme="green" fontSize="lg" px={6} py={3}>{ticket.classType}</Badge>
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

export default function TicketGrid({ tickets, onViewDetails, onReserve }) {
  const [expandedIndex, setExpandedIndex] = useState(null);
  const mappedTickets = tickets.map((ticket) => ({
    id: ticket.id,
    type: ticket.transport_type,
    company: ticket.company_name || 'N/A',
    price: `${(ticket.price / 1000000).toFixed(2)} ${ticket.currency}`,
    classType: ticket.class_type || 'Economy',
    from: ticket.departure_city,
    to: ticket.arrival_city,
    departureTime: ticket.departure_time,
    arrivalTime: ticket.arrival_time,
    features: ticket.features || [],
  }));

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
                key={idx}
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