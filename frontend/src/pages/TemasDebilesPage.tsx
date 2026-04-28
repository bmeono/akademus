import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { dashboardAPI } from '../services/api';
import { useAppStore } from '../store';
import { AlertTriangle, BookOpen, ChevronRight, ArrowLeft, Eye } from 'lucide-react';
import { Card } from '../components/common/Card';

interface Asignatura {
  asignatura_id: number;
  asignatura_nombre: string;
  total_errores: number;
  preguntas_falladas: number;
}

interface PreguntaFallada {
  pregunta_id: number;
  enunciado: string;
  opcion_seleccionada_id: number | null;
  opcion_seleccionada: string | null;
  opcion_correcta: string | null;
  asignatura_nombre: string;
}

export default function TemasDebilesPage() {
  const navigate = useNavigate();
  const { permisos } = useAppStore();
  const [asignaturas, setAsignaturas] = useState<Asignatura[]>([]);
  const [preguntas, setPreguntas] = useState<PreguntaFallada[]>([]);
  const [loading, setLoading] = useState(true);
  const [asignaturaSeleccionada, setAsignaturaSeleccionada] = useState<number | null>(null);
  const [asignaturaNombre, setAsignaturaNombre] = useState<string>('');

  useEffect(() => {
    if (permisos && permisos.temas_debiles === false) {
      navigate('/dashboard');
      return;
    }
    loadAsignaturas();
  }, [permisos]);

  const loadAsignaturas = async () => {
    try {
      const res = await dashboardAPI.getTemasDebilesDetalle();
      const response = res.data;
      console.log('>>> FULL RESPONSE:', JSON.stringify(response, null, 2));
      console.log('>>> DEBUG:', response.debug);
      
      const data = response.asignaturas || [];
      setAsignaturas(data);
    } catch (e: any) {
      console.error('Error:', e.response?.data || e.message);
    } finally {
      setLoading(false);
    }
  };

  const loadPreguntas = async (asignaturaId: number, nombre: string) => {
    console.log('>>> loadPreguntas START:', asignaturaId);
    setLoading(true);
    
    try {
      const res = await dashboardAPI.getPreguntasFalladas(asignaturaId);
      const data = res.data;
      console.log('>>> RESULT:', data);
      
      setPreguntas(data || []);
      setAsignaturaSeleccionada(asignaturaId);
      setAsignaturaNombre(nombre);
      console.log('>>> State updated');
    } catch (e: any) {
      console.error('>>> ERROR:', e);
    } 
    
    setLoading(false);
  };

  const goBack = () => {
    setAsignaturaSeleccionada(null);
    setAsignaturaNombre('');
    setPreguntas([]);
  };

if (loading) {
    return <div className="flex items-center justify-center h-64"><div className="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full"></div></div>;
  }
  
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        {asignaturaSeleccionada && (
          <button onClick={goBack} className="p-2 hover:bg-slate-100 rounded-lg">
            <ArrowLeft className="w-5 h-5" />
          </button>
        )}
        <div>
          <h1 className="text-3xl font-display font-bold text-slate-900">
            {asignaturaSeleccionada ? asignaturaNombre : 'Temas Débiles'}
          </h1>
          <p className="text-slate-500">
            {asignaturaSeleccionada 
              ? `Preguntas donde fallaste (${preguntas.length})` 
              : 'Asignaturas con más errores'}
          </p>
        </div>
      </div>

      {!asignaturaSeleccionada ? (
        <>
          {asignaturas.length === 0 ? (
            <div className="bg-white border border-slate-200 rounded-xl p-8 text-center">
              <BookOpen className="w-12 h-12 text-slate-300 mx-auto mb-4" />
              <p className="text-slate-500">Aún no tienes errores registrados.</p>
              <p className="text-sm text-slate-400">Completa simulacros para ver tus áreas de mejora.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {asignaturas.map((a) => {
                const handleClick = () => {
                  console.log('CLICK on:', a.asignatura_id, a.asignatura_nombre);
                  loadPreguntas(a.asignatura_id, a.asignatura_nombre);
                };
                return (
                  <div 
                    key={a.asignatura_id}
                    onClick={handleClick}
                    className="flex items-center justify-between p-4 bg-white border border-slate-200 rounded-xl cursor-pointer hover:border-red-300 hover:bg-red-50 transition-all"
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 bg-error-100 rounded-lg flex items-center justify-center">
                        <AlertTriangle className="w-5 h-5 text-error-600" />
                      </div>
                      <div>
                        <p className="font-medium text-slate-900">{a.asignatura_nombre}</p>
                        <p className="text-sm text-slate-500">{a.preguntas_falladas} preguntas falladas</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className="text-xl font-bold text-error-600">{a.total_errores}</p>
                        <p className="text-xs text-slate-500">errores</p>
                      </div>
                      <ChevronRight className="w-5 h-5 text-slate-400" />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </>
      ) : (
        <>
          {preguntas.length === 0 ? (
            <Card>
              <div className="text-center py-8">
                <BookOpen className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                <p className="text-slate-500">No hay preguntas falladas en esta asignatura.</p>
              </div>
            </Card>
          ) : (
            <div className="space-y-4">
              {preguntas.map((p, i) => (
                <Card key={p.pregunta_id} className="relative">
                  <div className="absolute top-4 right-4 flex items-center gap-1 text-xs text-slate-400">
                    <Eye className="w-3 h-3" />
                    #{i + 1}
                  </div>
                  <div className="pr-16">
                    <p className="font-medium text-slate-700 mb-3">{p.enunciado}</p>
                    {p.opcion_seleccionada && (
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-sm text-slate-500">Tu respuesta:</span>
                        <span className="px-2 py-1 bg-red-100 text-red-700 rounded text-sm">{p.opcion_seleccionada}</span>
                      </div>
                    )}
                    {p.opcion_correcta && (
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-slate-500">Correcta:</span>
                        <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-sm">{p.opcion_correcta}</span>
                      </div>
                    )}
                  </div>
                </Card>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}