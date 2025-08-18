import { Box, SimpleGrid } from "@chakra-ui/react";
import PaymentsTable from "views/user/dataTables/components/PaymentsTable";
import React from "react";

export default function PaymentsTablePage() {
  return (
    <Box pt={{ base: "130px", md: "80px", xl: "80px" }}>
      <SimpleGrid
        mb="20px"
      >
        <PaymentsTable />
      </SimpleGrid>
    </Box>
  );
}