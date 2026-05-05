-- ============================================================================
-- SEED DATA - Modelos Computación Django Backend
-- App de lectura rápida con gamificación
--
-- Cómo usar:
--   1. python manage.py migrate
--   2. python manage.py dbshell < scripts/seed.sql
--   3. Listo! Ya puedes probar la API con datos reales
-- ============================================================================

-- ============================================================================
-- 1. USUARIOS (auth_user)
-- ============================================================================
-- Contraseña para todos los usuarios: Pass1234!
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined)
VALUES
(1, 'pbkdf2_sha256$1200000$CwusNaEeLTSJpQGanrSkB4$DTlwqfLD4hg60nySRB8cm4lZFVcdwBZy80deO77m16g=', NULL, 1, 'admin', 'Admin', 'Sistema', 'admin@lecturapp.com', 1, 1, '2026-05-01 00:00:00'),
(2, 'pbkdf2_sha256$1200000$CwusNaEeLTSJpQGanrSkB4$DTlwqfLD4hg60nySRB8cm4lZFVcdwBZy80deO77m16g=', NULL, 0, 'lector1', 'Carlos', 'López', 'carlos@email.com', 0, 1, '2026-05-01 00:00:00'),
(3, 'pbkdf2_sha256$1200000$CwusNaEeLTSJpQGanrSkB4$DTlwqfLD4hg60nySRB8cm4lZFVcdwBZy80deO77m16g=', NULL, 0, 'lector2', 'María', 'García', 'maria@email.com', 0, 1, '2026-05-02 00:00:00');

-- ============================================================================
-- 2. TOKENS DE AUTENTICACIÓN (authtoken_token)
-- ============================================================================
INSERT INTO authtoken_token (key, user_id, created)
VALUES
('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 1, '2026-05-01 00:00:00'),
('bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', 2, '2026-05-01 00:00:00'),
('cccccccccccccccccccccccccccccccccccccccc', 3, '2026-05-02 00:00:00');

-- ============================================================================
-- 3. PERFILES DE USUARIO (cuentas_perfilusuario)
-- ============================================================================
INSERT INTO cuentas_perfilusuario (id, user_id, fecha_nacimiento, genero, pais, fecha_registro)
VALUES
(1, 1, '1990-03-15', 'M', 'México', '2026-05-01 00:00:00'),
(2, 2, '1995-07-22', 'M', 'Colombia', '2026-05-01 00:00:00'),
(3, 3, '2000-11-08', 'F', 'Argentina', '2026-05-02 00:00:00');

-- ============================================================================
-- 4. AUTORES (libros_autor)
-- ============================================================================
INSERT INTO libros_autor (id, nombre, pais, fecha_nacimiento)
VALUES
(1, 'Gabriel García Márquez', 'Colombia', '1927-03-06'),
(2, 'Isabel Allende', 'Chile', '1942-08-02'),
(3, 'Julio Cortázar', 'Argentina', '1914-08-26'),
(4, 'Mario Vargas Llosa', 'Perú', '1936-03-28'),
(5, 'Laura Esquivel', 'México', '1950-09-30');

-- ============================================================================
-- 5. LIBROS (libros_libro)
-- ============================================================================
INSERT INTO libros_libro (id, titulo, autor_id, isbn, fecha_publicacion, genero, numero_paginas, editorial, descripcion)
VALUES
(1, 'Cien años de soledad', 1, '9788437604947', '2026-05-01', 'Ficción', 471, 'Sudamericana', 'La historia de la familia Buendía en Macondo, una obra maestra del realismo mágico.'),
(2, 'El amor en los tiempos del cólera', 1, '9780307389732', '2026-05-01', 'Ficción', 368, 'Sudamericana', 'Una historia de amor que dura toda una vida.'),
(3, 'La casa de los espíritus', 2, '9780060883287', '2026-05-01', 'Ficción', 543, 'Plaza & Janés', 'La historia de la familia Trueba a lo largo de varias generaciones.'),
(4, 'Rayuela', 3, '9788437604572', '2026-05-01', 'Ficción', 736, 'Sudamericana', 'Una novela que se puede leer de múltiples maneras.'),
(5, 'Como agua para chocolate', 5, '9780385420167', '2026-05-01', 'Ficción', 256, 'Plaza & Janés', 'Novela de recetas y amores prohibidos en la Revolución Mexicana.');

-- ============================================================================
-- 6. SESIONES DE LECTURA (lectura_sesionlectura)
-- ============================================================================
INSERT INTO lectura_sesionlectura (id, usuario_id, libro_id, fecha_inicio, fecha_fin, duracion_segundos, paginas_leidas, palabras_por_pagina, palabras_por_minuto, activa, notas, fecha_creacion, fecha_actualizacion)
VALUES
-- lector1: 3 sesiones de Cien años de soledad
(1, 2, 1, '2026-05-01 09:00:00', '2026-05-01 09:30:00', 1800, 15, 250, 125, 0, 'Primera lectura. Me está gustando mucho.', '2026-05-01 09:00:00', '2026-05-01 09:30:00'),
(2, 2, 1, '2026-05-02 10:00:00', '2026-05-02 10:45:00', 2700, 25, 250, 139, 0, 'Cada vez más interesante.', '2026-05-02 10:00:00', '2026-05-02 10:45:00'),
(3, 2, 1, '2026-05-03 08:30:00', '2026-05-03 09:00:00', 1800, 20, 250, 167, 0, 'Tercera sesión, mejorando velocidad.', '2026-05-03 08:30:00', '2026-05-03 09:00:00'),
-- lector1: 1 sesión de Rayuela
(4, 2, 4, '2026-05-04 11:00:00', '2026-05-04 11:20:00', 1200, 10, 250, 125, 0, 'Rayuela es un reto interesante.', '2026-05-04 11:00:00', '2026-05-04 11:20:00'),
-- lector2: 2 sesiones de La casa de los espíritus
(5, 3, 3, '2026-05-02 14:00:00', '2026-05-02 14:35:00', 2100, 18, 250, 129, 0, '', '2026-05-02 14:00:00', '2026-05-02 14:35:00'),
(6, 3, 3, '2026-05-03 15:00:00', '2026-05-03 15:40:00', 2400, 22, 250, 138, 0, 'Me encanta la narrativa de Allende.', '2026-05-03 15:00:00', '2026-05-03 15:40:00'),
-- lector2: 1 sesión de Como agua para chocolate
(7, 3, 5, '2026-05-04 09:00:00', '2026-05-04 09:15:00', 900, 8, 250, 133, 0, '', '2026-05-04 09:00:00', '2026-05-04 09:15:00'),
-- admin: 1 sesión activa (para probar)
(8, 1, 2, '2026-05-05 10:00:00', '2026-05-05 10:30:00', 1800, 12, 250, 100, 0, '', '2026-05-05 10:00:00', '2026-05-05 10:30:00');

-- ============================================================================
-- 7. PROGRESO DE LIBROS (lectura_progresolibro)
-- ============================================================================
INSERT INTO lectura_progresolibro (id, usuario_id, libro_id, pagina_actual, paginas_totales, completado, fecha_inicio, fecha_completado, calificacion, fecha_actualizacion)
VALUES
(1, 2, 1, 60, 471, 0, '2026-05-01 09:00:00', NULL, NULL, '2026-05-03 09:00:00'),
(2, 2, 4, 10, 736, 0, '2026-05-04 11:00:00', NULL, NULL, '2026-05-04 11:20:00'),
(3, 3, 3, 40, 543, 0, '2026-05-02 14:00:00', NULL, NULL, '2026-05-03 15:40:00'),
(4, 3, 5, 8, 256, 0, '2026-05-04 09:00:00', NULL, NULL, '2026-05-04 09:15:00'),
(5, 1, 2, 12, 368, 0, '2026-05-05 10:00:00', NULL, NULL, '2026-05-05 10:30:00');

-- ============================================================================
-- 8. METAS DE LECTURA (metas_metalectura)
-- ============================================================================
INSERT INTO metas_metalectura (id, usuario_id, nombre, tipo, tipo_objetivo, objetivo_valor, activa, fecha_creacion, fecha_actualizacion)
VALUES
-- Metas de lector1
(1, 2, 'Leer 30 páginas al día', 'diaria', 'paginas', 30, 1, '2026-05-01 00:00:00', '2026-05-01 00:00:00'),
(2, 2, 'Leer 3 horas a la semana', 'semanal', 'minutos', 180, 1, '2026-05-01 00:00:00', '2026-05-01 00:00:00'),
(3, 2, 'Terminar 2 libros al mes', 'mensual', 'libros', 2, 1, '2026-05-01 00:00:00', '2026-05-01 00:00:00'),
-- Metas de lector2
(4, 3, 'Leer 20 páginas al día', 'diaria', 'paginas', 20, 1, '2026-05-02 00:00:00', '2026-05-02 00:00:00'),
(5, 3, 'Hacer 5 sesiones a la semana', 'semanal', 'sesiones', 5, 1, '2026-05-02 00:00:00', '2026-05-02 00:00:00');

-- ============================================================================
-- 9. PRUEBAS DE COMPRENSIÓN (comprension_pruebacomprension)
-- ============================================================================
INSERT INTO comprension_pruebacomprension (id, libro_id, titulo, pregunta, opcion_a, opcion_b, opcion_c, opcion_d, respuesta_correcta, dificultad, activa, fecha_creacion)
VALUES
-- Cien años de soledad (libro 1)
(1, 1, 'Capítulo 1 - Macondo', '¿Cómo se llamaba el fundador de Macondo?', 'Aureliano Buendía', 'José Arcadio Buendía', 'Arcadio', 'Melquíades', 'B', 'facil', 1, '2026-05-01 00:00:00'),
(2, 1, 'Capítulo 1 - La aldea', '¿Cuántas casas tenía Macondo al inicio del libro?', '10', '20', '30', '50', 'B', 'facil', 1, '2026-05-01 00:00:00'),
(3, 1, 'Personajes - Los gitanos', '¿Cómo se llamaba el gitano que visitaba Macondo?', 'Melquíades', 'Prudencio', 'Aureliano', 'José Arcadio', 'A', 'media', 1, '2026-05-01 00:00:00'),
(4, 1, 'Temática general', '¿Qué género literario representa mejor esta obra?', 'Realismo', 'Realismo mágico', 'Fantasía', 'Ficción científica', 'B', 'media', 1, '2026-05-01 00:00:00'),
-- La casa de los espíritus (libro 3)
(5, 3, 'Personajes - Los Trueba', '¿Quién narra la historia en La casa de los espíritus?', 'Esteban Trueba', 'Clara', 'Alba', 'Blanca', 'C', 'dificil', 1, '2026-05-01 00:00:00'),
(6, 3, 'Temática', '¿Qué poder especial tiene Clara?', 'Leer mentes', 'Predecir el futuro', 'Hablar con animales', 'Teletransportarse', 'B', 'media', 1, '2026-05-01 00:00:00'),
-- Como agua para chocolate (libro 5)
(7, 5, 'Argumento', '¿Qué relación tienen las recetas con la historia?', 'Son el tema principal', 'Cada capítulo comienza con una receta', 'No tienen relación', 'Son metafóricas', 'B', 'facil', 1, '2026-05-01 00:00:00'),
(8, 5, 'Protagonista', '¿Cómo se llama la protagonista?', 'Rosaura', 'Gertrudis', 'Tita', 'Mamá Elena', 'C', 'facil', 1, '2026-05-01 00:00:00');

-- ============================================================================
-- 10. INTENTOS DE PRUEBAS (comprension_intentoprueba)
-- ============================================================================
INSERT INTO comprension_intentoprueba (id, usuario_id, prueba_id, respuesta, correcta, fecha_intento)
VALUES
(1, 2, 1, 'B', 1, '2026-05-01 10:00:00'),
(2, 2, 2, 'B', 1, '2026-05-01 10:01:00'),
(3, 2, 3, 'A', 1, '2026-05-01 10:02:00'),
(4, 2, 4, 'C', 0, '2026-05-01 10:03:00'),  -- ¡Falló!
(5, 3, 5, 'C', 1, '2026-05-02 15:00:00'),
(6, 3, 6, 'A', 0, '2026-05-02 15:01:00'),  -- ¡Falló!
(7, 1, 1, 'B', 1, '2026-05-05 11:00:00'),
(8, 1, 4, 'B', 1, '2026-05-05 11:01:00');

-- ============================================================================
-- 11. LOGROS DE USUARIO (gamificacion_logrousuario)
-- NOTA: Los logros (gamificacion_logro) ya se crean automáticamente
--       con la migración 0002_seed_logros.py
-- ============================================================================
-- Logro 1 = "Primeros Pasos" (1 sesión)
INSERT INTO gamificacion_logrousuario (id, usuario_id, logro_id, fecha_desbloqueo)
VALUES
(1, 2, 1, '2026-05-01 09:30:00'),
(2, 3, 1, '2026-05-02 14:35:00'),
(3, 1, 1, '2026-05-05 10:30:00');

-- ============================================================================
-- ¡TODO LISTO! Datos cargados exitosamente.
-- ============================================================================
