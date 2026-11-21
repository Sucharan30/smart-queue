import axios from 'axios';

// Centralized API Base URL configured via Vite environment variables
// Local development default: http://localhost:8000
// Production (Vercel): Set VITE_API_BASE_URL in Vercel project settings to your Render backend URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

/**
 * Health Check API Service (Liveness Probe: GET /api/health)
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
 */
export const checkReadiness = async () => {
  try {
    const response = await apiClient.get('/api/ready');
    return { isReady: true, data: response.data };
  } catch (error) {
    return { isReady: false, error: error?.response?.data || error?.message };
  }
};

// ============================================================================
// CHECKPOINT 2: CLINIC, DEPARTMENT, DOCTOR & REGISTRATION API SERVICES
// ============================================================================

/**
 * Fetch all active clinics
 */
export const getClinics = async () => {
  const response = await apiClient.get('/api/clinics');
  return response.data;
};

/**
 * Fetch active departments for a clinic
 */
export const getDepartments = async (clinicId) => {
  if (!clinicId) return [];
  const response = await apiClient.get(`/api/clinics/${clinicId}/departments`);
  return response.data;
};

/**
 * Fetch available doctors for a department
 */
export const getDoctors = async (departmentId) => {
  if (!departmentId) return [];
  const response = await apiClient.get(`/api/departments/${departmentId}/doctors`);
  return response.data;
};

/**
 * Register a patient and generate a queue token
 */
export const registerPatient = async (payload) => {
  const response = await apiClient.post('/api/patients/register', payload);
  return response.data;
};

/**
 * Retrieve public token details
 */
export const getTokenDetails = async (tokenId) => {
  const response = await apiClient.get(`/api/tokens/${tokenId}`);
  return response.data;
};

/**
 * Retrieve token event transition history
 */
export const getTokenEvents = async (tokenId) => {
  const response = await apiClient.get(`/api/tokens/${tokenId}/events`);
  return response.data;
};

/**
 * List daily registrations with optional filters
 */
export const getRegistrations = async (params = {}) => {
  const response = await apiClient.get('/api/registrations', { params });
  return response.data;
};

export default apiClient;
