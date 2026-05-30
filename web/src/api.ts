import axios from 'axios'

// Keep the backend URL in one place so future API calls stay consistent.
const api = axios.create({
  baseURL: 'http://localhost:8000',
})

export default api
