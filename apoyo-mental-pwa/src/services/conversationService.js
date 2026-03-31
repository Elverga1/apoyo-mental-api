// src/services/conversationService.js
import axios from 'axios';
import authService from './authService';

const API_URL = 'http://localhost:8000';

const getAuthHeader = () => ({
  headers: { Authorization: `Bearer ${authService.getToken()}` }
});

class ConversationService {
  async getConversations() {
    const response = await axios.get(`${API_URL}/conversations`, getAuthHeader());
    return response.data;
  }

  async createConversation(title = 'Nueva conversación') {
    const response = await axios.post(`${API_URL}/conversations`, { title }, getAuthHeader());
    return response.data;
  }

  async getConversation(id) {
    const response = await axios.get(`${API_URL}/conversations/${id}`, getAuthHeader());
    return response.data;
  }

  async sendMessage(conversationId, content) {
    const response = await axios.post(
      `${API_URL}/conversations/${conversationId}/messages`,
      { role: 'user', content },
      getAuthHeader()
    );
    return response.data;
  }

  async deleteConversation(id) {
    await axios.delete(`${API_URL}/conversations/${id}`, getAuthHeader());
  }
}

export default new ConversationService();