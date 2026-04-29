-- Índices de rendimiento para Akademus
-- Ejecutar en la base de datos Neon

-- Índices para opciones (N+1 query fix)
CREATE INDEX IF NOT EXISTS idx_opciones_pregunta ON opciones(pregunta_id);

-- Índices para preguntas
CREATE INDEX IF NOT EXISTS idx_preguntas_tema ON preguntas(tema_id);
CREATE INDEX IF NOT EXISTS idx_preguntas_asignatura ON preguntas(asignatura_id);
CREATE INDEX IF NOT EXISTS idx_preguntas_usuario ON preguntas(usuario_id);
CREATE INDEX IF NOT EXISTS idx_preguntas_estado ON preguntas(estado);

-- Índices para respuestas_simulacro (dashboard JOINs)
CREATE INDEX IF NOT EXISTS idx_respuestas_simulacro_pregunta ON respuestas_simulacro(pregunta_id);
CREATE INDEX IF NOT EXISTS idx_respuestas_simulacro_simulacro ON respuestas_simulacro(simulacro_id);

-- Índices para simulacros
CREATE INDEX IF NOT EXISTS idx_simulacros_estado ON simulacros(estado);
CREATE INDEX IF NOT EXISTS idx_simulacros_usuario ON simulacros(usuario_id);

-- Índices para resultados_detalle
CREATE INDEX IF NOT EXISTS idx_resultados_detalle_simulacro ON resultados_detalle(simulacro_id);
CREATE INDEX IF NOT EXISTS idx_resultados_detalle_correcta ON resultados_detalle(es_correcta);

-- Index para flashcards
CREATE INDEX IF NOT EXISTS idx_flashcards_usuario ON flashcards(usuario_id);
CREATE INDEX IF NOT EXISTS idx_flashcards_pregunta ON flashcards(pregunta_id);

-- Index para usuario_permisos
CREATE INDEX IF NOT EXISTS idx_usuario_permisos_usuario ON usuario_permisos(usuario_id);