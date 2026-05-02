import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { simulacrosAPI } from '../services/api';
import { useAppStore } from '../store';
import { Card } from '../components/common/Card';
import { BookOpen, AlertTriangle, PlayCircle } from 'lucide-react';

export default function SimulacroPage() {
  const navigate = useNavigate();
  const { permisos } = useAppStore();
  const [especialidades, setEspecialidades]             = useState<any[]>([]);
  const [selectedEspecialidad, setSelectedEspecialidad] = useState<number | null>(null);
  const [loading, setLoading]                           = useState(false);
  const [initLoading, setInitLoading]                   = useState(true);
  const [error, setError]                               = useState<string | null>(null);
  const [simulacrosDisponibles, setSimulacrosDisponibles] = useState<number | null>(null);

  useEffect(() => {
    if (permisos && permisos.simulacros === false) {
      navigate('/dashboard');
      return;
    }
    init();
  }, [permisos]);

  const init = async () => {
    setInitLoading(true);
    try {
      const [espRes, creditosRes] = await Promise.all([
        simulacrosAPI.getEspecialidades(),
        simulacrosAPI.getCreditos().catch(() => ({ data: { simulacros_disponibles: null } })),
      ]);
      setEspecialidades(espRes.data);
      setSimulacrosDisponibles(creditosRes.data.simulacros_disponibles);
    } catch (e) {
      console.error(e);
    } finally {
      setInitLoading(false);
    }
  };

  const iniciarSimulacro = async () => {
    if (!selectedEspecialidad) return;
    setLoading(true);
    setError(null);
    try {
      const { data } = await simulacrosAPI.iniciarPorEspecialidad({
        especialidad_id: selectedEspecialidad,
      });
      // Si devuelve un simulacro existente (en_curso) o uno nuevo, ambos van a la sesión
      navigate(`/simulacros/${data.simulacro_id}`);
    } catch (e: any) {
      const status = e.response?.status;
      const detail = e.response?.data?.detail;
      if (status === 403) {
        setError('No tienes simulacros disponibles. Contacta al administrador para recargar tu cuenta.');
      } else {
        setError(typeof detail === 'string' ? detail : 'Error al iniciar simulacro. Intenta de nuevo.');
      }
    } finally {
      setLoading(false);
    }
  };

  const sinCreditos = simulacrosDisponibles !== null && simulacrosDisponibles <= 0;

  if (initLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div>
        <h1 className="text-3xl font-display font-bold text-slate-900">Nuevo Simulacro</h1>
        <p className="text-slate-500">Selecciona tu especialidad para comenzar</p>
      </div>

      {/* Créditos disponibles */}
      {simulacrosDisponibles !== null && (
        <div className={`p-3 rounded-lg text-sm font-medium flex items-center gap-2 ${
          sinCreditos
            ? 'bg-red-50 text-red-700 border border-red-200'
            : 'bg-green-50 text-green-700 border border-green-200'
        }`}>
          <span>{sinCreditos ? '⚠️' : '✓'}</span>
          {sinCreditos
            ? 'No tienes simulacros disponibles. Contacta al administrador.'
            : `Tienes ${simulacrosDisponibles} simulacro${simulacrosDisponibles !== 1 ? 's' : ''} disponible${simulacrosDisponibles !== 1 ? 's' : ''}.`
          }
        </div>
      )}

      <Card>
        <div className="space-y-6">
          <div>
            <label className="label">Especialidad</label>
            <select
              value={selectedEspecialidad || ''}
              onChange={(e) => setSelectedEspecialidad(Number(e.target.value) || null)}
              className="select w-full"
              disabled={sinCreditos}
            >
              <option value="">-- Selecciona una especialidad --</option>
              {especialidades.map((esp: any) => (
                <option key={esp.id} value={esp.id}>
                  {esp.nombre}
                </option>
              ))}
            </select>
          </div>

          {selectedEspecialidad && (
            <div className="p-4 bg-primary-50 rounded-xl border border-primary-200">
              <p className="text-sm text-primary-800">
                <strong>100 preguntas</strong> • <strong>180 minutos</strong>
              </p>
              <p className="text-xs text-primary-600 mt-1">
                La distribución de preguntas se basa en el perfil de la especialidad seleccionada.
              </p>
              <div className="mt-2 text-xs text-primary-700 space-y-0.5">
                <p>Penalización: <strong>-1.125 puntos</strong> por respuesta incorrecta</p>
                <p>Sin responder: <strong>0 puntos</strong></p>
              </div>
            </div>
          )}

          {error && (
            <div className="p-3 bg-red-50 text-red-700 rounded-lg text-sm border border-red-200 flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              {error}
            </div>
          )}

          <button
            onClick={iniciarSimulacro}
            disabled={!selectedEspecialidad || loading || sinCreditos}
            className="btn btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
                Cargando simulacro...
              </>
            ) : sinCreditos ? (
              'Sin simulacros disponibles'
            ) : (
              <>
                <PlayCircle className="w-4 h-4" />
                Iniciar Simulacro
              </>
            )}
          </button>
        </div>
      </Card>

      <Card>
        <h2 className="font-semibold text-slate-800 mb-3 flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-primary-600" />
          Reglas del Simulacro
        </h2>
        <ul className="text-sm text-slate-600 space-y-2">
          <li className="flex items-start gap-2">
            <span className="text-green-600 font-bold">✓</span>
            Respuesta correcta: puntaje según especialidad
          </li>
          <li className="flex items-start gap-2">
            <span className="text-red-600 font-bold">✗</span>
            Respuesta incorrecta: <strong>-1.125 puntos</strong>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-slate-400">○</span>
            Sin responder: <strong>0 puntos</strong>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-primary-600">⏱</span>
            Tiempo máximo: <strong>180 minutos</strong>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-amber-500">⚡</span>
            El crédito se descuenta al <strong>terminar</strong> el simulacro
          </li>
        </ul>
      </Card>
    </div>
  );
}
