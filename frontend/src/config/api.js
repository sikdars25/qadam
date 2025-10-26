/**
 * API Configuration
 * Centralized API endpoint management
 * Automatically uses Azure backend in production, localhost in development
 */

// Get API URL from environment variable
// Production: Azure Function App URL
// Development: Local Flask server
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

console.log('🌐 API URL:', API_URL);
console.log('🔧 Environment:', process.env.REACT_APP_ENV || 'development');

/**
 * API Endpoints
 * All backend API endpoints in one place
 */
export const API_ENDPOINTS = {
  // Health Check
  HEALTH: `${API_URL}/api/health`,
  
  // Papers
  PAPERS: `${API_URL}/api/papers`,
  UPLOAD_PAPER: `${API_URL}/api/upload-paper`,
  DELETE_PAPER: (id) => `${API_URL}/api/delete-paper/${id}`,
  PAPER_DETAILS: (id) => `${API_URL}/api/paper/${id}`,
  
  // Questions
  PARSE_QUESTIONS: `${API_URL}/api/parse-questions`,
  PARSE_SINGLE_QUESTION: `${API_URL}/api/parse-single-question`,
  QUESTIONS: (paperId) => `${API_URL}/api/questions/${paperId}`,
  
  // Textbooks
  TEXTBOOKS: `${API_URL}/api/textbooks`,
  UPLOAD_TEXTBOOK: `${API_URL}/api/upload-textbook`,
  DELETE_TEXTBOOK: (id) => `${API_URL}/api/delete-textbook/${id}`,
  TEXTBOOK_PDF: (id) => `${API_URL}/api/textbook-pdf/${id}`,
  TEXTBOOK_PAGE_IMAGE: (id, page) => `${API_URL}/api/textbook-page-image/${id}/${page}`,
  EXTRACT_CHAPTERS: `${API_URL}/api/extract-chapters`,
  
  // AI Services
  MAP_QUESTIONS: `${API_URL}/api/map-questions-to-chapters`,
  GENERATE_SOLUTION: `${API_URL}/api/generate-solution`,
  ANALYZE_PAPER: `${API_URL}/api/analyze-paper`,
  
  // Authentication
  LOGIN: `${API_URL}/api/login`,
  REGISTER: `${API_URL}/api/register`,
  LOGOUT: `${API_URL}/api/logout`,
  VERIFY_EMAIL: `${API_URL}/api/verify-email`,
  RESEND_VERIFICATION: `${API_URL}/api/resend-verification`,
  
  // User Management
  USER_PROFILE: `${API_URL}/api/user/profile`,
  UPDATE_PROFILE: `${API_URL}/api/user/update`,
  CHANGE_PASSWORD: `${API_URL}/api/user/change-password`,
  
  // Admin
  ADMIN_USERS: `${API_URL}/api/admin/users`,
  ADMIN_STATS: `${API_URL}/api/admin/stats`,
};

/**
 * Axios Configuration
 * Default settings for all API calls
 */
export const axiosConfig = {
  baseURL: API_URL,
  timeout: 30000, // 30 seconds
  withCredentials: true, // Send cookies with requests
  headers: {
    'Content-Type': 'application/json',
  },
};

/**
 * File Upload Configuration
 * For multipart/form-data requests
 */
export const fileUploadConfig = {
  ...axiosConfig,
  headers: {
    'Content-Type': 'multipart/form-data',
  },
  timeout: 120000, // 2 minutes for file uploads
};

export default API_URL;
