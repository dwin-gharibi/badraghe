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
  Select,
} from '@chakra-ui/react';
import { createColumnHelper, flexRender, getCoreRowModel, getSortedRowModel, useReactTable } from '@tanstack/react-table';
import Card from 'components/card/Card';
import Menu from 'components/menu/MainMenu';
import { listRefundRequests, getRefundRequestCount, getRefundRequestDetails } from 'services/api';
import { useToast } from '@chakra-ui/react';
import { FaSearch, FaEye, FaTrash, FaIdBadge, FaDollarSign, FaComment, FaCheckCircle, FaClock } from 'react-icons/fa';
import { ChevronLeftIcon, ChevronRightIcon } from '@chakra-ui/icons';
import { useAuth } from '../../../../useAuth';

const columnHelper = createColumnHelper();

export default function RefundRequestsTable() {
  const [sorting, setSorting] = useState([]);
  const [data, setData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 10 });
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedRefundRequest, setSelectedRefundRequest] = useState(null);
  const [modalLoading, setModalLoading] = useState(false);
  const textColor = useColorModeValue('secondaryGray.900', 'white');
  const borderColor = useColorModeValue('gray.200', 'whiteAlpha.100');
  const toast = useToast();
  const { user } = useAuth();
  const userId = user?.id;

  useEffect(() => {
    const fetchRefundRequests = async () => {
      if (!userId) {
        setError('User not authenticated');
        setLoading(false);
        return;
      }
      setLoading(true);
      try {
        const [refundRequests, count] = await Promise.all([
          listRefundRequests({
            limit: pagination.pageSize,
            offset: pagination.pageIndex * pagination.pageSize,
            user_id: userId,
            search: searchTerm || undefined,
          }),
          getRefundRequestCount({ user_id: userId }),
        ]);
        setData(refundRequests.data || refundRequests);
        setTotalCount(count.count);
      } catch (err) {
        setError(err.response?.data?.detail || err.message || 'Failed to fetch refund requests');
        toast({
          title: 'Error',
          description: err.response?.data?.detail || err.message || 'Failed to fetch refund requests',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setLoading(false);
      }
    };
    fetchRefundRequests();
  }, [pagination.pageIndex, pagination.pageSize, userId, searchTerm, toast]);

  useEffect(() => {
    if (!searchTerm) {
      setFilteredData(data);
      return;
    }
    const lowerSearch = searchTerm.toLowerCase();
    const filtered = data.filter((row) =>
      [
        row.id?.toString(),
        row.payment_id?.toString(),
        row.reason,
        row.status,
        row.created_at,
      ].some((value) => value?.toString().toLowerCase().includes(lowerSearch))
    );
    setFilteredData(filtered);
  }, [data, searchTerm]);

  const handleView = async (refundRequestId) => {
    setModalLoading(true);
    setIsModalOpen(true);
    try {
      const response = await getRefundRequestDetails(refundRequestId);
      setSelectedRefundRequest(response);
    } catch (err) {
      toast({
        title: 'Error',
        description: err.response?.data?.detail || err.message || 'Failed to fetch refund request details',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      setIsModalOpen(false);
    } finally {
      setModalLoading(false);
    }
  };

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
    setPagination((old) => ({ ...old, pageIndex: 0 }));
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
    columnHelper.accessor('payment_id', {
      id: 'payment_id',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaDollarSign style={{ marginRight: '8px' }} />
          PAYMENT ID
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue()}</Text>,
    }),
    columnHelper.accessor('reason', {
      id: 'reason',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaComment style={{ marginRight: '8px' }} />
          REASON
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue() || 'N/A'}</Text>,
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
            info.getValue() === 'approved' ? 'green' :
            info.getValue() === 'rejected' ? 'red' :
            info.getValue() === 'pending' ? 'yellow' : 'gray'
          }
          variant="solid"
        >
          {info.getValue() || 'N/A'}
        </Badge>
      ),
    }),
    columnHelper.accessor('created_at', {
      id: 'created_at',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaClock style={{ marginRight: '8px' }} />
          CREATED AT
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
    setSelectedRefundRequest(null);
  };

  if (error) return <Text color="red.500">{error}</Text>;

  return (
    <>
      <Card flexDirection="column" w="100%" px="0px" overflowX={{ sm: 'scroll', lg: 'hidden' }}>
        <Flex px="25px" mb="8px" justifyContent="space-between" align="center">
          <Text color={textColor} fontSize="22px" mb="4px" fontWeight="700" lineHeight="100%">
            Refund Requests Table
          </Text>
          <Menu />
        </Flex>
        <Flex px="25px" mb="8px" justifyContent="space-between" align="center">
          <InputGroup maxW="300px">
            <InputLeftElement pointerEvents="none">
              <FaSearch color="gray.300" />
            </InputLeftElement>
            <Input
              type="text"
              placeholder="Search refund requests..."
              value={searchTerm}
              onChange={handleSearch}
            />
          </InputGroup>
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
        <Box overflowY="auto" maxH="500px">
          {loading ? (
            <Stack>
              {[...Array(pagination.pageSize)].map((_, i) => (
                <Skeleton key={i} height="40px" />
              ))}
            </Stack>
          ) : filteredData.length === 0 ? (
            <Text textAlign="center" py="4" color={textColor}>
              No refund requests found matching your search.
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
      </Card>
      <Modal isOpen={isModalOpen} onClose={closeModal} size="lg">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Refund Request Details</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            {modalLoading ? (
              <Stack>
                <Skeleton height="20px" />
                <Skeleton height="20px" />
                <Skeleton height="20px" />
              </Stack>
            ) : selectedRefundRequest ? (
              <VStack align="start" spacing={4}>
                <Text><strong>ID:</strong> {selectedRefundRequest.id}</Text>
                <Text><strong>Payment ID:</strong> {selectedRefundRequest.payment_id}</Text>
                <Text><strong>Reason:</strong> {selectedRefundRequest.reason || 'N/A'}</Text>
                <Text><strong>Status:</strong> {selectedRefundRequest.status || 'N/A'}</Text>
                <Text><strong>Created At:</strong> {selectedRefundRequest.created_at || 'N/A'}</Text>
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