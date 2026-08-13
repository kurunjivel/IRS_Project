-- ============================================================
-- Migration 001: Add users table for authentication
-- Run against irs_db
-- ============================================================

USE irs_db;

-- Create users table if it doesn't already exist
CREATE TABLE IF NOT EXISTS users (
    user_id       INT           NOT NULL AUTO_INCREMENT,
    username      VARCHAR(100)  NOT NULL,
    password_hash VARCHAR(255)  NOT NULL,
    role          ENUM('EMPLOYEE', 'HR') NOT NULL,
    employee_id   INT           NULL,          -- FK to employees, NULL for HR users
    is_active     TINYINT(1)    NOT NULL DEFAULT 1,
    created_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (user_id),
    UNIQUE  KEY uq_users_username (username),
    UNIQUE  KEY uq_users_employee (employee_id),     -- one account per employee
    KEY     idx_users_role (role),

    CONSTRAINT fk_users_employee
        FOREIGN KEY (employee_id)
        REFERENCES employees (employee_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
