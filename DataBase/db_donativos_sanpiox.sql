-- ============================================================================
-- BASE DE DATOS: GESTOR SOLIDARIO DE DONATIVOS - COLEGIO SAN PIO X
-- Flujo: Control de Acceso por Roles (Agente Pastoral vs. Donante/Familia)
-- ============================================================================

DROP DATABASE IF EXISTS db_donativos_sanpiox;
CREATE DATABASE db_donativos_sanpiox
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE db_donativos_sanpiox;

-- ----------------------------------------------------------------------------
-- 1. USUARIOS DEL SISTEMA (Login y Control de Acceso por Rol)
-- ----------------------------------------------------------------------------
CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    codigo_usuario VARCHAR(15) NOT NULL UNIQUE,          -- Ej: 'A001' (Pastoral), 'U001' (Donante)
    nombre_completo VARCHAR(150) NOT NULL,               -- Ej: 'Prof. Taipe', 'Familia Quispe'
    correo_electronico VARCHAR(150) NOT NULL UNIQUE,     -- Credencial de acceso
    password_hash VARCHAR(255) NOT NULL,                 -- Hash Argon2 asignado por el Agente Pastoral
    telefono VARCHAR(25) NULL,                           -- Ej: '+51 999 999 999'
    tipo_usuario ENUM('Administrativo', 'Donante') NOT NULL,
    creado_por_id INT NULL,                              -- ID del Agente Pastoral que creó esta cuenta
    estado TINYINT(1) NOT NULL DEFAULT 1,                -- 1: Activo, 0: Bloqueado/Inactivo
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_usuario_creador
        FOREIGN KEY (creado_por_id) REFERENCES usuarios(id_usuario)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 1.1 SOLICITUDES DE RECUPERACION DE ACCESO
-- ----------------------------------------------------------------------------
CREATE TABLE solicitudes_recuperacion (
    id_solicitud INT AUTO_INCREMENT PRIMARY KEY,
    correo_electronico VARCHAR(150) NOT NULL,
    fecha_solicitud DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atendida TINYINT(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 2. DONANTES / PROCEDENCIA (Paso 1 del Formulario Pastoral)
-- ----------------------------------------------------------------------------
CREATE TABLE donantes (
    id_donante INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NULL,                                 -- Enlace opcional si el donante tiene cuenta web
    tipo_donante ENUM('Familia / Alumno', 'Empresa / Aliado', 'Anónimo') NOT NULL,
    nombre_razon_social VARCHAR(180) NOT NULL,           -- Ej: 'Familia Huamán Quispe'
    dni_ruc VARCHAR(20) NULL,                            -- DNI o RUC (NULL si es Anónimo)
    grado_seccion VARCHAR(100) NULL,                     -- Ej: '3ro de Secundaria - Sección "A"'
    telefono_whatsapp VARCHAR(25) NULL,
    fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_donantes_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 3. CATEGORÍAS DE VÍVERES Y METAS (Paso 2 y Portal de Transparencia)
-- ----------------------------------------------------------------------------
CREATE TABLE categorias_viveres (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre_categoria VARCHAR(100) NOT NULL UNIQUE,       -- Ej: 'Lácteos y Harinas', 'Arroz, Avena y Menestras'
    meta_kg DECIMAL(10, 2) NOT NULL DEFAULT 500.00,      -- Meta de campaña en Kg
    activo TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 4. DONACIONES / LOTES RECEPCIONADOS (Registrados solo por Agente Pastoral)
-- ----------------------------------------------------------------------------
CREATE TABLE donaciones (
    id_donacion INT AUTO_INCREMENT PRIMARY KEY,
    codigo_lote VARCHAR(30) NOT NULL UNIQUE,             -- Ej: '#PX-LOT-2025-045'
    id_donante INT NOT NULL,
    id_agente_pastoral INT NOT NULL,                     -- Agente Pastoral que registra la recepción
    destino_solidario VARCHAR(180) NOT NULL,             -- Ej: 'Comedor Popular "Santa Rosa"'
    observaciones_empaque TEXT NULL,
    estado_lote ENUM('Nuevo', 'En Almacén', 'Entregado') NOT NULL DEFAULT 'Nuevo',
    categoria_principal VARCHAR(100) NULL,               -- Categoria predominante del lote
    familias_beneficiadas INT NOT NULL DEFAULT 0,         -- Familias alcanzadas por la entrega
    fecha_ingreso DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_donaciones_donante
        FOREIGN KEY (id_donante) REFERENCES donantes(id_donante)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_donaciones_agente
        FOREIGN KEY (id_agente_pastoral) REFERENCES usuarios(id_usuario)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 5. DETALLE DE VÍVERES POR LOTE (Paso 2)
-- ----------------------------------------------------------------------------
CREATE TABLE detalle_donaciones (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_donacion INT NOT NULL,
    id_categoria INT NOT NULL,
    descripcion_producto VARCHAR(200) NOT NULL,
    cantidad INT NOT NULL,
    unidad_medida ENUM('Unid.', 'Kg', 'Paq.', 'L', 'Cajas') NOT NULL DEFAULT 'Unid.',
    peso_estimado_kg DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    fecha_vencimiento DATE NOT NULL,
    CONSTRAINT fk_detalle_donacion
        FOREIGN KEY (id_donacion) REFERENCES donaciones(id_donacion)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_detalle_categoria
        FOREIGN KEY (id_categoria) REFERENCES categorias_viveres(id_categoria)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- 6. ENTREGAS Y ACTAS OFICIALES (Lo que visualizan los Donantes en Transparencia)
-- ----------------------------------------------------------------------------
CREATE TABLE entregas_transparencia (
    id_entrega INT AUTO_INCREMENT PRIMARY KEY,
    id_donacion INT NOT NULL,
    id_agente_registra INT NOT NULL,                     -- Agente pastoral que publica el acta
    codigo_publico_lote VARCHAR(30) NOT NULL,            -- Ej: 'L001 / 2025'
    titulo_entrega VARCHAR(180) NOT NULL,                -- Ej: 'Entrega en Sede Central de Caritas Huancayo'
    descripcion_entrega TEXT NOT NULL,
    coordinador_recepcion VARCHAR(150) NOT NULL,         -- Ej: 'Hna. Teresa Gomez (Coordinadora Social)'
    codigo_acta VARCHAR(40) NOT NULL UNIQUE,             -- Ej: '#D3IMI3 - 30'
    estado_entrega ENUM('Entregado', 'Pendiente') NOT NULL DEFAULT 'Pendiente',
    fecha_entrega DATE NOT NULL,
    CONSTRAINT fk_entregas_donacion
        FOREIGN KEY (id_donacion) REFERENCES donaciones(id_donacion)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_entregas_agente
        FOREIGN KEY (id_agente_registra) REFERENCES usuarios(id_usuario)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- VISTAS PARA EL BACKEND (Tarjetas de Resumen y Portal de Transparencia)
-- ============================================================================

CREATE VIEW vw_resumen_donaciones AS
SELECT 
    d.id_donacion,
    d.codigo_lote,
    d.fecha_ingreso,
    COUNT(det.id_detalle) AS total_tipos_articulos,
    COALESCE(SUM(det.cantidad), 0) AS total_unidades_paquetes,
    COALESCE(SUM(det.peso_estimado_kg), 0.00) AS peso_neto_estimado_kg,
    COALESCE(SUM(
        CASE 
            WHEN DATEDIFF(det.fecha_vencimiento, DATE(d.fecha_ingreso)) < 30 THEN 1 
            ELSE 0 
        END
    ), 0) AS items_alerta_sanitaria
FROM donaciones d
LEFT JOIN detalle_donaciones det ON d.id_donacion = det.id_donacion
GROUP BY d.id_donacion, d.codigo_lote, d.fecha_ingreso;

CREATE VIEW vw_metas_transparencia AS
SELECT 
    c.id_categoria,
    c.nombre_categoria,
    c.meta_kg,
    COALESCE(SUM(det.peso_estimado_kg), 0.00) AS recolectado_kg,
    ROUND((COALESCE(SUM(det.peso_estimado_kg), 0.00) / c.meta_kg) * 100, 1) AS porcentaje_avance
FROM categorias_viveres c
LEFT JOIN detalle_donaciones det ON c.id_categoria = det.id_categoria
GROUP BY c.id_categoria, c.nombre_categoria, c.meta_kg;

-- ============================================================================
-- DATOS INICIALES DE PRUEBA
-- ============================================================================

-- 1. Primero se crea el Agente Pastoral (Administrativo)
-- Credenciales demo: pastoral@sanpiox.edu.pe / admin123 (hash Argon2)
INSERT INTO usuarios (codigo_usuario, nombre_completo, correo_electronico, password_hash, telefono, tipo_usuario, creado_por_id) VALUES
('A001', 'Prof. Taipe', 'pastoral@sanpiox.edu.pe', '$argon2id$v=19$m=65536,t=3,p=4$0um0FDgmgv5fKU1Gq+zBdQ$YhSoSws0g9/YqYbJmF7yFE5OBCFbIAUSR9NQwk1nm3c', '+51 999 999 999', 'Administrativo', NULL);

-- 2. El Agente Pastoral (id = 1) crea la cuenta para la Familia/Donante
-- Credenciales demo: donante@sanpiox.edu.pe / donante123 (hash Argon2)
INSERT INTO usuarios (codigo_usuario, nombre_completo, correo_electronico, password_hash, telefono, tipo_usuario, creado_por_id) VALUES
('U001', 'Familia Quispe', 'donante@sanpiox.edu.pe', '$argon2id$v=19$m=65536,t=3,p=4$pUpRDZT7SP0YflKroQUZzQ$QLekSVFrbD5hhI6IY2Ixzz48F8UOjhEhMOKYyt83ucU', '+51 999 999 999', 'Donante', 1);

-- 3. Categorías de Víveres
INSERT INTO categorias_viveres (nombre_categoria, meta_kg) VALUES
('Arroz, Avena y Menestras', 500.00),
('Conservas de Pescado & Aceites', 500.00),
('Leche evaporada y Suplementos de bebé', 500.00),
('Fideos y Sémolas Diversas', 500.00),
('Galletas y Cereales', 500.00),
('Menestras y Granos', 500.00),
('Lácteos y Harinas', 500.00),
('Otros', 500.00);

-- 4. Registro del Donante en el Paso 1
INSERT INTO donantes (id_usuario, tipo_donante, nombre_razon_social, dni_ruc, grado_seccion, telefono_whatsapp) VALUES
(2, 'Familia / Alumno', 'Familia Huamán Quispe', '45892104', '3ro de Secundaria - Sección "A"', '+51 964 123 456');

-- 5. Recepción de Donación registrada por Prof. Taipe (id_agente_pastoral = 1)
INSERT INTO donaciones (codigo_lote, id_donante, id_agente_pastoral, destino_solidario, observaciones_empaque, estado_lote, categoria_principal, familias_beneficiadas, fecha_ingreso) VALUES
('#PX-LOT-2025-045', 1, 1, 'Comedor Popular "Santa Rosa"', 'Empaques sellados y en excelente estado de conservación higiénica.', 'Nuevo', 'Lácteos y Harinas', 12, '2025-02-22 10:45:00');

-- 6. Artículos del Lote
INSERT INTO detalle_donaciones (id_donacion, id_categoria, descripcion_producto, cantidad, unidad_medida, peso_estimado_kg, fecha_vencimiento) VALUES
(1, 3, 'Leche Evaporada Entera (Lata 400g)', 24, 'Unid.', 9.60, '2025-10-15'),
(1, 6, 'Lenteja Serrana Seleccionada (Bolsa 1Kg)', 15, 'Kg', 15.00, '2026-03-20'),
(1, 5, 'Galletas Fortificadas de Quinua (Paq.)', 10, 'Paq.', 1.00, '2025-03-25');

-- 7. Entrega publicada en el Portal de Transparencia
INSERT INTO entregas_transparencia (id_donacion, id_agente_registra, codigo_publico_lote, titulo_entrega, descripcion_entrega, coordinador_recepcion, codigo_acta, estado_entrega, fecha_entrega) VALUES
(1, 1, 'L001 / 2025', 'Entrega en Sede Central de Caritas Huancayo', 'Se distribuyeron paquetes de víveres de primera necesidad a familias empadronadas.', 'Hna. Teresa Gomez (Coordinadora Social)', '#D3IMI3 - 30', 'Entregado', '2025-02-18');

