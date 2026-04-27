-- Add missing column to resultados_detalle
ALTER TABLE resultados_detalle ADD COLUMN IF NOT EXISTS tiempo_respuesta INTEGER DEFAULT 0;