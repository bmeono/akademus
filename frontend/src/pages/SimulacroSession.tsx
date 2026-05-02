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
  const [preguntas, setPreguntas]         = useState<Pregunta[]>([]);
  const [currentIndex, setCurrentIndex]   = useState(0);
  const [respuestas, setRespuestas]       = useState<Map<number, number>>(new Map());
  const [tiempoRestante, setTiempoRestante] = useState(180 * 60);
  const [showTimer, setShowTimer]         = useState(true);
  const [loading, setLoading]             = useState(true);
  const [finalizado, setFinalizado]       = useState(false);
  const [resultado, setResultado]         = useState<Resultado | null>(null);
  const [guardando, setGuardando]         = useState(false);

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

      // ✅ FIX: si el simulacro ya está finalizado, mostrar resultado directo
      if (data.estado === 'finalizado') {
        try {
          const resData = await simulacrosAPI.getResultado(simulacroId);
          setResultado(resData.data);
          setFinalizado(true);
          setLoading(false);
        } catch {
          // Si no hay resultado guardado, ir a la lista
          navigate('/simulacros');
        }
        return;
      }

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
    if (currentIndex < preguntas.length - 1) setCurrentIndex(currentIndex + 1);
  };

  const handleAnterior = () => {
    if (currentIndex > 0) setCurrentIndex(currentIndex - 1);
  };

  const handleFinalizar = useCallback(async () => {
    setFinalizado(true);
    setGuardando(true);

    const respuestasArray = Array.from(respuestas.entries()).map(([preguntaId, opcionId]) => ({
      pregunta_id: preguntaId,
      opcion_seleccionada_id: opcionId,
    }));

    try {
      const response = await api.post('/simulacros/' + simulacroId + '/finalizar', { respuestas: respuestasArray });
      const data = response.data;

      const resultadoData: Resultado = {
        id: data.id,
        total_preguntas: data.total_preguntas,
        aciertos: data.aciertos,
        errores: data.errores,
        sin_responder: data.sin_responder,
        puntaje_total: data.puntaje_total,
      };

      localStorage.setItem('ultimo_simulacro_id', String(data.id));
      setResultado(resultadoData);
    } catch (e) {
      console.error('Error al finalizar:', e);
    }

    setGuardando(false);
  }, [simulacroId, respuestas]);

  const formatTiempo = (segundos: number) => {
    const h = Math.floor(segundos / 3600);
    const m = Math.floor((segundos % 3600) / 60);
    const s = segundos % 60;
    if (h > 0) return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  const currentPregunta  = preguntas[currentIndex];
  const respuestaActual  = currentPregunta ? respuestas.get(currentPregunta.id) : null;
  const respondidas      = respuestas.size;
  const sinResponder     = preguntas.length - respondidas;

  // ── Loading ──
  if (loading && !finalizado) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full mx-auto mb-4" />
          <p className="text-slate-600 font-medium">Cargando preguntas...</p>
          <p className="text-slate-400 text-sm mt-1">Esto puede tomar unos segundos</p>
        </div>
      </div>
    );
  }

  // ── Guardando ──
  if (finalizado && (guardando || !resultado)) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full mx-auto mb-4" />
          <p className="text-slate-600 font-medium">Calculando resultados...</p>
        </div>
      </div>
    );
  }

  // ── Resultado ──
  if (finalizado && resultado) {
    const pct = resultado.total_preguntas > 0
      ? Math.round((resultado.aciertos / resultado.total_preguntas) * 100)
      : 0;

    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-lg p-8 max-w-md w-full space-y-6">
          <div className="text-center">
            <div className="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl font-bold text-primary-600">{pct}%</span>
            </div>
            <h2 className="text-2xl font-bold text-slate-900">¡Simulacro finalizado!</h2>
            <p className="text-slate-500 mt-1">Puntaje: <strong className="text-primary-600">{resultado.puntaje_total.toFixed(2)}</strong></p>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div className="bg-green-50 border border-green-100 rounded-xl p-3 text-center">
              <p className="text-2xl font-bold text-green-700">{resultado.aciertos}</p>
              <p className="text-xs text-green-600 mt-0.5">Correctas</p>
            </div>
            <div className="bg-red-50 border border-red-100 rounded-xl p-3 text-center">
              <p className="text-2xl font-bold text-red-700">{resultado.errores}</p>
              <p className="text-xs text-red-600 mt-0.5">Incorrectas</p>
            </div>
            <div className="bg-slate-50 border border-slate-100 rounded-xl p-3 text-center">
              <p className="text-2xl font-bold text-slate-600">{resultado.sin_responder}</p>
              <p className="text-xs text-slate-500 mt-0.5">Sin resp.</p>
            </div>
          </div>

          <div className="space-y-3">
            <button
              onClick={() => simulacrosAPI.downloadResultadoPDF(resultado.id)}
              className="w-full py-3 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded-xl transition-colors"
            >
              Descargar PDF
            </button>
            <button
              onClick={() => navigate('/simulacros')}
              className="w-full py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium rounded-xl transition-colors"
            >
              Nuevo simulacro
            </button>
            <button
              onClick={() => navigate('/dashboard')}
              className="w-full py-3 text-slate-500 hover:text-slate-700 font-medium transition-colors"
            >
              Ir al dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ── Simulacro en curso ──
  const pctProgreso = preguntas.length > 0 ? (respondidas / preguntas.length) * 100 : 0;
  const tiempoWarning = tiempoRestante < 600; // menos de 10 min

  return (
    <div className="min-h-screen bg-slate-900 text-white flex flex-col">

      {/* Barra superior */}
      <div className="bg-slate-800 border-b border-slate-700 px-6 py-3 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-4">
          <span className="font-display font-bold text-primary-400 text-lg">AKADEMUS</span>
          <span className="text-slate-400 text-sm">Simulacro #{simulacroId}</span>
        </div>

        <div className="flex items-center gap-6">
          {/* Progreso */}
          <div className="flex items-center gap-2">
            <div className="w-32 h-2 bg-slate-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-primary-500 rounded-full transition-all"
                style={{ width: `${pctProgreso}%` }}
              />
            </div>
            <span className="text-sm text-slate-300">{respondidas}/{preguntas.length}</span>
          </div>

          {/* Timer */}
          <button
            onClick={() => setShowTimer(!showTimer)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-mono font-bold transition-colors ${
              tiempoWarning
                ? 'bg-red-900 text-red-300 animate-pulse'
                : 'bg-slate-700 text-slate-200'
            }`}
          >
            {showTimer ? formatTiempo(tiempoRestante) : '⏱ Oculto'}
          </button>
        </div>
      </div>

      {/* Contenido principal */}
      <div className="flex flex-1 overflow-hidden">

        {/* Panel izquierdo: Mapa de preguntas */}
        <div className="w-56 bg-slate-800 border-r border-slate-700 flex flex-col overflow-hidden flex-shrink-0">
          <div className="p-3 border-b border-slate-700">
            <p className="text-xs text-slate-400 font-medium uppercase tracking-wide">Navegación</p>
            <p className="text-xs text-slate-500 mt-0.5">{sinResponder} sin responder</p>
          </div>
          <div className="flex-1 overflow-y-auto p-3">
            <div className="grid grid-cols-5 gap-1.5">
              {preguntas.map((p, i) => {
                const respondida = respuestas.has(p.id);
                const esCurrent  = i === currentIndex;
                return (
                  <button
                    key={p.id}
                    onClick={() => setCurrentIndex(i)}
                    className={`w-8 h-8 rounded text-xs font-semibold transition-all ${
                      esCurrent
                        ? 'bg-primary-500 text-white ring-2 ring-primary-300'
                        : respondida
                          ? 'bg-green-600 text-white'
                          : 'bg-slate-700 text-slate-400 hover:bg-slate-600'
                    }`}
                  >
                    {i + 1}
                  </button>
                );
              })}
            </div>
          </div>
          <div className="p-3 border-t border-slate-700 space-y-1.5">
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <div className="w-3 h-3 rounded bg-green-600" /> Respondida
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <div className="w-3 h-3 rounded bg-primary-500" /> Actual
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <div className="w-3 h-3 rounded bg-slate-700" /> Sin responder
            </div>
          </div>
        </div>

        {/* Panel central: Pregunta */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {currentPregunta && (
            <>
              {/* Pregunta */}
              <div className="flex-1 overflow-y-auto p-8">
                <div className="max-w-3xl mx-auto">
                  <div className="flex items-center gap-3 mb-6">
                    <span className="px-3 py-1 bg-primary-900 text-primary-300 text-sm rounded-full font-medium">
                      Pregunta {currentIndex + 1} de {preguntas.length}
                    </span>
                    {currentPregunta.dificultad && (
                      <span className={`px-2 py-0.5 text-xs rounded-full ${
                        currentPregunta.dificultad === 1 ? 'bg-green-900 text-green-300' :
                        currentPregunta.dificultad === 2 ? 'bg-yellow-900 text-yellow-300' :
                        'bg-red-900 text-red-300'
                      }`}>
                        {currentPregunta.dificultad === 1 ? 'Fácil' :
                         currentPregunta.dificultad === 2 ? 'Medio' : 'Difícil'}
                      </span>
                    )}
                  </div>

                  <p className="text-lg text-slate-100 leading-relaxed mb-6">
                    {currentPregunta.enunciado}
                  </p>

                  {currentPregunta.imagen_url && (
                    <img
                      src={currentPregunta.imagen_url}
                      alt="Imagen de la pregunta"
                      className="max-w-md rounded-lg border border-slate-600 mb-6"
                      onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
                    />
                  )}

                  <div className="space-y-3">
                    {currentPregunta.opciones.map((opcion, idx) => {
                      const letra   = String.fromCharCode(65 + idx);
                      const selected = respuestaActual === opcion.id;
                      return (
                        <button
                          key={opcion.id}
                          onClick={() => handleRespuesta(currentPregunta.id, opcion.id)}
                          className={`w-full text-left p-4 rounded-xl border-2 transition-all ${
                            selected
                              ? 'bg-primary-900 border-primary-500 text-white'
                              : 'bg-slate-800 border-slate-600 text-slate-300 hover:border-slate-400 hover:bg-slate-750'
                          }`}
                        >
                          <div className="flex items-start gap-3">
                            <span className={`flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-sm font-bold ${
                              selected ? 'bg-primary-500 text-white' : 'bg-slate-700 text-slate-400'
                            }`}>
                              {letra}
                            </span>
                            <span className="leading-relaxed pt-0.5">{opcion.texto}</span>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>

              {/* Navegación inferior */}
              <div className="border-t border-slate-700 bg-slate-800 px-8 py-4 flex items-center justify-between flex-shrink-0">
                <button
                  onClick={handleAnterior}
                  disabled={currentIndex === 0}
                  className="px-5 py-2 bg-slate-700 hover:bg-slate-600 disabled:opacity-30 disabled:cursor-not-allowed rounded-xl text-sm font-medium transition-colors"
                >
                  ← Anterior
                </button>

                <button
                  onClick={() => {
                    if (sinResponder > 0) {
                      const confirmar = window.confirm(
                        `Tienes ${sinResponder} pregunta${sinResponder !== 1 ? 's' : ''} sin responder.\n¿Deseas finalizar de todas formas?`
                      );
                      if (!confirmar) return;
                    }
                    handleFinalizar();
                  }}
                  className="px-6 py-2 bg-red-600 hover:bg-red-700 rounded-xl text-sm font-semibold transition-colors"
                >
                  Finalizar simulacro
                </button>

                <button
                  onClick={handleSiguiente}
                  disabled={currentIndex === preguntas.length - 1}
                  className="px-5 py-2 bg-slate-700 hover:bg-slate-600 disabled:opacity-30 disabled:cursor-not-allowed rounded-xl text-sm font-medium transition-colors"
                >
                  Siguiente →
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
