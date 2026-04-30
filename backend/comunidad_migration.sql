-- Agregar columna de créditos a usuarios
ALTER TABLE usuarios ADD COLUMN consultas_ia_disponibles INT DEFAULT 0;

-- Nueva tabla para historial de comunidad
CREATE TABLE IF NOT EXISTS comunidad_consultas (
    id SERIAL PRIMARY KEY,
    usuario_id INT REFERENCES usuarios(id),
    materia VARCHAR(100),
    pregunta TEXT,
    respuesta TEXT,
    fecha_consulta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice para consultas por usuario
CREATE INDEX IF NOT EXISTS idx_comunidad_usuario ON comunidad_consultas(usuario_id);