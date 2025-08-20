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
import { listReviews, getReview, deleteReview } from 'services/api';
import { useToast } from '@chakra-ui/react';
import { FaEye, FaEdit, FaTrash, FaIdBadge, FaUser, FaTicketAlt, FaStar, FaComment, FaClock } from 'react-icons/fa';
import { ChevronLeftIcon, ChevronRightIcon } from '@chakra-ui/icons';
import { useAuth } from '../../../../useAuth';

const columnHelper = createColumnHelper();

export default function ReviewsTable() {
  const [sorting, setSorting] = useState([]);
  const [data, setData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    review_text: '',
    rating: '',
    ticket_id: '',
  });
  const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 10 });
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedReview, setSelectedReview] = useState(null);
  const [modalLoading, setModalLoading] = useState(false);
  const textColor = useColorModeValue('secondaryGray.900', 'white');
  const borderColor = useColorModeValue('gray.200', 'whiteAlpha.100');
  const toast = useToast();
  const { user } = useAuth();
  const userId = user?.id;
  const navigate = useNavigate();

  useEffect(() => {
    const fetchReviews = async () => {
      if (!userId) {
        setError('User not authenticated');
        setLoading(false);
        return;
      }
      setLoading(true);
      try {
        const response = await listReviews({
          limit: pagination.pageSize,
          skip: pagination.pageIndex * pagination.pageSize,
          user_id: userId,
          review_text: filters.review_text || null,
          rating: filters.rating || null,
          ticket_id: filters.ticket_id || null,
        });
        setData(response.data || response);
        setTotalCount(response.total || response?.length || 0);
      } catch (err) {
        setError(err.response?.data?.detail || err.message || 'Failed to fetch reviews');
        toast({
          title: 'Error',
          description: err.response?.data?.detail || err.message || 'Failed to fetch reviews',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setLoading(false);
      }
    };
    fetchReviews();
  }, [pagination.pageIndex, pagination.pageSize, userId, filters, toast]);

  useEffect(() => {
    if (!filters.review_text && !filters.rating && !filters.ticket_id) {
      setFilteredData(data);
      return;
    }
    const lowerFilters = {
      review_text: filters.review_text.toLowerCase(),
      rating: filters.rating.toLowerCase(),
      ticket_id: filters.ticket_id.toLowerCase(),
    };
    const filtered = data.filter((row) =>
      [
        row.review_text?.toLowerCase().includes(lowerFilters.review_text) || !lowerFilters.review_text,
        row.rating?.toString().includes(lowerFilters.rating) || !lowerFilters.rating,
        row.ticket_id?.toString().includes(lowerFilters.ticket_id) || !lowerFilters.ticket_id,
        row.id?.toString(),
        row.user_id?.toString(),
        row.created_at,
        row.updated_at,
      ].every((value, index) => {
        if (index < 3) return value;
        return value?.toString().toLowerCase().includes(lowerFilters.review_text) ||
               value?.toString().toLowerCase().includes(lowerFilters.rating) ||
               value?.toString().toLowerCase().includes(lowerFilters.ticket_id) ||
               !lowerFilters.review_text && !lowerFilters.rating && !lowerFilters.ticket_id;
      })
    );
    setFilteredData(filtered);
  }, [data, filters]);

  const handleView = async (reviewId) => {
    setModalLoading(true);
    setIsModalOpen(true);
    try {
      const response = await getReview(reviewId);
      setSelectedReview(response);
    } catch (err) {
      toast({
        title: 'Error',
        description: err.response?.data?.detail || err.message || 'Failed to fetch review details',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      setIsModalOpen(false);
    } finally {
      setModalLoading(false);
    }
  };

  const handleEdit = (reviewId) => {
    navigate('/user/reviews/edit', { state: { reviewId } });
  };

  const handleDelete = async (reviewId) => {
    try {
      await deleteReview(reviewId);
      toast({
        title: 'Success',
        description: 'Review deleted successfully',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      const response = await listReviews({
        limit: pagination.pageSize,
        skip: pagination.pageIndex * pagination.pageSize,
        user_id: userId,
        review_text: filters.review_text || null,
        rating: filters.rating || null,
        ticket_id: filters.ticket_id || null,
      });
      setData(response.data || response);
      setTotalCount(response.total || response?.length || 0);
    } catch (err) {
      toast({
        title: 'Error',
        description: err.response?.data?.detail || err.message || 'Failed to delete review',
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
        <VStack spacing={1}>
          <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
            <FaTicketAlt style={{ marginRight: '8px' }} />
            TICKET ID
          </Flex>
        </VStack>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue()}</Text>,
    }),
    columnHelper.accessor('rating', {
      id: 'rating',
      header: () => (
        <VStack spacing={1}>
          <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
            <FaStar style={{ marginRight: '8px' }} />
            RATING
          </Flex>
        </VStack>
      ),
      cell: (info) => (
        <Badge
          colorScheme={info.getValue() >= 4 ? 'green' : info.getValue() >= 3 ? 'yellow' : 'red'}
          variant="solid"
        >
          {info.getValue()}
        </Badge>
      ),
    }),
    columnHelper.accessor('review_text', {
      id: 'review_text',
      header: () => (
        <VStack spacing={1}>
          <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
            <FaComment style={{ marginRight: '8px' }} />
            REVIEW
          </Flex>
        </VStack>
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
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{formatDateTime(info.getValue())}</Text>,
    }),
    columnHelper.accessor('updated_at', {
      id: 'updated_at',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaClock style={{ marginRight: '8px' }} />
          UPDATED AT
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
    setSelectedReview(null);
  };

  if (error) return <Text color="red.500">{error}</Text>;

  return (
    <>
      <Card flexDirection="column" w="100%" px="0px" overflowX={{ sm: 'scroll', lg: 'hidden' }}>
        <Flex px="25px" mb="8px" justifyContent="space-between" align="center">
          <Text color={textColor} fontSize="22px" mb="4px" fontWeight="700" lineHeight="100%">
            Reviews Table
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
              No reviews found matching your filters.
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
          <ModalHeader>Review Details</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            {modalLoading ? (
              <Stack>
                <Skeleton height="20px" />
                <Skeleton height="20px" />
                <Skeleton height="20px" />
              </Stack>
            ) : selectedReview ? (
              <VStack align="start" spacing={4}>
                <Text><strong>ID:</strong> {selectedReview.id}</Text>
                <Text><strong>User ID:</strong> {selectedReview.user_id}</Text>
                <Text><strong>Ticket ID:</strong> {selectedReview.ticket_id}</Text>
                <Text><strong>Rating:</strong> {selectedReview.rating}</Text>
                <Text><strong>Review:</strong> {selectedReview.review_text || 'N/A'}</Text>
                <Text><strong>Created At:</strong> {formatDateTime(selectedReview.created_at)}</Text>
                <Text><strong>Updated At:</strong> {formatDateTime(selectedReview.updated_at)}</Text>
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