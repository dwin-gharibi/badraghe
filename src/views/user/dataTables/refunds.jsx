import { Box, SimpleGrid } from "@chakra-ui/react";
import RefundRequestsTable from "views/user/dataTables/components/RefundRequestsTable";
import React from "react";

export default function RefundRequestsTablePage() {
  return (
    <Box pt={{ base: "130px", md: "80px", xl: "80px" }}>
      <SimpleGrid mb="20px">
        <RefundRequestsTable />
      </SimpleGrid>
    </Box>
  );
}