-- Tabla: Categorías
CREATE TABLE Categorias (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    parentCategory VARCHAR(255),
    imageUrl TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (parentCategory) REFERENCES Categorias(id)
);

-- Tabla: Productos
CREATE TABLE Productos (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    category VARCHAR(255),
    animalType VARCHAR(255),
    brand VARCHAR(255),
    stock INT NOT NULL,
    images TEXT,
    averageRating DECIMAL(3, 2),
    createdAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category) REFERENCES Categorias(id)
);

-- Tabla: Usuarios
CREATE TABLE Usuarios (
    id VARCHAR(255) PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    firstName VARCHAR(255),
    lastName VARCHAR(255),
    phoneNumber VARCHAR(50),
    role VARCHAR(50) NOT NULL,
    createdAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    lastLogin TIMESTAMP
);


-- Tabla: Direcciones de Usuario
CREATE TABLE Direcciones (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    street VARCHAR(255) NOT NULL,
    city VARCHAR(255) NOT NULL,
    state VARCHAR(255),
    country VARCHAR(255) NOT NULL,
    user_email VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES Usuarios(id)
);

-- Tabla: Carrito de Compras
CREATE TABLE Carrito (
    id Integer PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    items TEXT NOT NULL,
    totalAmount DECIMAL(10, 2) NOT NULL,
    createdAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ,
    FOREIGN KEY (user_id) REFERENCES Usuarios(id)
);

-- Tabla: Pedidos
CREATE TABLE Pedidos (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    items TEXT NOT NULL,
    totalAmount DECIMAL(10, 2) NOT NULL,
    shipping_address VARCHAR(255) NOT NULL,
    paymentMethod VARCHAR(50) NOT NULL,
    paymentStatus VARCHAR(50) NOT NULL,
    orderStatus VARCHAR(50) NOT NULL,
    createdAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Usuarios(id)
);

-- Tabla: Reseñas y Valoraciones
CREATE TABLE Resenas (
    id VARCHAR(255) PRIMARY KEY,
    productId VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    title VARCHAR(255),
    comment TEXT,
    helpful INT DEFAULT 0,
    createdAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (productId) REFERENCES Productos(id),
    FOREIGN KEY (user_id) REFERENCES Usuarios(id)
);
