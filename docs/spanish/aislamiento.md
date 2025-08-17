# Sistema de Aislamiento por Usuario - Documentación

## Introducción

Este sistema implementa un **aislamiento completo de datos por usuario**, garantizando que cada usuario solo pueda acceder, modificar y eliminar sus propios datos. Ningún usuario puede ver o interactuar con información de otros usuarios.

## Arquitectura del Sistema

### Estructura de Datos Jerárquica

```
USUARIO (users)
    ↓
PROYECTOS (projects) 
    ↓
SETS DE RIFAS (raffle_sets)
    ↓
RIFAS INDIVIDUALES (raffles)

COMPRADORES (buyers) ← Independiente pero vinculado al usuario
```

### Diferencias Importantes en el Manejo de Email

- **USERS (Usuarios del sistema)**: NO tienen email - autenticación solo con `username` y `password`
- **BUYERS (Compradores)**: SÍ tienen email - información de contacto del comprador real

## Cómo Funciona el Aislamiento

### 1. Nivel Base - Usuario
- Cada usuario se registra con `username` y `password` únicamente
- Recibe un ID único que será la base de toda la jerarquía
- No se almacena email para simplificar la autenticación

### 2. Nivel 1 - Proyectos
- Cada proyecto DEBE tener un `user_id` asignado
- Un usuario solo puede ver/modificar proyectos donde `user_id = su_id`
- Imposible acceder a proyectos de otros usuarios

### 3. Nivel 2 - Sets de Rifas
- Pertenecen a un proyecto específico
- **TRIGGER automático** asigna el `user_id` del proyecto padre
- Garantiza que el set pertenezca al mismo usuario que el proyecto

### 4. Nivel 3 - Rifas Individuales
- Pertenecen a un set específico
- **TRIGGER automático** asigna el `user_id` del set padre
- Mantiene la cadena de propiedad intacta

### 5. Nivel Independiente - Compradores
- Cada comprador DEBE tener un `user_id` asignado directamente
- Incluye `email` para información de contacto
- Un usuario solo puede ver/usar compradores donde `user_id = su_id`

## Ejemplo Práctico

### Escenario
- **Usuario A**: ID=1, username="admin_tienda"
- **Usuario B**: ID=2, username="vendedor_local"

### Flujo de Datos

#### 1. Usuario A crea un proyecto
```sql
INSERT INTO projects (name, description, user_id) 
VALUES ('Rifa Navideña 2024', 'Rifa para recaudar fondos navideños', 1);
-- Resultado: project_id = 101, user_id = 1
```

#### 2. Usuario A crea un set en su proyecto
```sql
INSERT INTO raffle_sets (name, project_id, init, final, unit_price) 
VALUES ('Set Principal', 101, 1, 100, 50);
-- TRIGGER automáticamente asigna user_id = 1
-- Resultado: set_id = 501, user_id = 1 (automático)
```

#### 3. Usuario A crea rifas en su set
```sql
INSERT INTO raffles (number, set_id) VALUES (1, 501);
INSERT INTO raffles (number, set_id) VALUES (2, 501);
-- TRIGGER automáticamente asigna user_id = 1 a cada rifa
```

#### 4. Usuario B intenta acceder a datos del Usuario A
```sql
-- Esta consulta NO devuelve nada para Usuario B:
SELECT * FROM projects WHERE user_id = 2;  -- VACÍO

-- Esta tampoco:
SELECT * FROM raffle_sets WHERE user_id = 2;  -- VACÍO

-- Usuario B NO PUEDE ver datos del Usuario A
```

## Implementación en el Código

### Consultas Seguras
```python
# ✅ CORRECTO - Siempre filtrar por user_id
def get_user_projects(db: Session, current_user_id: int):
    return db.query(Project).filter(Project.user_id == current_user_id).all()

# ❌ INCORRECTO - Sin filtro de usuario (INSEGURO)
def get_all_projects(db: Session):
    return db.query(Project).all()  # Devuelve datos de TODOS los usuarios
```

### Validación de Propiedad
```python
def delete_project(db: Session, project_id: int, current_user_id: int):
    # Verificar que el proyecto pertenece al usuario actual
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user_id  # CLAVE: validar propiedad
    ).first()
    
    if not project:
        raise HTTPException(404, "Proyecto no encontrado o no tienes permisos")
    
    db.delete(project)
    db.commit()
```

## Flujo de Seguridad

### 1. Autenticación
- Usuario se registra/autentica con `username` y `password`
- Recibe JWT token que contiene su `user_id`
- No se requiere email para el proceso de autenticación

### 2. Autorización
- Cada request valida el JWT token
- Extrae el `user_id` del token
- Todas las consultas filtran por ese `user_id`

### 3. Aislamiento
- Imposible acceder a datos de otros usuarios
- Triggers automáticos mantienen la integridad
- Índices optimizan consultas por usuario

## Protecciones Implementadas

### A Nivel de Base de Datos
- ✅ Cada tabla contiene `user_id`
- ✅ Triggers automáticos propagan la propiedad
- ✅ Índices compuestos optimizan consultas por usuario
- ✅ Restricciones de integridad referencial
- ✅ Autenticación simplificada sin email

### A Nivel de Aplicación
- ✅ Todas las queries filtran por `user_id`
- ✅ Validación de propiedad antes de modificar/eliminar
- ✅ JWT contiene el `user_id` del usuario autenticado
- ✅ Middleware de seguridad en todas las rutas
- ✅ Registro y login solo con username y password

## Ventajas del Sistema

1. **Aislamiento Completo**: Imposible acceso cruzado entre usuarios
2. **Automatización**: Triggers manejan la propagación de propiedad
3. **Escalabilidad**: Funciona eficientemente para miles de usuarios
4. **Simplicidad**: Autenticación solo con username, sin complejidad de email
5. **Auditoría**: Registro completo de accesos y modificaciones
6. **Performance**: Índices optimizados para consultas por usuario
7. **Flexibilidad**: Compradores pueden tener email para contacto

## Casos de Uso

### Registro de Usuario
```python
# Solo requiere username y password
user_data = {
    "username": "mi_tienda_online",
    "password": "mi_password_seguro"
}
```

### Creación de Comprador
```python
# Puede incluir email para contacto
buyer_data = {
    "name": "Juan Pérez",
    "email": "juan.perez@email.com",  # Para contacto
    "phone": "+54911234567"
}
```

## Conclusión

Este sistema garantiza que cada usuario opere en un entorno completamente aislado, donde solo puede acceder a sus propios datos. La diferenciación entre usuarios (sin email) y compradores (con email) permite una autenticación simple mientras mantiene la información de contacto necesaria para el negocio.
