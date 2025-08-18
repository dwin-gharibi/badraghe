import { Box, SimpleGrid } from "@chakra-ui/react";
import AllNotificationsTable from "views/user/dataTables/components/AllNotificationsTable";
import React from "react";

export default function AllNotificationsTablePage() {
  return (
    <Box pt={{ base: "130px", md: "80px", xl: "80px" }}>
      <SimpleGrid
        mb="20px"
      >

        <AllNotificationsTable />

      </SimpleGrid>
    </Box>
  );
}