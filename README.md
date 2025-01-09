# Proyecto de Tienda de Mascotas

Este proyecto implementa una arquitectura web por capas para una tienda de comida y material para mascotas, utilizando tecnologías como Python, Docker, Kubernetes (Minikube), Kong y Helm. A continuación, se describen los pasos necesarios para instalar las dependencias, desplegar los servicios y configurar la infraestructura.

## Instalación de Servicios Necesarios

### Python
1. Descarga e instala Python desde su página oficial: [https://www.python.org/downloads/](https://www.python.org/downloads/).
2. Verifica la instalación:
   ```bash
   python --version
   ```

### Docker
1. Descarga e instala Docker desde su página oficial: [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/).
2. Verifica la instalación:
   ```bash
   docker --version
   ```

### Kubernetes (Minikube)
1. Descarga e instala Minikube siguiendo las instrucciones: [https://minikube.sigs.k8s.io/docs/start/](https://minikube.sigs.k8s.io/docs/start/).
2. Verifica la instalación:
   ```bash
   minikube version
   ```

### Kong
1. Sigue las instrucciones para instalar Kong desde: [https://docs.konghq.com/](https://docs.konghq.com/).
2. Asegúrate de que está configurado correctamente.

# Instalación de PostgreSQL

Esta guía explica cómo instalar PostgreSQL y configurarlo en tu sistema.

## 1. Instalación en sistemas operativos comunes

### En Ubuntu/Debian
1. Actualiza los paquetes:
   ```bash
   sudo apt update
   sudo apt upgrade
   ```

2. Instala Postgres:
    ```bash
    sudo apt install postgresql postgresql-contrib
    ```
3. Verifica que esta instalado:
    ```bash
    psql --version
    ```
4. Inicia el servicio PostgreSQL:
    ```bash
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    ```


### Helm
1. Instala Helm siguiendo las instrucciones en: [https://helm.sh/docs/intro/install/](https://helm.sh/docs/intro/install/).
2. Instalalo si no de esta manera:
   ```bash
      helm repo add kong https://charts.konghq.com/ && helm repo update
   ```
3. Verifica la instalación:
   ```bash
   helm version
   ```

## Inicialización del Entorno y Creación de Servicios

### Iniciar Minikube
1. Inicia Minikube:
   ```bash
   minikube start --driver=docker
   ```
2. Configura Minikube para usar Docker como entorno:
   ```bash
   eval $(minikube docker-env)
   ```


## Configuración de la Base de Datos

1. Ejecuta el archivo deployment.yaml dentro de postgres para obtener el pod.

2. Accede al pod de PostgreSQL que has creado:
   ```bash
   kubectl exec -it <nombre_del_pod_postgres> -- bash
   ```
3. Conéctate a la base de datos:
   ```bash
   psql -U <usuario> -d <nombre de la database>
   ```
4. Ejecuta los scripts para crear y poblar las tablas:
   ```sql
   \i create_tables.sql
   \i insert_tables.sql
   ```
   ¡Ten cuidado con los nombres de las tablas si modificas algo es posible que te de error!

   
### Crear Imágenes Docker
Navega al directorio de cada servicio y crea la imagen Docker correspondiente:
```bash
cd user-service
docker build -t user-service:latest .

cd ../order-service
docker build -t order-service:latest .

cd ../product-service
docker build -t product-service:latest .

¡¡¡ ES POSIBLE QUE TENGAS QUE EJECUTAR OTRA VEZ ESTE COMANDO ANTES DEL DOCKER BUILD

   eval $(minikube docker-env)


 DENTRO DEL DIRECTORIO DONDE ESTA EL SERVICIO PARA QUITAR EL ERROR SOBRE LA IMAGEN DE LOS PODS!!!

Asi con los demas servicios...
```

### Aplicar Configuración Kubernetes
Aplica los archivos de despliegue (`deployment.yaml`) y servicio (`service.yaml`) para cada servicio:
```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```


### Configuración de Puertos
Todos los servicios deben apuntar al mismo puerto interno para facilitar la conexión. En este proyecto, el puerto utilizado es el `80`.

## Configuración de Kong

1. Instala Kong utilizando Helm:
   ```bash
   helm install kong kong/kong --set ingressController.installCRDs=false && \
   helm upgrade kong kong/kong --set admin.enabled=true --set admin.http.enabled=true
   ```
2. Verifica que Kong esté funcionando:
   ```bash
   kubectl get pods -n kong
   ```

## Verificar Despliegues
Para asegurarte de que todos los servicios están funcionando:
```bash
kubectl get pods
kubectl get svc
```

## Solución de Problemas
Si encuentras algún problema con los servicios, puedes inspeccionar los registros con:
```bash
kubectl logs <nombre del pod>
```

## Configuración de Ingress

Crea y aplica un archivo `ingress.yaml` donde definas las rutas de los endpoints y el puerto al que apuntan:
```bash
kubectl apply -f ingress.yaml
```

## Configuración del archivo `/etc/hosts`

Para asignar un nombre a la IP de Minikube, edita el archivo `/etc/hosts` utilizando el siguiente comando:

```bash
sudo nano /etc/hosts
```

Asegúrate de incluir la siguiente línea:

```
<ip de minikube>    api.petstore.com
```

Además, verifica que el archivo contenga las siguientes líneas predeterminadas:

```
<ip localhost>     localhost
<ip ubuntu>       alfonso-ubuntu
```

---

## Pruebas de los Servicios

### USERS
- **Inicio de sesión**:
  ```bash
  curl -X POST "http://api.petstore.com:<Puerto-KongProxy>/api/users/login" \
  -H "Content-Type: application/json" \
  -d '{ "email": "testuser@example.com", "password": "securepassword" }'
  ```
  Resultado:
  ```json
  {"access_token":"<TOKEN>","token_type":"bearer"}
  ```

- **Obtener perfil de usuario**:
  ```bash
  curl -X GET "http://api.petstore.com:<Puerto-KongProxy>/api/users/profile" \
  -H "Authorization: Bearer <TOKEN>"
  ```

  **Registrar usuario**:
  ```bash
  curl -X POST "http://api.petstore.com:32023/api/users/register" \
  -H "Content-Type: application/json" \
  -d '{
  "id": "user1",
  "username": "testuser",
  "email": "testuser@example.com",
  "password": "securepassword",
  "firstname": "Test",
  "lastname": "User",
  "phonenumber": "123456789",
  "role": "cliente"
  }'
  ```


### Direcciones
- **Listar direcciones**:
  ```bash
  curl -X GET "http://api.petstore.com:<Puerto-KongProxy>/api/users/addresses" \
  -H "Authorization: Bearer <TOKEN>"
  ```

- **Añadir dirección**:
  ```bash
  curl -X POST "http://api.petstore.com:<Puerto-KongProxy>/api/users/addresses" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{ "street": "123 Main St", "city": "Springfield", "state": "IL", "country": "USA" }'
  ```

### Productos
- **Listar productos**:
  ```bash
  curl -X GET "http://api.petstore.com:<Puerto-KongProxy>/api/products"
  ```

- **Añadir producto**:
  ```bash
  curl -X POST "http://api.petstore.com:<Puerto-KongProxy>/api/products" \
  -H "Content-Type: application/json" \
  -d '{ "id": "prod5", "name": "Dog Food", "description": "High-quality dog food", "price": 19.99, "category": "cat1", "animaltype": "Dog", "brand": "BrandA", "stock": 100, "images": "https://example.com/dog-food.jpg", "averagerating": 4.5 }'
  ```

- **Actualizar producto**:
  ```bash
  curl -X PUT "http://api.petstore.com:<Puerto-KongProxy>/api/products/prod006" \
  -H "Content-Type: application/json" \
  -d '{ "id": "prod5", "name": "Cat Toy Deluxe", "description": "An upgraded fun toy for cats", "price": 12.99, "category": "toys", "animaltype": "cat", "brand": "HappyPets Deluxe", "stock": 30, "images": "https://example.com/deluxe-image.jpg", "averagerating": 4.8 }'
  ```

- **Eliminar producto**:
  ```bash
  curl -X DELETE "http://api.petstore.com:<Puerto-KongProxy>/api/products/prod001"
  ```

### Carrito
- **Listar carritos**:
  ```bash
  curl -X GET "http://api.petstore.com:<Puerto-KongProxy>/api/cart"
  ```

- **Añadir carrito**:
  ```bash
  curl -X POST "http://api.petstore.com:<Puerto-KongProxy>/api/cart" \
  -H "Content-Type: application/json" \
  -d '{ "id": "1", "user_id": "user1", "items": "[{\"product_id\": \"prod1\", \"quantity\": 2}]", "totalamount": 45.50 }'
  ```

- **Si te pasas de cantidad de productos**:
  ``` bash
   curl -X POST "http://api.petstore.com:32023/api/cart" \
  -H "Content-Type: application/json" \
  -d '{ "id": "1", "user_id": "user1", "items": "[{\"product_id\": \"prod3\", \"quantity\": 21}]", "totalamount": 45.50 }'

    {"detail":"Not enough stock for product prod3. Available: 20"}%   

    ```


- **Actualizar carrito**:
  ```bash
  curl -X PUT "http://api.petstore.com:<Puerto-KongProxy>/api/cart/3" \
  -H "Content-Type: application/json" \
  -d '{ "items": "[{\"product_id\": \"prod1\", \"quantity\": 3}, {\"product_id\": \"prod3\", \"quantity\": 1}]", "totalamount": 70.00 }'
  ```

- **Eliminar carrito**:
  ```bash
  curl -X DELETE "http://api.petstore.com:<Puerto-KongProxy>/api/cart/1"
  ```

### Categorías
- **Listar categorías**:
  ```bash
  curl -X GET "http://api.petstore.com:<Puerto-KongProxy>/api/categories"
  ```

- **Añadir categoría**:
  ```bash
  curl -X POST "http://api.petstore.com:<Puerto-KongProxy>/api/categories" \
  -H "Content-Type: application/json" \
  -d '{ "id": "cat4", "name": "Food", "description": "All types of pet food", "parentCategory": null, "imageUrl": "https://example.com/images/food.jpg", "active": true }'
  ```

- **Actualizar categoría**:
  ```bash
  curl -X PUT "http://api.petstore.com:<Puerto-KongProxy>/api/categories/cat1" \
  -H "Content-Type: application/json" \
  -d '{ "name": "Premium Food", "description": "High-quality pet food", "active": false }'
  ```

- **Eliminar categoría**:
  ```bash
  curl -X DELETE "http://api.petstore.com:<Puerto-KongProxy>/api/categories/cat3"
  ```

### Pedidos
- **Crear pedido**:
  ```bash
    curl -X POST "http://api.petstore.com:<Puerto-KongProxy>/api/orders" \
    -H "Content-Type: application/json" \
    -d '{
    "user_id": "user1",
    "paymentmethod": "credit_card",
    "shipping_address": {
        "street": "123 Main St",
        "city": "Springfield",
        "state": "IL",
        "country": "USA"
    }
    }' 

    {
    "id": "3813a3b9-4a78-45a7-9e58-8063b14845fc",
    "user_id": "user1",
    "items": [
        {
        "product_id": "prod1",
        "quantity": 2
        }
    ],
    "totalamount": 51.98,
    "paymentmethod": "credit_card",
    "paymentstatus": "pending",
    "orderstatus": "pending",
    "createdat": "2025-01-09T16:04:51.625907",
    "updatedat": "2025-01-09T16:04:51.625909"'
    }
  ```

- **Listar pedidos**:
  ```bash
  curl -X GET "http://api.petstore.com:<Puerto-KongProxy>/api/orders"
  ```

- **Cancelar pedido**:
  ```bash
  curl -X POST "http://api.petstore.com:<Puerto-KongProxy>/api/orders/<orderId>/cancel"
  ```

### Reseñas
- **Listar reseñas**:
  ```bash
  curl -X GET "http://api.petstore.com:<Puerto-KongProxy>/api/reviews/prod1"
  ```

- **Añadir reseña**:
  ```bash
  curl -X POST "http://api.petstore.com:<Puerto-KongProxy>/api/reviews/prod1" \
  -H "Content-Type: application/json" \
  -d '{ "user_id": "user3", "rating": 3, "comment": "Average quality.", "productid": "prod1" }'
  ```

- **Actualizar reseña**:
  ```bash
  curl -X PUT "http://api.petstore.com:<Puerto-KongProxy>/api/reviews/prod1/<reviewId>" \
  -H "Content-Type: application/json" \
  -d '{ "user_id": "user1", "rating": 4, "comment": "Changed my opinion after more use.", "productid": "prod1" }'
  ```

- **Eliminar reseña**:
  ```bash
  curl -X DELETE "http://api.petstore.com:<Puerto-KongProxy>/api/reviews/prod1/<reviewId>"
  ```

### Búsqueda
- **Búsqueda general**:
  ```bash
  curl -X GET "http://api.petstore.com:<Puerto-KongProxy>/api/search?q=food&type=all"
  ```

Con estos pasos, tendrás tu entorno configurado y listo para realizar las solicitudes definidas en el proyecto.

