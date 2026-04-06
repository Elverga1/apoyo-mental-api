// src/services/authService.js
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class AuthService {
  async register(userData) {
    try {
      const response = await axios.post(`${API_URL}/auth/register`, {
        email: userData.email,
        username: userData.username,
        full_name: userData.fullName,
        password: userData.password
      });
      console.log('Registro exitoso:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error en registro:', error.response?.data);
      throw error.response?.data || { detail: 'Error en el registro' };
    }
  }

  async login(username, password) {
    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);
      
      const response = await axios.post(`${API_URL}/auth/login`, formData);
      
      console.log('Login response:', response.data);
      
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('username', username);
        console.log('Token guardado:', response.data.access_token);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Error en login:', error.response?.data);
      throw error.response?.data || { detail: 'Error en el login' };
    }
  }

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    console.log('Sesión cerrada');
  }

  getToken() {
    const token = localStorage.getItem('token');
    console.log('Token actual:', token ? 'Existe' : 'No existe');
    return token;
  }

  isAuthenticated() {
    const isAuth = !!this.getToken();
    console.log('Usuario autenticado:', isAuth);
    return isAuth;
  }

  getUsername() {
    return localStorage.getItem('username');
  }
}

export default new AuthService();
