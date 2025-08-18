import { Box, SimpleGrid } from "@chakra-ui/react";
import TicketsTable from "views/user/dataTables/components/TicketsTable";
import React from "react";

export default function TicketsTablePage() {
  return (
    <Box pt={{ base: "130px", md: "80px", xl: "80px" }}>
      <SimpleGrid mb="20px">
        <TicketsTable />
      </SimpleGrid>
    </Box>
  );
}