
CREATE DATABASE IF NOT EXISTS ecoconsumo;

USE ecoconsumo;

CREATE TABLE IF NOT EXISTS productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT NOT NULL,
    fecha_elaboracion DATE NOT NULL,
    fecha_vencimiento DATETIME NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL,
    imagen VARCHAR(255)
);

SELECT * FROM productos;
