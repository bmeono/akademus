import { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { simulacrosAPI } from '../services/api';
import api from '../services/api';

interface Opcion {
  id: number;
  texto: string;
}

interface Pregunta {
  id: number;
  enunciado: string;
  imagen_url?: string;
  dificultad: number;
  orden: number;
  opciones: Opcion[];
}

interface Resultado {
  id: number;
  total_preguntas: number;
  aciertos: number;
  errores: number;
  sin_responder: number;
  puntaje_total: number;
}

export default function SimulacroSession() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [preguntas, setPreguntas] = useState<Pregunta[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [respuestas, setRespuestas] = useState<Map<number, number>>(new Map());
  const [tiempoRestante, setTiempoRestante] = useState(180 * 60);
  const [showTimer, setShowTimer] = useState(true);
  const [loading, setLoading] = useState(true);
  const [finalizado, setFinalizado] = useState(false);
  const [resultado, setResultado] = useState<Resultado | null>(null);
  const [guardando, setGuardando] = useState(false);

  const simulacroId = Number(id);

  useEffect(() => {
    cargarSimulacro();
  }, [id]);

  useEffect(() => {
    if (finalizado || tiempoRestante <= 0) return;

    const timer = setInterval(() => {
      setTiempoRestante((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          handleFinalizar();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [finalizado, tiempoRestante]);

  const cargarSimulacro = async () => {
    try {
      const { data } = await simulacrosAPI.getTodasPreguntas(simulacroId);
      setPreguntas(data.preguntas);
      setTiempoRestante(data.tiempo_restante);
      setLoading(false);
    } catch (e) {
      console.error('Error al cargar simulacro:', e);
      navigate('/simulacros');
    }
  };

  const handleRespuesta = (preguntaId: number, opcionId: number) => {
    setRespuestas(new Map(respuestas.set(preguntaId, opcionId)));
  };

  const handleSiguiente = () => {
    if (currentIndex < preguntas.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const handleAnterior = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const handleFinalizar = useCallback(async () => {
    setFinalizado(true);
    setGuardando(true);

    const respuestasArray = Array.from(respuestas.entries()).map(([preguntaId, opcionId]) => ({
      pregunta_id: preguntaId,
      opcion_seleccionada_id: opcionId,
    }));

    console.log('Enviando respuestas:', respuestasArray.length);

    try {
      const response = await api.post('/simulacros/' + simulacroId + '/finalizar', { respuestas: respuestasArray });
      
      console.log('Status:', response.status);
      const data = response.data;
      console.log('Respuesta completa:', data);
      console.log('errores en data:', data.errores);
      
      const resultadoData = {
        id: data.id,
        total_preguntas: data.total_preguntas,
        aciertos: data.aciertos,
        errores: data.errores,
        sin_responder: data.sin_responder,
        puntaje_total: data.puntaje_total,
      };
      
      // Guardar ID en localStorage para PDF
      localStorage.setItem('ultimo_simulacro_id', String(data.id));
      
      console.log('resultadoData:', resultadoData);
      setResultado(resultadoData);
    } catch (e) {
      console.error('Error:', e);
    }
    
    setGuardando(false);
  }, [simulacroId, respuestas]);

  const formatTiempo = (segundos: number) => {
    const h = Math.floor(segundos / 3600);
    const m = Math.floor((segundos % 3600) / 60);
    const s = segundos % 60;
    if (h > 0) {
      return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    }
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  const currentPregunta = preguntas[currentIndex];
  const respuestaActual = currentPregunta ? respuestas.get(currentPregunta.id) : null;

  if (loading && !finalizado) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-slate-600">Cargando preguntas...</p>
        </div>
      </div>
    );
  }

  if (finalizado && (guardando || !resultado)) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-slate-600">Calculando resultados...</p>
        </div>
      </div>
    );
  }

  if (finalizado && resultado) {
    return (
      <div className="min-h-screen bg-slate-50 py-8">
        <div className="max-w-2xl mx-auto px-4">
          <div className="bg-white rounded-2xl shadow-lg p-8 text-center">
            <h1 className="text-3xl font-bold text-slate-900 mb-2">Simulacro Finalizado</h1>
            <p className="text-slate-500 mb-8">Aquí están tus resultados</p>

            <div className="grid grid-cols-3 gap-4 mb-8">
              <div className="bg-green-50 rounded-xl p-4">
                <p className="text-4xl font-bold text-green-600">{resultado.aciertos}</p>
                <p className="text-sm text-green-700">Aciertos</p>
              </div>
              <div className="bg-red-50 rounded-xl p-4">
                <p className="text-4xl font-bold text-red-600">{resultado.errores}</p>
                <p className="text-sm text-red-700">Errores</p>
              </div>
              <div className="bg-slate-100 rounded-xl p-4">
                <p className="text-4xl font-bold text-slate-600">{resultado.sin_responder}</p>
                <p className="text-sm text-slate-700">Sin responder</p>
              </div>
            </div>

            <div className="bg-primary-50 rounded-xl p-6 mb-8">
              <p className="text-sm text-primary-600 mb-1">Puntaje Total</p>
              <p className="text-5xl font-bold text-primary-700">{resultado.puntaje_total !== undefined ? resultado.puntaje_total.toFixed(2) : 'N/A'}</p>
            </div>

            <div className="flex flex-col gap-3">
              <button
                type="button"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  
                  // Intentar obtener ID desde cualquier fuente
                  let pid = simulacroId;
                  if (!pid || pid === 0 || isNaN(pid)) {
                    pid = resultado?.id;
                  }
                  if (!pid || pid === 0 || isNaN(pid)) {
                    const saved = localStorage.getItem('ultimo_simulacro_id');
                    pid = saved ? Number(saved) : null;
                  }
                  
                  console.log('PDF click: pid=', pid);
                  
                  // Si tenemos ID, intentar descargar directamente
                  if (pid && pid > 0) {
                    const token = localStorage.getItem('access_token');
                    const url = `https://akademus.onrender.com/simulacros/${pid}/resultado-pdf?token=${token}`;
                    window.open(url, '_blank');
                    return;
                  }
                  
                  // Si no hay ID, intentar /resultado endpoint para obtener datos
                  const savedId = localStorage.getItem('ultimo_simulacro_id');
                  if (savedId) {
                    const token = localStorage.getItem('access_token');
                    fetch(`https://akademus.onrender.com/simulacros/${savedId}/resultado`, {
                      headers: { 'Authorization': 'Bearer ' + token }
                    })
                    .then(res => res.json())
                    .then(data => {
                      console.log('Resultado API:', data);
                      if (data.id) {
                        const url = `https://akademus.onrender.com/simulacros/${data.id}/resultado-pdf?token=${token}`;
                        window.open(url, '_blank');
                      } else {
                        alert('No se pudo obtener resultado');
                      }
                    })
                    .catch(err => {
                      console.error(err);
                      alert('Error: ' + err.message);
                    });
                  } else {
                    alert('No hay ID de simulacro. Ejecuta un simulacro primero.');
                  }
                }}
                className="btn btn-secondary w-full flex items-center justify-center gap-2 bg-blue-500 hover:bg-blue-600 text-white p-3 rounded"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Descargar Resultados PDF
              </button>
              <button
                onClick={() => navigate('/simulacros')}
                className="btn btn-primary w-full"
              >
                Volver a Simulacros
              </button>
              <button
                onClick={() => navigate('/')}
                className="btn btn-secondary w-full"
              >
                Ir al Inicio
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!currentPregunta) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <p>No se pudieron cargar las preguntas</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="bg-white shadow-sm border-b sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="text-sm text-slate-600">
              Pregunta {currentIndex + 1} de {preguntas.length}
            </span>
            {showTimer && (
              <span className={`font-mono text-lg font-bold ${tiempoRestante < 300 ? 'text-red-600' : 'text-slate-900'}`}>
                {formatTiempo(tiempoRestante)}
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowTimer(!showTimer)}
              className="btn btn-sm btn-secondary"
            >
              {showTimer ? 'Ocultar tiempo' : 'Mostrar tiempo'}
            </button>
            <button
              onClick={handleFinalizar}
              className="btn btn-sm btn-danger"
            >
              Terminar Simulacro
            </button>
          </div>
        </div>

        <div className="bg-primary-500 h-1 transition-all" style={{ width: `${((currentIndex + 1) / preguntas.length) * 100}%` }} />
      </div>

      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="grid grid-cols-10 gap-2 mb-6">
          {preguntas.map((p, idx) => (
            <button
              key={p.id}
              onClick={() => setCurrentIndex(idx)}
              className={`w-8 h-8 rounded text-xs font-medium transition-colors ${
                idx === currentIndex
                  ? 'bg-primary-500 text-white'
                  : respuestas.has(p.id)
                  ? 'bg-green-500 text-white'
                  : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
              }`}
            >
              {idx + 1}
            </button>
          ))}
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-8">
          <p className="text-lg text-slate-900 mb-6 whitespace-pre-wrap">{currentPregunta.enunciado}</p>
          
          {(currentPregunta.universidad || currentPregunta.an_exam) && (
            <p className="text-sm text-slate-400 mb-6 italic">
              {currentPregunta.universidad && <span>{currentPregunta.universidad}</span>}
              {currentPregunta.universidad && currentPregunta.an_exam && <span> - </span>}
              {currentPregunta.an_exam && <span>{currentPregunta.an_exam}</span>}
            </p>
          )}

          {currentPregunta.imagen_url && currentPregunta.imagen_url.length > 0 && (
            <div className="mb-6">
              <img
                src={currentPregunta.imagen_url}
                alt="Imagen de la pregunta"
                className="max-w-full max-h-64 rounded-lg border border-slate-200"
                onError={(e) => {
                  const target = e.target as HTMLImageElement;
                  target.style.display = 'none';
                  const errorDiv = document.getElementById('img-error-' + currentPregunta.id);
                  if (errorDiv) errorDiv.style.display = 'block';
                }}
              />
              <p id={"img-error-" + currentPregunta.id} className="text-xs text-red-500 hidden">
               ❌ Error al cargar imagen. Verificá que la URL sea correcta.
              </p>
            </div>
          )}

          <div className="space-y-3">
            {currentPregunta.opciones.map((opcion, idx) => {
              const letra = String.fromCharCode(65 + idx);
              const esSeleccionada = respuestaActual === opcion.id;

              return (
                <button
                  key={opcion.id}
                  onClick={() => handleRespuesta(currentPregunta.id, opcion.id)}
                  className={`w-full text-left p-4 rounded-xl border-2 transition-all ${
                    esSeleccionada
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-slate-200 hover:border-primary-300 hover:bg-slate-50'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <span className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                      esSeleccionada ? 'bg-primary-500 text-white' : 'bg-slate-100 text-slate-700'
                    }`}>
                      {letra}
                    </span>
                    <span className="flex-1">{opcion.texto}</span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        <div className="flex justify-between mt-6">
          <button
            onClick={handleAnterior}
            disabled={currentIndex === 0}
            className="btn btn-secondary disabled:opacity-50"
          >
            Anterior
          </button>
          {currentIndex < preguntas.length - 1 ? (
            <button onClick={handleSiguiente} className="btn btn-primary">
              Siguiente
            </button>
          ) : (
            <button onClick={handleFinalizar} className="btn btn-success">
              Finalizar
            </button>
          )}
        </div>

        <div className="mt-6 p-4 bg-amber-50 rounded-xl border border-amber-200">
          <p className="text-sm text-amber-800">
            <strong>Recuerda:</strong> Respuesta correcta = puntaje según especialidad | 
            Incorrecta = -1.125 pts | Sin responder = 0 pts
          </p>
        </div>
      </div>
    </div>
  );
}