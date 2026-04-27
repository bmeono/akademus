import psycopg2

conn = psycopg2.connect(host='localhost', port=5432, user='postgres', password='1323Bri@ncisc0', database='akademus')
cur = conn.cursor()

# Hacer tema_id nullable
print("Haciendo tema_id nullable...")
cur.execute("ALTER TABLE preguntas ALTER COLUMN tema_id DROP NOT NULL")
conn.commit()
print("  tema_id ahora es nullable")

# Limpiar preguntas existentes si hay
cur.execute("DELETE FROM preguntas WHERE TRUE")
cur.execute("DELETE FROM opciones WHERE TRUE")
conn.commit()
print("  Preguntas y opciones limpiadas")

# Crear preguntas de prueba
print()
print("Creando preguntas de prueba...")

preguntas_test = [
    (75, "Si x + 5 = 12, cuanto vale x?"),
    (75, "Un tren viaja a 60 km/h. Cuantos km recorre en 2.5 horas?"),
    (75, "Cual es el 20% de 150?"),
    (75, "Si un producto cuesta 80 soles y tiene un descuento del 15%, cuanto pago?"),
    (75, "Cual es el MCD de 24 y 36?"),
    (76, "Cuanto mide la suma de los angulos internos de un triangulo?"),
    (76, "Si un circulo tiene radio 7 cm, cual es su area? (use pi = 3.1416)"),
    (76, "Cuantos lados tiene un hexagono?"),
    (76, "Un rectangulo mide 8 cm de largo y 5 cm de ancho. Cual es su perimetro?"),
    (76, "Si un triangulo tiene base 10 cm y altura 6 cm, cual es su area?"),
    (73, "Identifique el antonimo de ALEGRE:"),
    (73, "Cual es el sinonimo de DILIGENTE?"),
    (73, "Complete: El estudiante ___ todos los dias:"),
    (73, "Que tipo de texto es una cronica de un evento historico?"),
    (73, "Identifique la oracion con error ortografico:"),
    (77, "Resuelva: 2x + 3 = 11"),
    (77, "Factorice: x^2 - 9"),
    (77, "Cual es el valor de x en 3x = 24?"),
    (77, "Resuelva el sistema: x + y = 10, x - y = 4"),
    (77, "Si f(x) = 2x + 1, cuanto vale f(3)?"),
    (78, "Si sen(30) = 0.5, cuanto vale cos(60)?"),
    (78, "Convierta 90 grados a radianes"),
    (78, "Cual es el valor de tan(45)?"),
    (78, "Si un triangulo tiene angulos 30, 60 y 90, cual es el tercero?"),
    (78, "Cual es la identidad trigonometrica fundamental?"),
]

respuestas_test = [
    ["x = 5", "x = 7", "x = 17", "x = 6"],
    ["120 km", "150 km", "100 km", "140 km"],
    ["20", "30", "25", "35"],
    ["68 soles", "72 soles", "64 soles", "12 soles"],
    ["6", "12", "8", "18"],
    ["90 grados", "270 grados", "360 grados", "180 grados"],
    ["14 cm2", "153.94 cm2", "21.99 cm2", "43.98 cm2"],
    ["5", "7", "6", "8"],
    ["26 cm", "40 cm", "13 cm", "20 cm"],
    ["30 cm2", "16 cm2", "60 cm2", "32 cm2"],
    ["Triste", "Feliz", "Contento", "Satisfecho"],
    ["Vago", "Trabajador", "Lento", "Descuidado"],
    ["corre", "estudia", "duerme", "juega"],
    ["Descriptivo", "Argumentativo", "Narrativo", "Expositivo"],
    ["Hizo", "Hiso", "izo", "Echo"],
    ["x = 4", "x = 3.67", "x = 14", "x = 5.5"],
    ["(x-3)(x+3)", "(x-3)(x+3)", "(x-9)(x+9)", "(x-3)2"],
    ["x = 6", "x = 8", "x = 12", "x = 24"],
    ["x = 7, y = 3", "x = 6, y = 4", "x = 5, y = 5", "x = 8, y = 2"],
    ["7", "5", "4", "6"],
    ["0.5", "0.707", "1", "0.866"],
    ["pi/2", "pi", "2pi", "pi/4"],
    ["0", "1", "infinito", "0.5"],
    ["90 grados", "30 grados", "60 grados", "120 grados"],
    ["sen2 + cos2 = 1", "sen + cos = 1", "sen = cos", "tan = sen/cos"],
]

correctas = [1, 1, 1, 0, 1, 3, 1, 2, 0, 0, 0, 1, 1, 2, 2, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0]

# Insertar preguntas y respuestas
total_preg = 0
total_resp = 0

for i, (asig_id, enunciado) in enumerate(preguntas_test):
    # Insertar pregunta
    cur.execute("""
        INSERT INTO preguntas (asignatura_id, enunciado, dificultad, activa, tema_id)
        VALUES (%s, %s, %s, TRUE, NULL)
        RETURNING id
    """, (asig_id, enunciado, 2))
    preg_id = cur.fetchone()[0]
    total_preg += 1
    
    # Insertar respuestas
    for j, texto in enumerate(respuestas_test[i]):
        es_correcta = (j == correctas[i])
        cur.execute("""
            INSERT INTO opciones (pregunta_id, texto, es_correcta, activa)
            VALUES (%s, %s, %s, TRUE)
        """, (preg_id, texto, es_correcta))
        total_resp += 1

conn.commit()
print(f"  {total_preg} preguntas creadas")
print(f"  {total_resp} respuestas creadas")

# Mostrar resumen
print()
print("=== RESUMEN ===")
cur.execute("SELECT a.nombre, COUNT(p.id) FROM asignaturas a LEFT JOIN preguntas p ON a.id = p.asignatura_id GROUP BY a.id, a.nombre")
for r in cur.fetchall(): print(f"  {r[0]}: {r[1]} preguntas")

print()
print("=== RESPUESTAS POR PREGUNTA ===")
cur.execute("""
    SELECT p.enunciado, COUNT(o.id), SUM(CASE WHEN o.es_correcta THEN 1 ELSE 0 END)
    FROM preguntas p LEFT JOIN opciones o ON p.id = o.pregunta_id
    GROUP BY p.id, p.enunciado
    LIMIT 5
""")
for r in cur.fetchall(): print(f"  '{r[0][:40]}...' -> {r[1]} opciones, {r[2]} correcta(s)")

conn.close()
print()
print("OK - Base de datos actualizada")