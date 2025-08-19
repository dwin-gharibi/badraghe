import React, { useState } from 'react';
import {
  Box,
  Flex,
  Input,
  Icon,
  Button,
  VStack,
  HStack,
  Text,
  useColorModeValue,
  useToast,
  Spinner,
} from '@chakra-ui/react';
import {
  FaPlane,
  FaTrain,
  FaBus,
  FaMapMarkerAlt,
  FaCalendarAlt,
  FaSearch,
  FaGlobe,
} from 'react-icons/fa';
import { searchTickets } from 'services/api';

export default function TravelSearch({ onSearchResults }) {
  const [activeType, setActiveType] = useState('plane');
  const [formData, setFormData] = useState({
    keyword: '',
    from: '',
    to: '',
    travel_date: '',
  });
  const [page, setPage] = useState(1);
  const [isSearching, setIsSearching] = useState(false);
  const limit = 10;
  const toast = useToast();
  const types = [
    { key: 'plane', icon: FaPlane, label: 'Flight' },
    { key: 'train', icon: FaTrain, label: 'Train' },
    { key: 'bus', icon: FaBus, label: 'Bus' },
    { key: 'all', icon: FaGlobe, label: 'All' },
  ];
  const bgGlass = useColorModeValue('rgba(255,255,255,1)', 'rgba(26,32,44,1)');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setPage(1);
  };

  const handleSearch = async () => {
    setIsSearching(true);
    try {
      const response = await searchTickets({
        departure_city: formData.from || null,
        arrival_city: formData.to || null,
        travel_date: formData.travel_date || null,
        transport_type: activeType !== 'all' ? activeType : null,
        skip: (page - 1) * limit,
        limit,
      });
      if (response.length > 0) {
        onSearchResults(response, page, limit, response.length);
      } else {
        toast({
          title: 'No Results',
          description: 'No tickets found for your search',
          status: 'warning',
          duration: 5000,
          isClosable: true,
        });
      }
    } catch (err) {
      toast({
        title: 'Error',
        description: err.response?.data?.detail || err.message || 'Failed to search tickets',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <Box
      p={{ base: 6, md: 8 }}
      rounded="2xl"
      bg={bgGlass}
      backdropFilter="blur(16px)"
      boxShadow="xl"
      maxW="container.lg"
      mx="auto"
      mt={{ base: 8, md: 10 }}
    >
      <HStack justify="center" spacing={4} mb={6} wrap="wrap">
        {types.map((t) => (
          <Button
            key={t.key}
            leftIcon={<Icon as={t.icon} />}
            variant={activeType === t.key ? 'solid' : 'outline'}
            colorScheme="brand"
            onClick={() => {
              setActiveType(t.key);
              setPage(1);
            }}
            rounded="full"
            px={6}
            _hover={{ transform: 'scale(1.05)' }}
            transition="all 0.2s"
            mb={{ base: 2, md: 0 }}
            borderColor={activeType === t.key ? 'brand.500' : 'navy.700'}
            color={activeType === t.key ? 'white' : 'navy.700'}
            isDisabled={isSearching}
          >
            {t.label}
          </Button>
        ))}
      </HStack>
      <Flex
        direction={{ base: 'column', md: 'row' }}
        gap={4}
        align="center"
        justify="center"
        wrap="wrap"
      >
        <HStack
          bg="none"
          rounded="full"
          px={4}
          py={2}
          flex={{ base: '1 1 100%', md: '1 1 auto' }}
        >
          <Icon as={FaSearch} color="yellow.500" />
          <Input
            name="keyword"
            value={formData.keyword}
            onChange={handleInputChange}
            placeholder="Search destinations..."
            type="text"
            size="lg"
            border="none"
            _focus={{ boxShadow: 'none' }}
            isDisabled={isSearching}
          />
        </HStack>
        <HStack
          bg="none"
          rounded="full"
          px={4}
          py={2}
          flex={{ base: '1 1 45%', md: '1 1 auto' }}
        >
          <Icon as={FaMapMarkerAlt} color="green.300" />
          <Input
            name="from"
            value={formData.from}
            onChange={handleInputChange}
            placeholder="From"
            border="none"
            _focus={{ boxShadow: 'none' }}
            isDisabled={isSearching}
          />
        </HStack>
        <HStack
          bg="none"
          rounded="full"
          px={4}
          py={2}
          flex={{ base: '1 1 45%', md: '1 1 auto' }}
        >
          <Icon as={FaMapMarkerAlt} color="red.300" />
          <Input
            name="to"
            value={formData.to}
            onChange={handleInputChange}
            placeholder="To"
            border="none"
            _focus={{ boxShadow: 'none' }}
            isDisabled={isSearching}
          />
        </HStack>
        <HStack
          bg="none"
          rounded="full"
          px={4}
          py={2}
          flex={{ base: '1 1 45%', md: '1 1 auto' }}
        >
          <Icon as={FaCalendarAlt} color="brand.500" />
          <Input
            name="travel_date"
            type="date"
            value={formData.travel_date}
            onChange={handleInputChange}
            border="none"
            _focus={{ boxShadow: 'none' }}
            isDisabled={isSearching}
          />
        </HStack>
        <Button
          colorScheme="brand"
          size="lg"
          rounded="full"
          px={8}
          flex={{ base: '1 1 45%', md: 'auto' }}
          leftIcon={isSearching ? <Spinner size="sm" /> : <FaSearch />}
          _hover={{ transform: 'scale(1.01)' }}
          transition="all 0.2s"
          onClick={handleSearch}
          isLoading={isSearching}
        >
          Search
        </Button>
      </Flex>
    </Box>
  );
}