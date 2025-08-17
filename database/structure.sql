CREATE DATABASE IF NOT EXISTS raffles_draw;
USE raffles_draw;

-- ESTRUCTURA DE BASE DE DATOS CON AISLAMIENTO POR USUARIO
-- =====================================================

-- 1. TABLA DE USUARIOS (Base del sistema de aislamiento)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username)
);

-- 2. TABLA DE PROYECTOS (Primer nivel de propiedad)
CREATE TABLE IF NOT EXISTS projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    user_id INT NOT NULL,  -- CLAVE: Cada proyecto pertenece a UN usuario específico
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_user_name (user_id, name)
);

-- 3. TABLA DE COMPRADORES (Independiente pero vinculado al usuario)
CREATE TABLE IF NOT EXISTS buyers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100),  -- Los buyers SÍ pueden tener email para contacto
    user_id INT NOT NULL,  -- Cada comprador pertenece a UN usuario
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
);

-- 4. TABLA DE SETS DE RIFAS (Hereda user_id del proyecto)
CREATE TABLE IF NOT EXISTS raffle_sets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(60) NOT NULL,
    project_id INT NOT NULL,
    user_id INT NOT NULL,  -- Add user_id for direct user access control
    type VARCHAR(8) NOT NULL CHECK (type IN ('online', 'physical')),
    init INT NOT NULL,
    final INT NOT NULL,
    unit_price INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT valid_numbers CHECK (init <= final),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_project_id (project_id),
    INDEX idx_user_id (user_id)
);

-- 5. TABLA DE RIFAS INDIVIDUALES (Hereda user_id del set)
CREATE TABLE IF NOT EXISTS raffles (
    number INT PRIMARY KEY,
    set_id INT NOT NULL,
    buyer_id INT,
    user_id INT NOT NULL,  -- Se asigna automáticamente via TRIGGER
    payment_method VARCHAR(8) CHECK (payment_method in ('cash', 'card', 'transfer')),
    state VARCHAR(9) DEFAULT 'available' CHECK (state IN ('available', 'sold', 'reserved')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (buyer_id) REFERENCES buyers(id) ON DELETE SET NULL,
    FOREIGN KEY (set_id) REFERENCES raffle_sets(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_set_id (set_id),
    INDEX idx_user_id (user_id)
);

-- =====================================================
-- TRIGGERS PARA AUTO-ASIGNACIÓN DE user_id
-- =====================================================

DELIMITER $$

-- TRIGGER: Auto-asignar user_id en raffle_sets basado en el proyecto
CREATE TRIGGER IF NOT EXISTS tr_raffle_sets_user_id
    BEFORE INSERT ON raffle_sets
    FOR EACH ROW
BEGIN
    -- Si no se especifica user_id, tomarlo del proyecto padre
    IF NEW.user_id IS NULL THEN
        SELECT user_id INTO NEW.user_id
        FROM projects
        WHERE id = NEW.project_id;
    END IF;
END$$

-- TRIGGER: Auto-asignar user_id en raffles basado en el set
CREATE TRIGGER IF NOT EXISTS tr_raffles_user_id
    BEFORE INSERT ON raffles
    FOR EACH ROW
BEGIN
    -- Si no se especifica user_id, tomarlo del set padre
    IF NEW.user_id IS NULL THEN
        SELECT user_id INTO NEW.user_id
        FROM raffle_sets
        WHERE id = NEW.set_id;
    END IF;
END$$

DELIMITER ;

-- =====================================================
-- POLÍTICAS DE SEGURIDAD Y ACCESO
-- =====================================================

-- Índices compuestos para consultas eficientes por usuario
CREATE INDEX IF NOT EXISTS idx_projects_user_created ON projects(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_raffle_sets_user_created ON raffle_sets(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_raffles_user_status ON raffles(user_id, state);
CREATE INDEX IF NOT EXISTS idx_buyers_user_created ON buyers(user_id, created_at DESC);
