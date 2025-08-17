# Sistema de Inicialización de Base de Datos

## Resumen

El sistema de inicialización de base de datos ha sido completamente rediseñado para proporcionar una creación automática y robusta de la base de datos y tablas con manejo adecuado de errores y compatibilidad de zonas horarias. Este sistema asegura que la aplicación pueda iniciarse exitosamente independientemente del estado inicial de la base de datos.

## Características Principales

### Creación Automática de Base de Datos
- **Detección Inteligente**: Detecta automáticamente si la base de datos `raffles_db` existe
- **Creación Elegante**: Crea la base de datos si no existe usando permisos apropiados
- **Conciencia del Entorno**: Maneja entornos de desarrollo local y producción de manera diferente

### Soporte para Claves Primarias Compuestas
- **Aislamiento de Usuario**: Todas las entidades usan claves primarias compuestas que incluyen `user_id`
- **Estructura Jerárquica**: Mantiene relaciones apropiadas entre usuarios, proyectos, sets de rifas y rifas
- **Alcance de Auto-incremento**: Cada usuario tiene su propia secuencia de numeración comenzando desde 1

### Manejo Robusto de Errores
- **Recuperación de Conexión**: Maneja errores de "Base de datos desconocida" elegantemente
- **Múltiples Estrategias**: Alterna entre métodos de SQLAlchemy y SQL crudo
- **Registro Detallado**: Proporciona mensajes de error claros y confirmaciones de éxito

## Detalles de Implementación

### Flujo de Creación de Base de Datos

```python
def create_database_if_not_exists():
    """Crear la base de datos si no existe"""
    if settings.DATABASE_URL or settings.MYSQL_URL:
        # Entorno Railway - la base de datos ya debería existir
        return True
    
    # Conectar al servidor MySQL sin especificar base de datos
    sys_engine = create_engine(f"mysql+pymysql://{settings.MARIADB_USERNAME}:{settings.MARIADB_PASSWORD}@{settings.MARIADB_SERVER}:{settings.MARIADB_PORT}")
    
    with sys_engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {settings.MARIADB_DATABASE}"))
        return True
```

### Estrategia de Creación de Tablas

1. **Método Primario**: Creación de metadatos de SQLAlchemy
2. **Método de Respaldo**: Ejecución de SQL crudo desde structure.sql
3. **Verificación**: Siempre verifica que todas las tablas requeridas existan

### Integración de Inicio

El sistema se integra perfectamente con el inicio de FastAPI:

```python
# En database/__init__.py
try:
    if create_database_if_not_exists():
        Base.metadata.create_all(bind=engine)
        print("Base de datos inicializada exitosamente")
except Exception as e:
    print(f"Advertencia: No se pudo crear la base de datos/tablas: {e}")
```

## Soporte de Entornos

### Desarrollo Local
- Crea la base de datos y el usuario si no existen
- Maneja la configuración de MariaDB/MySQL automáticamente
- Proporciona mensajes de error detallados para resolución de problemas

### Producción/Railway
- Omite la creación de base de datos (asume base de datos administrada)
- Usa cadenas de conexión proporcionadas directamente
- Optimizado para entornos de despliegue en la nube

## Beneficios

### Experiencia del Desarrollador
- **Configuración Cero**: Funciona inmediatamente después de clonar
- **Retroalimentación Clara**: El registro detallado muestra exactamente qué está pasando
- **Inicio Resiliente**: La aplicación inicia incluso si la base de datos necesita inicialización

### Confiabilidad de Producción
- **Degradación Elegante**: Continúa la operación incluso con advertencias de inicialización
- **Detección de Entorno**: Se adapta automáticamente al entorno de despliegue
- **Agrupación de Conexiones**: Mantiene conexiones de base de datos eficientes

### Mantenimiento
- **Auto-reparación**: Automáticamente corrige bases de datos/tablas faltantes
- **Proceso Documentado**: Separación clara entre lógica de creación y conexión
- **Componentes Probables**: Cada función tiene una responsabilidad única y clara

## Componentes Relacionados

- **Sistema de Tokens JWT**: Corrigió problemas de zona horaria para validación adecuada de tokens
- **Claves Primarias Compuestas**: Habilita aislamiento de usuario y numeración predecible
- **Funciones Auxiliares Universales**: Operaciones de base de datos simplificadas en todos los modelos
