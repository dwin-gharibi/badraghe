import { Box, SimpleGrid } from "@chakra-ui/react";
import TicketsTable from "views/user/dataTables/components/TicketsTable";
import DiscountsTable from "views/user/dataTables/components/DiscountsTable";
import ReservationsTable from "views/user/dataTables/components/ReservationsTable";
import NotificationsTable from "views/user/dataTables/components/NotificationsTable";
import AllNotificationsTable from "views/user/dataTables/components/AllNotificationsTable";
import PaymentsTable from "views/user/dataTables/components/PaymentsTable";
import RefundRequestsTable from "views/user/dataTables/components/RefundRequestsTable";
import SupportTicketsTable from "views/user/dataTables/components/SupportTicketsTable";
import ReviewsTable from "views/user/dataTables/components/ReviewsTable";
import React from "react";

export default function Settings() {
  return (
    <Box pt={{ base: "130px", md: "80px", xl: "80px" }}>
      <SimpleGrid
        mb="20px"
        columns={{ sm: 1, md: 2, lg: 3 }}
        spacing={{ base: "20px", xl: "20px" }}
      >
        <TicketsTable />
        <DiscountsTable />
        <ReservationsTable />
        <NotificationsTable />
        <AllNotificationsTable />
        <PaymentsTable />
        <RefundRequestsTable />
        <SupportTicketsTable />
        <ReviewsTable />
      </SimpleGrid>
    </Box>
  );
}