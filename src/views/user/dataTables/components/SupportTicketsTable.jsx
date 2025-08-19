/* eslint-disable */
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
  InputGroup,
  InputLeftElement,
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
} from '@chakra-ui/react';
import { createColumnHelper, flexRender, getCoreRowModel, getSortedRowModel, useReactTable } from '@tanstack/react-table';
import Card from 'components/card/Card';
import Menu from 'components/menu/MainMenu';
import Pagination from 'components/Pagination';
import { getSupportTickets, deleteSupportTicket, getSupportTicket, getSupportStats } from 'services/api';
import { useToast } from '@chakra-ui/react';
import { FaSearch, FaEye, FaEdit, FaTrash, FaIdBadge, FaUser, FaTag, FaComment, FaCheckCircle, FaClock, FaCog, FaList, FaEnvelope, FaRocket } from 'react-icons/fa';

import { useAuth } from '../../../../useAuth';

const columnHelper = createColumnHelper();

export default function SupportTicketsTable() {
  const [sorting, setSorting] = useState([]);
  const [data, setData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [pageIndex, setPageIndex] = useState(0);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [modalLoading, setModalLoading] = useState(false);
  const pageSize = 10;
  const textColor = useColorModeValue('secondaryGray.900', 'white');
  const borderColor = useColorModeValue('gray.200', 'whiteAlpha.100');
  const toast = useToast();
  const { user } = useAuth();
  const userId = user?.id;

  useEffect(() => {
    const fetchSupportTickets = async () => {
      if (!userId) {
        setError('User not authenticated');
        setLoading(false);
        return;
      }
      setLoading(true);
      try {
        // Fetch total count
        let total = 0;
        try {
          const statsResponse = await getSupportStats();
          total = statsResponse.total_tickets || 0;
        } catch (statsErr) {
          console.warn('Failed to fetch total count:', statsErr);
        }

        // Fetch tickets
        const params = {
          skip: pageIndex * pageSize,
          limit: pageSize,
          user_id: userId,
          search: searchTerm || undefined,
        };
        const response = await getSupportTickets(params);
        const tickets = response.data || response;
        setData(tickets);
        // Set total count: use API count if available, else estimate
        if (total > 0) {
          setTotalCount(total);
        } else {
          setTotalCount(tickets.length === pageSize ? (pageIndex + 2) * pageSize : tickets.length);
        }
      } catch (err) {
        console.error('Error Details:', err);
        setError(err.response?.data?.detail || err.message || 'Failed to fetch support tickets');
        toast({
          title: 'Error',
          description: err.response?.data?.detail || err.message || 'Failed to fetch support tickets',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setLoading(false);
      }
    };
    fetchSupportTickets();
  }, [pageIndex, userId, searchTerm, toast]);

  // Client-side search filtering as fallback
  useEffect(() => {
    if (!searchTerm) {
      setFilteredData(data);
      return;
    }
    const lowerSearch = searchTerm.toLowerCase();
    const filtered = data.filter((row) =>
      [
        row.id?.toString(),
        row.user_id?.toString(),
        row.category_id?.toString(),
        row.subject,
        row.description,
        row.status,
        row.priority,
        row.assigned_to?.toString(),
        row.created_at,
        row.updated_at,
        row.category_name,
        row.user_email,
        row.assigned_email,
      ].some((value) => value?.toString().toLowerCase().includes(lowerSearch))
    );
    setFilteredData(filtered);
  }, [data, searchTerm]);

  const handleDelete = async (ticketId) => {
    try {
      await deleteSupportTicket(ticketId);
      toast({
        title: 'Success',
        description: 'Support ticket deleted successfully',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      const params = {
        skip: pageIndex * pageSize,
        limit: pageSize,
        user_id: userId,
        search: searchTerm || undefined,
      };
      const response = await getSupportTickets(params);
      setData(response.data || response);
      let total = 0;
      try {
        const statsResponse = await getSupportStats();
        total = statsResponse.total_tickets || 0;
      } catch (statsErr) {
        console.warn('Failed to fetch total count:', statsErr);
      }
      if (total > 0) {
        setTotalCount(total);
      } else {
        setTotalCount(response.data.length === pageSize ? (pageIndex + 2) * pageSize : response.data.length);
      }
    } catch (err) {
      toast({
        title: 'Error',
        description: err.response?.data?.detail || err.message || 'Failed to delete support ticket',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const handleView = async (ticketId) => {
    setModalLoading(true);
    setIsModalOpen(true);
    try {
      const response = await getSupportTicket(ticketId);
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

  const handleEdit = (ticketId) => {
    console.log('Edit ticket', ticketId);
    // Implement edit functionality (e.g., open a form modal) if needed
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
    columnHelper.accessor('user_id', {
      id: 'user_id',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaUser style={{ marginRight: '8px' }} />
          USER ID
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue()}</Text>,
    }),
    columnHelper.accessor('category_id', {
      id: 'category_id',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaTag style={{ marginRight: '8px' }} />
          CATEGORY ID
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue()}</Text>,
    }),
    columnHelper.accessor('subject', {
      id: 'subject',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaComment style={{ marginRight: '8px' }} />
          SUBJECT
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue()}</Text>,
    }),
    columnHelper.accessor('description', {
      id: 'description',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaList style={{ marginRight: '8px' }} />
          DESCRIPTION
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
            info.getValue() === 'resolved' ? 'green' :
            info.getValue() === 'closed' ? 'blue' :
            info.getValue() === 'in_progress' ? 'yellow' : 'orange'
          }
          variant="solid"
        >
          {info.getValue()}
        </Badge>
      ),
    }),
    columnHelper.accessor('priority', {
      id: 'priority',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaRocket style={{ marginRight: '8px' }} />
          PRIORITY
        </Flex>
      ),
      cell: (info) => (
        <Badge
          colorScheme={
            info.getValue() === 'high' ? 'red' :
            info.getValue() === 'medium' ? 'yellow' : 'green'
          }
          variant="solid"
        >
          {info.getValue()}
        </Badge>
      ),
    }),
    columnHelper.accessor('assigned_to', {
      id: 'assigned_to',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaUser style={{ marginRight: '8px' }} />
          ASSIGNED TO
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue() || 'N/A'}</Text>,
    }),
    columnHelper.accessor('created_at', {
      id: 'created_at',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaClock style={{ marginRight: '8px' }} />
          CREATED AT
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue()}</Text>,
    }),
    columnHelper.accessor('updated_at', {
      id: 'updated_at',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaClock style={{ marginRight: '8px' }} />
          UPDATED AT
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue()}</Text>,
    }),
    columnHelper.accessor('category_name', {
      id: 'category_name',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaTag style={{ marginRight: '8px' }} />
          CATEGORY NAME
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue() || 'N/A'}</Text>,
    }),
    columnHelper.accessor('user_email', {
      id: 'user_email',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaEnvelope style={{ marginRight: '8px' }} />
          USER EMAIL
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue() || 'N/A'}</Text>,
    }),
    columnHelper.accessor('assigned_email', {
      id: 'assigned_email',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaEnvelope style={{ marginRight: '8px' }} />
          ASSIGNED EMAIL
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue() || 'N/A'}</Text>,
    }),
    columnHelper.display({
      id: 'actions',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaCog style={{ marginRight: '8px' }} />
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
            icon={<FaEdit />}
            colorScheme="yellow"
            aria-label="Edit"
            onClick={() => handleEdit(info.row.original.id)}
          />
          <IconButton
            icon={<FaTrash />}
            colorScheme="red"
            aria-label="Delete"
            onClick={() => handleDelete(info.row.original.id)}
          />
        </Stack>
      ),
    }),
  ];

  const table = useReactTable({
    data: filteredData,
    columns,
    state: { sorting, pageIndex },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    manualPagination: true,
    pageCount: Math.ceil(totalCount / pageSize),
    debugTable: true,
  });

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
    setPageIndex(0);
  };

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
            My Support Tickets
          </Text>
          <Menu />
        </Flex>
        <Flex px="25px" mb="8px">
          <InputGroup maxW="300px">
            <InputLeftElement pointerEvents="none">
              <FaSearch color="gray.300" />
            </InputLeftElement>
            <Input
              type="text"
              placeholder="Search tickets..."
              value={searchTerm}
              onChange={handleSearch}
            />
          </InputGroup>
        </Flex>
        <Box overflowY="auto" maxH="500px">
          {loading ? (
            <Stack>
              {[...Array(pageSize)].map((_, i) => (
                <Skeleton key={i} height="40px" />
              ))}
            </Stack>
          ) : filteredData.length === 0 ? (
            <Text textAlign="center" py="4" color={textColor}>
              No support tickets found matching your search.
            </Text>
          ) : (
            <Table variant="simple" color="gray.500" mb="24px" mt="12px">
              <Thead position="sticky" top={0} bg={useColorModeValue('white', 'gray.800')}>
                {table.getHeaderGroups().map((headerGroup) => (
                  <Tr key={headerGroup.id}>
                    {headerGroup.headers.map((header) => (
                      <Th
                        key={header.id}
                        colSpan={header.colSpan}
                        pe="10px"
                        borderColor={borderColor}
                        cursor="pointer"
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
        <Flex justifyContent="center" mt="4">
          <Pagination
            currentPage={pageIndex + 1}
            totalCount={totalCount}
            pageSize={pageSize}
            onPageChange={(page) => setPageIndex(page - 1)}
          />
        </Flex>
      </Card>

      <Modal isOpen={isModalOpen} onClose={closeModal} size="lg">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Support Ticket Details</ModalHeader>
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
                <Text><strong>User ID:</strong> {selectedTicket.user_id}</Text>
                <Text><strong>User Email:</strong> {selectedTicket.user_email || 'N/A'}</Text>
                <Text><strong>Category ID:</strong> {selectedTicket.category_id}</Text>
                <Text><strong>Category Name:</strong> {selectedTicket.category_name || 'N/A'}</Text>
                <Text><strong>Subject:</strong> {selectedTicket.subject}</Text>
                <Text><strong>Description:</strong> {selectedTicket.description}</Text>
                <Text><strong>Status:</strong> {selectedTicket.status}</Text>
                <Text><strong>Priority:</strong> {selectedTicket.priority}</Text>
                <Text><strong>Assigned To:</strong> {selectedTicket.assigned_to || 'N/A'}</Text>
                <Text><strong>Assigned Email:</strong> {selectedTicket.assigned_email || 'N/A'}</Text>
                <Text><strong>Created At:</strong> {selectedTicket.created_at}</Text>
                <Text><strong>Updated At:</strong> {selectedTicket.updated_at}</Text>
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