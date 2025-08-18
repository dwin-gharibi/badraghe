import { Box, SimpleGrid } from "@chakra-ui/react";
import ReviewsTable from "views/user/dataTables/components/ReviewsTable";
import React from "react";

export default function ReviewsTablePage() {
  return (
    <Box pt={{ base: "130px", md: "80px", xl: "80px" }}>
      <SimpleGrid mb="20px">
        <ReviewsTable />
      </SimpleGrid>
    </Box>
  );
}