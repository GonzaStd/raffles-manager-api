CREATE DATABASE IF NOT EXISTS raffles_draw;
USE raffles_draw;
CREATE TABLE IF NOT EXISTS projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(60) NOT NULL UNIQUE,
    description TEXT,
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);
CREATE TABLE IF NOT EXISTS raffle_sets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    name VARCHAR(60) NOT NULL,
    type VARCHAR(8) NOT NULL CHECK (type IN ('online', 'physical')),
    init INT NOT NULL,
    final INT NOT NULL,
    unit_price INT NOT NULL,
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_numbers CHECK (init < final),
    CONSTRAINT unique_set UNIQUE (project_id, name),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
CREATE TABLE IF NOT EXISTS buyers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(60) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    register_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_name_phone UNIQUE (name, phone)
);
CREATE TABLE IF NOT EXISTS raffles (
    set_id INT AUTO_INCREMENT PRIMARY KEY,
    number INT NOT NULL,
    buyer_id INT,
    sell_date TIMESTAMP,
    payment_method VARCHAR(8) CHECK (payment_method in ('CASH', 'CARD', 'TRANSFER', 'OTHER')),
    state VARCHAR(9) DEFAULT 'available' CHECK (state IN ('available', 'sold', 'reserved')),
    FOREIGN KEY (buyer_id) REFERENCES buyers(id),
    FOREIGN KEY (set_id) REFERENCES raffle_sets(id)
);