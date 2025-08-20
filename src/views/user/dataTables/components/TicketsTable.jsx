import React, { useEffect, useState } from 'react';
import {
  Flex,
  Box,
  Table,
  Tbody,
  Td,
  Text,
  Th,
  Thead,
  Tr,
  useColorModeValue,
  Skeleton,
  Input,
  Badge,
  IconButton,
  Stack,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Button,
  VStack,
  Select,
} from '@chakra-ui/react';
import { createColumnHelper, flexRender, getCoreRowModel, getSortedRowModel, useReactTable } from '@tanstack/react-table';
import { useNavigate } from 'react-router-dom';
import Card from 'components/card/Card';
import Menu from 'components/menu/MainMenu';
import { searchTickets, getTicketDetails } from 'services/api';
import { useToast } from '@chakra-ui/react';
import { FaEye, FaTicketAlt, FaIdBadge, FaMapMarkerAlt, FaClock, FaDollarSign, FaPlane, FaChair, FaCheckCircle, FaBuilding } from 'react-icons/fa';
import { ChevronLeftIcon, ChevronRightIcon } from '@chakra-ui/icons';
import { useAuth } from '../../../../useAuth';

const columnHelper = createColumnHelper();

export default function TicketsTable() {
  const [sorting, setSorting] = useState([]);
  const [data, setData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    departure_city: '',
    arrival_city: '',
    transport_type: '',
    class_type: '',
  });
  const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 10 });
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [modalLoading, setModalLoading] = useState(false);
  const textColor = useColorModeValue('secondaryGray.900', 'white');
  const borderColor = useColorModeValue('gray.200', 'whiteAlpha.100');
  const toast = useToast();
  const { user } = useAuth();
  const userId = user?.id;
  const navigate = useNavigate();

  useEffect(() => {
    const fetchTickets = async () => {
      if (!userId) {
        setError('User not authenticated');
        setLoading(false);
        return;
      }
      setLoading(true);
      try {
        const response = await searchTickets({
          limit: pagination.pageSize,
          skip: pagination.pageIndex * pagination.pageSize,
          user_id: userId,
          departure_city: filters.departure_city || null,
          arrival_city: filters.arrival_city || null,
          transport_type: filters.transport_type || null,
          class_type: filters.class_type || null,
        });
        setData(response.data || response);
        setTotalCount(response.total || response?.length || 0);
      } catch (err) {
        setError(err.response?.data?.detail || err.message || 'Failed to fetch tickets');
        toast({
          title: 'Error',
          description: err.response?.data?.detail || err.message || 'Failed to fetch tickets',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setLoading(false);
      }
    };
    fetchTickets();
  }, [pagination.pageIndex, pagination.pageSize, userId, filters, toast]);

  useEffect(() => {
    if (!filters.departure_city && !filters.arrival_city && !filters.transport_type && !filters.class_type) {
      setFilteredData(data);
      return;
    }
    const lowerFilters = {
      departure_city: filters.departure_city.toLowerCase(),
      arrival_city: filters.arrival_city.toLowerCase(),
      transport_type: filters.transport_type.toLowerCase(),
      class_type: filters.class_type.toLowerCase(),
    };
    const filtered = data.filter((row) =>
      [
        row.departure_city?.toLowerCase().includes(lowerFilters.departure_city) || !lowerFilters.departure_city,
        row.arrival_city?.toLowerCase().includes(lowerFilters.arrival_city) || !lowerFilters.arrival_city,
        row.transport_type?.toLowerCase().includes(lowerFilters.transport_type) || !lowerFilters.transport_type,
        row.class_type?.toLowerCase().includes(lowerFilters.class_type) || !lowerFilters.class_type,
        row.id?.toString(),
        row.departure_time,
        row.arrival_time,
        row.price?.toString(),
        row.currency,
        row.available_seats?.toString(),
        row.status,
        row.transport_company_id?.toString(),
      ].every((value, index) => {
        if (index < 4) return value;
        return value?.toString().toLowerCase().includes(lowerFilters.departure_city) ||
               value?.toString().toLowerCase().includes(lowerFilters.arrival_city) ||
               value?.toString().toLowerCase().includes(lowerFilters.transport_type) ||
               value?.toString().toLowerCase().includes(lowerFilters.class_type) ||
               !lowerFilters.departure_city && !lowerFilters.arrival_city &&
               !lowerFilters.transport_type && !lowerFilters.class_type;
      })
    );
    setFilteredData(filtered);
  }, [data, filters]);

  const handleView = async (ticketId) => {
    setModalLoading(true);
    setIsModalOpen(true);
    try {
      const response = await getTicketDetails(ticketId);
      setSelectedTicket(response);
    } catch (err) {
      toast({
        title: 'Error',
        description: err.response?.data?.detail || err.message || 'Failed to fetch ticket details',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      setIsModalOpen(false);
    } finally {
      setModalLoading(false);
    }
  };

  const handleReserve = (ticket) => {
    navigate('/user/reserve', { state: { ticket } });
  };

  const handleFilterChange = (field, value) => {
    setFilters((prev) => ({ ...prev, [field]: value }));
    setPagination((old) => ({ ...old, pageIndex: 0 }));
  };

  const formatDateTime = (isoString) => {
    return isoString ? new Date(isoString).toLocaleString('en-US', { dateStyle: 'medium', timeStyle: 'short' }) : 'N/A';
  };

  const columns = [
    columnHelper.accessor('id', {
      id: 'id',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaIdBadge style={{ marginRight: '8px' }} />
          ID
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue()}</Text>,
    }),
    columnHelper.accessor('departure_city', {
      id: 'departure_city',
      header: () => (
        <VStack spacing={1}>
          <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
            <FaMapMarkerAlt style={{ marginRight: '8px' }} />
            DEPARTURE CITY
          </Flex>
        </VStack>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue()}</Text>,
    }),
    columnHelper.accessor('arrival_city', {
      id: 'arrival_city',
      header: () => (
        <VStack spacing={1}>
          <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
            <FaMapMarkerAlt style={{ marginRight: '8px' }} />
            ARRIVAL CITY
          </Flex>
        </VStack>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue()}</Text>,
    }),
    columnHelper.accessor('departure_time', {
      id: 'departure_time',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaClock style={{ marginRight: '8px' }} />
          DEPARTURE TIME
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{formatDateTime(info.getValue())}</Text>,
    }),
    columnHelper.accessor('arrival_time', {
      id: 'arrival_time',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaClock style={{ marginRight: '8px' }} />
          ARRIVAL TIME
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{formatDateTime(info.getValue())}</Text>,
    }),
    columnHelper.accessor('price', {
      id: 'price',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaDollarSign style={{ marginRight: '8px' }} />
          PRICE
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue()}</Text>,
    }),
    columnHelper.accessor('currency', {
      id: 'currency',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaDollarSign style={{ marginRight: '8px' }} />
          CURRENCY
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue()}</Text>,
    }),
    columnHelper.accessor('transport_type', {
      id: 'transport_type',
      header: () => (
        <VStack spacing={1}>
          <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
            <FaPlane style={{ marginRight: '8px' }} />
            TRANSPORT TYPE
          </Flex>
        </VStack>
      ),
      cell: (info) => (
        <Badge colorScheme={info.getValue() === 'plane' ? 'blue' : info.getValue() === 'bus' ? 'green' : 'yellow'} variant="solid">
          {info.getValue()}
        </Badge>
      ),
    }),
    columnHelper.accessor('class_type', {
      id: 'class_type',
      header: () => (
        <VStack spacing={1}>
          <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
            <FaChair style={{ marginRight: '8px' }} />
            CLASS TYPE
          </Flex>
        </VStack>
      ),
      cell: (info) => (
        <Badge colorScheme={info.getValue() === 'economy' ? 'green' : 'purple'} variant="solid">
          {info.getValue()}
        </Badge>
      ),
    }),
    columnHelper.accessor('available_seats', {
      id: 'available_seats',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaChair style={{ marginRight: '8px' }} />
          AVAILABLE SEATS
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue()}</Text>,
    }),
    columnHelper.accessor('status', {
      id: 'status',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaCheckCircle style={{ marginRight: '8px' }} />
          STATUS
        </Flex>
      ),
      cell: (info) => (
        <Badge
          colorScheme={
            info.getValue() === 'available' ? 'green' :
            info.getValue() === 'reserved' ? 'yellow' :
            info.getValue() === 'sold_out' ? 'red' : 'gray'
          }
          variant="solid"
        >
          {info.getValue() || 'N/A'}
        </Badge>
      ),
    }),
    columnHelper.accessor('transport_company_id', {
      id: 'transport_company_id',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaBuilding style={{ marginRight: '8px' }} />
          COMPANY ID
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue() || 'N/A'}</Text>,
    }),
    columnHelper.display({
      id: 'actions',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaEye style={{ marginRight: '8px' }} />
          ACTIONS
        </Flex>
      ),
      cell: (info) => (
        <Stack direction="row" spacing={2}>
          <IconButton
            icon={<FaEye />}
            colorScheme="blue"
            aria-label="View"
            onClick={() => handleView(info.row.original.id)}
          />
          <IconButton
            icon={<FaTicketAlt />}
            colorScheme="green"
            aria-label="View"
            onClick={() => handleReserve(info.row.original)}
          />
        </Stack>
      ),
    }),
  ];

  const table = useReactTable({
    data: filteredData,
    columns,
    state: { sorting, pagination },
    onSortingChange: setSorting,
    onPaginationChange: setPagination,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    manualPagination: true,
    pageCount: totalCount > 0 ? Math.ceil(totalCount / pagination.pageSize) : 1,
    debugTable: true,
  });

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedTicket(null);
  };

  if (error) return <Text color="red.500">{error}</Text>;

  return (
    <>
      <Card flexDirection="column" w="100%" px="0px" overflowX={{ sm: 'scroll', lg: 'hidden' }}>
        <Flex px="25px" mb="8px" justifyContent="space-between" align="center">
          <Text color={textColor} fontSize="22px" mb="4px" fontWeight="700" lineHeight="100%">
            Tickets Table
          </Text>
          <Menu />
        </Flex>
        <Box overflowY="auto" maxH="500px">
          {loading ? (
            <Stack>
              {[...Array(pagination.pageSize)].map((_, i) => (
                <Skeleton key={i} height="40px" />
              ))}
            </Stack>
          ) : filteredData.length === 0 ? (
            <Text textAlign="center" py="4" color={textColor}>
              No tickets found matching your filters.
            </Text>
          ) : (
            <Table variant="simple" color="gray.500" mb="24px" mt="12px">
              <Thead position="sticky" top={0} bg="white">
                {table.getHeaderGroups().map((headerGroup) => (
                  <Tr key={headerGroup.id}>
                    {headerGroup.headers.map((header) => (
                      <Th
                        key={header.id}
                        colSpan={header.colSpan}
                        pe="10px"
                        borderColor={borderColor}
                        cursor={header.column.getCanSort() ? 'pointer' : 'default'}
                        onClick={header.column.getToggleSortingHandler()}
                      >
                        <Flex
                          justifyContent="space-between"
                          align="center"
                          fontSize={{ sm: '10px', lg: '12px' }}
                          color="gray.400"
                        >
                          {flexRender(header.column.columnDef.header, header.getContext())}
                          {{ asc: ' 🔼', desc: ' 🔽' }[header.column.getIsSorted()] ?? null}
                        </Flex>
                      </Th>
                    ))}
                  </Tr>
                ))}
              </Thead>
              <Tbody>
                {table.getRowModel().rows.map((row) => (
                  <Tr key={row.id}>
                    {row.getVisibleCells().map((cell) => (
                      <Td
                        key={cell.id}
                        fontSize={{ sm: '14px' }}
                        minW={{ sm: '150px', md: '200px', lg: 'auto' }}
                        borderColor="transparent"
                      >
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </Td>
                    ))}
                  </Tr>
                ))}
              </Tbody>
            </Table>
          )}
        </Box>
        <Flex justifyContent="space-between" align="center" px="25px" mt="4">
          <Flex align="center">
            <Select
              value={pagination.pageSize}
              onChange={(e) => setPagination((old) => ({ ...old, pageSize: Number(e.target.value), pageIndex: 0 }))}
              w="100px"
            >
              <option value="5">5</option>
              <option value="10">10</option>
              <option value="20">20</option>
              <option value="50">50</option>
            </Select>
            <IconButton
              icon={<ChevronLeftIcon />}
              onClick={() => table.setPageIndex(pagination.pageIndex - 1)}
              isDisabled={pagination.pageIndex === 0}
              ml="2"
            />
            <Text mx="2" minW="150px" textAlign="center">
              Page {pagination.pageIndex + 1} of {table.getPageCount() || 1} ({totalCount} total)
            </Text>
            <IconButton
              icon={<ChevronRightIcon />}
              onClick={() => table.setPageIndex(pagination.pageIndex + 1)}
              isDisabled={pagination.pageIndex >= table.getPageCount() - 1}
            />
          </Flex>
        </Flex>
      </Card>
      <Modal isOpen={isModalOpen} onClose={closeModal} size="lg">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Ticket Details</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            {modalLoading ? (
              <Stack>
                <Skeleton height="20px" />
                <Skeleton height="20px" />
                <Skeleton height="20px" />
              </Stack>
            ) : selectedTicket ? (
              <VStack align="start" spacing={4}>
                <Text><strong>ID:</strong> {selectedTicket.id}</Text>
                <Text><strong>Departure City:</strong> {selectedTicket.departure_city}</Text>
                <Text><strong>Arrival City:</strong> {selectedTicket.arrival_city}</Text>
                <Text><strong>Departure Time:</strong> {formatDateTime(selectedTicket.departure_time)}</Text>
                <Text><strong>Arrival Time:</strong> {formatDateTime(selectedTicket.arrival_time)}</Text>
                <Text><strong>Price:</strong> {selectedTicket.price}</Text>
                <Text><strong>Currency:</strong> {selectedTicket.currency}</Text>
                <Text><strong>Transport Type:</strong> {selectedTicket.transport_type}</Text>
                <Text><strong>Class Type:</strong> {selectedTicket.class_type}</Text>
                <Text><strong>Available Seats:</strong> {selectedTicket.available_seats}</Text>
                <Text><strong>Status:</strong> {selectedTicket.status || 'N/A'}</Text>
                <Text><strong>Transport Company ID:</strong> {selectedTicket.transport_company_id || 'N/A'}</Text>
              </VStack>
            ) : (
              <Text>No data available</Text>
            )}
          </ModalBody>
          <ModalFooter>
            <Button colorScheme="blue" onClick={closeModal}>
              Close
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
}