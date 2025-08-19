SET FOREIGN_KEY_CHECKS = 0;
SET SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO';
-- Removed AUTOCOMMIT and transaction statements for PyMySQL compatibility
CREATE DATABASE IF NOT EXISTS raffles_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
use raffles_db;

DROP TABLE IF EXISTS raffles;
DROP TABLE IF EXISTS raffle_sets;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS buyers;
DROP TABLE IF EXISTS managers;
DROP TABLE IF EXISTS entities;