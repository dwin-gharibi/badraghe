import { Box, SimpleGrid } from "@chakra-ui/react";
import SupportTicketsTable from "views/user/dataTables/components/SupportTicketsTable";
import React from "react";

export default function SupportTicketsTablePage() {
  return (
    <Box pt={{ base: "130px", md: "80px", xl: "80px" }}>
      <SimpleGrid mb="20px">
        <SupportTicketsTable />
      </SimpleGrid>
    </Box>
  );
}