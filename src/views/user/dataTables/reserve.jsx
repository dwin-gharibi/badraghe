import { Box, SimpleGrid } from "@chakra-ui/react";
import TicketWizard from "views/user/dataTables/components/Wizard";
import React from "react";

export default function TicketWizardPage() {
  return (
    <Box pt={{ base: "130px", md: "80px", xl: "80px" }}>
      <SimpleGrid mb="20px">
        <TicketWizard />
      </SimpleGrid>
    </Box>
  );
}