import { Box, SimpleGrid } from "@chakra-ui/react";
import ServiceProvidersTable from "views/user/dataTables/components/ServiceProvidersTable";

import React from "react";

export default function ServiceProvidersTablePage() {
  return (
    <Box pt={{ base: "130px", md: "80px", xl: "80px" }}>
      <SimpleGrid
        mb="20px"
      >
        <ServiceProvidersTable />

      </SimpleGrid>
    </Box>
  );
}