import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getEvents = (params = {}) => api.get('/events', { params });
export const getEvent = (id, userId) => api.get(`/events/${id}`, { params: { user_id: userId } });
export const getSeatPulse = (id) => api.get(`/events/${id}/seat-pulse`);
export const createEvent = (data) => api.post('/events', data);
export const updateEvent = (id, data) => api.put(`/events/${id}`, data);
export const deleteEvent = (id) => api.delete(`/events/${id}`);

export const checkScheduleClash = (eventId, userId) => api.post(`/events/${eventId}/check-clash`, { user_id: userId });
export const registerForEvent = (eventId, userId, overrideConflict = false) =>
  api.post(`/events/${eventId}/register`, { user_id: userId, override_conflict: overrideConflict });
export const joinWaitlist = (eventId, userId) => api.post(`/events/${eventId}/waitlist`, { user_id: userId });
export const cancelRegistration = (regId, userId) => api.post(`/registrations/${regId}/cancel`, { user_id: userId });
export const claimWaitlistOffer = (waitlistId, userId) => api.post(`/waitlist/${waitlistId}/claim`, { user_id: userId });
export const getPassDetails = (regId) => api.get(`/registrations/${regId}/pass`);

export const getUsers = () => api.get('/users');
export const getUserRegistrations = (userId) => api.get(`/users/${userId}/registrations`);
export const getUserPassport = (userId) => api.get(`/users/${userId}/passport`);

export const verifyCheckin = (token, organizerId, eventId) =>
  api.post('/checkin/verify', { token, organizer_id: organizerId, event_id: eventId });
export const manualCheckinToggle = (registrationId, organizerId) =>
  api.post('/checkin/manual-toggle', { registration_id: registrationId, organizer_id: organizerId });

export const getOrganizerAnalytics = () => api.get('/organizer/analytics');
export const getEventAttendees = (eventId, params = {}) => api.get(`/organizer/events/${eventId}/attendees`, { params });

export const resetDemoData = () => api.post('/reset-demo');

export default api;

