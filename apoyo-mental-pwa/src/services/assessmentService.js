// src/services/assessmentService.js
import axios from 'axios';
import authService from './authService';

const API_URL = 'http://localhost:8000';

const getAuthHeader = () => ({
  headers: { Authorization: `Bearer ${authService.getToken()}` }
});

class AssessmentService {
  async saveAssessment(type, score, severity, answers) {
    const response = await axios.post(
      `${API_URL}/assessments`,
      { type, score, severity, answers },
      getAuthHeader()
    );
    return response.data;
  }

  async getAssessments(type = null) {
    const url = type ? `${API_URL}/assessments?assessment_type=${type}` : `${API_URL}/assessments`;
    const response = await axios.get(url, getAuthHeader());
    return response.data;
  }

  async getLatestAssessment(type) {
    const response = await axios.get(`${API_URL}/assessments/latest/${type}`, getAuthHeader());
    return response.data;
  }
}

export default new AssessmentService();