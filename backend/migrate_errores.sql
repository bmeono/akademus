-- Script para generar resultados_detalle de simulacros anteriores
-- Precaución: Esto recrea los datos basándose en lo guardado

-- 1. Limpiar resultados_detalle existentes
DELETE FROM resultados_detalle;

-- 2. Para cada simulacro terminado, generar registros
DO $$
DECLARE
    r_simulacro RECORD;
    r_pregunta RECORD;
    v_opcion_id INTEGER;
    v_opcion_correcta INTEGER;
    v_es_correcta BOOLEAN;
    v_puntaje DECIMAL;
BEGIN
    -- Para cada simulacro terminado
    FOR r_simulacro IN 
        SELECT s.id as simulacro_id, s.usuario_id 
        FROM simulacros s 
        WHERE s.estado = 'finalizado'
    LOOP
        -- Para cada pregunta del simulacro
        FOR r_pregunta IN
            SELECT rs.pregunta_id, rs.puntaje_pregunta
            FROM respuestas_simulacro rs
            WHERE rs.simulacro_id = r_simulacro.simulacro_id
        LOOP
            -- Buscar opción correcta
            SELECT id INTO v_opcion_correcta 
            FROM opciones 
            WHERE pregunta_id = r_pregunta.pregunta_id AND es_correcta = TRUE;
            
            -- Por defecto asume incorrecto (ya que no tenemos la respuesta original)
            -- Esto es una aproximación - los datos reales se pierden
            v_es_correcta := FALSE;
            v_opcion_id := NULL;
            
            -- Insertar registro
            INSERT INTO resultados_detalle (simulacro_id, pregunta_id, opcion_seleccionada_id, es_correcta, tiempo_respuesta)
            VALUES (r_simulacro.simulacro_id, r_pregunta.pregunta_id, v_opcion_id, v_es_correcta, 0);
        END LOOP;
    END LOOP;
    
    RAISE NOTICE 'Proceso completado';
END $$;

-- 3. Verificar registros creados
SELECT COUNT(*) as total_registros FROM resultados_detalle;