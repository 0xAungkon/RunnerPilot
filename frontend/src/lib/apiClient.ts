/**
 * API Client Configuration
 *
 * This module wraps the Hey API SDK with custom configuration,
 * authentication handling, and error management.
 */

import { client as sdkClient } from './api/client.gen';

/**
 * Initialize and configure the API client with:
 * - Base URL from environment variables
 * - Token-based authentication
 * - Error handling for expired tokens
 */
export const initializeApiClient = () => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  sdkClient.setConfig({
    baseUrl: baseUrl,
  });

  // Setup request interceptor to inject auth token
  sdkClient.interceptors.request.use((request) => {
    const token = localStorage.getItem('access_token');

    if (token) {
      request.headers.set('Authorization', `Bearer ${token}`);
    }

    return request;
  });

  // Setup response interceptor for token expiry and error handling
  sdkClient.interceptors.response.use((response) => {
    // Check if error response has 401 status (Unauthorized)
    if (response.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_profile');
      localStorage.removeItem('user_profile_time');

      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }

    return response;
  });
};

export { sdkClient as apiClient };
export default sdkClient;
