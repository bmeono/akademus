CREATE OR REPLACE FUNCTION calcular_resultado_simulacro(p_simulacro_id INTEGER, p_respuestas JSONB)
RETURNS JSONB AS $$
DECLARE
    v_usuario_id UUID;
    v_aciertos INTEGER := 0;
    v_errores INTEGER := 0;
    v_sin_responder INTEGER := 0;
    v_puntaje_total DECIMAL := 0;
    v_pregunta RECORD;
    v_pregunta_asignatura INTEGER;
    v_opcion_correcta INTEGER;
    v_resp JSONB;
    v_opcion_id INTEGER;
    v_max_puntaje DECIMAL;
    v_min_puntaje DECIMAL;
BEGIN
    DELETE FROM resultados_detalle WHERE simulacro_id = p_simulacro_id;

    FOR v_pregunta IN
        SELECT rs.pregunta_id, rs.puntaje_pregunta, p.asignatura_id
        FROM respuestas_simulacro rs
        JOIN preguntas p ON p.id = rs.pregunta_id
        WHERE rs.simulacro_id = p_simulacro_id 
        ORDER BY rs.orden
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
            v_pregunta_asignatura := v_pregunta.asignatura_id;
        ELSIF v_opcion_id = v_opcion_correcta THEN
            v_aciertos := v_aciertos + 1;
            v_puntaje_total := v_puntaje_total + v_pregunta.puntaje_pregunta;
        ELSE
            v_errores := v_errores + 1;
            v_puntaje_total := v_puntaje_total - 1.125;
        END IF;
    END LOOP;

    UPDATE simulacros SET puntaje_total = v_puntaje_total, estado = 'finalizado' WHERE id = p_simulacro_id;

    SELECT usuario_id INTO v_usuario_id FROM simulacros WHERE id = p_simulacro_id;
    SELECT max_puntaje, min_puntaje INTO v_max_puntaje, v_min_puntaje FROM usuarios WHERE id = v_usuario_id;

    IF v_max_puntaje IS NULL THEN
        UPDATE usuarios SET max_puntaje = v_puntaje_total, min_puntaje = v_puntaje_total WHERE id = v_usuario_id;
    ELSIF v_puntaje_total > v_max_puntaje THEN
        UPDATE usuarios SET max_puntaje = v_puntaje_total WHERE id = v_usuario_id;
    ELSIF v_puntaje_total < v_min_puntaje THEN
        UPDATE usuarios SET min_puntaje = v_puntaje_total WHERE id = v_usuario_id;
    END IF;

    RETURN jsonb_build_object(
        'id', p_simulacro_id,
        'puntaje_total', v_puntaje_total,
        'total_preguntas', v_aciertos + v_errores + v_sin_responder,
        'aciertos', v_aciertos,
        'errores', v_errores,
        'sin_responder', v_sin_responder
    );
END;
$$ LANGUAGE plpgsql;