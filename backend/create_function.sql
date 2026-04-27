-- Función para calcular resultado del simulacro y guardar detalles
DROP FUNCTION IF EXISTS calcular_resultado_simulacro(INTEGER, JSONB);

CREATE OR REPLACE FUNCTION calcular_resultado_simulacro(p_simulacro_id INTEGER, p_respuestas JSONB)
RETURNS JSONB AS $$
DECLARE
    v_aciertos INTEGER := 0;
    v_errores INTEGER := 0;
    v_sin_responder INTEGER := 0;
    v_puntaje_total DECIMAL := 0;
    v_pregunta RECORD;
    v_puntaje_pregunta DECIMAL;
    v_opcion_correcta INTEGER;
    v_resp JSONB;
    v_opcion_id INTEGER;
    v_es_correcta BOOLEAN;
    v_usuario_id INTEGER;
    v_total_preguntas INTEGER := 0;
BEGIN
    -- Limpiar resultados anteriores
    DELETE FROM resultados_detalle WHERE simulacro_id = p_simulacro_id;

    -- Obtener usuario_id del simulacro
    SELECT usuario_id INTO v_usuario_id FROM simulacros WHERE id = p_simulacro_id;

    -- Contar preguntas
    SELECT COUNT(*) INTO v_total_preguntas FROM respuestas_simulacro WHERE simulacro_id = p_simulacro_id;

    -- Procesar cada pregunta del simulacro
    FOR v_pregunta IN
        SELECT pregunta_id, puntaje_pregunta FROM respuestas_simulacro WHERE simulacro_id = p_simulacro_id ORDER BY orden
    LOOP
        v_opcion_id := NULL;
        v_es_correcta := FALSE;

        -- Buscar respuesta del usuario para esta pregunta
        FOR v_resp IN SELECT jsonb_array_elements(p_respuestas)
        LOOP
            IF (v_resp->>'pregunta_id')::INTEGER = v_pregunta.pregunta_id THEN
                v_opcion_id := (v_resp->>'opcion_seleccionada_id')::INTEGER;
                EXIT;
            END IF;
        END LOOP;

        -- Obtener opción correcta
        SELECT id INTO v_opcion_correcta FROM opciones WHERE pregunta_id = v_pregunta.pregunta_id AND es_correcta = TRUE;

        -- Calcular resultado
        IF v_opcion_id IS NULL THEN
            v_sin_responder := v_sin_responder + 1;
            v_es_correcta := FALSE;
        ELSIF v_opcion_correcta IS NOT NULL AND v_opcion_id = v_opcion_correcta THEN
            v_aciertos := v_aciertos + 1;
            v_puntaje_total := v_puntaje_total + v_pregunta.puntaje_pregunta;
            v_es_correcta := TRUE;
        ELSE
            v_errores := v_errores + 1;
            v_puntaje_total := v_puntaje_total - 1.125;
            v_es_correcta := FALSE;
        END IF;

        -- Guardar detalle de la respuesta
        INSERT INTO resultados_detalle (simulacro_id, pregunta_id, opcion_seleccionada_id, es_correcta, tiempo_respuesta)
        VALUES (p_simulacro_id, v_pregunta.pregunta_id, v_opcion_id, v_es_correcta, 0);
    END LOOP;

    -- Asegurar puntaje no negativo
    IF v_puntaje_total < 0 THEN
        v_puntaje_total := 0;
    END IF;

    -- Actualizar simulacro
    UPDATE simulacros SET puntaje_total = v_puntaje_total, estado = 'finalizado' WHERE id = p_simulacro_id;

    -- Actualizar max/min puntaje del usuario
    UPDATE usuarios SET 
        max_puntaje = GREATEST(COALESCE(max_puntaje, 0), v_puntaje_total),
        min_puntaje = LEAST(COALESCE(min_puntaje, 999999), v_puntaje_total)
    WHERE id = v_usuario_id;

    -- Retornar resultado
    RETURN jsonb_build_object(
        'id', p_simulacro_id,
        'puntaje_total', v_puntaje_total,
        'total_preguntas', v_total_preguntas,
        'aciertos', v_aciertos,
        'errores', v_errores,
        'sin_responder', v_sin_responder,
        'tiempo_total_segundos', 0
    );
END;
$$ LANGUAGE plpgsql;