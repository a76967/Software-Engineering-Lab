import axios from 'axios';

const ROOT_API_URL = 'http://localhost:8000';

export default {
  register(userData) {
    return axios.post(`${ROOT_API_URL}/register/`, userData);
  }
};