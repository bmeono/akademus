import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { comunidadAPI } from '../services/api';
import { useAppStore } from '../store';
import { Card } from '../components/common/Card';
import { MessageCircle, Send, ChevronDown, ChevronUp, Sparkles, Loader } from 'lucide-react';

interface HistorialItem {
  id: number;
  materia: string;
  pregunta: string;
  respuesta: string;
  fecha: string;
}

export default function ComunidadPage() {
  const navigate = useNavigate();
  const { permisos } = useAppStore();
  const [asignaturas, setAsignaturas] = useState<{id: number; nombre: string}[]>([]);
  const [historial, setHistorial] = useState<HistorialItem[]>([]);
  const [creditos, setCreditos] = useState(0);
  const [materia, setMateria] = useState<number | null>(null);
  const [pregunta, setPregunta] = useState('');
  const [respuesta, setRespuesta] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [consultando, setConsultando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<number | null>(null);

  useEffect(() => {
    if (permisos && permisos.comunidad === false) {
      navigate('/dashboard');
      return;
    }
    loadData();
  }, [permisos]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [asigRes, histRes, credRes] = await Promise.all([
        comunidadAPI.getAsignaturas(),
        comunidadAPI.getHistorial(),
        comunidadAPI.getCreditos()
      ]);
      setAsignaturas(asigRes.data.asignaturas || []);
      setHistorial(histRes.data.historial || []);
      setCreditos(credRes.data.creditos || 0);
    } catch (e: any) {
      if (e.response?.status === 403) {
        setError('Sin créditos disponibles. Contacta al administrador.');
      } else {
        setError('Error al cargar datos');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleEnviar = async () => {
    if (!pregunta.trim() || !materia || consultando) return;
    setConsultando(true);
    setError(null);
    setRespuesta(null);
    try {
      const nombreMateria = asignaturas.find(a => a.id === materia)?.nombre || '';
      const res = await comunidadAPI.consultar(nombreMateria, pregunta.trim());
      setRespuesta(res.data.respuesta);
      setCreditos(creditos - 1);
      await loadData();
    } catch (e: any) {
      if (e.response?.status === 403) {
        setError('Sin créditos disponibles. Contacta al administrador.');
      } else {
        setError('Error al procesar consulta');
      }
    } finally {
      setConsultando(false);
    }
  };

  const toggleExpand = (id: number) => {
    setExpanded(expanded === id ? null : id);
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64"><Loader className="w-8 h-8 animate-spin text-primary-600" /></div>;
  }

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <MessageCircle className="w-8 h-8 text-primary-600" />
          <h1 className="text-3xl font-display font-bold text-slate-900">Comunidad AKADEMUS</h1>
        </div>
        <div className="bg-primary-100 px-4 py-2 rounded-full">
          <span className="text-sm text-primary-700">Consultas restantes: </span>
          <span className="font-bold text-primary-700">{creditos}</span>
        </div>
      </div>

      <Card className="p-6 bg-gradient-to-br from-primary-50 to-primary-100 border border-primary-200">
        <div className="flex items-start gap-4">
          <Sparkles className="w-10 h-10 text-primary-600 flex-shrink-0 mt-1" />
          <div>
            <h2 className="text-lg font-semibold text-primary-800 mb-2">Tu Tutor Virtual IA</h2>
            <p className="text-primary-700 text-sm leading-relaxed">
              Resolveré tus dudas académicas paso a paso. Envíame una sola pregunta a la vez para darte la mejor explicación posible.
            </p>
          </div>
        </div>
      </Card>

      <Card>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Materia</label>
            <select
              value={materia || ''}
              onChange={(e) => setMateria(Number(e.target.value))}
              className="w-full p-3 border border-slate-200 rounded-xl focus:border-primary-400 focus:ring-2 focus:ring-primary-100"
            >
              <option value="">Selecciona una materia</option>
              {asignaturas.map(a => (
                <option key={a.id} value={a.id}>{a.nombre}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Tu pregunta (máx. 500 caracteres)</label>
            <textarea
              value={pregunta}
              onChange={(e) => setPregunta(e.target.value.slice(0, 500))}
              placeholder="Escribe tu duda aquí..."
              rows={4}
              maxLength={500}
              className="w-full p-3 border border-slate-200 rounded-xl focus:border-primary-400 focus:ring-2 focus:ring-primary-100 resize-none"
            />
            <p className="text-xs text-slate-400 text-right mt-1">{pregunta.length}/500</p>
          </div>

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">{error}</div>
          )}

          {respuesta && (
            <div className="p-4 bg-green-50 border border-green-200 rounded-xl">
              <h3 className="font-semibold text-green-800 mb-2 flex items-center gap-2">
                <Sparkles className="w-4 h-4" /> Respuesta del Tutor:
              </h3>
              <p className="text-green-700 whitespace-pre-wrap leading-relaxed">{respuesta}</p>
            </div>
          )}

          <button
            onClick={handleEnviar}
            disabled={!pregunta.trim() || !materia || consultando}
            className="w-full py-3 bg-primary-600 hover:bg-primary-700 disabled:bg-slate-300 text-white font-semibold rounded-xl transition-colors flex items-center justify-center gap-2"
          >
            {consultando ? <Loader className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
            {consultando ? 'Procesando...' : 'Enviar Pregunta'}
          </button>
        </div>
      </Card>

      {historial.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold text-slate-800 mb-3">Mi Historial</h2>
          <div className="space-y-2">
            {historial.map(item => (
              <div key={item.id} className="bg-white border border-slate-200 rounded-xl overflow-hidden">
                <button
                  onClick={() => toggleExpand(item.id)}
                  className="w-full p-4 flex items-center justify-between text-left hover:bg-slate-50"
                >
                  <div>
                    <span className="inline-block px-2 py-1 bg-primary-100 text-primary-700 text-xs rounded-full mr-2">{item.materia}</span>
                    <span className="text-slate-600 text-sm">{item.pregunta.slice(0, 80)}{item.pregunta.length > 80 ? '...' : ''}</span>
                    <p className="text-xs text-slate-400 mt-1">{new Date(item.fecha).toLocaleDateString('es-PE')}</p>
                  </div>
                  {expanded === item.id ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
                </button>
                {expanded === item.id && (
                  <div className="p-4 bg-slate-50 border-t border-slate-200">
                    <p className="text-slate-700 text-sm leading-relaxed">{item.respuesta}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}