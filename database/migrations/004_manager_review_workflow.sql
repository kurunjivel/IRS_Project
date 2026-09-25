-- Migration 004: Manager Role & Review Calibration Workflow
-- Adds manager_id column to employees, and creates manager_reviews & manager_review_audit tables.

ALTER TABLE employees ADD COLUMN manager_id INT NULL;

CREATE TABLE IF NOT EXISTS manager_reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    manager_id INT NOT NULL,
    quarter VARCHAR(20) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'PENDING',
    technical_competency INT NOT NULL DEFAULT 3,
    communication INT NOT NULL DEFAULT 3,
    leadership INT NOT NULL DEFAULT 3,
    teamwork INT NOT NULL DEFAULT 3,
    ownership INT NOT NULL DEFAULT 3,
    overall_assessment TEXT,
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS manager_review_audit (
    audit_id INT AUTO_INCREMENT PRIMARY KEY,
    review_id INT NOT NULL,
    employee_id INT NOT NULL,
    manager_id INT NOT NULL,
    previous_status VARCHAR(30),
    new_status VARCHAR(30) NOT NULL,
    comments TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
