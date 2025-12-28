// API Configuration
// Priority: 1. VITE_API_URL env var, 2. Detect from window location, 3. localhost
const getApiUrl = () => {
    // Check if VITE_API_URL is set
    if (import.meta.env.VITE_API_URL) {
        console.log('Using VITE_API_URL:', import.meta.env.VITE_API_URL);
        return import.meta.env.VITE_API_URL;
    }

    // In production, try to detect backend URL from current location
    if (window.location.hostname.includes('onrender.com')) {
        // Replace 'frontend' with 'backend' in the hostname
        const backendUrl = window.location.origin.replace('hms-frontend', 'hms-backend');
        console.log('Detected Render deployment, using:', backendUrl);
        return backendUrl;
    }

    // Development fallback
    console.log('Using localhost for development');
    return 'http://localhost:5000';
};

const API_BASE_URL = getApiUrl();

export default API_BASE_URL;
