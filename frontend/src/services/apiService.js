import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// File upload service
export const uploadFile = async (file, type) => {
  const formData = new FormData();
  formData.append('file', file);

  const endpoint = type === 'requirements' 
    ? '/upload-requirements' 
    : '/upload-design';

  const response = await api.post(endpoint, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

// Analysis service
export const analyzeDocuments = async (requirements, design, threshold = 0.3) => {
  const response = await api.post('/analyze', {
    requirements,
    design,
    threshold,
  });
  return response.data;
};

// LLM feedback service
export const getLLMFeedback = async (requirements, design, threshold = 0.3) => {
  const response = await api.post('/analyze/llm-feedback', {
    requirements,
    design,
    threshold,
  });
  return response.data;
};

// Chat service
export const sendChatMessage = async (message, conversationId = null) => {
  const response = await api.post('/chat', {
    message,
    conversation_id: conversationId,
  });
  return response.data;
};

// Conversation history
export const getChatHistory = async (conversationId) => {
  const response = await api.get(`/chat/${conversationId}/history`);
  return response.data;
};

// Get all conversations
export const getAllConversations = async () => {
  const response = await api.get('/chat/conversations');
  return response.data;
};

// Health check
export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
