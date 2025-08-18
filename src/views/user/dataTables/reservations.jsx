import { Box, SimpleGrid } from "@chakra-ui/react";
import ReservationsTable from "views/user/dataTables/components/ReservationsTable";

import React from "react";

export default function ReservationsTablePage() {
  return (
    <Box pt={{ base: "130px", md: "80px", xl: "80px" }}>
      <SimpleGrid
        mb="20px"
      >
        <ReservationsTable />

      </SimpleGrid>
    </Box>
  );
}