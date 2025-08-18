import { Box, SimpleGrid } from "@chakra-ui/react";
import AllPaymentsTable from "views/user/dataTables/components/AllPaymentsTable";
import React from "react";

export default function AllPaymentsTablePage() {
  return (
    <Box pt={{ base: "130px", md: "80px", xl: "80px" }}>
      <SimpleGrid
        mb="20px"
      >
        <AllPaymentsTable />
      </SimpleGrid>
    </Box>
  );
}