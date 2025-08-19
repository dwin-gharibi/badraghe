import React, { useState } from 'react';
import {
  Box,
  Flex,
  Heading,
  Text,
  Button,
  Image,
  Link,
  HStack,
  VStack,
  IconButton,
  Container,
  Stack,
  Collapse,
  useDisclosure,
  useColorModeValue,
} from '@chakra-ui/react';
import { FaFacebookF, FaTwitter, FaGithub, FaLinkedinIn, FaInstagram, FaChevronLeft, FaChevronRight } from 'react-icons/fa';
import { HamburgerIcon, CloseIcon } from '@chakra-ui/icons';
import NumbersSection from 'components/landing/Numbers';
import NumbersSection2 from 'components/landing/Numbers2';
import TravelSearch from 'components/landing/Search';
import Cta from 'components/landing/Cta';
import HeroSection from 'components/landing/Hero';
import SexyNavbar from 'components/landing/Navbar';
import TicketGrid from 'components/landing/Ticket';
import logoSvg from 'assets/img/logos/logo-badraghe.svg';
import noTicketsImage from 'assets/img/logos/badraghe-logo.png';
import { useNavigate } from 'react-router-dom';
import { getFlightDetails, getTrainDetails, getBusDetails } from 'services/api';
import { useToast } from '@chakra-ui/react';

export default function BadragheTravel() {
  const { isOpen, onToggle } = useDisclosure();
  const bg = useColorModeValue('white', 'white');
  const textColor = useColorModeValue('secondaryGray.900', 'gray.100');
  const subTextColor = useColorModeValue('secondaryGray.500', 'secondaryGray.400');
  const navigate = useNavigate();
  const toast = useToast();
  const [tickets, setTickets] = useState([]);
  const [page, setPage] = useState(1);
  const [totalTickets, setTotalTickets] = useState(0);
  const [hasSearched, setHasSearched] = useState(false);
  const limit = 9;
  const [loading, setLoading] = useState(false);

  const handleSearchResults = (searchTickets, currentPage, limit) => {
    const validTickets = Array.isArray(searchTickets) ? searchTickets : [];
    setTickets(validTickets);
    setTotalTickets(validTickets.length);
    setPage(currentPage);
    setHasSearched(true);
  };

  const handleViewDetails = async (ticketId, transportType) => {
    setLoading(true);
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
      setTickets((prevTickets) =>
        prevTickets.map((ticket) =>
          ticket.id === ticketId ? { ...ticket, ...response, transport_type: transportType } : ticket
        )
      );
      toast({
        title: 'Now you can see ticket details',
        description: response.summary || 'Details loaded successfully',
        status: 'info',
        duration: 7000,
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

  const handlePageChange = (direction) => {
    if (direction === 'next' && page * limit < totalTickets) {
      setPage(page + 1);
    } else if (direction === 'prev' && page > 1) {
      setPage(page - 1);
    }
  };

  return (
    <Flex direction="column" minH="100vh" fontFamily="DM Sans" bg={bg}>
      <SexyNavbar />
      <HeroSection />
      <TravelSearch onSearchResults={handleSearchResults} />
      {hasSearched && tickets.length === 0 ? (
        <VStack py={12} px={{ base: 4, md: 8 }} spacing={6} align="center">
          <Image
            src={noTicketsImage}
            alt="No Tickets Found"
            maxW={{ base: '200px', md: '300px' }}
            opacity={0.7}
          />
          <Text fontSize="xl" fontWeight="bold" color={textColor}>
            No Tickets Found
          </Text>
          <Text fontSize="md" color={subTextColor} textAlign="center">
            Try adjusting your search criteria to find available tickets.
          </Text>
          <Button
            colorScheme="brand"
            size="md"
            onClick={() => navigate('/')}
            _hover={{ transform: 'scale(1.05)', transition: '0.3s' }}
          >
            Search Again
          </Button>
        </VStack>
      ) : tickets.length > 0 ? (
        <Box py={12} px={{ base: 4, md: 8 }}>
          <VStack spacing={6} align="stretch">
            <TicketGrid
              tickets={tickets.slice((page - 1) * limit, page * limit)}
              onViewDetails={handleViewDetails}
              onReserve={(ticket) => navigate('/user/reserve', { state: { ticket } })}
              loading={loading}
            />
            <HStack justify="center" mt={4}>
              <Button
                onClick={() => handlePageChange('prev')}
                isDisabled={page === 1}
                leftIcon={<FaChevronLeft />}
                colorScheme="brand"
                size="sm"
              >
                Previous
              </Button>
              <Text color={textColor}>
                Page {page} of {Math.ceil(totalTickets / limit)}
              </Text>
              <Button
                onClick={() => handlePageChange('next')}
                isDisabled={page * limit >= totalTickets}
                rightIcon={<FaChevronRight />}
                colorScheme="brand"
                size="sm"
              >
                Next
              </Button>
            </HStack>
          </VStack>
        </Box>
      ) : null}
      <NumbersSection />
      <NumbersSection2 />
      <Cta />
      <Box flex="1" />
      <Box bg={bg} py={12} borderTop="1px solid" borderColor="secondaryGray.300">
        <Container maxW="container.xl">
          <VStack spacing={6}>
            <Image h="36px" src={logoSvg} alt="Footer Logo" />
            <HStack spacing={6} wrap="wrap" justify="center">
              {['About', 'Features', 'Blog', 'Rules', 'Partners', 'Help', 'Terms'].map((link) => (
                <Link key={link} fontSize="sm" color={subTextColor}>
                  {link}
                </Link>
              ))}
            </HStack>
            <HStack spacing={4}>
              <IconButton
                as="a"
                href="#"
                icon={<FaFacebookF />}
                variant="ghost"
                color="#4267B2"
                _hover={{ color: '#365899' }}
                aria-label="Facebook"
              />
              <IconButton
                as="a"
                href="#"
                icon={<FaTwitter />}
                variant="ghost"
                color="#1DA1F2"
                _hover={{ color: '#0d95e8' }}
                aria-label="Twitter"
              />
              <IconButton
                as="a"
                href="#"
                icon={<FaGithub />}
                variant="ghost"
                color="#333333"
                _hover={{ color: '#242424' }}
                aria-label="GitHub"
              />
              <IconButton
                as="a"
                href="#"
                icon={<FaLinkedinIn />}
                variant="ghost"
                color="#0077B5"
                _hover={{ color: '#046293' }}
                aria-label="LinkedIn"
              />
              <IconButton
                as="a"
                href="#"
                icon={<FaInstagram />}
                variant="ghost"
                color="url(#instagramGradient)"
                _hover={{ opacity: 0.8 }}
                aria-label="Instagram"
              />
            </HStack>
            <Text fontSize="sm" color={subTextColor} textAlign="center">
              © {new Date().getFullYear()}, Badraghe. All rights reserved.
            </Text>
          </VStack>
        </Container>
      </Box>
    </Flex>
  );
}