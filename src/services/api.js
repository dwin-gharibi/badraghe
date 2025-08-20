import axios from 'axios';

const api = axios.create({
  baseURL: 'https://api1.badraghe.dwin.codes',
  timeout: 600000,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const sendOtp = async (phoneOrEmail) => {
  try {
    const response = await api.post('/send-otp', { phone_or_email: phoneOrEmail });
    return response.data;
  } catch (error) {
    console.error('Send OTP Error:', error);
    throw error.response?.data?.detail || 'Failed to send OTP';
  }
};

export const verifyOtp = async (phoneOrEmail, otpCode) => {
  try {
    const response = await api.post('/verify-otp', { phone_or_email: phoneOrEmail, otp_code: otpCode });
    const { token } = response.data;
    if (token) {
      localStorage.setItem('authToken', token);
    }
    return response.data;
  } catch (error) {
    console.error('Verify OTP Error:', error);
    throw error.response?.data?.detail || 'Failed to verify OTP';
  }
};

export const signup = async (data) => {
  try {
    const response = await api.post('/signup', data);
    return response.data;
  } catch (error) {
    console.error('Signup Error:', error);
    throw error.response?.data?.detail || 'Failed to sign up';
  }
};

export const login = async (username, password) => {
  try {
    const response = await api.post(
      '/token',
      { username, password, grant_type: 'password' },
      { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
    );
    const { access_token } = response.data;
    if (access_token) {
      localStorage.setItem('authToken', access_token);
    }
    return response.data;
  } catch (error) {
    console.error('Login Error:', error);
    throw error.response?.data?.detail || 'Failed to login';
  }
};

export const recommendTickets = async ({ from_city = null, to_city = null, user_pref = '' }) => {
  try {
    const response = await api.get('/ai/recommend-tickets', { params: { from_city, to_city, user_pref } });
    return response.data;
  } catch (error) {
    console.error('Recommend Tickets Error:', error);
    throw error.response?.data?.detail || 'Failed to recommend tickets';
  }
};

export const explainTrainDetails = async (ticketId) => {
  try {
    const response = await api.get('/ai/train-details', { params: { ticket_id: ticketId } });
    return response.data;
  } catch (error) {
    console.error('Explain Train Details Error:', error);
    throw error.response?.data?.detail || 'Failed to explain train details';
  }
};

export const explainBusDetails = async (ticketId) => {
  try {
    const response = await api.get('/ai/bus-details', { params: { ticket_id: ticketId } });
    return response.data;
  } catch (error) {
    console.error('Explain Bus Details Error:', error);
    throw error.response?.data?.detail || 'Failed to explain bus details';
  }
};

export const explainFlightDetails = async (ticketId) => {
  try {
    const response = await api.get('/ai/flight-details', { params: { ticket_id: ticketId } });
    return response.data;
  } catch (error) {
    console.error('Explain Flight Details Error:', error);
    throw error.response?.data?.detail || 'Failed to explain flight details';
  }
};

export const explainBusFeatures = async (ticketId) => {
  try {
    const response = await api.get('/ai/bus-features', { params: { ticket_id: ticketId } });
    return response.data;
  } catch (error) {
    console.error('Explain Bus Features Error:', error);
    throw error.response?.data?.detail || 'Failed to explain bus features';
  }
};

export const getUserProfile = async () => {
  try {
    const response = await api.get('/users/profile');
    return response.data;
  } catch (error) {
    console.error('Get Profile Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch profile';
  }
};

export const updateUserProfile = async (data) => {
  try {
    const response = await api.put('/users/profile', data);
    return response.data;
  } catch (error) {
    console.error('Update Profile Error:', error);
    throw error.response?.data?.detail || 'Failed to update profile';
  }
};

export const getUsers = async ({ skip = 0, limit = 100 } = {}) => {
  try {
    const response = await api.get('/users/', { params: { skip, limit } });
    return response.data;
  } catch (error) {
    console.error('Get Users Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch users';
  }
};

export const getUser = async (userId) => {
  try {
    const response = await api.get(`/users/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Get User Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch user';
  }
};

export const updateUser = async (userId, data) => {
  try {
    const response = await api.put(`/users/${userId}`, data);
    return response.data;
  } catch (error) {
    console.error('Update User Error:', error);
    throw error.response?.data?.detail || 'Failed to update user';
  }
};

export const deleteUser = async (userId) => {
  try {
    const response = await api.delete(`/users/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Delete User Error:', error);
    throw error.response?.data?.detail || 'Failed to delete user';
  }
};

export const updateUserStatus = async (userId, userStatus) => {
  try {
    const response = await api.patch(`/users/${userId}/status`, null, {
      params: { user_status: userStatus },
    });
    return response.data;
  } catch (error) {
    console.error('Update User Status Error:', error);
    throw error.response?.data?.detail || 'Failed to update user status';
  }
};

export const updateUserBalance = async (userId, userBalance) => {
  try {
    const response = await api.patch(`/users/${userId}/balance`, null, {
      params: { user_balance: userBalance },
    });
    return response.data;
  } catch (error) {
    console.error('Update User Balance Error:', error);
    throw error.response?.data?.detail || 'Failed to update user balance';
  }
};

export const getUserBalance = async (userId) => {
  try {
    const response = await api.get(`/users/${userId}/balance`);
    return response.data;
  } catch (error) {
    console.error('Get User Balance Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch user balance';
  }
};

export const getUserRoles = async (userId) => {
  try {
    const response = await api.get(`/users/${userId}/roles`);
    return response.data;
  } catch (error) {
    console.error('Get User Roles Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch user roles';
  }
};

export const getUserPermissions = async (userId) => {
  try {
    const response = await api.get(`/users/${userId}/permissions`);
    return response.data;
  } catch (error) {
    console.error('Get User Permissions Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch user permissions';
  }
};

export const getCities = async () => {
  try {
    const response = await api.get('/cities/');
    return response.data;
  } catch (error) {
    console.error('Get Cities Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch cities';
  }
};

export const searchDepartureCities = async (query) => {
  try {
    const response = await api.get('/cities/departure', { params: { q: query } });
    return response.data;
  } catch (error) {
    console.error('Search Departure Cities Error:', error);
    throw error.response?.data?.detail || 'Failed to search departure cities';
  }
};

export const searchArrivalCities = async (query) => {
  try {
    const response = await api.get('/cities/arrival', { params: { q: query } });
    return response.data;
  } catch (error) {
    console.error('Search Arrival Cities Error:', error);
    throw error.response?.data?.detail || 'Failed to search arrival cities';
  }
};

export const searchTickets = async ({
  departure_city = null,
  arrival_city = null,
  travel_date = null,
  transport_type = null,
  price_min = null,
  price_max = null,
  company_name = null,
  departure_time = null,
  class_type = null,
  skip = 0,
  limit = 100,
} = {}) => {
  try {
    const response = await api.get('/tickets/search', {
      params: {
        departure_city,
        arrival_city,
        travel_date,
        transport_type,
        price_min,
        price_max,
        company_name,
        departure_time,
        class_type,
        skip,
        limit,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Search Tickets Error:', error);
    throw error.response?.data?.detail || 'Failed to search tickets';
  }
};

export const getTicketStats = async ({ transport_type = null, class_type = null } = {}) => {
  try {
    const response = await api.get('/tickets/stats', { params: { transport_type, class_type } });
    return response.data;
  } catch (error) {
    console.error('Get Ticket Stats Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch ticket stats';
  }
};

export const createTicket = async (data) => {
  try {
    const response = await api.post('/tickets/', data);
    return response.data;
  } catch (error) {
    console.error('Create Ticket Error:', error);
    throw error.response?.data?.detail || 'Failed to create ticket';
  }
};

export const getTicket = async (ticketId) => {
  try {
    const response = await api.get(`/tickets/${ticketId}`);
    return response.data;
  } catch (error) {
    console.error('Get Ticket Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch ticket';
  }
};

export const checkTicketExists = async (ticketId) => {
  try {
    const response = await api.head(`/tickets/${ticketId}`);
    return response.status === 200;
  } catch (error) {
    console.error('Check Ticket Exists Error:', error);
    throw error.response?.data?.detail || 'Failed to check ticket existence';
  }
};

export const updateTicket = async (ticketId, data) => {
  try {
    const response = await api.put(`/tickets/${ticketId}`, data);
    return response.data;
  } catch (error) {
    console.error('Update Ticket Error:', error);
    throw error.response?.data?.detail || 'Failed to update ticket';
  }
};

export const deleteTicket = async (ticketId) => {
  try {
    const response = await api.delete(`/tickets/${ticketId}`);
    return response.data;
  } catch (error) {
    console.error('Delete Ticket Error:', error);
    throw error.response?.data?.detail || 'Failed to delete ticket';
  }
};

export const addTrainDetails = async (ticketId, data) => {
  try {
    const response = await api.post(`/tickets/${ticketId}/train-details`, data);
    return response.data;
  } catch (error) {
    console.error('Add Train Details Error:', error);
    throw error.response?.data?.detail || 'Failed to add train details';
  }
};

export const addBusDetails = async (ticketId, data) => {
  try {
    const response = await api.post(`/tickets/${ticketId}/bus-details`, data);
    return response.data;
  } catch (error) {
    console.error('Add Bus Details Error:', error);
    throw error.response?.data?.detail || 'Failed to add bus details';
  }
};

export const addFlightDetails = async (ticketId, data) => {
  try {
    const response = await api.post(`/tickets/${ticketId}/flight-details`, data);
    return response.data;
  } catch (error) {
    console.error('Add Flight Details Error:', error);
    throw error.response?.data?.detail || 'Failed to add flight details';
  }
};

export const addFeatureToTicket = async (ticketId, featureName) => {
  try {
    const response = await api.post(`/tickets/${ticketId}/features`, null, {
      params: { feature_name: featureName },
    });
    return response.data;
  } catch (error) {
    console.error('Add Feature to Ticket Error:', error);
    throw error.response?.data?.detail || 'Failed to add feature to ticket';
  }
};

export const getReservationStats = async ({ transport_type = null, start_date = null, end_date = null } = {}) => {
  try {
    const response = await api.get('/reservations/stats', { params: { transport_type, start_date, end_date } });
    return response.data;
  } catch (error) {
    console.error('Get Reservation Stats Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch reservation stats';
  }
};

export const createReservation = async (data) => {
  try {
    const response = await api.post('/reservations/', data);
    return response.data;
  } catch (error) {
    console.error('Create Reservation Error:', error);
    throw error.response?.data?.detail || 'Failed to create reservation';
  }
};

export const getReservation = async (reservationId) => {
  try {
    const response = await api.get(`/reservations/${reservationId}`);
    return response.data;
  } catch (error) {
    console.error('Get Reservation Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch reservation';
  }
};

export const checkReservationExists = async (reservationId) => {
  try {
    const response = await api.head(`/reservations/${reservationId}`);
    return response.status === 200;
  } catch (error) {
    console.error('Check Reservation Exists Error:', error);
    throw error.response?.data?.detail || 'Failed to check reservation existence';
  }
};

export const updateReservation = async (reservationId, data) => {
  try {
    const response = await api.put(`/reservations/${reservationId}`, data);
    return response.data;
  } catch (error) {
    console.error('Update Reservation Error:', error);
    throw error.response?.data?.detail || 'Failed to update reservation';
  }
};

export const deleteReservation = async (reservationId) => {
  try {
    const response = await api.delete(`/reservations/${reservationId}`);
    return response.data;
  } catch (error) {
    console.error('Delete Reservation Error:', error);
    throw error.response?.data?.detail || 'Failed to delete reservation';
  }
};

export const payForReservation = async (reservationId, paymentData) => {
  try {
    const response = await api.post(
      `/reservations/${reservationId}/pay`,
      {
        payment_method_id: paymentData.payment_method_id,
        amount: paymentData.amount,
        currency: paymentData.currency,
      }
    );
    return response.data;
  } catch (error) {
    console.error('Pay for Reservation Error:', error);
    throw error.response?.data?.detail || 'Failed to pay for reservation';
  }
};

export const verifyPayment = async (reservationId, { Authority, Status }) => {
  try {
    const response = await api.get(`/reservations/${reservationId}/verify-payment`, { params: { Authority, Status } });
    return response.data;
  } catch (error) {
    console.error('Verify Payment Error:', error);
    throw error.response?.data?.detail || 'Failed to verify payment';
  }
};

export const getUserReservationHistory = async (userId, {
  reservation_status = null,
  transport_type = null,
  start_date = null,
  end_date = null,
  skip = 0,
  limit = 100,
} = {}) => {
  try {
    const response = await api.get(`/reservations/user/${userId}/history`, {
      params: { reservation_status, transport_type, start_date, end_date, skip, limit },
    });
    return response.data;
  } catch (error) {
    console.error('Get User Reservation History Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch reservation history';
  }
};

export const getCancellationPenalty = async (reservationId) => {
  try {
    const response = await api.get(`/reservations/penalty/${reservationId}`);
    return response.data;
  } catch (error) {
    console.error('Get Cancellation Penalty Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch cancellation penalty';
  }
};

export const cancelReservation = async (reservationId, userId, cancellationReason) => {
  try {
    const response = await api.post(`/reservations/cancel/${reservationId}/`, null, {
      params: { user_id: userId, cancellation_reason: cancellationReason },
    });
    return response.data;
  } catch (error) {
    console.error('Cancel Reservation Error:', error);
    throw error.response?.data?.detail || 'Failed to cancel reservation';
  }
};

export const createDiscount = async (data) => {
  try {
    const response = await api.post('/discounts/', data);
    return response.data;
  } catch (error) {
    console.error('Create Discount Error:', error);
    throw error.response?.data?.detail || 'Failed to create discount';
  }
};

export const getDiscounts = async ({ active_only = true, code = null, discount_type = null, skip = 0, limit = 100 } = {}) => {
  try {
    const response = await api.get('/discounts/', { params: { active_only, code, discount_type, skip, limit } });
    return response.data;
  } catch (error) {
    console.error('Get Discounts Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch discounts';
  }
};

export const getDiscount = async (discountId) => {
  try {
    const response = await api.get(`/discounts/${discountId}`);
    return response.data;
  } catch (error) {
    console.error('Get Discount Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch discount';
  }
};

export const updateDiscount = async (discountId, data) => {
  try {
    const response = await api.put(`/discounts/${discountId}`, data);
    return response.data;
  } catch (error) {
    console.error('Update Discount Error:', error);
    throw error.response?.data?.detail || 'Failed to update discount';
  }
};

export const partialUpdateDiscount = async (discountId, data) => {
  try {
    const response = await api.patch(`/discounts/${discountId}`, data);
    return response.data;
  } catch (error) {
    console.error('Partial Update Discount Error:', error);
    throw error.response?.data?.detail || 'Failed to partially update discount';
  }
};

export const deleteDiscount = async (discountId) => {
  try {
    const response = await api.delete(`/discounts/${discountId}`);
    return response.data;
  } catch (error) {
    console.error('Delete Discount Error:', error);
    throw error.response?.data?.detail || 'Failed to delete discount';
  }
};

export const applyDiscountToTicket = async (ticketId, discountId) => {
  try {
    const response = await api.post('/discounts/apply-to-ticket', null, {
      params: { ticket_id: ticketId, discount_id: discountId },
    });
    return response.data;
  } catch (error) {
    console.error('Apply Discount to Ticket Error:', error);
    throw error.response?.data?.detail || 'Failed to apply discount';
  }
};

export const removeDiscountFromTicket = async (ticketId, discountId) => {
  try {
    const response = await api.delete('/discounts/remove-from-ticket', {
      params: { ticket_id: ticketId, discount_id: discountId },
    });
    return response.data;
  } catch (error) {
    console.error('Remove Discount from Ticket Error:', error);
    throw error.response?.data?.detail || 'Failed to remove discount';
  }
};

export const getTicketDiscounts = async (ticketId, { skip = 0, limit = 100 } = {}) => {
  try {
    const response = await api.get(`/discounts/ticket/${ticketId}`, { params: { skip, limit } });
    return response.data;
  } catch (error) {
    console.error('Get Ticket Discounts Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch ticket discounts';
  }
};

export const getUserLoyalty = async (userId) => {
  try {
    const response = await api.get(`/discounts/user-loyalty/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Get User Loyalty Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch user loyalty';
  }
};

export const addLoyaltyPoints = async (userId, data) => {
  try {
    const response = await api.post(`/discounts/user-loyalty/${userId}/add-points`, data);
    return response.data;
  } catch (error) {
    console.error('Add Loyalty Points Error:', error);
    throw error.response?.data?.detail || 'Failed to add loyalty points';
  }
};

export const redeemLoyaltyPoints = async (userId, data) => {
  try {
    const response = await api.post(`/discounts/user-loyalty/${userId}/redeem`, data);
    return response.data;
  } catch (error) {
    console.error('Redeem Loyalty Points Error:', error);
    throw error.response?.data?.detail || 'Failed to redeem loyalty points';
  }
};

export const getAllFeatures = async () => {
  try {
    const response = await api.get('/features/');
    return response.data;
  } catch (error) {
    console.error('Get All Features Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch features';
  }
};

export const createFeature = async (data) => {
  try {
    const response = await api.post('/features/', data);
    return response.data;
  } catch (error) {
    console.error('Create Feature Error:', error);
    throw error.response?.data?.detail || 'Failed to create feature';
  }
};

export const assignFeatureToTrain = async (trainId, featureId) => {
  try {
    const response = await api.post('/features/assign-to-train', null, {
      params: { train_id: trainId, feature_id: featureId },
    });
    return response.data;
  } catch (error) {
    console.error('Assign Feature to Train Error:', error);
    throw error.response?.data?.detail || 'Failed to assign feature to train';
  }
};

export const assignFeatureToFlight = async (flightId, featureId) => {
  try {
    const response = await api.post('/features/assign-to-flight', null, {
      params: { train_id: flightId, feature_id: featureId },
    });
    return response.data;
  } catch (error) {
    console.error('Assign Feature to Flight Error:', error);
    throw error.response?.data?.detail || 'Failed to assign feature to flight';
  }
};

export const assignFeatureToBus = async (busId, featureId) => {
  try {
    const response = await api.post('/features/assign-to-bus', null, {
      params: { train_id: busId, feature_id: featureId },
    });
    return response.data;
  } catch (error) {
    console.error('Assign Feature to Bus Error:', error);
    throw error.response?.data?.detail || 'Failed to assign feature to bus';
  }
};

export const getFeature = async (featureId) => {
  try {
    const response = await api.get(`/features/${featureId}`);
    return response.data;
  } catch (error) {
    console.error('Get Feature Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch feature';
  }
};

export const updateFeature = async (featureId, data) => {
  try {
    const response = await api.patch(`/features/${featureId}`, data);
    return response.data;
  } catch (error) {
    console.error('Update Feature Error:', error);
    throw error.response?.data?.detail || 'Failed to update feature';
  }
};

export const deleteFeature = async (featureId) => {
  try {
    const response = await api.delete(`/features/${featureId}`);
    return response.data;
  } catch (error) {
    console.error('Delete Feature Error:', error);
    throw error.response?.data?.detail || 'Failed to delete feature';
  }
};

export const getUnreadNotificationCount = async () => {
  try {
    const response = await api.get('/notifications/unread-count');
    return response.data;
  } catch (error) {
    console.error('Get Unread Notification Count Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch unread notification count';
  }
};

export const getNotificationStats = async ({ user_id = null } = {}) => {
  try {
    const response = await api.get('/notifications/stats', { params: { user_id } });
    return response.data;
  } catch (error) {
    console.error('Get Notification Stats Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch notification stats';
  }
};

export const getUserNotifications = async ({
  unread_only = false,
  status_filter = null,
  type_filter = null,
  start_date = null,
  end_date = null,
  skip = 0,
  limit = 100,
} = {}) => {
  try {
    const response = await api.get('/notifications/', {
      params: { unread_only, status_filter, type_filter, start_date, end_date, skip, limit },
    });
    return response.data;
  } catch (error) {
    console.error('Get User Notifications Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch notifications';
  }
};

export const getAllNotifications = async ({
  user_id = null,
  status_filter = null,
  type_filter = null,
  is_read = null,
  start_date = null,
  end_date = null,
  skip = 0,
  limit = 100,
} = {}) => {
  try {
    const response = await api.get('/notifications/all', {
      params: { user_id, status_filter, type_filter, is_read, start_date, end_date, skip, limit },
    });
    return response.data;
  } catch (error) {
    console.error('Get All Notifications Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch all notifications';
  }
};

export const createNotification = async (data) => {
  try {
    const response = await api.post('/notifications/', data);
    return response.data;
  } catch (error) {
    console.error('Create Notification Error:', error);
    throw error.response?.data?.detail || 'Failed to create notification';
  }
};

export const createBatchNotifications = async (userIds, message, notificationType = 'system') => {
  try {
    const response = await api.post('/notifications/batch', userIds, {
      params: { message, notification_type: notificationType },
    });
    return response.data;
  } catch (error) {
    console.error('Create Batch Notifications Error:', error);
    throw error.response?.data?.detail || 'Failed to create batch notifications';
  }
};

export const markMultipleNotificationsAsRead = async (notificationIds) => {
  try {
    const response = await api.patch('/notifications/batch/read', notificationIds);
    return response.data;
  } catch (error) {
    console.error('Mark Multiple Notifications as Read Error:', error);
    throw error.response?.data?.detail || 'Failed to mark notifications as read';
  }
};

export const getTicketDetails = async (ticketId) => {
  try {
    const response = await api.get(`/tickets/${ticketId}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch ticket details');
  }
};

export const markNotificationAsRead = async (notificationId) => {
  try {
    const response = await api.patch(`/notifications/${notificationId}/read`);
    return response.data;
  } catch (error) {
    console.error('Mark Notification as Read Error:', error);
    throw error.response?.data?.detail || 'Failed to mark notification as read';
  }
};

export const getNotificationDetails = async (notificationId) => {
  try {
    const response = await api.get(`/notifications/${notificationId}`);
    return response.data;
  } catch (error) {
    console.error('Get Notification Details Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch notification details';
  }
};

export const updateNotification = async (notificationId, data) => {
  try {
    const response = await api.put(`/notifications/${notificationId}`, data);
    return response.data;
  } catch (error) {
    console.error('Update Notification Error:', error);
    throw error.response?.data?.detail || 'Failed to update notification';
  }
};

export const deleteNotification = async (notificationId) => {
  try {
    const response = await api.delete(`/notifications/${notificationId}`);
    return response?.data ?? ""
  } catch (error) {
    console.error('Delete Notification Error:', error);
    throw error.response?.data?.detail || 'Failed to delete notification';
  }
};

export const deleteAllUserNotifications = async () => {
  try {
    const response = await api.delete('/notifications/user/all');
    return response?.data ?? "";
  } catch (error) {
    console.error('Delete All User Notifications Error:', error);
    throw error.response?.data?.detail || 'Failed to delete all user notifications';
  }
};

export const listRefundRequests = async () => {
  try {
    const response = await api.get('/payments/refunds');
    return response.data;
  } catch (error) {
    console.error('List Refund Requests Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch refund requests';
  }
};

export const handleRefund = async (refundId, data) => {
  try {
    const response = await api.post(`/payments/refunds/${refundId}/action`, data);
    return response.data;
  } catch (error) {
    console.error('Handle Refund Error:', error);
    throw error.response?.data?.detail || 'Failed to handle refund';
  }
};

export const getPaymentMethods = async () => {
  try {
    const response = await api.get('/payments/methods');
    return response.data;
  } catch (error) {
    console.error('Get Payment Methods Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch payment methods';
  }
};

export const createPayment = async (data) => {
  try {
    const response = await api.post('/payments/', data);
    return response.data;
  } catch (error) {
    console.error('Create Payment Error:', error);
    throw error.response?.data?.detail || 'Failed to create payment';
  }
};

export const getAllPayments = async ({ skip = 0, limit = 100 } = {}) => {
  try {
    const response = await api.get('/payments/', { params: { skip, limit } });
    return response.data;
  } catch (error) {
    console.error('Get All Payments Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch all payments';
  }
};

export const getUserPayments = async ({ skip = 0, limit = 100 } = {}) => {
  try {
    const response = await api.get('/payments/user', { params: { skip, limit } });
    return response.data;
  } catch (error) {
    console.error('Get User Payments Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch user payments';
  }
};

export const requestRefund = async (paymentId, reason) => {
  try {
    const response = await api.post(`/payments/${paymentId}/refund`, null, {
      params: { reason },
    });
    return response.data;
  } catch (error) {
    console.error('Request Refund Error:', error);
    throw error.response?.data?.detail || 'Failed to request refund';
  }
};

export const deletePayment = async (paymentId) => {
  try {
    const response = await api.delete(`/payments/${paymentId}`);
    return response.data;
  } catch (error) {
    console.error('Delete Payment Error:', error);
    throw error.response?.data?.detail || 'Failed to delete payment';
  }
};

export const verifyPaymentById = async ({ reservation_id, user_id, Authority, Status }) => {
  try {
    const response = await api.get('/payments/verify', { params: { reservation_id, user_id, Authority, Status } });
    return response.data;
  } catch (error) {
    console.error('Verify Payment by ID Error:', error);
    throw error.response?.data?.detail || 'Failed to verify payment';
  }
};

export const getPaymentById = async (paymentId) => {
  try {
    const response = await api.get(`/payments/${paymentId}`);
    return response.data;
  } catch (error) {
    console.error('Get Payment by ID Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch payment';
  }
};

export const patchPayment = async (paymentId, data) => {
  try {
    const response = await api.patch(`/payments/${paymentId}`, data);
    return response.data;
  } catch (error) {
    console.error('Patch Payment Error:', error);
    throw error.response?.data?.detail || 'Failed to patch payment';
  }
};

export const replacePayment = async (paymentId, data) => {
  try {
    const response = await api.put(`/payments/${paymentId}`, data);
    return response.data;
  } catch (error) {
    console.error('Replace Payment Error:', error);
    throw error.response?.data?.detail || 'Failed to replace payment';
  }
};

export const checkPaymentExists = async (paymentId) => {
  try {
    const response = await api.head(`/payments/${paymentId}`);
    return response.status === 200;
  } catch (error) {
    console.error('Check Payment Exists Error:', error);
    throw error.response?.data?.detail || 'Failed to check payment existence';
  }
};

export const updatePaymentStatus = async (paymentId, data) => {
  try {
    const response = await api.put(`/payments/${paymentId}/status`, data);
    return response.data;
  } catch (error) {
    console.error('Update Payment Status Error:', error);
    throw error.response?.data?.detail || 'Failed to update payment status';
  }
};

export const getSupportCategories = async ({ include_inactive = false } = {}) => {
  try {
    const response = await api.get('/support/categories', { params: { include_inactive } });
    return response.data;
  } catch (error) {
    console.error('Get Support Categories Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch support categories';
  }
};

export const createSupportCategory = async (data) => {
  try {
    const response = await api.post('/support/categories', data);
    return response.data;
  } catch (error) {
    console.error('Create Support Category Error:', error);
    throw error.response?.data?.detail || 'Failed to create support category';
  }
};

export const updateSupportCategory = async (categoryId, data) => {
  try {
    const response = await api.put(`/support/categories/${categoryId}`, data);
    return response.data;
  } catch (error) {
    console.error('Update Support Category Error:', error);
    throw error.response?.data?.detail || 'Failed to update support category';
  }
};

export const createSupportTicket = async (data) => {
  try {
    const response = await api.post('/support/tickets', data);
    return response.data;
  } catch (error) {
    console.error('Create Support Ticket Error:', error);
    throw error.response?.data?.detail || 'Failed to create support ticket';
  }
};

export const getSupportTickets = async ({
  status = null,
  category_id = null,
  priority = null,
  assigned_to_me = false,
  user_id = null,
  search = null,
  start_date = null,
  end_date = null,
  skip = 0,
  limit = 100,
} = {}) => {
  try {
    const params = {};
    if (status) params.status = status;
    if (category_id) params.category_id = category_id;
    if (priority) params.priority = priority;
    if (assigned_to_me) params.assigned_to_me = assigned_to_me;
    if (user_id) params.user_id = user_id;
    if (search) params.search = search;
    if (start_date) params.start_date = start_date;
    if (end_date) params.end_date = end_date;
    params.skip = skip;
    params.limit = limit;

    const response = await api.get('/support/tickets', { params });
    return response.data;
  } catch (error) {
    console.error('Get Support Tickets Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch support tickets';
  }
};

export const getSupportTicket = async (ticketId) => {
  try {
    const response = await api.get(`/support/tickets/${ticketId}`);
    return response.data;
  } catch (error) {
    console.error('Get Support Ticket Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch support ticket';
  }
};

export const updateSupportTicket = async (ticketId, data) => {
  try {
    const response = await api.put(`/support/tickets/${ticketId}`, data);
    return response.data;
  } catch (error) {
    console.error('Update Support Ticket Error:', error);
    throw error.response?.data?.detail || 'Failed to update support ticket';
  }
};

export const deleteSupportTicket = async (ticketId) => {
  try {
    const response = await api.delete(`/support/tickets/${ticketId}`);
    return response.data;
  } catch (error) {
    console.error('Delete Support Ticket Error:', error);
    throw error.response?.data?.detail || 'Failed to delete support ticket';
  }
};

export const addTicketMessage = async (ticketId, data) => {
  try {
    const response = await api.post(`/support/tickets/${ticketId}/messages`, data);
    return response.data;
  } catch (error) {
    console.error('Add Ticket Message Error:', error);
    throw error.response?.data?.detail || 'Failed to add ticket message';
  }
};

export const getTicketMessages = async (ticketId, { skip = 0, limit = 100 } = {}) => {
  try {
    const response = await api.get(`/support/tickets/${ticketId}/messages`, { params: { skip, limit } });
    return response.data;
  } catch (error) {
    console.error('Get Ticket Messages Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch ticket messages';
  }
};

export const getSupportStats = async ({ time_range = null } = {}) => {
  try {
    const response = await api.get('/support/stats', { params: { time_range } });
    return response.data;
  } catch (error) {
    console.error('Get Support Stats Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch support stats';
  }
};

export const createFlightDetails = async (data) => {
  try {
    const response = await api.post('/vehicles/flight-details', data);
    return response.data;
  } catch (error) {
    console.error('Create Flight Details Error:', error);
    throw error.response?.data?.detail || 'Failed to create flight details';
  }
};

export const getFlightDetails = async (ticketId) => {
  try {
    const response = await api.get(`/vehicles/flight-details/${ticketId}`);
    return response.data;
  } catch (error) {
    console.error('Get Flight Details Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch flight details';
  }
};

export const updateFlightDetails = async (ticketId, data) => {
  try {
    const response = await api.put(`/vehicles/flight-details/${ticketId}`, data);
    return response.data;
  } catch (error) {
    console.error('Update Flight Details Error:', error);
    throw error.response?.data?.detail || 'Failed to update flight details';
  }
};

export const createTrainDetails = async (data) => {
  try {
    const response = await api.post('/vehicles/train-details', data);
    return response.data;
  } catch (error) {
    console.error('Create Train Details Error:', error);
    throw error.response?.data?.detail || 'Failed to create train details';
  }
};

export const getTrainDetails = async (ticketId) => {
  try {
    const response = await api.get(`/vehicles/train-details/${ticketId}`);
    return response.data;
  } catch (error) {
    console.error('Get Train Details Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch train details';
  }
};

export const updateTrainDetails = async (ticketId, data) => {
  try {
    const response = await api.patch(`/vehicles/train-details/${ticketId}`, data);
    return response.data;
  } catch (error) {
    console.error('Update Train Details Error:', error);
    throw error.response?.data?.detail || 'Failed to update train details';
  }
};

export const createBusDetails = async (data) => {
  try {
    const response = await api.post('/vehicles/bus-details', data);
    return response.data;
  } catch (error) {
    console.error('Create Bus Details Error:', error);
    throw error.response?.data?.detail || 'Failed to create bus details';
  }
};

export const getBusDetails = async (ticketId) => {
  try {
    const response = await api.get(`/vehicles/bus-details/${ticketId}`);
    return response.data;
  } catch (error) {
    console.error('Get Bus Details Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch bus details';
  }
};

export const updateBusDetails = async (ticketId, data) => {
  try {
    const response = await api.put(`/vehicles/bus-details/${ticketId}`, data);
    return response.data;
  } catch (error) {
    console.error('Update Bus Details Error:', error);
    throw error.response?.data?.detail || 'Failed to update bus details';
  }
};

export const createVehicleFeature = async (data) => {
  try {
    const response = await api.post('/vehicles/features', data);
    return response.data;
  } catch (error) {
    console.error('Create Vehicle Feature Error:', error);
    throw error.response?.data?.detail || 'Failed to create vehicle feature';
  }
};

export const getVehicleFeatures = async ({ search = null, skip = 0, limit = 100 } = {}) => {
  try {
    const response = await api.get('/vehicles/features', { params: { search, skip, limit } });
    return response.data;
  } catch (error) {
    console.error('Get Vehicle Features Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch vehicle features';
  }
};

export const assignFeatureToVehicle = async (data) => {
  try {
    const response = await api.post('/vehicles/features/assign', data);
    return response.data;
  } catch (error) {
    console.error('Assign Feature to Vehicle Error:', error);
    throw error.response?.data?.detail || 'Failed to assign feature to vehicle';
  }
};

export const unassignFeatureFromVehicle = async ({ vehicle_type, vehicle_id, feature_id }) => {
  try {
    const response = await api.delete('/vehicles/features/unassign', {
      params: { vehicle_type, vehicle_id, feature_id },
    });
    return response.data;
  } catch (error) {
    console.error('Unassign Feature from Vehicle Error:', error);
    throw error.response?.data?.detail || 'Failed to unassign feature from vehicle';
  }
};

export const getAssignedFeatures = async ({ vehicle_type, vehicle_id }) => {
  try {
    const response = await api.get('/vehicles/features/assigned', { params: { vehicle_type, vehicle_id } });
    return response.data;
  } catch (error) {
    console.error('Get Assigned Features Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch assigned features';
  }
};

export const getFlightStatistics = async ({ airline = null, from_date = null, to_date = null } = {}) => {
  try {
    const response = await api.get('/vehicles/statistics/flights', { params: { airline, from_date, to_date } });
    return response.data;
  } catch (error) {
    console.error('Get Flight Statistics Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch flight statistics';
  }
};

export const getTrainStatistics = async ({ min_rating = null, max_rating = null } = {}) => {
  try {
    const response = await api.get('/vehicles/statistics/trains', { params: { min_rating, max_rating } });
    return response.data;
  } catch (error) {
    console.error('Get Train Statistics Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch train statistics';
  }
};

export const getBusStatistics = async ({ bus_type = null } = {}) => {
  try {
    const response = await api.get('/vehicles/statistics/buses', { params: { bus_type } });
    return response.data;
  } catch (error) {
    console.error('Get Bus Statistics Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch bus statistics';
  }
};

export const getAllReports = async ({
  status_filter = null,
  category = null,
  assigned_to = null,
  user_id = null,
  ticket_id = null,
  start_date = null,
  end_date = null,
  skip = 0,
  limit = 100,
} = {}) => {
  try {
    const response = await api.get('/reports/all', {
      params: { status_filter, category, assigned_to, user_id, ticket_id, start_date, end_date, skip, limit },
    });
    return response.data;
  } catch (error) {
    console.error('Get All Reports Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch all reports';
  }
};

export const getReportStats = async ({ time_range = null } = {}) => {
  try {
    const response = await api.get('/reports/stats', { params: { time_range } });
    return response.data;
  } catch (error) {
    console.error('Get Report Stats Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch report stats';
  }
};

export const createReport = async (data) => {
  try {
    const response = await api.post('/reports/', data);
    return response.data;
  } catch (error) {
    console.error('Create Report Error:', error);
    throw error.response?.data?.detail || 'Failed to create report';
  }
};

export const getUserReports = async ({
  status_filter = null,
  category = null,
  start_date = null,
  end_date = null,
  skip = 0,
  limit = 100,
} = {}) => {
  try {
    const response = await api.get('/reports/', {
      params: { status_filter, category, start_date, end_date, skip, limit },
    });
    return response.data;
  } catch (error) {
    console.error('Get User Reports Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch user reports';
  }
};

export const getReportDetails = async (reportId) => {
  try {
    const response = await api.get(`/reports/${reportId}`);
    return response.data;
  } catch (error) {
    console.error('Get Report Details Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch report details';
  }
};

export const updateReport = async (reportId, data) => {
  try {
    const response = await api.patch(`/reports/${reportId}`, data);
    return response.data;
  } catch (error) {
    console.error('Update Report Error:', error);
    throw error.response?.data?.detail || 'Failed to update report';
  }
};

export const deleteReport = async (reportId) => {
  try {
    const response = await api.delete(`/reports/${reportId}`);
    return response.data;
  } catch (error) {
    console.error('Delete Report Error:', error);
    throw error.response?.data?.detail || 'Failed to delete report';
  }
};

export const addReportComment = async (reportId, comment) => {
  try {
    const response = await api.post(`/reports/${reportId}/resolve`, null, {
      params: { comment },
    });
    return response.data;
  } catch (error) {
    console.error('Add Report Comment Error:', error);
    throw error.response?.data?.detail || 'Failed to add report comment';
  }
};

export const createRole = async (data) => {
  try {
    const response = await api.post('/roles/', data);
    return response.data;
  } catch (error) {
    console.error('Create Role Error:', error);
    throw error.response?.data?.detail || 'Failed to create role';
  }
};

export const getRoles = async ({ active_only = false, skip = 0, limit = 100 } = {}) => {
  try {
    const response = await api.get('/roles/', { params: { active_only, skip, limit } });
    return response.data;
  } catch (error) {
    console.error('Get Roles Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch roles';
  }
};

export const getRole = async (roleId) => {
  try {
    const response = await api.get(`/roles/${roleId}`);
    return response.data;
  } catch (error) {
    console.error('Get Role Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch role';
  }
};

export const updateRole = async (roleId, data) => {
  try {
    const response = await api.put(`/roles/${roleId}`, data);
    return response.data;
  } catch (error) {
    console.error('Update Role Error:', error);
    throw error.response?.data?.detail || 'Failed to update role';
  }
};

export const partialUpdateRole = async (roleId, data) => {
  try {
    const response = await api.patch(`/roles/${roleId}`, data);
    return response.data;
  } catch (error) {
    console.error('Partial Update Role Error:', error);
    throw error.response?.data?.detail || 'Failed to partially update role';
  }
};

export const deleteRole = async (roleId) => {
  try {
    const response = await api.delete(`/roles/${roleId}`);
    return response.data;
  } catch (error) {
    console.error('Delete Role Error:', error);
    throw error.response?.data?.detail || 'Failed to delete role';
  }
};

export const getRolePermissions = async (roleId) => {
  try {
    const response = await api.get(`/roles/${roleId}/permissions`);
    return response.data;
  } catch (error) {
    console.error('Get Role Permissions Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch role permissions';
  }
};

export const assignPermissionToRole = async (roleId, permissionId) => {
  try {
    const response = await api.post(`/roles/${roleId}/permissions/${permissionId}`);
    return response.data;
  } catch (error) {
    console.error('Assign Permission to Role Error:', error);
    throw error.response?.data?.detail || 'Failed to assign permission to role';
  }
};

export const removePermissionFromRole = async (roleId, permissionId) => {
  try {
    const response = await api.delete(`/roles/${roleId}/permissions/${permissionId}`);
    return response.data;
  } catch (error) {
    console.error('Remove Permission from Role Error:', error);
    throw error.response?.data?.detail || 'Failed to remove permission from role';
  }
};

export const getSupportTicketCount = async ({ user_id }) => {
  try {
    const response = await api.get(`/support/count`, {
      params: { user_id },
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch support ticket count');
  }
};

export const getPaymentCount = async ({ user_id }) => {
  try {
    const response = await api.get(`/payments/count`, {
      params: { user_id },
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch payment count');
  }
};

export const getPaymentDetails = async (paymentId) => {
  try {
    const response = await api.get(`/payments/${paymentId}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch payment details');
  }
};

export const getRefundRequestCount = async ({ user_id }) => {
  try {
    const response = await api.get(`/payments/refunds/count`, {
      params: { user_id },
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch refund request count');
  }
};

export const getRefundRequestDetails = async (refundRequestId) => {
  try {
    const response = await api.get(`/payments/refunds/${refundRequestId}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch refund request details');
  }
};


export const createPermission = async (data) => {
  try {
    const response = await api.post('/roles/permissions', data);
    return response.data;
  } catch (error) {
    console.error('Create Permission Error:', error);
    throw error.response?.data?.detail || 'Failed to create permission';
  }
};

export const getPermissions = async ({ type_filter = null, status_filter = null, skip = 0, limit = 100 } = {}) => {
  try {
    const response = await api.get('/roles/permissions', { params: { type_filter, status_filter, skip, limit } });
    return response.data;
  } catch (error) {
    console.error('Get Permissions Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch permissions';
  }
};

export const updatePermission = async (permissionId, data) => {
  try {
    const response = await api.patch(`/roles/permissions/${permissionId}`, data);
    return response.data;
  } catch (error) {
    console.error('Update Permission Error:', error);
    throw error.response?.data?.detail || 'Failed to update permission';
  }
};

export const deletePermission = async (permissionId) => {
  try {
    const response = await api.delete(`/roles/permissions/${permissionId}`);
    return response.data;
  } catch (error) {
    console.error('Delete Permission Error:', error);
    throw error.response?.data?.detail || 'Failed to delete permission';
  }
};

export const getServiceProviders = async ({ name = null, skip = 0, limit = 100 } = {}) => {
  try {
    const response = await api.get('/service-providers/', { params: { name, skip, limit } });
    return response.data;
  } catch (error) {
    console.error('Get Service Providers Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch service providers';
  }
};

export const createServiceProvider = async (data) => {
  try {
    const response = await api.post('/service-providers/', data);
    return response.data;
  } catch (error) {
    console.error('Create Service Provider Error:', error);
    throw error.response?.data?.detail || 'Failed to create service provider';
  }
};

export const getProviderTickets = async (providerId, {
  status = null,
  from_date = null,
  to_date = null,
  skip = 0,
  limit = 100,
} = {}) => {
  try {
    const response = await api.get(`/service-providers/${providerId}/tickets`, {
      params: { status, from_date, to_date, skip, limit },
      timeout: 300000000
    });
    return response.data;
  } catch (error) {
    console.error('Get Provider Tickets Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch provider tickets';
  }
};

export const updateServiceProvider = async (providerId, data) => {
  try {
    const response = await api.put(`/service-providers/${providerId}`, data);
    return response.data;
  } catch (error) {
    console.error('Update Service Provider Error:', error);
    throw error.response?.data?.detail || 'Failed to update service provider';
  }
};

export const partialUpdateServiceProvider = async (providerId, data) => {
  try {
    const response = await api.patch(`/service-providers/${providerId}`, data);
    return response.data;
  } catch (error) {
    console.error('Partial Update Service Provider Error:', error);
    throw error.response?.data?.detail || 'Failed to partially update service provider';
  }
};

export const deleteServiceProvider = async (providerId) => {
  try {
    const response = await api.delete(`/service-providers/${providerId}`);
    return response.data;
  } catch (error) {
    console.error('Delete Service Provider Error:', error);
    throw error.response?.data?.detail || 'Failed to delete service provider';
  }
};

export const updateProviderStatus = async (providerId, providerStatus) => {
  try {
    const response = await api.patch(`/service-providers/${providerId}/status`, null, {
      params: { provider_status: providerStatus },
    });
    return response.data;
  } catch (error) {
    console.error('Update Provider Status Error:', error);
    throw error.response?.data?.detail || 'Failed to update provider status';
  }
};

export const getProviderCancellationPenalty = async (providerId) => {
  try {
    const response = await api.get(`/service-providers/${providerId}/cancellation-penalty`);
    return response.data;
  } catch (error) {
    console.error('Get Provider Cancellation Penalty Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch provider cancellation penalty';
  }
};

export const createReview = async (data) => {
  try {
    const response = await api.post('/reviews/', data);
    return response.data;
  } catch (error) {
    console.error('Create Review Error:', error);
    throw error.response?.data?.detail || 'Failed to create review';
  }
};

export const listReviews = async ({
  ticket_id = null,
  user_id = null,
  min_rating = null,
  max_rating = null,
  ticket_status = null,
  review_status = null,
  from_date = null,
  to_date = null,
  skip = 0,
  limit = 50,
} = {}) => {
  try {
    const response = await api.get('/reviews/', {
      params: { ticket_id, user_id, min_rating, max_rating, ticket_status, review_status, from_date, to_date, skip, limit },
    });
    return response.data;
  } catch (error) {
    console.error('List Reviews Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch reviews';
  }
};

export const getReview = async (reviewId) => {
  try {
    const response = await api.get(`/reviews/${reviewId}`);
    return response.data;
  } catch (error) {
    console.error('Get Review Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch review';
  }
};

export const updateReview = async (reviewId, data) => {
  try {
    const response = await api.patch(`/reviews/${reviewId}`, data);
    return response.data;
  } catch (error) {
    console.error('Update Review Error:', error);
    throw error.response?.data?.detail || 'Failed to update review';
  }
};

export const deleteReview = async (reviewId) => {
  try {
    const response = await api.delete(`/reviews/${reviewId}`);
    return response.data;
  } catch (error) {
    console.error('Delete Review Error:', error);
    throw error.response?.data?.detail || 'Failed to delete review';
  }
};

export const checkReviewExists = async (reviewId) => {
  try {
    const response = await api.head(`/reviews/${reviewId}`);
    return response.status === 200;
  } catch (error) {
    console.error('Check Review Exists Error:', error);
    throw error.response?.data?.detail || 'Failed to check review existence';
  }
};

export const getReviewsByUser = async (userId) => {
  try {
    const response = await api.get(`/reviews/user/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Get Reviews by User Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch reviews by user';
  }
};

export const getReviewsByTicket = async (ticketId) => {
  try {
    const response = await api.get(`/reviews/ticket/${ticketId}`);
    return response.data;
  } catch (error) {
    console.error('Get Reviews by Ticket Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch reviews by ticket';
  }
};

export const getTicketReviewStats = async (ticketId) => {
  try {
    const response = await api.get(`/reviews/ticket/${ticketId}/stats`);
    return response.data;
  } catch (error) {
    console.error('Get Ticket Review Stats Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch ticket review stats';
  }
};

export const createReferral = async (data) => {
  try {
    const response = await api.post('/referrals/', data);
    return response.data;
  } catch (error) {
    console.error('Create Referral Error:', error);
    throw error.response?.data?.detail || 'Failed to create referral';
  }
};

export const listReferrals = async ({ referrer_id = null, referred_id = null, skip = 0, limit = 50 } = {}) => {
  try {
    const response = await api.get('/referrals/', { params: { referrer_id, referred_id, skip, limit } });
    return response.data;
  } catch (error) {
    console.error('List Referrals Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch referrals';
  }
};

export const listMyReferrals = async ({ skip = 0, limit = 50 } = {}) => {
  try {
    const response = await api.get('/referrals/me', { params: { skip, limit } });
    return response.data;
  } catch (error) {
    console.error('List My Referrals Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch my referrals';
  }
};

export const countMyReferrals = async () => {
  try {
    const response = await api.get('/referrals/count');
    return response.data;
  } catch (error) {
    console.error('Count My Referrals Error:', error);
    throw error.response?.data?.detail || 'Failed to count my referrals';
  }
};

export const getReferralStats = async (referrerId) => {
  try {
    const response = await api.get(`/referrals/stats/${referrerId}`);
    return response.data;
  } catch (error) {
    console.error('Get Referral Stats Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch referral stats';
  }
};

export const deleteReferral = async (referralId) => {
  try {
    const response = await api.delete(`/referrals/${referralId}`);
    return response.data;
  } catch (error) {
    console.error('Delete Referral Error:', error);
    throw error.response?.data?.detail || 'Failed to delete referral';
  }
};

export const updateReferral = async (referralId, data) => {
  try {
    const response = await api.patch(`/referrals/${referralId}`, data);
    return response.data;
  } catch (error) {
    console.error('Update Referral Error:', error);
    throw error.response?.data?.detail || 'Failed to update referral';
  }
};

export const checkReferralExists = async (referralId) => {
  try {
    const response = await api.head(`/referrals/${referralId}`);
    return response.status === 200;
  } catch (error) {
    console.error('Check Referral Exists Error:', error);
    throw error.response?.data?.detail || 'Failed to check referral existence';
  }
};

export const putReferral = async (referralId, data) => {
  try {
    const response = await api.put(`/referrals/${referralId}`, data);
    return response.data;
  } catch (error) {
    console.error('Put Referral Error:', error);
    throw error.response?.data?.detail || 'Failed to replace referral';
  }
};

export const getReferredUsers = async (referrerId) => {
  try {
    const response = await api.get(`/referrals/referred-users/${referrerId}`);
    return response.data;
  } catch (error) {
    console.error('Get Referred Users Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch referred users';
  }
};

export const whoReferredUser = async (userId) => {
  try {
    const response = await api.get(`/referrals/referred-by/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Who Referred User Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch who referred user';
  }
};

export const getRecentReferrals = async ({ limit = 20 } = {}) => {
  try {
    const response = await api.get('/referrals/recent', { params: { limit } });
    return response.data;
  } catch (error) {
    console.error('Get Recent Referrals Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch recent referrals';
  }
};

export const getReferralLeaderboard = async ({ limit = 10 } = {}) => {
  try {
    const response = await api.get('/referrals/leaders', { params: { limit } });
    return response.data;
  } catch (error) {
    console.error('Get Referral Leaderboard Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch referral leaderboard';
  }
};

export const getRoot = async () => {
  try {
    const response = await api.get('/');
    return response.data;
  } catch (error) {
    console.error('Get Root Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch root';
  }
};

export const checkHealth = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    console.error('Check Health Error:', error);
    throw error.response?.data?.detail || 'Failed to check health';
  }
};


export const sendAIQuery = async (query) => {
  try {
    const response = await api.get('/ai/recommend-tickets', { params: { query } });
    return response.data;
  } catch (error) {
    console.error('Send AI Query Error:', error);
    throw error.response?.data?.detail || 'Failed to process AI query';
  }
};

export const getAIAssistance = async (task) => {
  try {
    const response = await api.get('/ai/assist', { params: { task } });
    return response.data;
  } catch (error) {
    console.error('Get AI Assistance Error:', error);
    throw error.response?.data?.detail || 'Failed to get AI assistance';
  }
};

export const recommendTrips = async (mode, from_city, to_city) => {
  try {
    const response = await api.get('/ai/recommend', { params: { mode, from_city, to_city } });
    return response.data;
  } catch (error) {
    console.error('Recommend Trips Error:', error);
    throw error.response?.data?.detail || 'Failed to recommend trips';
  }
};

export const getTrainDetailsAI = async (ticket_id) => {
  try {
    const response = await api.get('/ai/train-details', { params: { ticket_id } });
    return response.data;
  } catch (error) {
    console.error('Get Train Details Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch train details';
  }
};

export const getBusDetailsAI = async (ticket_id) => {
  try {
    const response = await api.get('/ai/bus-details', { params: { ticket_id } });
    return response.data;
  } catch (error) {
    console.error('Get Bus Details Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch bus details';
  }
};

export const getFlightDetailsAI = async (ticket_id) => {
  try {
    const response = await api.get('/ai/flight-details', { params: { ticket_id } });
    return response.data;
  } catch (error) {
    console.error('Get Flight Details Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch flight details';
  }
};

export const getBusFeaturesAI = async (ticket_id) => {
  try {
    const response = await api.get('/ai/bus-features', { params: { ticket_id } });
    return response.data;
  } catch (error) {
    console.error('Get Bus Features Error:', error);
    throw error.response?.data?.detail || 'Failed to fetch bus features';
  }
};

export const getNotificationCount = async ({ unread_only = false }) => {
  try {
    const response = await api.get(`/notifications/count`, {
      params: { unread_only },
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });
    return response.data.count;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to fetch notification count');
  }
};

export default api;