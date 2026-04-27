import { useState, useEffect, useCallback } from 'react';
import { Play, Pause, RotateCcw } from 'lucide-react';

interface TimerProps {
  segundos: number;
  onComplete?: () => void;
  onTick?: (restantes: number) => void;
  activo?: boolean;
}

export function Timer({ segundos, onComplete, onTick, activo = true }: TimerProps) {
  const [tiempo, setTiempo] = useState(segundos);
  const [corriendo, setCorriendo] = useState(activo);
  
  useEffect(() => {
    setTiempo(segundos);
  }, [segundos]);
  
  useEffect(() => {
    if (!corriendo || tiempo <= 0) return;
    
    const interval = setInterval(() => {
      setTiempo((t) => {
        const nuevo = t - 1;
        onTick?.(nuevo);
        if (nuevo <= 0) {
          setCorriendo(false);
          onComplete?.();
          return 0;
        }
        return nuevo;
      });
    }, 1000);
    
    return () => clearInterval(interval);
  }, [corriendo, tiempo, onComplete, onTick]);
  
  const formatTime = (s: number) => {
    const mins = Math.floor(s / 60);
    const secs = s % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };
  
  const porcentaje = (tiempo / segundos) * 100;
  const color = tiempo < 60 ? 'text-error-500' : tiempo < 300 ? 'text-warning-500' : 'text-slate-900';
  
  return (
    <div className="flex items-center gap-4">
      <div className={`font-mono text-5xl font-bold tabular-nums ${color}`}>
        {formatTime(tiempo)}
      </div>
      <div className="w-32 h-2 bg-slate-200 rounded-full overflow-hidden">
        <div
          className={`h-full transition-all duration-1000 ${
            tiempo < 60 ? 'bg-error-500' : tiempo < 300 ? 'bg-warning-500' : 'bg-primary-500'
          }`}
          style={{ width: `${porcentaje}%` }}
        />
      </div>
      <button
        onClick={() => setCorriendo(!corriendo)}
        className="p-2 rounded-lg hover:bg-slate-100 transition-colors"
      >
        {corriendo ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
      </button>
      <button
        onClick={() => setTiempo(segundos)}
        className="p-2 rounded-lg hover:bg-slate-100 transition-colors"
      >
        <RotateCcw className="w-5 h-5" />
      </button>
    </div>
  );
}