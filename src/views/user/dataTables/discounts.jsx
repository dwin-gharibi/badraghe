import { Box, SimpleGrid } from "@chakra-ui/react";
import DiscountsTable from "views/user/dataTables/components/DiscountsTable";
import React from "react";

export default function DiscountsTablePage() {
  return (
    <Box pt={{ base: "130px", md: "80px", xl: "80px" }}>
      <SimpleGrid
        mb="20px"
      >
        <DiscountsTable />
      </SimpleGrid>
    </Box>
  );
}