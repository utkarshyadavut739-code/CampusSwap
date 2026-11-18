-- Run once:  mysql -u root -p < database/schema.sql

CREATE DATABASE IF NOT EXISTS tack
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE tack;

CREATE TABLE IF NOT EXISTS users (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  name          VARCHAR(80)  NOT NULL,
  email         VARCHAR(120) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  phone         CHAR(10)     NOT NULL,
  hostel        VARCHAR(40)  NOT NULL,
  created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS listings (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  seller_id      INT          NOT NULL,
  title          VARCHAR(100) NOT NULL,
  category       VARCHAR(40)  NOT NULL,
  price          INT          NOT NULL DEFAULT 0,
  item_condition ENUM('new','used','parts') NOT NULL,
  description    TEXT,
  hostel         VARCHAR(40)  NOT NULL,
  phone          CHAR(10)     NOT NULL,
  image_path     VARCHAR(80)  NULL,
  status         ENUM('active','sold') NOT NULL DEFAULT 'active',
  created_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_listing_seller FOREIGN KEY (seller_id)
    REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_status_created (status, created_at),
  INDEX idx_category (category),
  INDEX idx_seller (seller_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS messages (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  listing_id INT           NOT NULL,
  sender_id  INT           NOT NULL,
  body       VARCHAR(500)  NOT NULL,
  created_at TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_msg_listing FOREIGN KEY (listing_id)
    REFERENCES listings(id) ON DELETE CASCADE,
  CONSTRAINT fk_msg_sender FOREIGN KEY (sender_id)
    REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_msg_listing (listing_id)
) ENGINE=InnoDB;
