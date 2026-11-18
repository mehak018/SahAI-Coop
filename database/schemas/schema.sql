-- =============================================================================
-- SahAI-Coop Database Schema (SIH26088)
-- Multilingual Cooperative Governance & Legal Assistance Chatbot
-- Target RDBMS: MySQL 8.0+
-- Character Set: utf8mb4 (Full Unicode / Multilingual support for Hindi & Marathi)
-- =============================================================================

CREATE DATABASE IF NOT EXISTS `sahai_coop_db` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE `sahai_coop_db`;

-- -----------------------------------------------------------------------------
-- 1. Users Table
-- Stores citizen / farmer / cooperative member registration details & preferences
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL,
    `email` VARCHAR(255) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `preferred_language` VARCHAR(10) NOT NULL DEFAULT 'en',
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_users_email` (`email`),
    INDEX `idx_users_language` (`preferred_language`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 2. Chat Sessions Table
-- Groups messages into conversational sessions for each user
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `chat_sessions` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `title` VARCHAR(255) NOT NULL DEFAULT 'New Conversation',
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_chat_sessions_user` 
        FOREIGN KEY (`user_id`) 
        REFERENCES `users` (`id`) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    INDEX `idx_chat_sessions_user_id` (`user_id`),
    INDEX `idx_chat_sessions_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 3. Messages Table
-- Stores conversation history (user questions & bot responses with citations)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `messages` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `session_id` INT NOT NULL,
    `sender` VARCHAR(20) NOT NULL, -- 'user' or 'bot'
    `content` TEXT NOT NULL,
    `language` VARCHAR(10) NOT NULL DEFAULT 'en',
    `topic_category` VARCHAR(100) NULL, -- e.g., 'Crop Insurance', 'PACS Services', 'Grievance'
    `source_reference` TEXT NULL, -- Citations and links to official schemes/acts
    `timestamp` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_messages_session` 
        FOREIGN KEY (`session_id`) 
        REFERENCES `chat_sessions` (`id`) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    INDEX `idx_messages_session_id` (`session_id`),
    INDEX `idx_messages_sender` (`sender`),
    INDEX `idx_messages_topic` (`topic_category`),
    INDEX `idx_messages_timestamp` (`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 4. Knowledge / Sample Answers Table (`sample_responses`)
-- Predefined verified responses for cooperative laws, PMFBY, PACS, and schemes.
-- Prepares the structural foundation for the AI RAG engine.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `sample_responses` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `topic_keyword` VARCHAR(100) NOT NULL,
    `question_pattern` TEXT NOT NULL,
    `answer_text` TEXT NOT NULL,
    `language` VARCHAR(10) NOT NULL DEFAULT 'en', -- 'en', 'hi', 'mr'
    `source_title` VARCHAR(255) NOT NULL,
    `source_url` VARCHAR(500) NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_sample_topic` (`topic_keyword`),
    INDEX `idx_sample_language` (`language`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
