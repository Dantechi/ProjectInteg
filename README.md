# 🐾 Adopciones & Refugios API

**Sistema integral para gestionar refugios de animales, mascotas, historiales de cuidado y adopciones.**

Una aplicación web moderna construida con FastAPI que permite a los refugios de animales gestionar su inventario de mascotas, registrar historiales de cuidado, procesar adopciones y visualizar estadísticas en dashboards interactivos.

---

## 📋 Contenido

- [Características](#características)
- [Requisitos Previos](#requisitos-previos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [API Endpoints](#api-endpoints)
- [Base de Datos](#base-de-datos)
- [Tecnologías](#tecnologías)
- [Contribución](#contribución)

---

## ✨ Características

### 🏠 Gestión de Refugios
- Crear, leer, actualizar y eliminar refugios
- Registrar ubicación y estado activo/inactivo
- Subir fotos de refugios a Supabase Storage
- Ver mascotas asociadas a cada refugio

### 🐕 Gestión de Mascotas
- Registro completo de mascotas (nombre, especie, raza, edad, sexo)
- Tipos de animales soportados: Perros, Gatos, Conejos, Pájaros
- Subir fotos de mascotas a Supabase
- Vincular mascotas a refugios específicos
- Marcar mascotas como disponibles o adoptadas

### 📋 Historial de Cuidados
- Registrar eventos de cuidado (ej: vacunación, baño, revisión médica)
- Asociar costos a cada evento
- Seguimiento de fechas de cada evento
- Ver historial detallado por mascota
- Cálculo automático de costos totales por mascota

### 👨‍👩‍👧‍👦 Gestión de Adopciones
- Registrar adopciones con información del adoptante
- Vincular adopciones a mascotas y refugios
- Historial completo de adopciones
- Fecha de adopción automática o personalizada

### 📊 Dashboards y Estadísticas
- Gráfico de mascotas por refugio
- Gráfico de adopciones por mes (últimos 5 años)
- Vista rápida de métricas importantes
- Datos en tiempo real desde la base de datos

### 🎨 Interfaz Web
- Interfaz web responsiva con HTML/CSS
- Navegación intuitiva entre secciones
- Formularios para crear y actualizar registros
- Sistema de mensajes de éxito/error
- Diseño moderno y limpio

---

## 🔧 Requisitos Previos

- **Python 3.9+**
- **pip** (gestor de paquetes de Python)
- **PostgreSQL 12+** (en Clever Cloud u otro servidor)
- **Supabase** (para almacenar fotos)
- **Conexión a Internet** (para acceder a las bases de datos en la nube)

---

## 📦 Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/Dantechi/ProjectInteg.git
cd ProjectInteg
```

### 2. Crear un Entorno Virtual

```bash
python -m venv .venv
```

**Activar el entorno virtual:**

- **En Windows (PowerShell):**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```

- **En Windows (CMD):**
  ```cmd
  .venv\Scripts\activate.bat
  ```

- **En macOS/Linux:**
  ```bash
  source .venv/bin/activate
  ```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuración

### 1. Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
# Base de Datos PostgreSQL (Clever Cloud)
POSTGRESQL_ADDON_USER=tu_usuario
POSTGRESQL_ADDON_PASSWORD=tu_contraseña
POSTGRESQL_ADDON_HOST=tu_host.cleverapps.io
POSTGRESQL_ADDON_PORT=5432
POSTGRESQL_ADDON_DB=tu_base_de_datos

# Supabase (Almacenamiento de Fotos)
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_clave_publica_supabase
SUPABASE_BUCKET=nombre_del_bucket
```

### 2. Obtener Credenciales

#### PostgreSQL en Clever Cloud
1. Ve a tu panel de Clever Cloud
2. Accede a tu aplicación
3. En "Add-ons" busca PostgreSQL
4. Copia las credenciales del complemento

#### Supabase
1. Crea una cuenta en [Supabase](https://supabase.com)
2. Crea un nuevo proyecto
3. Ve a "Storage" y crea un bucket llamado (por defecto) "fotos"
4. Copia la URL del proyecto y la clave pública desde "Settings > API"

### 3. Crear el Bucket en Supabase (Opcional)

Si deseas un nombre diferente para el bucket, cámbialo en el archivo `.env` y crea manualmente en Supabase.

---

## 🚀 Uso

### Ejecutar la Aplicación

Con el entorno virtual activado:

```bash
uvicorn main:app --reload
```

La aplicación estará disponible en `http://localhost:8000`

### Acceder a la Interfaz Web

- **Inicio:** http://localhost:8000/
- **Refugios:** http://localhost:8000/web/refugios
- **Mascotas:** http://localhost:8000/web/mascotas
- **Historial de Cuidados:** http://localhost:8000/web/historial
- **Adopciones:** http://localhost:8000/web/adopciones
- **Dashboards:** http://localhost:8000/web/dashboards

### Documentación Interactiva de la API

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 📁 Estructura del Proyecto

```
ProjectInteg/
├── main.py                      # Aplicación principal de FastAPI
├── models.py                    # Modelos de datos (SQLModel)
├── db.py                        # Configuración de la base de datos
├── refugio.py                   # Router y lógica de refugios
├── mascota.py                   # Router y lógica de mascotas
├── adopcion.py                  # Router y lógica de adopciones
├── historial.py                 # Router y lógica de historial de cuidados
├── upload.py                    # Funcionalidades de carga de archivos
├── stats.py                     # Estadísticas y funciones auxiliares
├── requirements.txt             # Dependencias de Python
├── .env                         # Variables de entorno (NO INCLUIR EN GIT)
├── adopciones.sqlite3           # Base de datos SQLite local (opcional)
│
├── migrations/                  # Scripts de migración SQL
│   └── 001_add_foto_url.sql    # Migración para añadir campo de foto
│
├── static/                      # Archivos estáticos (CSS, imágenes)
│   └── css/
│       └── styless.css         # Estilos CSS
│
├── templates/                   # Plantillas HTML (Jinja2)
│   ├── base.html               # Plantilla base
│   ├── home.html               # Página de inicio
│   ├── refugios_list.html      # Listado de refugios
│   ├── mascotas.html           # Listado de mascotas
│   ├── historial.html          # Historial de cuidados
│   ├── historial_detalle.html  # Detalle de historial por mascota
│   ├── adopciones.html         # Listado de adopciones
│   ├── dashboards.html         # Dashboards con gráficos
│   └── error.html              # Página de error
│
├── supa/                        # Módulo de Supabase
│   └── supabase.py             # Cliente y funciones de Supabase
│
└── README.md                    # Este archivo
```

---

## 🔌 API Endpoints

### Refugios

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/refugios` | Listar todos los refugios |
| GET | `/api/refugios/{id}` | Obtener detalles de un refugio |
| POST | `/api/refugios` | Crear un nuevo refugio |
| PUT | `/api/refugios/{id}` | Actualizar un refugio |
| DELETE | `/api/refugios/{id}` | Eliminar un refugio |

### Mascotas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/mascotas` | Listar todas las mascotas |
| GET | `/api/mascotas/{id}` | Obtener detalles de una mascota |
| POST | `/api/mascotas` | Crear una nueva mascota |
| PUT | `/api/mascotas/{id}` | Actualizar una mascota |
| DELETE | `/api/mascotas/{id}` | Eliminar una mascota |

### Historial de Cuidados

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/historial` | Listar todos los registros de cuidado |
| GET | `/api/historial/{id}` | Obtener detalle de un registro |
| POST | `/api/historial` | Crear un registro de cuidado |
| PUT | `/api/historial/{id}` | Actualizar un registro |
| DELETE | `/api/historial/{id}` | Eliminar un registro |

### Adopciones

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/adopciones` | Listar todas las adopciones |
| GET | `/api/adopciones/{id}` | Obtener detalle de una adopción |
| POST | `/api/adopciones` | Registrar una nueva adopción |
| PUT | `/api/adopciones/{id}` | Actualizar una adopción |
| DELETE | `/api/adopciones/{id}` | Eliminar una adopción |

---

## 🗄️ Base de Datos

### Esquema de Datos

La aplicación utiliza **PostgreSQL** con las siguientes tablas:

#### Tabla `refugio`
```sql
id (PK)          INTEGER PRIMARY KEY
nombre           VARCHAR(255) NOT NULL
ubicacion        VARCHAR(255) NOT NULL
activo           BOOLEAN DEFAULT TRUE
foto_url         VARCHAR(500)
```

#### Tabla `mascota`
```sql
id (PK)          INTEGER PRIMARY KEY
nombre           VARCHAR(255) NOT NULL
especie          VARCHAR(50) NOT NULL (Dog, Cat, Rabbit, Bird)
raza             VARCHAR(100)
edad             INTEGER NOT NULL
sexo             VARCHAR(10) NOT NULL
estado           BOOLEAN DEFAULT TRUE
foto_url         VARCHAR(500)
refugio_id (FK)  INTEGER REFERENCES refugio(id)
```

#### Tabla `adopcion`
```sql
id (PK)          INTEGER PRIMARY KEY
adoptante        VARCHAR(255) NOT NULL
fecha_adopcion   DATE NOT NULL
mascota_id (FK)  INTEGER REFERENCES mascota(id)
refugio_id (FK)  INTEGER REFERENCES refugio(id)
```

#### Tabla `historialcuidado`
```sql
id (PK)          INTEGER PRIMARY KEY
tipo_evento      VARCHAR(255) NOT NULL
costo            FLOAT NOT NULL
fecha            DATE NOT NULL
mascota_id (FK)  INTEGER REFERENCES mascota(id)
```

### Conexión a Base de Datos

La aplicación usa:
- **Motor:** SQLAlchemy con asyncio
- **ORM:** SQLModel
- **Adaptador:** asyncpg para PostgreSQL
- **Pool de Conexiones:** NullPool (configurable para servidores en la nube)

---

## 🛠️ Tecnologías

### Backend
- **FastAPI** - Framework web moderno y rápido
- **SQLModel** - Combina Pydantic y SQLAlchemy
- **SQLAlchemy** - ORM de Python
- **asyncpg** - Driver asíncrono para PostgreSQL
- **Uvicorn** - Servidor ASGI

### Frontend
- **HTML5** - Estructura
- **CSS3** - Estilos
- **Jinja2** - Motor de plantillas
- **JavaScript** - Interactividad (básico)

### Almacenamiento
- **PostgreSQL** - Base de datos relacional
- **Supabase Storage** - Almacenamiento de fotos

### Otros
- **python-dotenv** - Gestión de variables de entorno
- **python-multipart** - Manejo de formularios
- **Supabase Python** - Cliente para Supabase

---

## 🔐 Seguridad

### Recomendaciones

1. **Variables de Entorno:** Nunca commitees el archivo `.env` al repositorio
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Credenciales de Base de Datos:** Usa credenciales seguras en Clever Cloud

3. **CORS:** Configura CORS según sea necesario en producción

4. **Validación de Entrada:** La aplicación valida todos los datos de entrada con Pydantic

5. **SQL Injection:** Se previene automáticamente con SQLModel/SQLAlchemy

---

## 📝 Ejemplos de Uso

### Crear un Refugio (vía API)

```bash
curl -X POST "http://localhost:8000/api/refugios" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Refugio Feliz",
    "ubicacion": "Calle Principal 123",
    "activo": true
  }'
```

### Crear una Mascota (vía API)

```bash
curl -X POST "http://localhost:8000/api/mascotas" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Max",
    "especie": "Dog",
    "raza": "Labrador",
    "edad": 3,
    "sexo": "M",
    "estado": true,
    "refugio_id": 1
  }'
```

### Registrar un Evento de Cuidado (vía API)

```bash
curl -X POST "http://localhost:8000/api/historial" \
  -H "Content-Type: application/json" \
  -d '{
    "mascota_id": 1,
    "tipo_evento": "Vacunación",
    "costo": 45.50,
    "fecha": "2025-12-04"
  }'
```

---

## 🐛 Troubleshooting

### Error: "No están configuradas las credenciales de Supabase"

**Solución:** Verifica que las variables `SUPABASE_URL` y `SUPABASE_KEY` estén correctamente definidas en `.env`

### Error: "connect() missing required positional argument: 'ioloop'"

**Solución:** Asegúrate de tener la última versión de `asyncpg`:
```bash
pip install --upgrade asyncpg
```

### Error: "Port 8000 already in use"

**Solución:** Usa un puerto diferente:
```bash
uvicorn main:app --reload --port 8001
```

### Las fotos no se cargan en Supabase

**Solución:**
1. Verifica que el bucket existe en Supabase
2. Comprueba que el bucket tiene permisos de lectura pública
3. Revisa los logs de Supabase para errores de autenticación

---

## 📞 Soporte y Contacto

- **Repositorio:** [GitHub - ProjectInteg](https://github.com/Dantechi/ProjectInteg)
- **Issues:** Abre un issue en GitHub para reportar problemas
- **Contribuciones:** Las pull requests son bienvenidas

---

## 📄 Licencia

Este proyecto está bajo licencia MIT. Consulta el archivo `LICENSE` para más detalles.

---

## 🎯 Próximas Mejoras (Roadmap)

- [ ] Autenticación y autorización de usuarios
- [ ] Rol de administrador vs voluntario
- [ ] Búsqueda avanzada de mascotas
- [ ] Exportar reportes a PDF
- [ ] Notificaciones por email
- [ ] Sistema de comentarios y notas en historiales
- [ ] Integración con redes sociales para promocionar adopciones
- [ ] App móvil
- [ ] Tests unitarios e integración

---

**Creado con ❤️ para los amigos peludos del mundo.**
