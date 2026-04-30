import { useEffect, useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { useAppStore } from '../store';
import { usersAPI, adminAPI } from '../services/api';
import { usersAPI as authService } from '../services/api';
import { LayoutDashboard, BookOpen, Brain, LogOut, User, Settings, AlertTriangle, MessageCircle } from 'lucide-react';

export default function DashboardLayout() {
  const { user, logout, setUser, setAuthenticated, setPermisos, permisos } = useAppStore();
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const init = async () => {
      if (user && permisos) {
        setLoading(false);
        return;
      }

      const tryFetch = async (attempt: number): Promise<boolean> => {
        try {
          const { data } = await usersAPI.me();
          setUser(data);
          setAuthenticated(true);

          try {
            const perms = await adminAPI.getMisPermisos();
            setPermisos(perms.data);
          } catch {
            setPermisos({});
          }
          return true;
        } catch {
          if (attempt < 2) {
            await new Promise(r => setTimeout(r, 2000));
            return tryFetch(attempt + 1);
          }
          return false;
        }
      };

      const success = await tryFetch(0);
      if (!success) {
        logout();
        navigate('/login');
      }
      setLoading(false);
    };
    init();
  }, []);

  const handleLogout = async () => {
    try {
      await authService.logout();
    } catch {}
    localStorage.clear();
    logout();
    navigate('/login');
  };

  const menuItems = [
    permisos?.dashboard && { icon: LayoutDashboard, label: 'Dashboard', href: '/dashboard' },
    permisos?.simulacros && { icon: BookOpen, label: 'Simulacros', href: '/simulacros' },
    permisos?.temas_debiles && { icon: AlertTriangle, label: 'Temas Débiles', href: '/temas-debiles' },
    permisos?.flashcards && { icon: Brain, label: 'Flashcards', href: '/flashcards' },
    permisos?.comunidad && { icon: MessageCircle, label: 'Comunidad AKADEMUS', href: '/comunidad' },
  ].filter(Boolean);

  const isAdmin = user?.rol_id === 1;
  if (isAdmin && permisos?.admin !== false) {
    menuItems.push({ icon: Settings, label: 'Admin', href: '/admin' });
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 flex">
      <aside className="w-64 bg-white border-r border-slate-200 fixed h-full">
        <div className="p-6">
          <h1 className="text-2xl font-display font-bold text-gradient">Akademus</h1>
        </div>

        <nav className="px-4 space-y-1">
          {menuItems.map((item) => (
            <a 
              key={item.href}
              href={item.href}
              className="flex items-center gap-3 px-4 py-3 rounded-xl text-slate-600 hover:bg-slate-100 hover:text-primary-600 transition-colors"
             >
              <item.icon className="w-5 h-5" />
              {item.label}
            </a>
          ))}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-200">
          <div className="flex items-center gap-3 px-4 py-3 mb-2">
            <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-primary-600" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-medium text-slate-900 truncate">{user?.nombre || 'Usuario'}</p>
              <p className="text-xs text-slate-500 truncate">{user?.email}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-slate-600 hover:bg-slate-100 hover:text-error-600 transition-colors"
          >
            <LogOut className="w-5 h-5" />
            Cerrar Sesión
          </button>
        </div>
      </aside>

      <main className="flex-1 ml-64 p-8">
        <Outlet />
      </main>
    </div>
  );
}
