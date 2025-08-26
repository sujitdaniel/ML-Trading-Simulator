// API configuration for the frontend
export const API_CONFIG = {
  // Base URL for the backend API
  // Smart detection: use localhost for browser, backend for Docker internal
  BASE_URL: (() => {
    // If running in browser, always use localhost
    if (typeof window !== 'undefined') {
      return 'http://localhost:8000';
    }
    // If running in Docker container, use the service name
    return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  })(),
  
  // API endpoints
  ENDPOINTS: {
    HEALTH: '/health',
    BACKTEST: '/backtest',
    INDICATORS: '/indicators',
    AVAILABLE_TICKERS: '/available-tickers'
  },
  
  // Default request headers
  DEFAULT_HEADERS: {
    'Content-Type': 'application/json',
  },
  
  // Debug logging
  DEBUG: true
};

// Helper function to build full API URLs
export const buildApiUrl = (endpoint: string): string => {
  // In Docker, the backend service is accessible via the service name
  const baseUrl = API_CONFIG.BASE_URL;
  
  if (API_CONFIG.DEBUG) {
    console.log('🌐 Using API base URL:', baseUrl);
    console.log('🔗 Building URL for endpoint:', endpoint);
  }
  
  return `${baseUrl}${endpoint}`;
};

// Helper function to make API requests with proper error handling
export const apiRequest = async (
  endpoint: string, 
  options: RequestInit = {}
): Promise<Response> => {
  const url = buildApiUrl(endpoint);
  
  if (API_CONFIG.DEBUG) {
    console.log('🌐 Making API request to:', url);
    console.log('📤 Request options:', options);
  }
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...API_CONFIG.DEFAULT_HEADERS,
        ...options.headers,
      },
    });
    
    if (API_CONFIG.DEBUG) {
      console.log('📥 Response status:', response.status);
      console.log('📥 Response headers:', Object.fromEntries(response.headers.entries()));
    }
    
    return response;
  } catch (error) {
    console.error('❌ API request failed:', error);
    throw error;
  }
};

// Test function to verify API connectivity
export const testApiConnection = async (): Promise<boolean> => {
  try {
    const response = await apiRequest('/health');
    if (response.ok) {
      const data = await response.json();
      console.log('✅ API connection successful:', data);
      return true;
    } else {
      console.error('❌ API connection failed:', response.status);
      return false;
    }
  } catch (error) {
    console.error('❌ API connection error:', error);
    return false;
  }
};
