import React from 'react';

import { Icon } from '@chakra-ui/react';
import {
  MdBarChart,
  MdPerson,
  MdHome,
  MdLock,
  MdDashboard,
  MdDiscount,
  MdDesignServices,
  MdSupervisorAccount,
  MdCancelScheduleSend,
  MdOutlineStar,
  MdPayments,
  MdOutlineShoppingCart,
  MdAirplaneTicket,
  MdGroup,
} from 'react-icons/md';

import PrivateRoute from "components/auth/PrivateRoute";
import MainDashboard from 'views/user/default';
import NFTMarketplace from 'views/user/marketplace';
import Profile from 'views/user/profile';
import DataTables from 'views/user/dataTables';

import RefundRequestsTablePage from 'views/user/dataTables/refunds';
import ReviewsTablePage from 'views/user/dataTables/reviews';
import PaymentsTablePage from 'views/user/dataTables/payments';
import AllNotificationsTablePage from 'views/user/dataTables/notifications';

import TicketsTablePage from 'views/user/dataTables/tickets';
import SupportTicketsTablePage from 'views/user/dataTables/support_tickets';

import UsersTablePage from 'views/user/dataTables/users';

import DiscountsTablePage from 'views/user/dataTables/discounts';
import ReferralsTablePage from 'views/user/dataTables/referrals';
import ReservationsTablePage from 'views/user/dataTables/reservations';
import ServiceProvidersTablePage from 'views/user/dataTables/service_providers';
import TicketWizardPage from 'views/user/dataTables/reserve';


import RTL from 'views/user/rtl';

import SignInCentered from 'views/auth/signIn';
import SignUpCentered from 'views/auth/signup';
import TicketWizard from 'views/auth/reserve';

import OtpCentered from 'views/auth/otp';
import BillingPage from 'views/auth/billing';

import BaragheLanding from 'views/main/landing';

const routes = [
  {
    name: 'Landing',
    layout: '',
    path: '/',
    component: <BaragheLanding />,
  },
  {
    name: 'Dashboard',
    layout: '/user',
    path: '/nft-marketplace',
    icon: (
      <Icon
        as={MdDashboard}
        width="20px"
        height="20px"
        color="inherit"
      />
    ),
    component: (
    <PrivateRoute><NFTMarketplace /></PrivateRoute>),
    secondary: true,
  },
  {
    name: 'Discount Codes',
    layout: '/user',
    icon: <Icon as={MdDiscount} width="20px" height="20px" color="inherit" />,
    path: '/discounts',
    component: (<PrivateRoute><DiscountsTablePage /></PrivateRoute>),
  },
  {
    name: 'Referrals',
    layout: '/user',
    icon: <Icon as={MdGroup} width="20px" height="20px" color="inherit" />,
    path: '/referrals',
    component: (<PrivateRoute><ReferralsTablePage /></PrivateRoute>),
  },
  {
    name: 'Reservations',
    layout: '/user',
    icon: <Icon as={MdAirplaneTicket} width="20px" height="20px" color="inherit" />,
    path: '/reservations',
    component: (<PrivateRoute><ReservationsTablePage /></PrivateRoute>),
  },
  {
    name: 'Service Providers',
    layout: '/user',
    icon: <Icon as={MdDesignServices} width="20px" height="20px" color="inherit" />,
    path: '/service-providers',
    component: (<PrivateRoute><ServiceProvidersTablePage /></PrivateRoute>),
  },

  {
    name: 'Users',
    layout: '/user',
    icon: <Icon as={MdSupervisorAccount} width="20px" height="20px" color="inherit" />,
    path: '/users',
    component: (<PrivateRoute><UsersTablePage /></PrivateRoute>),
  },
  {
    name: 'Reserve a ticket',
    layout: '/user',
    icon: <Icon as={MdSupervisorAccount} width="20px" height="20px" color="inherit" />,
    path: '/reserve',
    component: (<PrivateRoute><TicketWizardPage /></PrivateRoute>),
  },

  {
    name: 'Refunds',
    layout: '/user',
    icon: <Icon as={MdCancelScheduleSend} width="20px" height="20px" color="inherit" />,
    path: '/refunds',
    component: (<PrivateRoute><RefundRequestsTablePage /></PrivateRoute>),
  },
  {
    name: 'Payments',
    layout: '/user',
    icon: <Icon as={MdPayments} width="20px" height="20px" color="inherit" />,
    path: '/payments',
    component: (<PrivateRoute><PaymentsTablePage /></PrivateRoute>),
  },
  {
    name: 'Reviews',
    layout: '/user',
    icon: <Icon as={MdOutlineStar} width="20px" height="20px" color="inherit" />,
    path: '/reviews',
    component: (<PrivateRoute><ReviewsTablePage /></PrivateRoute>),
  },
  {
    name: 'Data Tables',
    layout: '/user',
    icon: <Icon as={MdBarChart} width="20px" height="20px" color="inherit" />,
    path: '/notifications',
    component: (<PrivateRoute><AllNotificationsTablePage /></PrivateRoute>),
  },
  {
    name: 'Data Tables',
    layout: '/user',
    icon: <Icon as={MdBarChart} width="20px" height="20px" color="inherit" />,
    path: '/support-tickets',
    component: (<PrivateRoute><SupportTicketsTablePage /></PrivateRoute>),
  },
  {
    name: 'Data Tables',
    layout: '/user',
    icon: <Icon as={MdBarChart} width="20px" height="20px" color="inherit" />,
    path: '/tickets',
    component: (<PrivateRoute><TicketsTablePage /></PrivateRoute>),
  },
  {
    name: 'Profile',
    layout: '/user',
    path: '/profile',
    icon: <Icon as={MdPerson} width="20px" height="20px" color="inherit" />,
    component: (<PrivateRoute><Profile /></PrivateRoute>),
  },
  {
    name: 'Reserve',
    layout: '/auth',
    path: '/reserve',
    icon: <Icon as={MdLock} width="20px" height="20px" color="inherit" />,
    component: <TicketWizard />,
  },
  {
    name: 'Billing',
    layout: '/auth',
    path: '/billing',
    icon: <Icon as={MdLock} width="20px" height="20px" color="inherit" />,
    component: <BillingPage />,
  },
  {
    name: 'Sign In',
    layout: '/auth',
    path: '/sign-in',
    icon: <Icon as={MdLock} width="20px" height="20px" color="inherit" />,
    component: <SignInCentered />,
  },
  {
    name: 'Sign Up',
    layout: '/auth',
    path: '/sign-up',
    icon: <Icon as={MdLock} width="20px" height="20px" color="inherit" />,
    component: <SignUpCentered />,
  },
  {
    name: 'Otp',
    layout: '/auth',
    path: '/otp',
    icon: <Icon as={MdLock} width="20px" height="20px" color="inherit" />,
    component: <OtpCentered />,
  },
  {
    name: 'RTL user',
    layout: '/rtl',
    path: '/rtl-default',
    icon: <Icon as={MdHome} width="20px" height="20px" color="inherit" />,
    component: <RTL />,
  },
];

export default routes;
