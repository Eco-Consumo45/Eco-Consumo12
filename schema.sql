-- Base de datos de Eco Consumo
-- Ejecutar una sola vez en MySQL Workbench (o: mysql -u root -p < schema.sql)

CREATE DATABASE IF NOT EXISTS eco_consumo
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE eco_consumo;

CREATE TABLE IF NOT EXISTS usuarios (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    nombre           VARCHAR(60)  NOT NULL,
    apellido         VARCHAR(60)  NOT NULL,
    fecha_nacimiento DATE         NOT NULL,
    mail             VARCHAR(120) NOT NULL,
    usuario          VARCHAR(40)  NOT NULL,
    clave_hash       VARCHAR(255) NOT NULL,   -- NUNCA se guarda la contraseña en texto plano
    direccion        VARCHAR(200) NOT NULL,
    creado_en        TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_usuarios_mail    UNIQUE (mail),
    CONSTRAINT uq_usuarios_usuario UNIQUE (usuario)
);
