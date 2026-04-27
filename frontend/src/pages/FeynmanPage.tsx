import { useEffect, useState } from 'react';
import { feynmanAPI } from '../services/api';
import { Card } from '../components/common/Card';
import { Send, CheckCircle, Clock, AlertCircle } from 'lucide-react';

export default function FeynmanPage() {
  const [temas, setTemas] = useState<any[]>([]);
  const [misExplicaciones, setMisExplicaciones] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [temaId, setTemaId] = useState<number>(0);
  const [explicacion, setExplicacion] = useState('');
  
  useEffect(() => {
    loadData();
  }, []);
  
  const loadData = async () => {
    const [tData, eData] = await Promise.all([
      feynmanAPI.getTemas(),
      feynmanAPI.getMisExplicaciones(),
    ]);
    setTemas(tData.data);
    setMisExplicaciones(eData.data);
  };
  
  const enviar = async () => {
    if (!temaId || explicacion.length < 100) return;
    setLoading(true);
    try {
      await feynmanAPI.enviarExplicacion({ tema_id: temaId, explicacion });
      setExplicacion('');
      loadData();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };
  
  const getEstadoIcon = (estado: string) => {
    switch (estado) {
      case 'aprobado': return <CheckCircle className="w-4 h-4 text-success-500" />;
      case 'revisado': return <CheckCircle className="w-4 h-4 text-primary-500" />;
      case 'refuerzo': return <AlertCircle className="w-4 h-4 text-warning-500" />;
      default: return <Clock className="w-4 h-4 text-slate-400" />;
    }
  };
  
  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div>
        <h1 className="text-3xl font-display font-bold text-slate-900">Técnica Feynman</h1>
        <p className="text-slate-500">Explica conceptos con tus propias palabras</p>
      </div>
      
      {/* Enviar explicación */}
      <Card>
        <div className="space-y-4">
          <select
            value={temaId}
            onChange={(e) => setTemaId(Number(e.target.value))}
            className="input"
          >
            <option value={0}>Selecciona un tema</option>
            {temas.map((t) => (
              <option key={t.id} value={t.id}>{t.nombre}</option>
            ))}
          </select>
          
          <textarea
            value={explicacion}
            onChange={(e) => setExplicacion(e.target.value)}
            placeholder="Explica el concepto con tus palabras... (mínimo 100 caracteres)"
            className="input min-h-[150px]"
          />
          
          <div className="flex justify-between items-center">
            <span className="text-sm text-slate-500">{explicacion.length}/100 caracteres mínimos</span>
            <button onClick={enviar} disabled={loading || !temaId || explicacion.length < 100} className="btn-primary">
              <Send className="w-5 h-5" />
              Enviar
            </button>
          </div>
        </div>
      </Card>
      
      {/* Historial */}
      <Card>
        <h2 className="text-lg font-semibold mb-4">Mis explicaciones</h2>
        <div className="space-y-3">
          {misExplicaciones.length === 0 ? (
            <p className="text-slate-500 text-center py-8">No has enviado explicaciones aún</p>
          ) : (
            misExplicaciones.map((exp) => (
              <div key={exp.id} className="p-4 bg-slate-50 rounded-xl">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-slate-500">{new Date(exp.fecha_creacion).toLocaleDateString()}</span>
                  <div className="flex items-center gap-1">
                    {getEstadoIcon(exp.estado)}
                    <span className="text-sm font-medium capitalize">{exp.estado}</span>
                  </div>
                </div>
                <p className="text-slate-700 line-clamp-3">{exp.explicacion_usuario}</p>
                {exp.comentario_admin && (
                  <div className="mt-2 p-2 bg-primary-50 rounded-lg text-sm">
                    <span className="font-medium">Feedback: </span>{exp.comentario_admin}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </Card>
    </div>
  );
}