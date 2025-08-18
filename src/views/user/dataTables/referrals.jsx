import { Box, SimpleGrid } from "@chakra-ui/react";

import ReferralsTable from "views/user/dataTables/components/ReferralsTable";
import React from "react";

export default function ReferralsTablePage() {
  return (
    <Box pt={{ base: "130px", md: "80px", xl: "80px" }}>
      <SimpleGrid
        mb="20px"
      >
        <ReferralsTable />

      </SimpleGrid>
    </Box>
  );
}