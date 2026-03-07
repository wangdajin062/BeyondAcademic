import axios from 'axios';
import { LoginRequest, LoginResponse } from '../types/auth';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export const authAPI = {
  async testLogin(payload: LoginRequest): Promise<LoginResponse> {
    const response = await axios.post(`${API_BASE_URL}/auth/test-login`, payload);
    return response.data;
  },
};
