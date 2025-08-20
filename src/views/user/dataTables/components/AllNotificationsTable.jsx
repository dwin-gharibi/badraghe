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
import { getUserNotifications, deleteNotification, getNotificationDetails, getUnreadNotificationCount } from 'services/api';
import { useToast } from '@chakra-ui/react';
import { FaSearch, FaEye, FaTrash, FaIdBadge, FaUser, FaComment, FaTag, FaCheckCircle, FaClock, FaCog } from 'react-icons/fa';
import { useAuth } from '../../../../useAuth';

const columnHelper = createColumnHelper();

export default function AllNotificationsTable() {
  const [sorting, setSorting] = useState([]);
  const [data, setData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [pageIndex, setPageIndex] = useState(0);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedNotification, setSelectedNotification] = useState(null);
  const [modalLoading, setModalLoading] = useState(false);
  const pageSize = 10;
  const textColor = useColorModeValue('secondaryGray.900', 'white');
  const borderColor = useColorModeValue('gray.200', 'whiteAlpha.100');
  const toast = useToast();
  const { user } = useAuth();
  const userId = user?.id;

  useEffect(() => {
    const fetchNotifications = async () => {
      if (!userId) {
        setError('User not authenticated');
        setLoading(false);
        return;
      }
      setLoading(true);
      try {
        let total = 0;
        try {
          const countResponse = await getUnreadNotificationCount();
          total = countResponse.total || countResponse.count || 0;
        } catch (countErr) {
          console.warn('Failed to fetch total count:', countErr);
        }

        const params = {
          skip: pageIndex * pageSize,
          limit: pageSize,
          user_id: userId,
        };
        const response = await getUserNotifications(params);
        const notifications = response.data || response;
        setData(notifications);
        if (total > 0) {
          setTotalCount(total);
        } else {
          setTotalCount(notifications.length === pageSize ? (pageIndex + 2) * pageSize : notifications.length);
        }
      } catch (err) {
        console.error('Full Error:', err);
        setError(err.response?.data?.detail || err.message || 'Failed to fetch notifications');
        toast({
          title: 'Error',
          description: err.response?.data?.detail || err.message || 'Failed to fetch notifications',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setLoading(false);
      }
    };
    fetchNotifications();
  }, [pageIndex, userId, toast]);

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
        row.message,
        row.notification_type,
        row.status,
        row.is_read?.toString(),
        row.created_at,
        row.updated_at,
        row.sent_at,
        row.user_email,
      ].some((value) => value?.toString().toLowerCase().includes(lowerSearch))
    );
    setFilteredData(filtered);
  }, [data, searchTerm]);

  const handleDelete = async (notificationId) => {
    try {
      await deleteNotification(notificationId);
      toast({
        title: 'Success',
        description: 'Notification deleted successfully',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      const params = {
        skip: pageIndex * pageSize,
        limit: pageSize,
        user_id: userId,
      };
      const response = await getUserNotifications(params);
      setData(response.data || response);
      let total = 0;
      try {
        const countResponse = await getUnreadNotificationCount();
        total = countResponse.total || countResponse.count || 0;
      } catch (countErr) {
        console.warn('Failed to fetch total count:', countErr);
      }
      if (total > 0) {
        setTotalCount(total);
      } else {
        setTotalCount(response.data.length === pageSize ? (pageIndex + 2) * pageSize : response.data.length);
      }
    } catch (err) {
      toast({
        title: 'Error',
        description: err.response?.data?.detail || err.message || 'Failed to delete notification',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const handleView = async (notificationId) => {
    setModalLoading(true);
    setIsModalOpen(true);
    try {
      const response = await getNotificationDetails(notificationId);
      setSelectedNotification(response);
    } catch (err) {
      toast({
        title: 'Error',
        description: err.response?.data?.detail || err.message || 'Failed to fetch notification details',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      setIsModalOpen(false);
    } finally {
      setModalLoading(false);
    }
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
    columnHelper.accessor('message', {
      id: 'message',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaComment style={{ marginRight: '8px' }} />
          MESSAGE
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue()}</Text>,
    }),
    columnHelper.accessor('notification_type', {
      id: 'notification_type',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaTag style={{ marginRight: '8px' }} />
          TYPE
        </Flex>
      ),
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue()}</Text>,
    }),
    columnHelper.accessor('is_read', {
      id: 'is_read',
      header: () => (
        <Flex align="center" justifyContent="space-between" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">
          <FaCheckCircle style={{ marginRight: '8px' }} />
          READ
        </Flex>
      ),
      cell: (info) => (
        <Badge colorScheme={info.getValue() ? 'green' : 'red'} variant="solid">
          {info.getValue() ? 'Yes' : 'No'}
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
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue()}</Text>,
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
    setSelectedNotification(null);
  };

  if (error) return <Text color="red.500">{error}</Text>;

  return (
    <>
      <Card flexDirection="column" w="100%" px="0px" overflowX={{ sm: 'scroll', lg: 'hidden' }}>
        <Flex px="25px" mb="8px" justifyContent="space-between" align="center">
          <Text color={textColor} fontSize="22px" mb="4px" fontWeight="700" lineHeight="100%">
            My Notifications
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
              placeholder="Search notifications..."
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
              No notifications found matching your search.
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
          <ModalHeader>Notification Details</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            {modalLoading ? (
              <Stack>
                <Skeleton height="20px" />
                <Skeleton height="20px" />
                <Skeleton height="20px" />
              </Stack>
            ) : selectedNotification ? (
              <VStack align="start" spacing={4}>
                <Text><strong>ID:</strong> {selectedNotification.id}</Text>
                <Text><strong>User ID:</strong> {selectedNotification.user_id}</Text>
                <Text><strong>User Email:</strong> {selectedNotification.user_email || 'N/A'}</Text>
                <Text><strong>Message:</strong> {selectedNotification.message}</Text>
                <Text><strong>Type:</strong> {selectedNotification.notification_type}</Text>
                <Text><strong>Status:</strong> {selectedNotification.status}</Text>
                <Text><strong>Read:</strong> {selectedNotification.is_read ? 'Yes' : 'No'}</Text>
                <Text><strong>Sent At:</strong> {selectedNotification.sent_at || 'N/A'}</Text>
                <Text><strong>Created At:</strong> {selectedNotification.created_at}</Text>
                <Text><strong>Updated At:</strong> {selectedNotification.updated_at}</Text>
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