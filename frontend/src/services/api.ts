import axios, { AxiosInstance, AxiosError } from 'axios';

// API base URL - production backend on Render
const API_URL = 'https://akademus.onrender.com';

// Instancia de axios
const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    console.log('>>> API Interceptor - Token:', token ? token.substring(0, 20) + '...' : 'NULO');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para manejar errores
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;
    
    // Si 401 y no hemos reintentado, intenta refresh
    if (error.response?.status === 401 && originalRequest && !(originalRequest as any)._retry) {
      (originalRequest as any)._retry = true;
      
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_URL}/auth/refresh`, {}, {
            headers: { Authorization: `Bearer ${refreshToken}` }
          });
          
          const { access_token, refresh_token } = response.data;
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);
          
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        } catch {
          logout();
        }
      }
    }
    
    return Promise.reject(error);
  }
);

// Auth
export const authAPI = {
  register: (data: any) => api.post('/auth/register', data),
  login: (data: any) => api.post('/auth/login', data),
  verifyOTP: (data: any) => api.post('/auth/verify-otp', data),
  verify2FA: (data: any) => api.post('/auth/verify-2fa', data),
  refresh: () => api.post('/auth/refresh'),
  logout: () => api.post('/auth/logout'),
};

// Users
export const usersAPI = {
  me: () => api.get('/users/me'),
  update: (data: any) => api.put('/users/me', data),
  getEspecialidades: () => api.get('/users/especialidades'),
  getGrupos: () => api.get('/users/especialidades/grupos'),
};

// Simulacros
export const simulacrosAPI = {
  getConfig: () => api.get('/simulacros/config'),
  getEspecialidades: () => api.get('/simulacros/especialidades'),
  iniciar: (data: any) => api.post('/simulacros/iniciar', data),
  iniciarPorEspecialidad: (data: any) => api.post('/simulacros/iniciar-por-especialidad', data),
  getPregunta: (id: number, orden: number) => api.get(`/simulacros/${id}/pregunta/${orden}`),
  getTodasPreguntas: (id: number) => api.get(`/simulacros/${id}/todas`),
  getResultado: (id: number) => api.get(`/simulacros/${id}/resultado`),
  responder: (id: number, data: any) => api.post(`/simulacros/${id}/responder`, data),
  finalizar: (id: number, respuestas: any[]) => api.post(`/simulacros/${id}/finalizar`, { respuestas }),
  historial: () => api.get('/simulacros/historial'),
  downloadResultadoPDF: (id: number) => {
    const token = localStorage.getItem('access_token');
    window.open(`https://akademus.onrender.com/simulacros/${id}/resultado-pdf?token=${token}`, '_blank');
  },
};

// Flashcards
export const flashcardsAPI = {
  getAsignaturas: () => api.get('/flashcards/asignaturas'),
  getPreguntasPorAsignatura: (asignaturaId: number) => api.get(`/flashcards/asignatura/${asignaturaId}/preguntas`),
  responder: (preguntaId: number, correcta: boolean) => api.post('/flashcards/responder', { pregunta_id: preguntaId, correcta }),
  getProgreso: () => api.get('/flashcards/progreso'),
  setup: () => api.get('/flashcards/init'),
};

//Dashboard
export const feynmanAPI = {
  getTemas: () => api.get('/feynman/temas'),
  enviarExplicacion: (data: any) => api.post('/feynman/explicacion', data),
  getMisExplicaciones: () => api.get('/feynman/mis-explicaciones'),
  getPendientes: () => api.get('/admin/feynman/pendientes'),
  calificar: (id: number, data: any) => api.put(`/admin/feynman/${id}/calificar`, data),
};

// Dashboard
export const dashboardAPI = {
  getResumen: () => api.get('/dashboard/resumen'),
  getEvolucion: () => api.get('/dashboard/evolucion'),
  getTemasDebiles: () => api.get('/dashboard/temas-debiles'),
  getEstadisticasUsuario: () => api.get('/dashboard/estadisticas-usuario'),
  getTemasDebilesDetalle: () => api.get('/dashboard/temas-debiles-detalle'),
  getPreguntasFalladas: (asignaturaId: number) => api.get(`/dashboard/temas-debiles/${asignaturaId}/preguntas`),
  getUltimoSimulacro: () => api.get('/dashboard/ultimo-simulacro'),
};

// Admin - Permisos
export const adminAPI = {
  getUsuariosPermisos: () => api.get('/admin/usuarios-permisos'),
  updatePermiso: (data: any) => api.put('/admin/usuarios-permisos', data),
  getMisPermisos: () => api.get('/admin/mis-permisos'),
  initPermisos: () => api.get('/admin/init-permisos'),
};

function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  window.location.href = '/login';
}

// Comunidad IA
export const comunidadAPI = {
  getAsignaturas: () => api.get('/comunidad/asignaturas'),
  consultar: (materia: string, pregunta: string) => api.post('/comunidad/consultar', { materia, pregunta }),
  getHistorial: () => api.get('/comunidad/historial'),
  getCreditos: () => api.get('/comunidad/creditos'),
};

export default api;