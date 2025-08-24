import { defineBoot } from '#q-app/wrappers';
import axios, { type AxiosInstance } from 'axios';

declare module 'vue' {
  interface ComponentCustomProperties {
    $axios: AxiosInstance;
    $api: AxiosInstance;
  }
}

// Be careful when using SSR for cross-request state pollution
// due to creating a Singleton instance here;
// If any client changes this (global) instance, it might be a
// good idea to move this instance creation inside of the
// "export default () => {}" function below (which runs individually
// for each client)
const api = axios.create({
  baseURL: process.env.API_URL || 'http://localhost:8000',
});

// Add request interceptor
api.interceptors.request.use((config) => {
  console.log('Request:', {
    method: config.method?.toUpperCase(),
    url: config.url,
    params: config.params,
    data: config.data
  });
  return config;
}, (error) => {
  console.error('Request Error:', error);
  return Promise.reject(new Error(error));
});

// Add response interceptor
api.interceptors.response.use((response) => {
  console.log('Response:', {
    status: response.status,
    statusText: response.statusText,
    data: response.data
  });
  return response;
}, (error) => {
  console.error('Response Error:', {
    status: error.response?.status,
    message: error.message,
    response: error.response?.data
  });
  return Promise.reject(new Error(error.message || 'An error occurred'));
});

export default defineBoot(({ app }) => {
  // for use inside Vue files (Options API) through this.$axios and this.$api

  app.config.globalProperties.$axios = axios;
  // ^ ^ ^ this will allow you to use this.$axios (for Vue Options API form)
  //       so you won't necessarily have to import axios in each vue file

  app.config.globalProperties.$api = api;
  // ^ ^ ^ this will allow you to use this.$api (for Vue Options API form)
  //       so you can easily perform requests against your app's API
});

export { api };
