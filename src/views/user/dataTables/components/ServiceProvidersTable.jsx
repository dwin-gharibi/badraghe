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
} from '@chakra-ui/react';
import { createColumnHelper, flexRender, getCoreRowModel, getSortedRowModel, useReactTable } from '@tanstack/react-table';
import Card from 'components/card/Card';
import Menu from 'components/menu/MainMenu';
import Pagination from 'components/Pagination';
import { getServiceProviders, deleteServiceProvider } from 'services/api';
import { useToast } from '@chakra-ui/react';
import { FaSearch, FaEye, FaEdit, FaTrash } from 'react-icons/fa';

const columnHelper = createColumnHelper();

export default function ServiceProvidersTable() {
  const [sorting, setSorting] = useState([]);
  const [data, setData] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [pageIndex, setPageIndex] = useState(0);
  const pageSize = 10;
  const textColor = useColorModeValue('secondaryGray.900', 'white');
  const borderColor = useColorModeValue('gray.200', 'whiteAlpha.100');
  const toast = useToast();

  useEffect(() => {
    const fetchServiceProviders = async () => {
      setLoading(true);
      try {
        const params = { skip: pageIndex * pageSize, limit: pageSize };
        if (searchTerm) params.name = searchTerm;
        const response = await getServiceProviders(params);
        setData(response.data || response);
        setTotalCount(response.total || response.length);
      } catch (err) {
        console.error('Full Error:', err);
        setError(err.response?.data?.detail || err.message || 'Failed to fetch service providers');
        toast({
          title: 'Error',
          description: err.response?.data?.detail || err.message || 'Failed to fetch service providers',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setLoading(false);
      }
    };
    fetchServiceProviders();
  }, [pageIndex, searchTerm, toast]);

  const handleDelete = async (providerId) => {
    try {
      await deleteServiceProvider(providerId);
      toast({
        title: 'Success',
        description: 'Service provider deleted successfully',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      const params = { skip: pageIndex * pageSize, limit: pageSize };
      if (searchTerm) params.name = searchTerm;
      const response = await getServiceProviders(params);
      setData(response.data || response);
      setTotalCount(response.total || response.length);
    } catch (err) {
      toast({
        title: 'Error',
        description: err.response?.data?.detail || err.message || 'Failed to delete service provider',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const columns = [
    columnHelper.accessor('id', {
      id: 'id',
      header: () => <Text justifyContent="space-between" align="center" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">ID</Text>,
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue()}</Text>,
    }),
    columnHelper.accessor('name', {
      id: 'name',
      header: () => <Text justifyContent="space-between" align="center" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">NAME</Text>,
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue()}</Text>,
    }),
    columnHelper.accessor('status', {
      id: 'status',
      header: () => <Text justifyContent="space-between" align="center" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">STATUS</Text>,
      cell: (info) => (
        <Badge
          colorScheme={info.getValue() === 'active' ? 'green' : 'red'}
          variant="solid"
        >
          {info.getValue()}
        </Badge>
      ),
    }),
    columnHelper.accessor('created_at', {
      id: 'created_at',
      header: () => <Text justifyContent="space-between" align="center" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">CREATED AT</Text>,
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue()}</Text>,
    }),
    columnHelper.accessor('updated_at', {
      id: 'updated_at',
      header: () => <Text justifyContent="space-between" align="center" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">UPDATED AT</Text>,
      cell: (info) => <Text color={textColor} fontSize="sm" fontWeight="700">{info.getValue() || 'N/A'}</Text>,
    }),
    columnHelper.display({
      id: 'actions',
      header: () => <Text justifyContent="space-between" align="center" fontSize={{ sm: '10px', lg: '12px' }} color="gray.400">ACTIONS</Text>,
      cell: (info) => (
        <Stack direction="row" spacing={2}>
          <IconButton
            icon={<FaEye />}
            colorScheme="blue"
            aria-label="View"
            onClick={() => console.log('View provider', info.row.original.id)}
          />
          <IconButton
            icon={<FaEdit />}
            colorScheme="yellow"
            aria-label="Edit"
            onClick={() => console.log('Edit provider', info.row.original.id)}
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
    data,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    debugTable: true,
  });

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
    setPageIndex(0);
  };

  if (error) return <Text color="red.500">{error}</Text>;

  return (
    <Card flexDirection="column" w="100%" px="0px" overflowX={{ sm: 'scroll', lg: 'hidden' }}>
      <Flex px="25px" mb="8px" justifyContent="space-between" align="center">
        <Text color={textColor} fontSize="22px" mb="4px" fontWeight="700" lineHeight="100%">
          Service Providers Table
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
            placeholder="Search by name"
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
  );
}