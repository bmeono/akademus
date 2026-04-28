import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { dashboardAPI } from '../services/api';
import { useAppStore } from '../store';
import { Activity, Flame, Target, BookOpen, Brain, TrendingUp, AlertTriangle, ArrowUp, ArrowDown, CheckCircle, XCircle, MinusCircle } from 'lucide-react';
import { Card } from '../components/common/Card';

export default function DashboardPage() {
  const navigate = useNavigate();
  const { permisos } = useAppStore();
  const [resumen, setResumen] = useState<any>(null);
  const [evolucion, setEvolucion] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [asignaturasConErrores, setAsignaturasConErrores] = useState(0);
  const [ultimoSimulacro, setUltimoSimulacro] = useState<any>(null);

  useEffect(() => {
    if (permisos && permisos.dashboard === false) {
      navigate('/simulacros');
      return;
    }
    const loadData = async () => {
      try {
        const [resData, evoData, statsData, temasData, ultimoData] = await Promise.all([
          dashboardAPI.getResumen(),
          dashboardAPI.getEvolucion(),
          dashboardAPI.getEstadisticasUsuario(),
          dashboardAPI.getTemasDebilesDetalle(),
          dashboardAPI.getUltimoSimulacro(),
        ]);
        setResumen(resData.data);
        setEvolucion(evoData.data);
        setStats(statsData.data);
        setAsignaturasConErrores(temasData.data.length);
        setUltimoSimulacro(ultimoData.data);
      } catch (e) {
        console.error(e);
      }
    };
    loadData();
  }, []);
  
  if (!resumen) {
    return <div className="flex items-center justify-center h-64"><div className="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full"></div></div>;
  }
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-display font-bold text-slate-900">Dashboard</h1>
          <p className="text-slate-500">Bienvenido de nuevo</p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 bg-warning-50 rounded-xl">
          <Flame className="w-5 h-5 text-warning-500" />
          <span className="font-semibold text-warning-600">{resumen.racha_dias} días</span>
          <span className="text-slate-500">racha</span>
        </div>
      </div>
      
      {/* Stats grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="flex items-center gap-4">
          <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
            <Target className="w-6 h-6 text-primary-600" />
          </div>
          <div>
            <p className="text-2xl font-bold text-slate-900">{resumen.promedio_aciertos}%</p>
            <p className="text-sm text-slate-500">Aciertos</p>
          </div>
        </Card>
        
        <Card className="flex items-center gap-4">
          <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
            <ArrowUp className="w-6 h-6 text-green-600" />
          </div>
          <div>
            <p className="text-2xl font-bold text-green-600">{stats?.max_puntaje?.toFixed(2) || '-'}</p>
            <p className="text-sm text-slate-500">Máximo puntaje</p>
          </div>
        </Card>

        <Card className="flex items-center gap-4">
          <div className="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center">
            <ArrowDown className="w-6 h-6 text-red-600" />
          </div>
          <div>
            <p className="text-2xl font-bold text-red-600">{stats?.min_puntaje?.toFixed(2) || '-'}</p>
            <p className="text-sm text-slate-500">Mínimo puntaje</p>
          </div>
        </Card>

        <Card className="flex items-center gap-4">
          <div className="w-12 h-12 bg-error-100 rounded-xl flex items-center justify-center">
            <Brain className="w-6 h-6 text-error-600" />
          </div>
          <div>
            <p className="text-2xl font-bold text-slate-900">{asignaturasConErrores}</p>
            <p className="text-sm text-slate-500">Asignaturas con errores</p>
          </div>
        </Card>
      </div>
      
      {/* Gráfico de Evolución + Último Simulacro */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/*
        <Card>
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-primary-600" />
            <h2 className="text-lg font-semibold">Evolución</h2>
          </div>
          <div className="h-40 flex items-end gap-2">
            {evolucion.map((item, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-2">
                <div 
                  className="w-full bg-primary-500 rounded-t-lg transition-all hover:bg-primary-600"
                  style={{ height: `${item.promedio_aciertos}%` }}
                />
                <span className="text-xs text-slate-500">{item.semana}</span>
              </div>
            ))}
          </div>
        </Card>
        */}

        {/* Último Simulacro (barras apiladas) */}
        <Card>
          <div className="flex items-center gap-2 mb-4">
            <Activity className="w-5 h-5 text-primary-600" />
            <h2 className="text-lg font-semibold">Último Simulacro</h2>
          </div>
          {ultimoSimulacro && ultimoSimulacro.total > 0 ? (
            <div className="space-y-4">
              {/* Barra visual */}
              <div className="h-8 rounded-lg overflow-hidden flex">
                {ultimoSimulacro.buenas > 0 && (
                  <div 
                    className="h-full bg-green-500 flex items-center justify-center transition-all"
                    style={{ width: `${(ultimoSimulacro.buenas / ultimoSimulacro.total) * 100}%` }}
                  />
                )}
                {ultimoSimulacro.malas > 0 && (
                  <div 
                    className="h-full bg-red-500 flex items-center justify-center transition-all"
                    style={{ width: `${(ultimoSimulacro.malas / ultimoSimulacro.total) * 100}%` }}
                  />
                )}
                {ultimoSimulacro.no_respondidas > 0 && (
                  <div 
                    className="h-full bg-slate-400 flex items-center justify-center transition-all"
                    style={{ width: `${(ultimoSimulacro.no_respondidas / ultimoSimulacro.total) * 100}%` }}
                  />
                )}
              </div>
              
              {/* Leyenda */}
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="flex items-center justify-center gap-1 mb-1">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span className="font-semibold text-green-600">{ultimoSimulacro.buenas}</span>
                  </div>
                  <p className="text-xs text-slate-500">Buenas ({Math.round(ultimoSimulacro.buenas / ultimoSimulacro.total * 100)}%)</p>
                </div>
                <div>
                  <div className="flex items-center justify-center gap-1 mb-1">
                    <XCircle className="w-4 h-4 text-red-500" />
                    <span className="font-semibold text-red-600">{ultimoSimulacro.malas}</span>
                  </div>
                  <p className="text-xs text-slate-500">Malas ({Math.round(ultimoSimulacro.malas / ultimoSimulacro.total * 100)}%)</p>
                </div>
                <div>
                  <div className="flex items-center justify-center gap-1 mb-1">
                    <MinusCircle className="w-4 h-4 text-slate-400" />
                    <span className="font-semibold text-slate-600">{ultimoSimulacro.no_respondidas}</span>
                  </div>
                  <p className="text-xs text-slate-500">Sin responder ({Math.round(ultimoSimulacro.no_respondidas / ultimoSimulacro.total * 100)}%)</p>
                </div>
              </div>
              <div className="pt-2 border-t text-center">
                <span className="font-semibold text-slate-900">Total: {ultimoSimulacro.total}</span>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-slate-500">
              <BookOpen className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>No hay simulacros completados</p>
            </div>
          )}
        </Card>
      </div>
      
      {/* Temas débiiles */}
      {resumen.temas_debiles?.length > 0 && (
        <Card>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-error-600" />
              <h2 className="text-lg font-semibold">Temas a mejorar</h2>
            </div>
            <a href="/temas-debiles" className="text-sm text-primary-600 hover:underline">
              Ver detalle
            </a>
          </div>
          <div className="space-y-2">
            {resumen.temas_debiles.map((tema: any) => (
              <div key={tema.tema_id} className="flex items-center justify-between p-3 bg-error-50 rounded-lg border border-error-200">
                <span className="font-medium text-error-700">{tema.nombre}</span>
                <span className="font-bold text-error-600">{tema.porcentaje}%</span>
              </div>
            ))}
          </div>
          <a href="/temas-debiles" className="mt-4 btn-primary inline-flex w-full justify-center">
            Reforzar temas
          </a>
        </Card>
      )}
    </div>
  );
}