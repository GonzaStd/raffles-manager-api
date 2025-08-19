-- DATABASE STRUCTURE FOR MYSQL/MARIADB
-- =====================================
-- Entity-Manager isolation system with predictable numbering
-- Compatible with Railway, MariaDB and MySQL 8.0+

-- Initial configuration for MySQL
--SET FOREIGN_KEY_CHECKS = 0;
--SET SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO';
-- Removed AUTOCOMMIT and transaction statements for PyMySQL compatibility
-- CREATE DATABASE IF NOT EXISTS raffles_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
--use raffles_db;

-- =========================================================
-- DROP EXISTING TABLES (IN CORRECT ORDER)
-- =========================================================

--DROP TABLE IF EXISTS raffles;
--DROP TABLE IF EXISTS raffle_sets;
--DROP TABLE IF EXISTS projects;
--DROP TABLE IF EXISTS buyers;
--DROP TABLE IF EXISTS managers;
--DROP TABLE IF EXISTS entities;

-- =========================================================
-- CREATE TABLES WITH COMPOSITE PRIMARY KEYS
-- =========================================================

-- 1. ENTITIES TABLE (Base of the isolation system)
CREATE TABLE entities (
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    description VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_entity_name (name),
    KEY idx_entity_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. MANAGERS TABLE (Composite PK: entity_id + manager_number)
CREATE TABLE managers (
    entity_id INT NOT NULL,
    manager_number INT NOT NULL,
    username VARCHAR(50) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (entity_id, manager_number),
    UNIQUE KEY uk_manager_entity_username (entity_id, username),
    KEY idx_manager_username (username),
    KEY idx_manager_entity (entity_id),
    CONSTRAINT fk_manager_entity FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. BUYERS TABLE (Composite PK: entity_id + buyer_number)
CREATE TABLE buyers (
    entity_id INT NOT NULL,
    buyer_number INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    created_by_manager_number INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,


    KEY idx_buyer_entity (entity_id),
    KEY idx_buyer_name_phone (name, phone),
    KEY idx_buyer_manager (entity_id, created_by_manager_number),
    CONSTRAINT fk_buyer_entity FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE,
    CONSTRAINT fk_buyer_created_by_manager FOREIGN KEY (entity_id, created_by_manager_number)
     REFERENCES managers(entity_id, manager_number) ON DELETE RESTRICT,
    PRIMARY KEY (entity_id, buyer_number),
    UNIQUE KEY uk_buyer_name_phone_entity (entity_id, name, phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. PROJECTS TABLE (Composite PK: entity_id + project_number)
CREATE TABLE projects (
    entity_id INT NOT NULL,
    project_number INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (entity_id, project_number),
    KEY idx_project_entity (entity_id),
    KEY idx_project_name (name),
    CONSTRAINT fk_project_entity FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. RAFFLE SETS TABLE (Composite PK: entity_id + project_number + set_number)
CREATE TABLE raffle_sets (
    entity_id INT NOT NULL,
    project_number INT NOT NULL,
    set_number INT NOT NULL,
    name VARCHAR(60) NOT NULL,
    type ENUM('online', 'physical') NOT NULL,
    init INT NOT NULL,
    final INT NOT NULL,
    unit_price INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (entity_id, project_number, set_number),
    KEY idx_raffleset_entity_project (entity_id, project_number),
    KEY idx_raffleset_name (name),
    CONSTRAINT fk_raffleset_project FOREIGN KEY (entity_id, project_number) REFERENCES projects(entity_id, project_number) ON DELETE CASCADE,
    CONSTRAINT chk_raffleset_valid_numbers CHECK (init <= final),
    CONSTRAINT chk_raffleset_type CHECK (type IN ('online', 'physical'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. RAFFLES TABLE (Composite PK: entity_id + project_number + raffle_number)
CREATE TABLE raffles (
    entity_id INT NOT NULL,
    project_number INT NOT NULL,
    raffle_number INT NOT NULL,
    set_number INT NOT NULL,
    buyer_entity_id INT,
    buyer_number INT,
    sold_by_entity_id INT,
    sold_by_manager_number INT,
    payment_method ENUM('cash', 'card', 'transfer'),
    state ENUM('available', 'sold', 'reserved') DEFAULT 'available',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (entity_id, project_number, raffle_number),
    KEY idx_raffle_entity_project (entity_id, project_number),
    KEY idx_raffle_state (state),
    KEY idx_raffle_buyer (buyer_entity_id, buyer_number),
    KEY idx_raffle_manager (sold_by_entity_id, sold_by_manager_number),
    CONSTRAINT fk_raffle_set FOREIGN KEY (entity_id, project_number, set_number) REFERENCES raffle_sets(entity_id, project_number, set_number) ON DELETE CASCADE,
    CONSTRAINT fk_raffle_buyer FOREIGN KEY (buyer_entity_id, buyer_number) REFERENCES buyers(entity_id, buyer_number) ,
    CONSTRAINT fk_raffle_manager FOREIGN KEY (sold_by_entity_id, sold_by_manager_number) REFERENCES managers(entity_id, manager_number) ,
    CONSTRAINT chk_raffle_payment_method CHECK (payment_method IN ('cash', 'card', 'transfer')),
    CONSTRAINT chk_raffle_state CHECK (state IN ('available', 'sold', 'reserved'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================================
-- AUTO-INCREMENT TRIGGERS FOR COMPOSITE PRIMARY KEYS
-- =========================================================

DELIMITER $$

-- Trigger for managers auto-increment
CREATE TRIGGER tr_managers_auto_increment
    BEFORE INSERT ON managers
    FOR EACH ROW
BEGIN
    IF NEW.manager_number IS NULL OR NEW.manager_number = 0 THEN
        SET NEW.manager_number = (
            SELECT COALESCE(MAX(manager_number), 0) + 1
            FROM managers
            WHERE entity_id = NEW.entity_id
        );
    END IF;
END$$

-- Trigger for buyers auto-increment
CREATE TRIGGER tr_buyers_auto_increment
    BEFORE INSERT ON buyers
    FOR EACH ROW
BEGIN
    IF NEW.buyer_number IS NULL OR NEW.buyer_number = 0 THEN
        SET NEW.buyer_number = (
            SELECT COALESCE(MAX(buyer_number), 0) + 1
            FROM buyers
            WHERE entity_id = NEW.entity_id
        );
    END IF;
END$$

-- Trigger for projects auto-increment
CREATE TRIGGER tr_projects_auto_increment
    BEFORE INSERT ON projects
    FOR EACH ROW
BEGIN
    IF NEW.project_number IS NULL OR NEW.project_number = 0 THEN
        SET NEW.project_number = (
            SELECT COALESCE(MAX(project_number), 0) + 1
            FROM projects
            WHERE entity_id = NEW.entity_id
        );
    END IF;
END$$

-- Trigger for raffle_sets auto-increment
CREATE TRIGGER tr_raffle_sets_auto_increment
    BEFORE INSERT ON raffle_sets
    FOR EACH ROW
BEGIN
    IF NEW.set_number IS NULL OR NEW.set_number = 0 THEN
        SET NEW.set_number = (
            SELECT COALESCE(MAX(set_number), 0) + 1
            FROM raffle_sets
            WHERE entity_id = NEW.entity_id AND project_number = NEW.project_number
        );
    END IF;
END$$

-- Trigger for raffles auto-increment
CREATE TRIGGER tr_raffles_auto_increment
    BEFORE INSERT ON raffles
    FOR EACH ROW
BEGIN
    IF NEW.raffle_number IS NULL OR NEW.raffle_number = 0 THEN
        SET NEW.raffle_number = (
            SELECT COALESCE(MAX(raffle_number), 0) + 1
            FROM raffles
            WHERE entity_id = NEW.entity_id AND project_number = NEW.project_number
        );
    END IF;
END$$

DELIMITER ;

-- =========================================================
-- FINALIZATION
-- =========================================================

SET FOREIGN_KEY_CHECKS = 1;
-- Removed COMMIT for PyMySQL compatibility
