import { Box, SimpleGrid } from "@chakra-ui/react";
import UsersTable from "views/user/dataTables/components/UsersTable";

import React from "react";

export default function UsersTablePage() {
  return (
    <Box pt={{ base: "130px", md: "80px", xl: "80px" }}>
      <SimpleGrid
        mb="20px"
      >
        <UsersTable />

      </SimpleGrid>
    </Box>
  );
}