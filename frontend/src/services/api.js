import axios from 'axios';

// Centralized API Base URL configured via Vite environment variables
// Local development default: http://localhost:8000
// Production (Vercel): Set VITE_API_BASE_URL in Vercel project settings to your Render backend URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 8000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

/**
 * Health Check API Service (Liveness Probe: GET /api/health)
 * Queries backend to retrieve live application, API, and database status.
 * Standardizes UI consumption:
 * - 'connected': FastAPI backend is live and Supabase DB is verified
 * - 'database_unavailable': FastAPI backend is online, but Supabase connection is down/unconfigured
 * - 'backend_unavailable': FastAPI backend is unreachable (e.g. Render spin-up or network error)
 */
export const checkHealth = async () => {
  try {
    const response = await apiClient.get('/api/health');
    const data = response.data;

    const dbConnected = data?.database?.status === 'connected';

    if (dbConnected) {
      return {
        overallStatus: 'connected',
        backendOnline: true,
        databaseConnected: true,
        message: 'FastAPI backend and Supabase PostgreSQL database are connected and operational.',
        data,
      };
    } else {
      return {
        overallStatus: 'database_unavailable',
        backendOnline: true,
        databaseConnected: false,
        message: data?.database?.message || 'Supabase PostgreSQL connection is unconfigured or unreachable.',
        data,
      };
    }
  } catch (error) {
    return {
      overallStatus: 'backend_unavailable',
      backendOnline: false,
      databaseConnected: false,
      message: error?.message || 'Unable to connect to FastAPI backend server.',
      error,
    };
  }
};

/**
 * Readiness Check API Service (Readiness Probe: GET /api/ready)
 * Evaluates whether backend and Supabase database are ready to process traffic.
 */
export const checkReadiness = async () => {
  try {
    const response = await apiClient.get('/api/ready');
    return {
      isReady: true,
      data: response.data,
    };
  } catch (error) {
    return {
      isReady: false,
      error: error?.response?.data || error?.message,
    };
  }
};

export default apiClient;
