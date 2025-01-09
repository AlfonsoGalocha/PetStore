INSERT INTO Categorias (id, name, description, parentCategory, imageUrl, active)
VALUES 
('cat1', 'Alimento para Perros', 'Categoría para productos alimenticios para perros', NULL, 'https://example.com/dog-food.jpg', TRUE),
('cat2', 'Juguetes para Gatos', 'Juguetes divertidos para gatos', NULL, 'https://example.com/cat-toys.jpg', TRUE),
('cat3', 'Camas para Mascotas', 'Camas confortables para diferentes tipos de mascotas', NULL, 'https://example.com/pet-beds.jpg', TRUE);


-- Insertar registros en Productos
INSERT INTO Productos (id, name, description, price, category, animalType, brand, stock, images, averageRating)
VALUES 
('prod1', 'Croquetas Premium', 'Alimento balanceado para perros', 25.99, 'cat1', 'Perro', 'MarcaA', 100, 'https://example.com/croquetas.jpg', 4.5),
('prod2', 'Pelota de Goma', 'Pelota resistente para perros', 5.99, 'cat2', 'Perro', 'MarcaB', 50, 'https://example.com/pelota.jpg', 4.2),
('prod3', 'Arnés Ajustable', 'Arnés cómodo para gatos', 15.99, 'cat3', 'Gato', 'MarcaC', 20, 'https://example.com/arnes.jpg', 4.8);

-- Insertar registros en Usuarios
INSERT INTO Usuarios (id, username, email, password, firstName, lastName, phoneNumber, role, createdAt)
VALUES 
('user1', 'johndoe', 'johndoe@example.com', 'hashed_password1', 'John', 'Doe', '+1234567890', 'usuario', CURRENT_TIMESTAMP),
('user2', 'adminuser', 'admin@example.com', 'hashed_password2', 'Admin', 'User', '+0987654321', 'admin', CURRENT_TIMESTAMP),
('user3', 'janedoe', 'janedoe@example.com', 'hashed_password3', 'Jane', 'Doe', '+1122334455', 'usuario', CURRENT_TIMESTAMP);

-- Insertar registros en Direcciones
INSERT INTO Direcciones (id, user_id, street, city, state, country)
VALUES 
('addr1', 'user1', '123 Calle Principal', 'Madrid', 'Madrid', 'España'),
('addr2', 'user2', '456 Avenida Secundaria', 'Barcelona', 'Cataluña', 'España'),
('addr3', 'user3', '789 Camino Real', 'Sevilla', 'Andalucía', 'España');


-- Insertar registros en Carrito
INSERT INTO Carrito (id, user_id, items, totalAmount, createdAt, updatedAt)
VALUES 
(1, 'user1', '[{"product_id": "prod1", "quantity": 2}]', 99.98, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(2, 'user2', '[{"product_id": "prod2", "quantity": 3}]', 29.97, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(3, 'user3', '[{"product_id": "prod3", "quantity": 1}]', 89.99, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);


-- Insertar registros en Pedidos
INSERT INTO Pedidos (id, user_id, items, totalAmount, shipping_address, paymentMethod, paymentStatus, orderStatus, createdAt, updatedAt)
VALUES 
('order1', 'user1', '[{"product_id": "prod1", "quantity": 2}]', 99.98, '123 Calle Principal', 'Tarjeta', 'Completado', 'Entregado', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('order2', 'user2', '[{"product_id": "prod2", "quantity": 3}]', 29.97, '456 Avenida Secundaria', 'PayPal', 'Pendiente', 'Procesando', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('order3', 'user3', '[{"product_id": "prod3", "quantity": 1}]', 89.99, '789 Camino Real', 'Transferencia', 'Completado', 'Entregado', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Insertar registros en Reseñas y Valoraciones
INSERT INTO Resenas (id, productId, user_id, rating, title, comment, helpful)
VALUES 
('review1', 'prod1', 'user1', 5, 'Excelente comida para perros', 'A mi perro le encanta este alimento', 10),
('review2', 'prod2', 'user2', 4, 'Ratón divertido', 'A mi gato le gusta mucho jugar con este ratón', 5),
('review3', 'prod3', 'user3', 5, 'Cama increíble', 'Cama muy cómoda para mi perro', 8);