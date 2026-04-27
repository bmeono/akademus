-- Tabla de flashcards con repetición espaciada
CREATE TABLE IF NOT EXISTS flashcards (
    id SERIAL PRIMARY KEY,
    usuario_id UUID NOT NULL REFERENCES usuarios(id),
    pregunta_id INTEGER NOT NULL REFERENCES preguntas(id),
    
    -- Estado de la tarjeta
    estado VARCHAR(20) DEFAULT 'activa',  -- activa, dominada
    
    -- Repetición espaciada
    facilidad INTEGER DEFAULT 2500,  -- factor Ease (x100 para evitar decimales)
    intervalo INTEGER DEFAULT 1,  -- días hasta próxima revisión
    repeticiones INTEGER DEFAULT 0,  -- veces que ha respondido correctamente
    
    -- Fechas
    proxima_revision DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(usuario_id, pregunta_id)
);

-- Tabla de historial de repeticiones
CREATE TABLE IF NOT EXISTS flashcard_historial (
    id SERIAL PRIMARY KEY,
    flashcard_id INTEGER NOT NULL REFERENCES flashcards(id),
    usuario_id UUID NOT NULL REFERENCES usuarios(id),
    
    calidad_respuesta INTEGER,  -- 0-5 (0=olvidé, 5=muy fácil)
    tiempo_respuesta INTEGER DEFAULT 0,  -- segundos
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agregar columnas si no existen
ALTER TABLE flashcards ADD COLUMN IF NOT EXISTS estado VARCHAR(20) DEFAULT 'activa';
ALTER TABLE flashcards ADD COLUMN IF NOT EXISTS facilidad INTEGER DEFAULT 2500;
ALTER TABLE flashcards ADD COLUMN IF NOT EXISTS intervalo INTEGER DEFAULT 1;
ALTER TABLE flashcards ADD COLUMN IF NOT EXISTS repeticiones INTEGER DEFAULT 0;
ALTER TABLE flashcards ADD COLUMN IF NOT EXISTS proxima_revision DATE DEFAULT CURRENT_DATE;