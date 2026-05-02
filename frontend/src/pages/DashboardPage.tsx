import { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { dashboardAPI } from '../services/api';
import { useAppStore } from '../store';
import {
  Flame, Target, BookOpen, Brain, AlertTriangle,
  ArrowUp, ArrowDown, TrendingUp, ChevronRight, BarChart2,
} from 'lucide-react';
import { Card } from '../components/common/Card';

function DonutChart({ correctas, incorrectas, blancos, total }: {
  correctas: number; incorrectas: number; blancos: number; total: number;
}) {
  if (total === 0) return null;
  const cx = 80, cy = 80, r = 60, stroke = 22;
  const circ = 2 * Math.PI * r;
  const pctC = correctas / total;
  const pctI = incorrectas / total;
  const pctB = blancos / total;
  const dashC = circ * pctC;
  const dashI = circ * pctI;
  const dashB = circ * pctB;
  const offC = 0;
  const offI = circ * (1 - pctC);
  const offB = circ * (1 - pctC - pctI);

  return (
    <div className="flex items-center gap-8">
      <svg width="160" height="160" viewBox="0 0 160 160" className="flex-shrink-0">
        <circle cx={cx} cy={cy} r={r} fill="none" stroke="#f1f5f9" strokeWidth={stroke} />
        {pctB > 0 && (
          <circle cx={cx} cy={cy} r={r} fill="none" stroke="#94a3b8" strokeWidth={stroke}
            strokeDasharray={`${dashB} ${circ - dashB}`} strokeDashoffset={offB}
            strokeLinecap="butt" transform="rotate(-90 80 80)" />
        )}
        {pctI > 0 && (
          <circle cx={cx} cy={cy} r={r} fill="none" stroke="#ef4444" strokeWidth={stroke}
            strokeDasharray={`${dashI} ${circ - dashI}`} strokeDashoffset={offI}
            strokeLinecap="butt" transform="rotate(-90 80 80)" />
        )}
        {pctC > 0 && (
          <circle cx={cx} cy={cy} r={r} fill="none" stroke="#22c55e" strokeWidth={stroke}
            strokeDasharray={`${dashC} ${circ - dashC}`} strokeDashoffset={offC}
            strokeLinecap="butt" transform="rotate(-90 80 80)" />
        )}
        <text x={cx} y={cy - 6} textAnchor="middle" fontSize="22" fontWeight="bold" fill="#1e293b">
          {Math.round(pctC * 100)}%
        </text>
        <text x={cx} y={cy + 14} textAnchor="middle" fontSize="10" fill="#64748b">aciertos</text>
      </svg>

      <div className="space-y-3 flex-1">
        {[
          { color: 'bg-green-500', label: 'Correctas',     value: correctas,   textColor: 'text-green-700' },
          { color: 'bg-red-500',   label: 'Incorrectas',   value: incorrectas, textColor: 'text-red-700' },
          { color: 'bg-slate-400', label: 'Sin responder', value: blancos,     textColor: 'text-slate-600' },
        ].map(({ color, label, value, textColor }) => (
          <div key={label} className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${color}`} />
              <span className="text-sm text-slate-600">{label}</span>
            </div>
            <span className={`font-bold ${textColor}`}>{value}</span>
          </div>
        ))}
        <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
          <span className="text-xs text-slate-400">Total preguntas</span>
          <span className="font-semibold text-slate-700">{total}</span>
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const navigate = useNavigate();
  const { permisos, user } = useAppStore();
  const [resumen, setResumen]                         = useState<any>(null);
  const [stats, setStats]                             = useState<any>(null);
  const [asignaturasConErrores, setAsignaturasConErrores] = useState(0);
  const [ultimoSimulacro, setUltimoSimulacro]         = useState<any>(null);
  const [loading, setLoading]                         = useState(true);

  useEffect(() => {
    if (permisos && permisos.dashboard === false) { navigate('/simulacros'); return; }
    const load = async () => {
      try {
        const [resData, statsData, temasData, ultimoData] = await Promise.all([
          dashboardAPI.getResumen(),
          dashboardAPI.getEstadisticasUsuario(),
          dashboardAPI.getTemasDebilesDetalle(),
          dashboardAPI.getUltimoSimulacro(),
        ]);
        setResumen(resData.data);
        setStats(statsData.data);
        const temas = temasData.data?.asignaturas || temasData.data;
        setAsignaturasConErrores(Array.isArray(temas) ? temas.length : 0);
        setUltimoSimulacro(ultimoData.data);
      } catch (e) { console.error(e); }
      finally { setLoading(false); }
    };
    load();
  }, []);

  if (loading) {
    return <div className="flex items-center justify-center h-64"><div className="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full" /></div>;
  }
  if (!resumen) {
    return <div className="flex items-center justify-center h-64 text-slate-500">Error al cargar. Recarga la página.</div>;
  }

  const tieneSimulacro = ultimoSimulacro && ultimoSimulacro.total > 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-display font-bold text-slate-900">
            Hola, {user?.nombre?.split(' ')[0] || 'Estudiante'} 👋
          </h1>
          <p className="text-slate-500 mt-0.5">Aquí está tu resumen de hoy</p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 bg-amber-50 border border-amber-200 rounded-xl">
          <Flame className="w-5 h-5 text-amber-500" />
          <span className="font-bold text-amber-600">{resumen.racha_dias}</span>
          <span className="text-slate-500 text-sm">días de racha</span>
        </div>
      </div>

      {/* Métricas */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="flex flex-col gap-3">
          <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
            <Target className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <p className="text-2xl font-bold text-slate-900">{resumen.promedio_aciertos}%</p>
            <p className="text-sm text-slate-500">Promedio aciertos</p>
          </div>
        </Card>
        <Card className="flex flex-col gap-3">
          <div className="w-10 h-10 bg-green-100 rounded-xl flex items-center justify-center">
            <ArrowUp className="w-5 h-5 text-green-600" />
          </div>
          <div>
            <p className="text-2xl font-bold text-green-600">{stats?.max_puntaje != null ? stats.max_puntaje.toFixed(2) : '—'}</p>
            <p className="text-sm text-slate-500">Mejor puntaje</p>
          </div>
        </Card>
        <Card className="flex flex-col gap-3">
          <div className="w-10 h-10 bg-red-100 rounded-xl flex items-center justify-center">
            <ArrowDown className="w-5 h-5 text-red-600" />
          </div>
          <div>
            <p className="text-2xl font-bold text-red-600">{stats?.min_puntaje != null ? stats.min_puntaje.toFixed(2) : '—'}</p>
            <p className="text-sm text-slate-500">Menor puntaje</p>
          </div>
        </Card>
        <Card className="flex flex-col gap-3">
          <div className="w-10 h-10 bg-orange-100 rounded-xl flex items-center justify-center">
            <AlertTriangle className="w-5 h-5 text-orange-600" />
          </div>
          <div>
            <p className="text-2xl font-bold text-slate-900">{asignaturasConErrores}</p>
            <p className="text-sm text-slate-500">Áreas a mejorar</p>
          </div>
        </Card>
      </div>

      {/* Pastel + Accesos rápidos */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <div className="flex items-center gap-2 mb-5">
            <BarChart2 className="w-5 h-5 text-primary-600" />
            <h2 className="text-lg font-semibold text-slate-900">Último Simulacro</h2>
          </div>
          {tieneSimulacro ? (
            <DonutChart
              correctas={ultimoSimulacro.buenas}
              incorrectas={ultimoSimulacro.malas}
              blancos={ultimoSimulacro.no_respondidas}
              total={ultimoSimulacro.total}
            />
          ) : (
            <div className="text-center py-10 text-slate-400">
              <BookOpen className="w-12 h-12 mx-auto mb-3 opacity-40" />
              <p className="font-medium">Sin simulacros completados</p>
              <Link to="/simulacros" className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-xl text-sm font-medium hover:bg-primary-700 transition-colors">
                Iniciar simulacro
              </Link>
            </div>
          )}
        </Card>

        <div className="space-y-3">
          <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wide px-1">Accesos rápidos</h2>
          {[
            { to: '/simulacros',    icon: BookOpen,      label: 'Nuevo Simulacro', desc: 'Practica con preguntas reales',  bg: 'bg-blue-50 border-blue-100',    color: 'text-blue-600'   },
            { to: '/flashcards',    icon: Brain,         label: 'Flashcards',       desc: 'Repasa tus errores',             bg: 'bg-purple-50 border-purple-100', color: 'text-purple-600' },
            { to: '/temas-debiles', icon: AlertTriangle, label: 'Temas Débiles',    desc: 'Identifica áreas a mejorar',     bg: 'bg-orange-50 border-orange-100', color: 'text-orange-600' },
          ].map(item => (
            <Link key={item.to} to={item.to} className={`flex items-center gap-4 p-4 rounded-xl border ${item.bg} hover:shadow-sm transition-all group`}>
              <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-white shadow-sm">
                <item.icon className={`w-5 h-5 ${item.color}`} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-slate-800 text-sm">{item.label}</p>
                <p className="text-xs text-slate-500 truncate">{item.desc}</p>
              </div>
              <ChevronRight className="w-4 h-4 text-slate-400 group-hover:translate-x-0.5 transition-transform" />
            </Link>
          ))}
        </div>
      </div>

      {/* Temas débiles */}
      {resumen.temas_debiles?.length > 0 && (
        <Card>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-orange-500" />
              <h2 className="text-lg font-semibold text-slate-900">Temas a reforzar</h2>
            </div>
            <Link to="/temas-debiles" className="text-sm text-primary-600 hover:underline flex items-center gap-1">
              Ver todo <ChevronRight className="w-4 h-4" />
            </Link>
          </div>
          <div className="space-y-2">
            {resumen.temas_debiles.slice(0, 5).map((tema: any) => (
              <div key={tema.tema_id} className="flex items-center justify-between p-3 bg-orange-50 rounded-xl border border-orange-100">
                <span className="font-medium text-orange-800 text-sm">{tema.nombre}</span>
                <div className="flex items-center gap-2">
                  <div className="w-20 h-2 bg-orange-200 rounded-full overflow-hidden">
                    <div className="h-full bg-orange-500 rounded-full" style={{ width: `${tema.porcentaje}%` }} />
                  </div>
                  <span className="text-sm font-bold text-orange-600 w-10 text-right">{tema.porcentaje}%</span>
                </div>
              </div>
            ))}
          </div>
          <Link to="/temas-debiles" className="mt-4 flex items-center justify-center gap-2 w-full py-2.5 bg-primary-600 text-white rounded-xl text-sm font-medium hover:bg-primary-700 transition-colors">
            <TrendingUp className="w-4 h-4" />
            Reforzar temas débiles
          </Link>
        </Card>
      )}
    </div>
  );
}
