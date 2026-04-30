import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import DashboardLayout from './pages/DashboardLayout';
import DashboardPage from './pages/DashboardPage';
import SimulacroPage from './pages/SimulacroPage';
import SimulacroSession from './pages/SimulacroSession';
import FlashcardsPage from './pages/FlashcardsPage';
import FeynmanPage from './pages/FeynmanPage';
import AdminPage from './pages/AdminPage';
import TemasDebilesPage from './pages/TemasDebilesPage';
import ComunidadPage from './pages/ComunidadPage';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const hasToken = localStorage.getItem('access_token');
  console.log('>>> ProtectedRoute - Token:', hasToken ? 'SI' : 'NO');
  
  if (!hasToken) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
}

function ExternalRedirect({ url }: { url: string }) {
  const search = window.location.search;
  const targetUrl = search ? `${url}${search}` : url;
  window.location.href = targetUrl;
  return null;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        
        {/* Google OAuth redirect - public routes */}
        <Route path="/auth/google" element={<ExternalRedirect url="https://akademus.onrender.com/auth/google" />} />
        <Route path="/auth/google/callback" element={<ExternalRedirect url="https://akademus.onrender.com/auth/google/callback" />} />
        
        <Route path="/" element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="simulacros" element={<SimulacroPage />} />
          <Route path="simulacros/:id" element={<SimulacroSession />} />
          <Route path="flashcards" element={<FlashcardsPage />} />
          <Route path="feynman" element={<FeynmanPage />} />
          <Route path="admin" element={<AdminPage />} />
          <Route path="temas-debiles" element={<TemasDebilesPage />} />
          <Route path="comunidad" element={<ComunidadPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}