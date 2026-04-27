CREATE OR REPLACE FUNCTION calcular_resultado_simulacro(p_simulacro_id INTEGER, p_respuestas JSONB)
RETURNS JSONB AS $$
DECLARE
    v_aciertos INTEGER := 0;
    v_errores INTEGER := 0;
    v_sin_responder INTEGER := 0;
    v_puntaje_total DECIMAL := 0;
    v_pregunta RECORD;
    v_opcion_correcta INTEGER;
    v_resp JSONB;
    v_opcion_id INTEGER;
BEGIN
    DELETE FROM resultados_detalle WHERE simulacro_id = p_simulacro_id;

    FOR v_pregunta IN
        SELECT pregunta_id, puntaje_pregunta FROM respuestas_simulacro WHERE simulacro_id = p_simulacro_id ORDER BY orden
    LOOP
        v_opcion_id := NULL;

        FOR v_resp IN SELECT jsonb_array_elements(p_respuestas)
        LOOP
            IF (v_resp->>'pregunta_id')::INTEGER = v_pregunta.pregunta_id THEN
                v_opcion_id := (v_resp->>'opcion_seleccionada_id')::INTEGER;
                EXIT;
            END IF;
        END LOOP;

        SELECT id INTO v_opcion_correcta FROM opciones WHERE pregunta_id = v_pregunta.pregunta_id AND es_correcta = TRUE;

        IF v_opcion_id IS NULL THEN
            v_sin_responder := v_sin_responder + 1;
        ELSIF v_opcion_id = v_opcion_correcta THEN
            v_aciertos := v_aciertos + 1;
            v_puntaje_total := v_puntaje_total + v_pregunta.puntaje_pregunta;
        ELSE
            v_errores := v_errores + 1;
            v_puntaje_total := v_puntaje_total - 1.125;
        END IF;
    END LOOP;

    UPDATE simulacros SET puntaje_total = v_puntaje_total, estado = 'finalizado' WHERE id = p_simulacro_id;

    RETURN jsonb_build_object(
        'id', p_simulacro_id,
        'puntaje_total', v_puntaje_total,
        'total_preguntas', v_aciertos + v_errores + v_sin_responder,
        'aciertos', v_aciertos,
        'errores', v_errores,
        'sin_responder', v_sin_responder,
        'tiempo_total_segundos', 0
    );
END;
$$ LANGUAGE plpgsql;