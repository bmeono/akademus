import { useState } from 'react';
import { Mail, Lock, Phone, User } from 'lucide-react';
import { Button } from '../common/Button';
import { Input } from '../common/Card';
import { authAPI } from '../../services/api';
import { useAppStore } from '../../store';

interface LoginFormProps {
  onSwitchToRegister: () => void;
}

export function LoginForm({ onSwitchToRegister }: LoginFormProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { setUser, setAuthenticated } = useAppStore();
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const { data } = await authAPI.login({ email, password });
      
      // Si tiene requires_2fa o no tiene access_token, ir a 2FA
      if (data.requires_2fa || !data.access_token) {
        localStorage.setItem('temp_token', data.temp_token);
        window.location.href = '/verify-2fa';
      } else {
        // Guardar tokens y redirigir
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        window.location.href = '/dashboard';
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al iniciar sesión');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="text-center mb-6">
        <h1 className="text-3xl font-display font-bold text-slate-900">Bienvenido</h1>
        <p className="text-slate-500 mt-1">Inicia sesión para continuar</p>
      </div>
      
      {error && (
        <div className="p-3 bg-error-50 border border-error-200 rounded-lg text-error-700 text-sm">
          {error}
        </div>
      )}
      
      <div className="relative">
        <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
        <input
          type="email"
          placeholder="Correo electrónico"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full pl-12 pr-4 py-3 rounded-xl border-2 border-slate-200 bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 focus:outline-none transition-all"
          required
        />
      </div>
      
      <div className="relative">
        <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
        <input
          type="password"
          placeholder="Contraseña"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full pl-12 pr-4 py-3 rounded-xl border-2 border-slate-200 bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 focus:outline-none transition-all"
          required
        />
      </div>
      
      <Button type="submit" loading={loading} className="w-full">
        Iniciar Sesión
      </Button>
      
      <p className="text-center text-slate-500 text-sm">
        ¿No tienes cuenta?{' '}
        <button type="button" onClick={onSwitchToRegister} className="text-primary-600 hover:underline font-medium">
          Regístrate
        </button>
      </p>
    </form>
  );
}

interface RegisterFormProps {
  onSwitchToLogin: () => void;
}

export function RegisterForm({ onSwitchToLogin }: RegisterFormProps) {
  const [nombre, setNombre] = useState('');
  const [email, setEmail] = useState('');
  const [telefono, setTelefono] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const { data } = await authAPI.register({ nombre_completo: nombre, email, telefono, password });
      localStorage.setItem('temp_token', data.temp_token);
      window.location.href = '/verify-otp';
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al registrar');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="text-center mb-6">
        <h1 className="text-3xl font-display font-bold text-slate-900">Crear Cuenta</h1>
        <p className="text-slate-500 mt-1">Únete a Akademus</p>
      </div>
      
      {error && (
        <div className="p-3 bg-error-50 border border-error-200 rounded-lg text-error-700 text-sm">
          {error}
        </div>
      )}
      
      <div className="relative">
        <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
        <input
          type="text"
          placeholder="Nombre completo"
          value={nombre}
          onChange={(e) => setNombre(e.target.value)}
          className="w-full pl-12 pr-4 py-3 rounded-xl border-2 border-slate-200 bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 focus:outline-none transition-all"
          required
        />
      </div>
      
      <div className="relative">
        <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
        <input
          type="email"
          placeholder="Correo electrónico"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full pl-12 pr-4 py-3 rounded-xl border-2 border-slate-200 bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 focus:outline-none transition-all"
          required
        />
      </div>
      
      <div className="relative">
        <Phone className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
        <input
          type="tel"
          placeholder="Teléfono (+51...)"
          value={telefono}
          onChange={(e) => setTelefono(e.target.value)}
          className="w-full pl-12 pr-4 py-3 rounded-xl border-2 border-slate-200 bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 focus:outline-none transition-all"
          required
        />
      </div>
      
      <div className="relative">
        <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
        <input
          type="password"
          placeholder="Contraseña"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full pl-12 pr-4 py-3 rounded-xl border-2 border-slate-200 bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 focus:outline-none transition-all"
          required
          minLength={6}
        />
      </div>
      
      <Button type="submit" loading={loading} className="w-full">
        Crear Cuenta
      </Button>
      
      <p className="text-center text-slate-500 text-sm">
        ¿Ya tienes cuenta?{' '}
        <button type="button" onClick={onSwitchToLogin} className="text-primary-600 hover:underline font-medium">
          Inicia sesión
        </button>
      </p>
    </form>
  );
}