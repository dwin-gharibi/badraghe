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
  MdOutlineRocket,
  MdAirplaneTicket,
  MdGroup,
  MdNotifications,
  MdSupport,
  MdExitToApp
} from 'react-icons/md';

import PrivateRoute from "components/auth/PrivateRoute";
import NFTMarketplace from 'views/user/marketplace';
import Profile from 'views/user/profile';

import RefundRequestsTablePage from 'views/user/dataTables/refunds';
import ReviewsTablePage from 'views/user/dataTables/reviews';
import PaymentsTablePage from 'views/user/dataTables/payments';
import AllNotificationsTablePage from 'views/user/dataTables/notifications';
import Logout from 'Logout';
import TicketsTablePage from 'views/user/dataTables/tickets';
import SupportTicketsTablePage from 'views/user/dataTables/support_tickets';

import UsersTablePage from 'views/user/dataTables/users';

import DiscountsTablePage from 'views/user/dataTables/discounts';
import ReferralsTablePage from 'views/user/dataTables/referrals';
import ReservationsTablePage from 'views/user/dataTables/reservations';
import ServiceProvidersTablePage from 'views/user/dataTables/service_providers';
import TicketWizardPage from 'views/user/dataTables/reserve';
import SignInCentered from 'views/auth/signIn';
import SignUpCentered from 'views/auth/signup';
import OtpCentered from 'views/auth/otp';

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
    path: '/dashboard',
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
    name: 'Reservations',
    layout: '/user',
    icon: <Icon as={MdAirplaneTicket} width="20px" height="20px" mt="5px" color="inherit" />,
    path: '/reservations',
    component: (<PrivateRoute><ReservationsTablePage /></PrivateRoute>),
  },
  {
    name: 'Reserve a ticket',
    layout: '/user',
    icon: <Icon as={MdSupervisorAccount} width="20px" height="20px" mt="5px" color="inherit" />,
    path: '/reserve',
    component: (<PrivateRoute><TicketWizardPage /></PrivateRoute>),
  },
  {
    name: 'Tickets',
    layout: '/user',
    icon: <Icon as={MdOutlineRocket} width="20px" height="20px" mt="5px" color="inherit" />,
    path: '/tickets',
    component: (<PrivateRoute><TicketsTablePage /></PrivateRoute>),
  },
  {
    name: 'Refunds',
    layout: '/user',
    icon: <Icon as={MdCancelScheduleSend} width="20px" height="20px" mt="5px" color="inherit" />,
    path: '/refunds',
    component: (<PrivateRoute><RefundRequestsTablePage /></PrivateRoute>),
  },
  {
    name: 'Payments',
    layout: '/user',
    icon: <Icon as={MdPayments} width="20px" height="20px" mt="5px" color="inherit" />,
    path: '/payments',
    component: (<PrivateRoute><PaymentsTablePage /></PrivateRoute>),
  },
  {
    name: 'Reviews',
    layout: '/user',
    icon: <Icon as={MdOutlineStar} width="20px" height="20px" mt="5px" color="inherit" />,
    path: '/reviews',
    component: (<PrivateRoute><ReviewsTablePage /></PrivateRoute>),
  },
  {
    name: 'Notifications',
    layout: '/user',
    icon: <Icon as={MdNotifications} width="20px" height="20px" mt="5px" color="inherit" />,
    path: '/notifications',
    component: (<PrivateRoute><AllNotificationsTablePage /></PrivateRoute>),
  },
  {
    name: 'Support Tickets',
    layout: '/user',
    icon: <Icon as={MdSupport} width="20px" height="20px" mt="5px" color="inherit" />,
    path: '/support-tickets',
    component: (<PrivateRoute><SupportTicketsTablePage /></PrivateRoute>),
  },
  {
    name: 'Profile',
    layout: '/user',
    path: '/profile',
    icon: <Icon as={MdPerson} width="20px" height="20px" mt="5px" color="inherit" />,
    component: (<PrivateRoute><Profile /></PrivateRoute>),
  },
  {
    name: 'Discount Codes',
    layout: '/user',
    icon: <Icon as={MdDiscount} width="20px" height="20px" mt="5px" color="inherit" />,
    path: '/discounts',
    component: (<PrivateRoute><DiscountsTablePage /></PrivateRoute>),
  },
  {
    name: 'Referrals',
    layout: '/user',
    icon: <Icon as={MdGroup} width="20px" height="20px" mt="5px" color="inherit" />,
    path: '/referrals',
    component: (<PrivateRoute><ReferralsTablePage /></PrivateRoute>),
  },
  {
    name: 'Users',
    layout: '/user',
    icon: <Icon as={MdSupervisorAccount} width="20px" height="20px" mt="5px" color="inherit" />,
    path: '/users',
    component: (<PrivateRoute><UsersTablePage /></PrivateRoute>),
  },
  {
    name: 'Sign In',
    layout: '/auth',
    path: '/sign-in',
    icon: <Icon as={MdLock} width="20px" height="20px" mt="5px" color="inherit" />,
    component: <SignInCentered />,
  },
  {
    name: 'Sign Up',
    layout: '/auth',
    path: '/sign-up',
    icon: <Icon as={MdLock} width="20px" height="20px" mt="5px" color="inherit" />,
    component: <SignUpCentered />,
  },
  {
    name: 'Logout',
    layout: '/auth',
    path: '/logout',
    icon: <Icon as={MdExitToApp} width="20px" height="20px" mt="5px" color="inherit" />,
    component: <Logout />,
  },
  {
    name: 'Otp',
    layout: '/auth',
    path: '/otp',
    icon: <Icon as={MdLock} width="20px" height="20px" mt="5px" color="inherit" />,
    component: <OtpCentered />,
  },
];

export default routes;
