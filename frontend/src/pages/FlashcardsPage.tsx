import { useEffect, useState } from 'react';
import { flashcardsAPI } from '../services/api';
import { Card } from '../components/common/Card';
import { Brain, ChevronRight, ArrowLeft, CheckCircle, XCircle, BookOpen, Target } from 'lucide-react';

interface Asignatura {
  asignatura_id: number;
  asignatura_nombre: string;
  total_errores: number;
  preguntas_falladas: number;
}

interface Pregunta {
  pregunta_id: number;
  enunciado: string;
  opcion_correcta: string;
  opcion_incorrecta: string;
  imagen_url?: string;
  flashcard_id?: number;
  respondida?: boolean;
  respondida_correcta?: boolean;
}

export default function FlashcardsPage() {
  const [asignaturas, setAsignaturas] = useState<Asignatura[]>([]);
  const [preguntas, setPreguntas] = useState<Pregunta[]>([]);
  const [loading, setLoading] = useState(true);
  const [asignaturaSeleccionada, setAsignaturaSeleccionada] = useState<number | null>(null);
  const [asignaturaNombre, setAsignaturaNombre] = useState<string>('');
  const [preguntaActual, setPreguntaActual] = useState<number>(0);
  const [respondido, setRespondido] = useState<{correcto: boolean | null; respuesta: string}>({correcto: null, respuesta: ''});

  useEffect(() => {
    loadAsignaturas();
  }, []);

  const loadAsignaturas = async () => {
    setLoading(true);
    try {
      const res = await flashcardsAPI.getAsignaturas();
      setAsignaturas(res.data.asignaturas || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const loadPreguntas = async (asignaturaId: number, nombre: string) => {
    console.log('Loading preguntas for:', asignaturaId, nombre);
    setLoading(true);
    setRespondido({correcto: null, respuesta: ''});
    setPreguntaActual(0);
    try {
      const res = await flashcardsAPI.getPreguntasPorAsignatura(asignaturaId);
      console.log('Preguntas response:', res.data);
      setPreguntas(res.data.preguntas || []);
      setAsignaturaSeleccionada(asignaturaId);
      setAsignaturaNombre(nombre);
    } catch (e) {
      console.error('Error loading preguntas:', e);
} finally {
      setLoading(false);
    }
  };

  const goBack = () => {
    setAsignaturaSeleccionada(null);
    setAsignaturaNombre('');
    setPreguntas([]);
    loadAsignaturas();
  };

  const continuarLuego = () => {
    setAsignaturaSeleccionada(null);
    setAsignaturaNombre('');
    setPreguntas([]);
    loadAsignaturas();
  };
  
  // Vista de preguntas dentro de una asignatura
  const pregunta = preguntas[preguntaActual];
  
  const handleRespuesta = async (opcion: string, esCorrecta: boolean) => {
    if (respondido.correcto !== null) return;
    setRespondido({correcto: esCorrecta, respuesta: opcion});
    
    try {
      await flashcardsAPI.responder(pregunta?.pregunta_id, esCorrecta);
    } catch (e) {
      console.error('Error guardando respuesta:', e);
    }
  };

  if (asignaturaSeleccionada && pregunta) {
    return (
      <div className="space-y-6 max-w-2xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-4">
          <button onClick={goBack} className="p-2 hover:bg-slate-100 rounded-lg">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-2xl font-display font-bold text-slate-900">{asignaturaNombre}</h1>
            <p className="text-slate-500">Pregunta {preguntaActual + 1} de {preguntas.length}</p>
          </div>
        </div>

        {/* Progreso */}
        <div className="w-full bg-slate-200 rounded-full h-2">
          <div 
            className="bg-primary-500 h-2 rounded-full transition-all"
            style={{ width: `${((preguntaActual + 1) / preguntas.length) * 100}%` }}
          />
        </div>

        {/* Tarjeta */}
        <Card className="min-h-[450px] flex flex-col overflow-hidden">
          {/* Header de tarjeta con gradiente */}
          <div className="bg-gradient-to-r from-primary-500 to-primary-600 p-6 text-white">
            <p className="text-sm font-medium opacity-90">Enunciado</p>
          </div>
          
          {/* Pregunta */}
          <div className="flex-1 p-6 bg-white">
            <p className="text-lg text-slate-800 font-medium leading-relaxed">{pregunta?.enunciado}</p>
            {pregunta?.imagen_url && pregunta?.imagen_url.length > 0 && (
              <div className="mt-3">
                <img
                  src={pregunta.imagen_url}
                  alt="Imagen de la pregunta"
                  className="max-w-full max-h-48 rounded-lg border border-slate-200"
                  onError={(e) => {
                    (e.target as HTMLImageElement).style.display = 'none';
                  }}
                />
              </div>
            )}
          </div>

          {/* Opciones */}
          <div className="p-6 space-y-4 bg-slate-50">
            <button
              onClick={() => handleRespuesta(pregunta.opcion_correcta, true)}
              disabled={respondido.correcto !== null}
              className={`w-full p-5 text-left rounded-xl border-2 transition-all duration-200 ${
                respondido.correcto === null 
                  ? 'border-white hover:border-primary-400 hover:bg-white hover:shadow-md bg-white'
                  : pregunta.opcion_correcta === respondido.respuesta
                    ? 'bg-green-50 border-green-500 shadow-md'
                    : 'bg-slate-100 border-slate-200 opacity-50'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-medium text-slate-800">{pregunta.opcion_correcta}</span>
                {respondido.correcto !== null && pregunta.opcion_correcta === respondido.respuesta && (
                  <CheckCircle className="w-6 h-6 text-green-600" />
                )}
              </div>
            </button>

            <button
              onClick={() => handleRespuesta(pregunta.opcion_incorrecta, false)}
              disabled={respondido.correcto !== null}
              className={`w-full p-5 text-left rounded-xl border-2 transition-all duration-200 ${
                respondido.correcto === null 
                  ? 'border-white hover:border-error-400 hover:bg-white hover:shadow-md bg-white'
                  : pregunta.opcion_incorrecta === respondido.respuesta
                    ? 'bg-red-50 border-red-500 shadow-md'
                    : 'bg-slate-100 border-slate-200 opacity-50'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-medium text-slate-800">{pregunta.opcion_incorrecta}</span>
                {respondido.correcto !== null && pregunta.opcion_incorrecta === respondido.respuesta && (
                  <XCircle className="w-6 h-6 text-red-600" />
                )}
              </div>
            </button>
          </div>

          {/* Resultado */}
          {respondido.correcto !== null && (
            <div className={`p-4 text-center ${respondido.correcto ? 'bg-green-100' : 'bg-red-100'}`}>
              <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full font-semibold ${
                respondido.correcto ? 'text-green-700' : 'text-red-700'
              }`}>
                {respondido.correcto ? (
                  <>
                    <CheckCircle className="w-5 h-5" />
                    <span>¡Correcto!</span>
                  </>
                ) : (
                  <>
                    <XCircle className="w-5 h-5" />
                    <span>Incorrecto</span>
                  </>
                )}
              </div>
            </div>
          )}

          {/* Botón siguiente o continuar luego */}
          {respondido.correcto !== null && (
            <div className="p-6 border-t border-slate-200 space-y-3 bg-white">
              <button
                onClick={() => {
                  if (preguntaActual < preguntas.length - 1) {
                    setPreguntaActual(preguntaActual + 1);
                    setRespondido({correcto: null, respuesta: ''});
                  } else {
                    setAsignaturaSeleccionada(null);
                    setAsignaturaNombre('');
                    setPreguntas([]);
                    loadAsignaturas();
                  }
                }}
                className="w-full py-3 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded-xl transition-colors"
              >
                {preguntaActual < preguntas.length - 1 ? 'Siguiente pregunta' : 'Finalizar'}
              </button>
              <button
                onClick={continuarLuego}
className="w-full py-3 bg-slate-100 hover:bg-slate-200 text-slate-600 font-medium rounded-xl transition-colors"
              >
                Continuar luego
              </button>
            </div>
          )}
        </Card>
      </div>
    );
  }

  // Vista de lista de asignaturas
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Brain className="w-8 h-8 text-primary-600" />
        <h1 className="text-3xl font-display font-bold text-slate-900">Flashcards</h1>
      </div>

      {asignaturas.length === 0 ? (
        <Card className="text-center py-12">
          <BookOpen className="w-16 h-16 text-slate-300 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-slate-700 mb-2">No hay errores aún</h2>
          <p className="text-slate-500">Completa simulacros para ver tus áreas de mejora</p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {asignaturas.map((asig) => (
            <Card 
              key={asig.asignatura_id}
              onClick={() => {
                alert('Click en: ' + asig.asignatura_id);
                loadPreguntas(asig.asignatura_id, asig.asignatura_nombre);
              }}
              className="flex items-center justify-between cursor-pointer hover:border-primary-300 transition-all"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-error-100 rounded-xl flex items-center justify-center">
                  <Target className="w-6 h-6 text-error-600" />
                </div>
                <div>
                  <p className="font-semibold text-slate-900">{asig.asignatura_nombre}</p>
                  <p className="text-sm text-slate-500">{asig.preguntas_falladas} preguntas</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-2xl font-bold text-error-600">{asig.total_errores}</span>
                <ChevronRight className="w-5 h-5 text-slate-400" />
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}