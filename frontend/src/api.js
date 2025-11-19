import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const searchDocuments = async (query, filters = {}, topK = 5) => {
  const response = await api.post('/api/search', {
    query,
    filters,
    top_k: topK,
  });
  return response.data;
};

export const chatWithDocuments = async (query, history = [], filters = {}, topK = 5) => {
  const response = await api.post('/api/chat', {
    query,
    history,
    filters,
    top_k: topK,
  });
  return response.data;
};

export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
