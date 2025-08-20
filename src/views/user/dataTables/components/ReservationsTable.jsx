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
  FormControl,
  FormLabel,
  keyframes,
} from '@chakra-ui/react';
import { createColumnHelper, flexRender, getCoreRowModel, getSortedRowModel, useReactTable } from '@tanstack/react-table';
import { useNavigate } from 'react-router-dom';
import Card from 'components/card/Card';
import Menu from 'components/menu/MainMenu';
import { getUserReservationHistory, cancelReservation, getReservation, getCancellationPenalty, payForReservation } from 'services/api';
import { useToast } from '@chakra-ui/react';
import { FaEye, FaTrash, FaIdBadge, FaTicketAlt, FaCheckCircle, FaDollarSign, FaClock, FaCreditCard, FaPlane, FaTrain, FaBus } from 'react-icons/fa';
import { ChevronLeftIcon, ChevronRightIcon } from '@chakra-ui/icons';
import { useAuth } from '../../../../useAuth';

const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
`;

const columnHelper = createColumnHelper();

export default function ReservationsTable() {
  const [sorting, setSorting] = useState([]);
  const [data, setData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    ticket_id: '',
    status: '',
    payment_id: '',
  });
  const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 10 });
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);
  const [isPayModalOpen, setIsPayModalOpen] = useState(false);
  const [isCancelModalOpen, setIsCancelModalOpen] = useState(false);
  const [selectedReservation, setSelectedReservation] = useState(null);
  const [modalLoading, setModalLoading] = useState(false);
  const [cancelPenalty, setCancelPenalty] = useState(null);
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState('');
  const textColor = useColorModeValue('secondaryGray.900', 'white');
  const borderColor = useColorModeValue('gray.200', 'whiteAlpha.100');
  const toast = useToast();
  const { user } = useAuth();
  const userId = user?.id;
  const navigate = useNavigate();

  useEffect(() => {
    const fetchReservations = async () => {
      if (!userId) {
        setError('User not authenticated');
        setLoading(false);
        return;
      }
      setLoading(true);
      try {
        const response = await getUserReservationHistory(userId, {
          limit: pagination.pageSize,
          skip: pagination.pageIndex * pagination.pageSize,
          ticket_id: filters.ticket_id || null,
          reservation_status: filters.status || null,
          payment_id: filters.payment_id || null,
        });
        setData(response.data || response);
        console.log(response)
        setTotalCount(response.total || response?.length || 0);
      } catch (err) {
        setError(err.response?.data?.detail || err.message || 'Failed to fetch reservations');
        toast({
          title: 'Error',
          description: err.response?.data?.detail || err.message || 'Failed to fetch reservations',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setLoading(false);
      }
    };
    fetchReservations();
  }, [pagination.pageIndex, pagination.pageSize, userId, filters, toast]);

  useEffect(() => {
    if (!filters.ticket_id && !filters.status && !filters.payment_id) {
      setFilteredData(data);
      return;
    }
    const lowerFilters = {
      ticket_id: filters.ticket_id.toLowerCase(),
      status: filters.status.toLowerCase(),
      payment_id: filters.payment_id.toLowerCase(),
    };
    const filtered = data.filter((row) =>
      [
        row.ticket_id?.toString().toLowerCase().includes(lowerFilters.ticket_id) || !lowerFilters.ticket_id,
        row.status?.toLowerCase().includes(lowerFilters.status) || !lowerFilters.status,
        row.payment_id?.toString().toLowerCase().includes(lowerFilters.payment_id) || !lowerFilters.payment_id,
      ].every(Boolean)
    );
    setFilteredData(filtered);
  }, [data, filters]);

  const handleView = async (reservationId) => {
    setModalLoading(true);
    setIsDetailsModalOpen(true);
    try {
      const response = await getReservation(reservationId);
      setSelectedReservation(response);
    } catch (err) {
      toast({
        title: 'Error',
        description: err.response?.data?.detail || err.message || 'Failed to fetch reservation details',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      setIsDetailsModalOpen(false);
    } finally {
      setModalLoading(false);
    }
  };

  const handleCancel = async (reservationId) => {
    setModalLoading(true);
    setIsCancelModalOpen(true);
    try {
      const penalty = await getCancellationPenalty(reservationId);
      setCancelPenalty(penalty);
      setSelectedReservation({ id: reservationId });
    } catch (err) {
      toast({
        title: 'Error',
        description: err.response?.data?.detail || err.message || 'Failed to fetch cancellation penalty',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      setIsCancelModalOpen(false);
    } finally {
      setModalLoading(false);
    }
  };

  const confirmCancel = async () => {
    try {
      await cancelReservation(selectedReservation.id, userId, 'User requested cancellation');
      toast({
        title: 'Success',
        description: 'Reservation canceled successfully',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      const response = await getUserReservationHistory(userId, {
        limit: pagination.pageSize,
        skip: pagination.pageIndex * pagination.pageSize,
        ticket_id: filters.ticket_id || null,
        reservation_status: filters.status || null,
        payment_id: filters.payment_id || null,
      });
      setData(response.data || response);
      setTotalCount(response.total || response.data?.length || 0);
      setIsCancelModalOpen(false);
      setCancelPenalty(null);
      setSelectedReservation(null);
    } catch (err) {
      toast({
        title: 'Error',
        description: err.response?.data?.detail || err.message || 'Failed to cancel reservation',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const handlePay = (reservation) => {
    setSelectedReservation(reservation);
    setIsPayModalOpen(true);
  };

  const confirmPay = async () => {
    if (!selectedPaymentMethod) {
      toast({
        title: 'Error',
        description: 'Please select a payment method',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      return;
    }
    try {
      await payForReservation(selectedReservation.id, { payment_method_id: Number(selectedPaymentMethod) });
      toast({
        title: 'Success',
        description: 'Payment processed successfully',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      const response = await getUserReservationHistory(userId, {
        limit: pagination.pageSize,
        skip: pagination.pageIndex * pagination.pageSize,
        ticket_id: filters.ticket_id || null,
        reservation_status: filters.status || null,
        payment_id: filters.payment_id || null,
      });
      setData(response.data || response);
      setTotalCount(response.total || response.data?.length || 0);
      setIsPayModalOpen(false);
      setSelectedPaymentMethod('');
      setSelectedReservation(null);
    } catch (err) {
      toast({
        title: 'Error',
        description: err.response?.data?.detail || err.message || 'Failed to process payment',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
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
    columnHelper.accessor('ticket_id', {
      id: 'ticket_id',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaTicketAlt style={{ marginRight: '8px' }} />
          TICKET ID
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
            info.getValue() === 'paid' ? 'green' :
            info.getValue() === 'canceled' ? 'red' :
            info.getValue() === 'expired' ? 'gray' : 'yellow'
          }
          variant="solid"
        >
          {info.getValue()}
        </Badge>
      ),
    }),
    columnHelper.accessor('price_paid', {
      id: 'price_paid',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaDollarSign style={{ marginRight: '8px' }} />
          PRICE PAID
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue() || 'N/A'}</Text>,
    }),
    columnHelper.accessor('currency', {
      id: 'currency',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaDollarSign style={{ marginRight: '8px' }} />
          CURRENCY
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue() || 'N/A'}</Text>,
    }),
    columnHelper.accessor('reserved_at', {
      id: 'reserved_at',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaClock style={{ marginRight: '8px' }} />
          RESERVED AT
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{formatDateTime(info.getValue())}</Text>,
    }),
    columnHelper.accessor('expires_at', {
      id: 'expires_at',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaClock style={{ marginRight: '8px' }} />
          EXPIRES AT
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{formatDateTime(info.getValue())}</Text>,
    }),
    columnHelper.accessor('payment_id', {
      id: 'payment_id',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaCreditCard style={{ marginRight: '8px' }} />
          PAYMENT ID
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue() || 'N/A'}</Text>,
    }),
    columnHelper.accessor('ticket_details.departure_city', {
      id: 'departure_city',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaTicketAlt style={{ marginRight: '8px' }} />
          DEPARTURE CITY
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue() || 'N/A'}</Text>,
    }),
    columnHelper.accessor('ticket_details.arrival_city', {
      id: 'arrival_city',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaTicketAlt style={{ marginRight: '8px' }} />
          ARRIVAL CITY
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue() || 'N/A'}</Text>,
    }),
    columnHelper.accessor('ticket_details.departure_time', {
      id: 'departure_time',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaClock style={{ marginRight: '8px' }} />
          DEPARTURE TIME
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{formatDateTime(info.getValue())}</Text>,
    }),
    columnHelper.accessor('ticket_details.arrival_time', {
      id: 'arrival_time',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaClock style={{ marginRight: '8px' }} />
          ARRIVAL TIME
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{formatDateTime(info.getValue())}</Text>,
    }),
    columnHelper.accessor('ticket_details.price', {
      id: 'ticket_price',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaDollarSign style={{ marginRight: '8px' }} />
          TICKET PRICE
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue() || 'N/A'}</Text>,
    }),
    columnHelper.accessor('ticket_details.currency', {
      id: 'ticket_currency',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaDollarSign style={{ marginRight: '8px' }} />
          TICKET CURRENCY
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue() || 'N/A'}</Text>,
    }),
    columnHelper.accessor('ticket_details.transport_type', {
      id: 'transport_type',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaTicketAlt style={{ marginRight: '8px' }} />
          TRANSPORT TYPE
        </Flex>
      ),
      cell: (info) => (
        <Badge
          colorScheme={
            info.getValue() === 'plane' ? 'blue' :
            info.getValue() === 'train' ? 'green' :
            info.getValue() === 'bus' ? 'red' : 'gray'
          }
          variant="solid"
          display="flex"
          alignItems="center"
        >
          {info.getValue() === 'plane' ? <FaPlane style={{ marginRight: '4px' }} /> :
           info.getValue() === 'train' ? <FaTrain style={{ marginRight: '4px' }} /> :
           info.getValue() === 'bus' ? <FaBus style={{ marginRight: '4px' }} /> : null}
          {info.getValue() ? info.getValue().charAt(0).toUpperCase() + info.getValue().slice(1) : 'N/A'}
        </Badge>
      ),
    }),
    columnHelper.accessor('ticket_details.class_type', {
      id: 'class_type',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaTicketAlt style={{ marginRight: '8px' }} />
          CLASS TYPE
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue() || 'N/A'}</Text>,
    }),
    columnHelper.accessor('ticket_details.available_seats', {
      id: 'available_seats',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaTicketAlt style={{ marginRight: '8px' }} />
          AVAILABLE SEATS
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue() || 'N/A'}</Text>,
    }),
    columnHelper.accessor('payment_details.status', {
      id: 'payment_status',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaCreditCard style={{ marginRight: '8px' }} />
          PAYMENT STATUS
        </Flex>
      ),
      cell: (info) => (
        <Badge
          colorScheme={info.getValue() === 'successful' ? 'green' : 'gray'}
          variant="solid"
        >
          {info.getValue() || 'N/A'}
        </Badge>
      ),
    }),
    columnHelper.accessor('payment_details.transaction_id', {
      id: 'transaction_id',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaCreditCard style={{ marginRight: '8px' }} />
          TRANSACTION ID
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue() || 'N/A'}</Text>,
    }),
    columnHelper.accessor('payment_details.payment_date', {
      id: 'payment_date',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaClock style={{ marginRight: '8px' }} />
          PAYMENT DATE
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{formatDateTime(info.getValue())}</Text>,
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
            _hover={{ transform: 'scale(1.1)' }}
            transition="transform 0.2s"
          />
          <IconButton
            icon={<FaCreditCard />}
            colorScheme="green"
            aria-label="Pay"
            onClick={() => handlePay(info.row.original)}
            isDisabled={info.row.original.status === 'canceled' || info.row.original.status === 'paid'}
            _hover={{ transform: 'scale(1.1)' }}
            transition="transform 0.2s"
          />
          <IconButton
            icon={<FaTrash />}
            colorScheme="red"
            aria-label="Cancel"
            onClick={() => handleCancel(info.row.original.id)}
            isDisabled={info.row.original.status === 'canceled'}
            _hover={{ transform: 'scale(1.1)' }}
            transition="transform 0.2s"
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

  const closeDetailsModal = () => {
    setIsDetailsModalOpen(false);
    setSelectedReservation(null);
  };

  const closePayModal = () => {
    setIsPayModalOpen(false);
    setSelectedPaymentMethod('');
    setSelectedReservation(null);
  };

  const closeCancelModal = () => {
    setIsCancelModalOpen(false);
    setCancelPenalty(null);
    setSelectedReservation(null);
  };

  if (error) return <Text color="red.500">{error}</Text>;

  return (
    <>
      <Card flexDirection="column" w="100%" px="0px" overflowX={{ sm: 'scroll', lg: 'hidden' }} bg="white" boxShadow="0px 40px 58px -20px rgba(112, 144, 176, 0.26)" animation={`${fadeIn} 0.5s ease-out`}>
        <Flex px="25px" mb="8px" justifyContent="space-between" align="center">
          <Text color={textColor} fontSize="22px" mb="4px" fontWeight="700" lineHeight="100%">
            Reservations Table
          </Text>
          <Menu />
        </Flex>
        <Flex px="25px" mb="16px" justifyContent="space-between" align="center">
          <Input
            placeholder="Filter by Ticket ID"
            value={filters.ticket_id}
            onChange={(e) => handleFilterChange('ticket_id', e.target.value)}
            width="200px"
            size="sm"
          />
          <Select
            placeholder="Filter by Status"
            value={filters.status}
            onChange={(e) => handleFilterChange('status', e.target.value)}
            width="200px"
            size="sm"
          >
            <option value="temporary">Temporary</option>
            <option value="reserved">Reserved</option>
            <option value="paid">Paid</option>
            <option value="canceled">Canceled</option>
            <option value="expired">Expired</option>
          </Select>
          <Input
            placeholder="Filter by Payment ID"
            value={filters.payment_id}
            onChange={(e) => handleFilterChange('payment_id', e.target.value)}
            width="200px"
            size="sm"
          />
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
              No reservations found matching your filters.
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
              size="sm"
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
              _hover={{ transform: 'scale(1.1)' }}
              transition="transform 0.2s"
            />
            <Text mx="2" minW="150px" textAlign="center">
              Page {pagination.pageIndex + 1} of {table.getPageCount() || 1} ({totalCount} total)
            </Text>
            <IconButton
              icon={<ChevronRightIcon />}
              onClick={() => table.setPageIndex(pagination.pageIndex + 1)}
              isDisabled={pagination.pageIndex >= table.getPageCount() - 1}
              _hover={{ transform: 'scale(1.1)' }}
              transition="transform 0.2s"
            />
          </Flex>
        </Flex>
      </Card>
      <Modal isOpen={isDetailsModalOpen} onClose={closeDetailsModal} size="lg">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Reservation Details</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            {modalLoading ? (
              <Stack>
                <Skeleton height="20px" />
                <Skeleton height="20px" />
                <Skeleton height="20px" />
              </Stack>
            ) : selectedReservation ? (
              <VStack align="start" spacing={4}>
                <Text><strong>ID:</strong> {selectedReservation.id}</Text>
                <Text><strong>Ticket ID:</strong> {selectedReservation.ticket_id}</Text>
                <Text><strong>Status:</strong> {selectedReservation.status}</Text>
                <Text><strong>Price Paid:</strong> {selectedReservation.price_paid || 'N/A'}</Text>
                <Text><strong>Currency:</strong> {selectedReservation.currency || 'N/A'}</Text>
                <Text><strong>Reserved At:</strong> {formatDateTime(selectedReservation.reserved_at)}</Text>
                <Text><strong>Expires At:</strong> {formatDateTime(selectedReservation.expires_at)}</Text>
                <Text><strong>Payment ID:</strong> {selectedReservation.payment_id || 'N/A'}</Text>
                <Text><strong>Departure City:</strong> {selectedReservation.ticket_details?.departure_city || 'N/A'}</Text>
                <Text><strong>Arrival City:</strong> {selectedReservation.ticket_details?.arrival_city || 'N/A'}</Text>
                <Text><strong>Departure Time:</strong> {formatDateTime(selectedReservation.ticket_details?.departure_time)}</Text>
                <Text><strong>Arrival Time:</strong> {formatDateTime(selectedReservation.ticket_details?.arrival_time)}</Text>
                <Text><strong>Ticket Price:</strong> {selectedReservation.ticket_details?.price || 'N/A'}</Text>
                <Text><strong>Ticket Currency:</strong> {selectedReservation.ticket_details?.currency || 'N/A'}</Text>
                <Text><strong>Transport Type:</strong> {selectedReservation.ticket_details?.transport_type || 'N/A'}</Text>
                <Text><strong>Class Type:</strong> {selectedReservation.ticket_details?.class_type || 'N/A'}</Text>
                <Text><strong>Available Seats:</strong> {selectedReservation.ticket_details?.available_seats || 'N/A'}</Text>
                <Text><strong>Payment Status:</strong> {selectedReservation.payment_details?.status || 'N/A'}</Text>
                <Text><strong>Transaction ID:</strong> {selectedReservation.payment_details?.transaction_id || 'N/A'}</Text>
                <Text><strong>Payment Date:</strong> {formatDateTime(selectedReservation.payment_details?.payment_date)}</Text>
              </VStack>
            ) : (
              <Text>No data available</Text>
            )}
          </ModalBody>
          <ModalFooter>
            <Button colorScheme="blue" onClick={closeDetailsModal}>
              Close
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
      <Modal isOpen={isPayModalOpen} onClose={closePayModal} size="md">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Pay for Reservation</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4}>
              <Text>Select a payment method to proceed with the payment.</Text>
              <FormControl>
                <FormLabel>Payment Method</FormLabel>
                <Select
                  placeholder="Select payment method"
                  value={selectedPaymentMethod}
                  onChange={(e) => setSelectedPaymentMethod(e.target.value)}
                >
                  <option value="1">Credit Card</option>
                  <option value="2">Debit Card</option>
                  <option value="3">PayPal</option>
                </Select>
              </FormControl>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button colorScheme="blue" mr={3} onClick={confirmPay} isDisabled={!selectedPaymentMethod}>
              Confirm Payment
            </Button>
            <Button variant="ghost" onClick={closePayModal}>
              Cancel
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
      <Modal isOpen={isCancelModalOpen} onClose={closeCancelModal} size="md">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Cancel Reservation</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            {modalLoading ? (
              <Stack>
                <Skeleton height="20px" />
                <Skeleton height="20px" />
              </Stack>
            ) : cancelPenalty ? (
              <VStack align="start" spacing={4}>
                <Text><strong>Cancellation Penalty:</strong> {cancelPenalty.amount || 'N/A'} {cancelPenalty.currency || 'N/A'}</Text>
                <Text>Are you sure you want to cancel this reservation?</Text>
              </VStack>
            ) : (
              <Text>No penalty information available</Text>
            )}
          </ModalBody>
          <ModalFooter>
            <Button colorScheme="red" mr={3} onClick={confirmCancel}>
              Confirm Cancellation
            </Button>
            <Button variant="ghost" onClick={closeCancelModal}>
              Close
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
}