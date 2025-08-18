import React from 'react';
import { Flex, Button, IconButton, Text, useColorModeValue } from '@chakra-ui/react';
import { FaChevronLeft, FaChevronRight } from 'react-icons/fa';

const Pagination = ({ currentPage, totalCount, pageSize, onPageChange }) => {
  const totalPages = Math.ceil(totalCount / pageSize);
  const textColor = useColorModeValue('secondaryGray.900', 'white');

  const handlePageChange = (page) => {
    if (page >= 1 && page <= totalPages) {
      onPageChange(page);
    }
  };

  const getPageNumbers = () => {
    const pages = [];
    const maxPagesToShow = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxPagesToShow / 2));
    let endPage = Math.min(totalPages, startPage + maxPagesToShow - 1);

    if (endPage - startPage + 1 < maxPagesToShow) {
      startPage = Math.max(1, endPage - maxPagesToShow + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }
    return pages;
  };

  return (
    <Flex align="center" justify="center" gap={2}>
      <IconButton
        icon={<FaChevronLeft />}
        isDisabled={currentPage === 1}
        onClick={() => handlePageChange(currentPage - 1)}
        aria-label="Previous page"
        colorScheme="blue"
      />
      {getPageNumbers().map((page) => (
        <Button
          key={page}
          onClick={() => handlePageChange(page)}
          colorScheme={currentPage === page ? 'blue' : 'gray'}
          variant={currentPage === page ? 'solid' : 'outline'}
        >
          {page}
        </Button>
      ))}
      <IconButton
        icon={<FaChevronRight />}
        isDisabled={currentPage === totalPages}
        onClick={() => handlePageChange(currentPage + 1)}
        aria-label="Next page"
        colorScheme="blue"
      />
      <Text color={textColor} fontSize="sm">
        Page {currentPage} of {totalPages}
      </Text>
    </Flex>
  );
};

export default Pagination;