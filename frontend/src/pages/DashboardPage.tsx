import { useEffect, useState, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { dashboardAPI } from '../services/api';
import api from '../services/api';
import { useAppStore } from '../store';
import {
  Flame, Target, BookOpen, Brain, AlertTriangle,
  ArrowUp, ArrowDown, TrendingUp, ChevronRight, BarChart2,
  CheckCircle, XCircle, MinusCircle, ChevronLeft,
} from 'lucide-react';
import { Card } from '../components/common/Card';

// ── Barra apilada horizontal ──────────────────────────────────────────────────
function BarraSimulacro({ correctas, incorrectas, blancos, total }: {
  correctas: number; incorrectas: number; blancos: number; total: number;
}) {
  if (total === 0) return null;
  const pctC = Math.round((correctas  / total) * 100);
  const pctI = Math.round((incorrectas / total) * 100);
  const pctB = Math.round((blancos     / total) * 100);

  return (
    <div className="space-y-4">
      {/* Barra apilada */}
      <div className="relative h-10 rounded-xl overflow-hidden flex bg-slate-100">
        {correctas > 0 && (
          <div
            className="h-full bg-green-500 flex items-center justify-center transition-all duration-700"
            style={{ width: `${pctC}%` }}
          >
            {pctC >= 8 && (
              <span className="text-white text-xs font-bold drop-shadow">{pctC}%</span>
            )}
          </div>
        )}
        {incorrectas > 0 && (
          <div
            className="h-full bg-red-500 flex items-center justify-center transition-all duration-700"
            style={{ width: `${pctI}%` }}
          >
            {pctI >= 8 && (
              <span className="text-white text-xs font-bold drop-shadow">{pctI}%</span>
            )}
          </div>
        )}
        {blancos > 0 && (
          <div
            className="h-full bg-slate-400 flex items-center justify-center transition-all duration-700"
            style={{ width: `${pctB}%` }}
          >
            {pctB >= 8 && (
              <span className="text-white text-xs font-bold drop-shadow">{pctB}%</span>
            )}
          </div>
        )}
      </div>

      {/* Leyenda debajo de la barra */}
      <div className="grid grid-cols-3 gap-3">
        <div className="flex items-center gap-3 p-3 bg-green-50 rounded-xl border border-green-100">
          <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
          <div>
            <p className="text-xl font-bold text-green-700">{correctas}</p>
            <p className="text-xs text-green-600">Correctas · {pctC}%</p>
          </div>
        </div>
        <div className="flex items-center gap-3 p-3 bg-red-50 rounded-xl border border-red-100">
          <XCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
          <div>
            <p className="text-xl font-bold text-red-700">{incorrectas}</p>
            <p className="text-xs text-red-600">Incorrectas · {pctI}%</p>
          </div>
        </div>
        <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-xl border border-slate-200">
          <MinusCircle className="w-5 h-5 text-slate-400 flex-shrink-0" />
          <div>
            <p className="text-xl font-bold text-slate-600">{blancos}</p>
            <p className="text-xs text-slate-500">Sin resp. · {pctB}%</p>
          </div>
        </div>
      </div>

      <div className="flex justify-between text-xs text-slate-400 pt-1 border-t border-slate-100">
        <span>Total preguntas: <strong className="text-slate-600">{total}</strong></span>
      </div>
    </div>
  );
}

// ── Slider de publicidad ──────────────────────────────────────────────────────
interface Anuncio { id: number; imagen_url: string; enlace_url?: string; descripcion?: string; }

function SliderPublicidad({ anuncios }: { anuncios: Anuncio[] }) {
  const [current, setCurrent] = useState(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const resetTimer = () => {
    if (timerRef.current) clearInterval(timerRef.current);
    if (anuncios.length > 1) {
      timerRef.current = setInterval(() => {
        setCurrent(prev => (prev + 1) % anuncios.length);
      }, 4000);
    }
  };

  useEffect(() => {
    resetTimer();
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, [anuncios.length]);

  const goTo = (idx: number) => {
    setCurrent(idx);
    resetTimer();
  };

  const prev = () => goTo((current - 1 + anuncios.length) % anuncios.length);
  const next = () => goTo((current + 1) % anuncios.length);

  if (anuncios.length === 0) return null;

  const anuncio = anuncios[current];

  return (
    <div className="relative w-full rounded-2xl overflow-hidden bg-slate-800 shadow-lg select-none" style={{ height: '140px' }}>
      {/* Imagen */}
      {anuncio.enlace_url ? (
        <a href={anuncio.enlace_url} target="_blank" rel="noopener noreferrer" className="block w-full h-full">
          <img
            src={anuncio.imagen_url}
            alt={anuncio.descripcion || 'Publicidad'}
            className="w-full h-full object-cover transition-opacity duration-500"
            key={anuncio.id}
          />
        </a>
      ) : (
        <img
          src={anuncio.imagen_url}
          alt={anuncio.descripcion || 'Publicidad'}
          className="w-full h-full object-cover transition-opacity duration-500"
          key={anuncio.id}
        />
      )}

      {/* Controles (solo si hay más de 1) */}
      {anuncios.length > 1 && (
        <>
          <button
            onClick={prev}
            className="absolute left-2 top-1/2 -translate-y-1/2 w-7 h-7 bg-black/40 hover:bg-black/60 rounded-full flex items-center justify-center text-white transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <button
            onClick={next}
            className="absolute right-2 top-1/2 -translate-y-1/2 w-7 h-7 bg-black/40 hover:bg-black/60 rounded-full flex items-center justify-center text-white transition-colors"
          >
            <ChevronRight className="w-4 h-4" />
          </button>

          {/* Puntos indicadores */}
          <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex gap-1.5">
            {anuncios.map((_, i) => (
              <button
                key={i}
                onClick={() => goTo(i)}
                className={`rounded-full transition-all ${
                  i === current ? 'w-5 h-2 bg-white' : 'w-2 h-2 bg-white/50'
                }`}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}

// ── Página principal ──────────────────────────────────────────────────────────
export default function DashboardPage() {
  const navigate = useNavigate();
  const { permisos, user } = useAppStore();
  const [resumen, setResumen]                         = useState<any>(null);
  const [stats, setStats]                             = useState<any>(null);
  const [asignaturasConErrores, setAsignaturasConErrores] = useState(0);
  const [ultimoSimulacro, setUltimoSimulacro]         = useState<any>(null);
  const [anuncios, setAnuncios]                       = useState<Anuncio[]>([]);
  const [loading, setLoading]                         = useState(true);

  useEffect(() => {
    if (permisos && permisos.dashboard === false) { navigate('/simulacros'); return; }
    const load = async () => {
      try {
        const [resData, statsData, temasData, ultimoData, pubData] = await Promise.all([
          dashboardAPI.getResumen(),
          dashboardAPI.getEstadisticasUsuario(),
          dashboardAPI.getTemasDebilesDetalle(),
          dashboardAPI.getUltimoSimulacro(),
          api.get('/publicidad').catch(() => ({ data: [] })),
        ]);
        setResumen(resData.data);
        setStats(statsData.data);
        const temas = temasData.data?.asignaturas || temasData.data;
        setAsignaturasConErrores(Array.isArray(temas) ? temas.length : 0);
        setUltimoSimulacro(ultimoData.data);
        setAnuncios(pubData.data || []);
      } catch (e) { console.error(e); }
      finally { setLoading(false); }
    };
    load();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full" />
      </div>
    );
  }
  if (!resumen) {
    return <div className="flex items-center justify-center h-64 text-slate-500">Error al cargar. Recarga la página.</div>;
  }

  const tieneSimulacro = ultimoSimulacro && ultimoSimulacro.total > 0;

  return (
    <div className="space-y-6">
      {/* ── Header ── */}
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

      {/* ── Métricas ── */}
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

      {/* ── Último simulacro + Accesos rápidos ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Barra apilada */}
        <Card className="lg:col-span-2">
          <div className="flex items-center gap-2 mb-5">
            <BarChart2 className="w-5 h-5 text-primary-600" />
            <h2 className="text-lg font-semibold text-slate-900">Último Simulacro</h2>
          </div>
          {tieneSimulacro ? (
            <BarraSimulacro
              correctas={ultimoSimulacro.buenas}
              incorrectas={ultimoSimulacro.malas}
              blancos={ultimoSimulacro.no_respondidas}
              total={ultimoSimulacro.total}
            />
          ) : (
            <div className="text-center py-10 text-slate-400">
              <BookOpen className="w-12 h-12 mx-auto mb-3 opacity-40" />
              <p className="font-medium">Sin simulacros completados</p>
              <p className="text-sm mt-1">Realiza tu primer simulacro para ver estadísticas</p>
              <Link
                to="/simulacros"
                className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-xl text-sm font-medium hover:bg-primary-700 transition-colors"
              >
                Iniciar simulacro
              </Link>
            </div>
          )}
        </Card>

        {/* Accesos rápidos */}
        <div className="space-y-3">
          <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wide px-1">Accesos rápidos</h2>
          {[
            { to: '/simulacros',    icon: BookOpen,      label: 'Nuevo Simulacro', desc: 'Practica con preguntas reales',  bg: 'bg-blue-50 border-blue-100',     color: 'text-blue-600'   },
            { to: '/flashcards',    icon: Brain,         label: 'Flashcards',       desc: 'Repasa tus errores',             bg: 'bg-purple-50 border-purple-100', color: 'text-purple-600' },
            { to: '/temas-debiles', icon: AlertTriangle, label: 'Temas Débiles',    desc: 'Identifica áreas a mejorar',     bg: 'bg-orange-50 border-orange-100', color: 'text-orange-600' },
          ].map(item => (
            <Link key={item.to} to={item.to}
              className={`flex items-center gap-4 p-4 rounded-xl border ${item.bg} hover:shadow-sm transition-all group`}
            >
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

      {/* ── Temas débiles ── */}
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
          <Link to="/temas-debiles"
            className="mt-4 flex items-center justify-center gap-2 w-full py-2.5 bg-primary-600 text-white rounded-xl text-sm font-medium hover:bg-primary-700 transition-colors"
          >
            <TrendingUp className="w-4 h-4" />
            Reforzar temas débiles
          </Link>
        </Card>
      )}

      {/* ── Slider de publicidad ── */}
      {anuncios.length > 0 && (
        <div>
          <p className="text-xs text-slate-400 mb-2 text-right">Publicidad</p>
          <SliderPublicidad anuncios={anuncios} />
        </div>
      )}
    </div>
  );
}
