import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { simulacrosAPI } from '../services/api';
import { useAppStore } from '../store';
import { Card } from '../components/common/Card';

export default function SimulacroPage() {
  const navigate = useNavigate();
  const { permisos } = useAppStore();
  const [especialidades, setEspecialidades] = useState<any[]>([]);
  const [selectedEspecialidad, setSelectedEspecialidad] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (permisos && permisos.simulacros === false) {
      navigate('/dashboard');
      return;
    }
    simulacrosAPI.getEspecialidades().then(r => setEspecialidades(r.data));
  }, [permisos]);

  const iniciarSimulacro = async () => {
    if (!selectedEspecialidad) return;
    setLoading(true);
    setError(null);
    try {
      const { data } = await simulacrosAPI.iniciarPorEspecialidad({
        especialidad_id: selectedEspecialidad,
      });
      navigate(`/simulacros/${data.simulacro_id}`);
    } catch (e: any) {
      console.error(e);
      const detail = e.response?.data?.detail;
      const errorMsg = typeof detail === 'string' ? detail : 'Error al iniciar simulacro';
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div>
        <h1 className="text-3xl font-display font-bold text-slate-900">Nuevo Simulacro</h1>
        <p className="text-slate-500">Selecciona tu especialidad para comenzar</p>
      </div>

      <Card>
        <div className="space-y-6">
          <div>
            <label className="label">Especialidad</label>
            <select
              value={selectedEspecialidad || ''}
              onChange={(e) => setSelectedEspecialidad(Number(e.target.value) || null)}
              className="select w-full"
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
              <div className="mt-2 text-xs text-primary-700">
                <p>Penalización: <strong>-1.125 puntos</strong> por respuesta incorrecta</p>
                <p>Sin responder: <strong>0 puntos</strong></p>
              </div>
            </div>
          )}

          {error && (
            <div className="p-3 bg-red-50 text-red-700 rounded-lg text-sm">
              {error}
            </div>
          )}

          <button
            onClick={iniciarSimulacro}
            disabled={!selectedEspecialidad || loading}
            className="btn btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Cargando...' : 'Iniciar Simulacro'}
          </button>
        </div>
      </Card>

      <Card>
        <h2 className="font-semibold text-slate-800 mb-3">Reglas del Simulacro</h2>
        <ul className="text-sm text-slate-600 space-y-2">
          <li className="flex items-start gap-2">
            <span className="text-green-600">✓</span>
            Respuesta correcta: puntaje según especialidad
          </li>
          <li className="flex items-start gap-2">
            <span className="text-red-600">✗</span>
            Respuesta incorrecta: <strong>-1.125 puntos</strong>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-slate-400">○</span>
            Sin responder: <strong>0 puntos</strong>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-primary-600">⏱</span>
            Tiempo máximo: 120 minutos
          </li>
        </ul>
      </Card>
    </div>
  );
}