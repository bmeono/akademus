import { useEffect, useState, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { simulacrosAPI } from '../services/api';
import api from '../services/api';

interface Opcion   { id: number; texto: string; }
interface Pregunta { id: number; enunciado: string; imagen_url?: string; dificultad: number; orden: number; opciones: Opcion[]; }
interface Resultado { id: number; total_preguntas: number; aciertos: number; errores: number; sin_responder: number; puntaje_total: number; }

export default function SimulacroSession() {
  const { id }       = useParams();
  const navigate     = useNavigate();
  const simulacroId  = Number(id);

  const [preguntas, setPreguntas]           = useState<Pregunta[]>([]);
  const [currentIndex, setCurrentIndex]     = useState(0);
  const [respuestas, setRespuestas]         = useState<Map<number, number>>(new Map());
  const [tiempoRestante, setTiempoRestante] = useState(180 * 60);
  const [loading, setLoading]               = useState(true);
  const [finalizado, setFinalizado]         = useState(false);
  const [resultado, setResultado]           = useState<Resultado | null>(null);
  const [guardando, setGuardando]           = useState(false);
  const [tiempoAgotado, setTiempoAgotado]   = useState(false);

  // ✅ Ref para acceder al estado más reciente dentro del timer sin recrarlo cada segundo
  const respuestasRef  = useRef<Map<number, number>>(new Map());
  const finalizadoRef  = useRef(false);

  // Mantener refs sincronizados
  useEffect(() => { respuestasRef.current = respuestas; }, [respuestas]);
  useEffect(() => { finalizadoRef.current = finalizado; }, [finalizado]);

  // ── Cargar simulacro ──
  useEffect(() => {
    cargarSimulacro();
  }, [id]);

  // ── Timer: se crea UNA sola vez cuando tiempoRestante queda fijado ──
  useEffect(() => {
    if (loading || finalizado || tiempoRestante <= 0) return;

    const interval = setInterval(() => {
      setTiempoRestante(prev => {
        if (prev <= 1) {
          clearInterval(interval);
          // Tiempo agotado: auto-finalizar con las respuestas actuales
          if (!finalizadoRef.current) {
            setTiempoAgotado(true);
            finalizarConRespuestas(respuestasRef.current);
          }
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  // ✅ Solo depende de `loading` y `finalizado`, NO de tiempoRestante
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loading, finalizado]);

  const cargarSimulacro = async () => {
    try {
      const { data } = await simulacrosAPI.getTodasPreguntas(simulacroId);

      // Si ya está finalizado, mostrar resultado
      if (data.estado === 'finalizado') {
        try {
          const resData = await simulacrosAPI.getResultado(simulacroId);
          setResultado(resData.data);
          setFinalizado(true);
        } catch {
          navigate('/simulacros');
        }
        setLoading(false);
        return;
      }

      setPreguntas(data.preguntas);
      setTiempoRestante(data.tiempo_restante > 0 ? data.tiempo_restante : 180 * 60);
      setLoading(false);
    } catch (e) {
      console.error('Error al cargar simulacro:', e);
      navigate('/simulacros');
    }
  };

  // Función base que acepta las respuestas explícitamente (para el timer)
  const finalizarConRespuestas = async (respuestasActuales: Map<number, number>) => {
    setFinalizado(true);
    finalizadoRef.current = true;
    setGuardando(true);

    const respuestasArray = Array.from(respuestasActuales.entries()).map(([preguntaId, opcionId]) => ({
      pregunta_id: preguntaId,
      opcion_seleccionada_id: opcionId,
    }));

    try {
      const response = await api.post('/simulacros/' + simulacroId + '/finalizar', { respuestas: respuestasArray });
      const data = response.data;
      localStorage.setItem('ultimo_simulacro_id', String(data.id));
      setResultado({
        id: data.id,
        total_preguntas: data.total_preguntas,
        aciertos: data.aciertos,
        errores: data.errores,
        sin_responder: data.sin_responder,
        puntaje_total: data.puntaje_total,
      });
    } catch (e) {
      console.error('Error al finalizar:', e);
    }
    setGuardando(false);
  };

  // Función que usa el estado React actual (para el botón manual)
  const handleFinalizar = useCallback(() => {
    finalizarConRespuestas(respuestasRef.current);
  }, [simulacroId]);

  const handleRespuesta = (preguntaId: number, opcionId: number) => {
    if (finalizado) return;
    setRespuestas(prev => {
      const next = new Map(prev);
      next.set(preguntaId, opcionId);
      respuestasRef.current = next;
      return next;
    });
  };

  const formatTiempo = (segundos: number) => {
    const h = Math.floor(segundos / 3600);
    const m = Math.floor((segundos % 3600) / 60);
    const s = segundos % 60;
    return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const currentPregunta = preguntas[currentIndex];
  const respuestaActual = currentPregunta ? respuestas.get(currentPregunta.id) : null;
  const respondidas     = respuestas.size;
  const sinResponder    = preguntas.length - respondidas;
  const tiempoWarning   = tiempoRestante < 600;  // menos de 10 min → rojo
  const tiempoUrgente   = tiempoRestante < 300;  // menos de 5 min → parpadeo

  // ── Loading ──
  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full mx-auto mb-4" />
          <p className="text-slate-300 font-medium">Cargando preguntas...</p>
          <p className="text-slate-500 text-sm mt-1">Esto puede tomar unos segundos</p>
        </div>
      </div>
    );
  }

  // ── Guardando resultado ──
  if (finalizado && (guardando || !resultado)) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full mx-auto mb-4" />
          <p className="text-slate-300 font-medium">
            {tiempoAgotado ? '⏱ Tiempo agotado. Calculando resultados...' : 'Calculando resultados...'}
          </p>
        </div>
      </div>
    );
  }

  // ── Resultado final ──
  if (finalizado && resultado) {
    const pct = resultado.total_preguntas > 0
      ? Math.round((resultado.aciertos / resultado.total_preguntas) * 100)
      : 0;

    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full space-y-6">
          {tiempoAgotado && (
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 text-center text-amber-700 text-sm font-medium">
              ⏱ El tiempo se agotó — simulacro finalizado automáticamente
            </div>
          )}
          <div className="text-center">
            <div className="w-24 h-24 rounded-full flex items-center justify-center mx-auto mb-4 border-4"
              style={{ borderColor: pct >= 60 ? '#22c55e' : pct >= 40 ? '#f59e0b' : '#ef4444' }}>
              <span className="text-3xl font-bold" style={{ color: pct >= 60 ? '#16a34a' : pct >= 40 ? '#d97706' : '#dc2626' }}>
                {pct}%
              </span>
            </div>
            <h2 className="text-2xl font-bold text-slate-900">¡Simulacro finalizado!</h2>
            <p className="text-slate-500 mt-1">
              Puntaje: <strong className="text-primary-600 text-lg">{resultado.puntaje_total.toFixed(2)}</strong>
            </p>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div className="bg-green-50 border border-green-100 rounded-xl p-4 text-center">
              <p className="text-2xl font-bold text-green-700">{resultado.aciertos}</p>
              <p className="text-xs text-green-600 mt-0.5">Correctas</p>
            </div>
            <div className="bg-red-50 border border-red-100 rounded-xl p-4 text-center">
              <p className="text-2xl font-bold text-red-700">{resultado.errores}</p>
              <p className="text-xs text-red-600 mt-0.5">Incorrectas</p>
            </div>
            <div className="bg-slate-50 border border-slate-100 rounded-xl p-4 text-center">
              <p className="text-2xl font-bold text-slate-600">{resultado.sin_responder}</p>
              <p className="text-xs text-slate-500 mt-0.5">Sin resp.</p>
            </div>
          </div>

          <div className="space-y-3">
            <button
              onClick={() => simulacrosAPI.downloadResultadoPDF(resultado.id)}
              className="w-full py-3 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded-xl transition-colors"
            >
              📄 Descargar PDF
            </button>
            <button
              onClick={() => navigate('/simulacros')}
              className="w-full py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium rounded-xl transition-colors"
            >
              Nuevo simulacro
            </button>
            <button
              onClick={() => navigate('/dashboard')}
              className="w-full py-2 text-slate-400 hover:text-slate-600 text-sm transition-colors"
            >
              Ir al dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ── Simulacro en curso ──
  return (
    <div className="min-h-screen bg-slate-900 text-white flex flex-col">

      {/* ── Barra superior ── */}
      <div className="bg-slate-800 border-b border-slate-700 px-6 py-3 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-4">
          <span className="font-display font-bold text-primary-400 text-lg">AKADEMUS</span>
          <span className="text-slate-500 text-sm hidden sm:block">Simulacro #{simulacroId}</span>
        </div>

        <div className="flex items-center gap-6">
          {/* Progreso */}
          <div className="hidden sm:flex items-center gap-2">
            <div className="w-28 h-2 bg-slate-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-primary-500 rounded-full transition-all"
                style={{ width: `${preguntas.length > 0 ? (respondidas / preguntas.length) * 100 : 0}%` }}
              />
            </div>
            <span className="text-sm text-slate-400">{respondidas}/{preguntas.length}</span>
          </div>

          {/* ── Timer ── siempre visible, prominente */}
          <div className={`flex items-center gap-2 px-4 py-2 rounded-xl font-mono font-bold text-lg tracking-widest ${
            tiempoUrgente
              ? 'bg-red-700 text-white animate-pulse'
              : tiempoWarning
                ? 'bg-red-900 text-red-300'
                : 'bg-slate-700 text-slate-100'
          }`}>
            <span>⏱</span>
            <span>{formatTiempo(tiempoRestante)}</span>
          </div>
        </div>
      </div>

      {/* ── Contenido ── */}
      <div className="flex flex-1 overflow-hidden">

        {/* Panel lateral: mapa de preguntas */}
        <div className="w-52 bg-slate-800 border-r border-slate-700 flex flex-col overflow-hidden flex-shrink-0 hidden md:flex">
          <div className="p-3 border-b border-slate-700">
            <p className="text-xs text-slate-400 font-medium uppercase tracking-wide">Navegación</p>
            <p className="text-xs text-slate-500 mt-0.5">
              {sinResponder > 0 ? `${sinResponder} sin responder` : '✓ Todas respondidas'}
            </p>
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
          <div className="p-3 border-t border-slate-700 space-y-1">
            <div className="flex items-center gap-2 text-xs text-slate-400"><div className="w-3 h-3 rounded bg-green-600" /> Respondida</div>
            <div className="flex items-center gap-2 text-xs text-slate-400"><div className="w-3 h-3 rounded bg-primary-500" /> Actual</div>
            <div className="flex items-center gap-2 text-xs text-slate-400"><div className="w-3 h-3 rounded bg-slate-700" /> Sin responder</div>
          </div>
        </div>

        {/* Panel central: pregunta */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {currentPregunta && (
            <>
              <div className="flex-1 overflow-y-auto p-6 lg:p-8">
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
                        {currentPregunta.dificultad === 1 ? 'Fácil' : currentPregunta.dificultad === 2 ? 'Medio' : 'Difícil'}
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
                      const letra    = String.fromCharCode(65 + idx);
                      const selected = respuestaActual === opcion.id;
                      return (
                        <button
                          key={opcion.id}
                          onClick={() => handleRespuesta(currentPregunta.id, opcion.id)}
                          disabled={finalizado}
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
              <div className="border-t border-slate-700 bg-slate-800 px-6 py-4 flex items-center justify-between flex-shrink-0">
                <button
                  onClick={() => setCurrentIndex(i => Math.max(0, i - 1))}
                  disabled={currentIndex === 0}
                  className="px-5 py-2 bg-slate-700 hover:bg-slate-600 disabled:opacity-30 disabled:cursor-not-allowed rounded-xl text-sm font-medium transition-colors"
                >
                  ← Anterior
                </button>

                {/* Responsive: en móvil mostrar progreso aquí */}
                <div className="flex md:hidden items-center gap-2 text-sm text-slate-400">
                  <span>{respondidas}/{preguntas.length}</span>
                  <div className={`font-mono font-bold px-2 py-1 rounded ${tiempoWarning ? 'text-red-400' : 'text-slate-300'}`}>
                    {formatTiempo(tiempoRestante)}
                  </div>
                </div>

                <button
                  onClick={() => {
                    if (sinResponder > 0) {
                      const ok = window.confirm(
                        `Tienes ${sinResponder} pregunta${sinResponder !== 1 ? 's' : ''} sin responder.\n¿Deseas finalizar el simulacro de todas formas?`
                      );
                      if (!ok) return;
                    }
                    handleFinalizar();
                  }}
                  disabled={finalizado}
                  className="px-6 py-2 bg-red-600 hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl text-sm font-semibold transition-colors"
                >
                  Finalizar simulacro
                </button>

                <button
                  onClick={() => setCurrentIndex(i => Math.min(preguntas.length - 1, i + 1))}
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
