import { useState, useEffect } from 'react';
import { LoginForm, RegisterForm } from '../components/auth/AuthForms';
import { GraduationCap } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';

export default function LoginPage() {
  const [modo, setModo] = useState<'login' | 'register'>('login');
  const [searchParams] = useSearchParams();
  
  // Handle Google OAuth callback
  useEffect(() => {
    const accessToken = searchParams.get('access_token');
    const refreshToken = searchParams.get('refresh_token');
    const googleLogin = searchParams.get('google_login');
    
    if (accessToken && refreshToken && googleLogin) {
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshToken);
      window.location.href = '/dashboard';
    }
  }, [searchParams]);
  
  // Si ya tiene token, ir directamente al dashboard
  if (localStorage.getItem('access_token')) {
    window.location.href = '/dashboard';
    return null;
  }
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-primary-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-600 rounded-2xl shadow-lg shadow-primary-600/25 mb-4">
            <GraduationCap className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl font-display font-bold text-gradient">Akademus</h1>
          <p className="text-slate-500 mt-1">Simulador de Exámenes de Admisión</p>
        </div>
        
        <div className="bg-white rounded-2xl shadow-xl p-8 border border-slate-100">
          {modo === 'login' ? (
            <LoginForm onSwitchToRegister={() => setModo('register')} />
          ) : (
            <RegisterForm onSwitchToLogin={() => setModo('login')} />
          )}
        </div>
        
        <p className="text-center text-slate-400 text-sm mt-6">
          © 2024 Akademus. Todos los derechos reservados.
        </p>
      </div>
    </div>
  );
}