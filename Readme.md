# API de Gestión de Inventario - FastAPI & SQLModel 🚀

Esta es una API RESTful construida con **FastAPI** y **SQLModel** para la gestión de un catálogo de productos y sus categorías. El proyecto implementa una arquitectura limpia (Clean Architecture) separando responsabilidades en modelos, esquemas, servicios y enrutadores.

Destaca por la implementación de una **relación Muchos a Muchos (N:M)** entre Productos y Categorías, resolviendo de manera elegante los problemas comunes de importaciones circulares en SQLModel y optimizando las consultas a la base de datos para prevenir el problema N+1.

## 🛠️ Tecnologías Utilizadas

* **Framework Web:** [FastAPI](https://fastapi.tiangolo.com/)
* **ORM & Validación:** [SQLModel](https://sqlmodel.tiangolo.com/) (Combina el poder de SQLAlchemy y Pydantic)
* **Base de Datos:** Compatible con PostgreSQL, SQLite, MySQL (Dependiendo de la configuración en `database.py`)
* **Lenguaje:** Python 3.10+

## 📁 Estructura del Proyecto

El proyecto sigue una estructura modular por dominios (features):

```text
app/
├── core/
│   └── database.py          # Configuración de la DB y dependencia get_session
├── modules/
│   ├── categoria/
│   │   ├── models.py        # Entidad Categoria (SQLModel table=True)
│   │   ├── schemas.py       # Validaciones Pydantic (Create, Read, Update)
│   │   ├── services.py      # Lógica de negocio y consultas a la BD
│   │   └── router.py        # Endpoints de FastAPI
│   │
│   └── producto/
│       ├── models.py        # Entidad Producto y Tabla Intermedia (ProductoCategoriaLink)
│       ├── schemas.py       # Validaciones Pydantic
│       ├── services.py      # Lógica de negocio y asignación N:M
│       └── router.py        # Endpoints de FastAPI
└── main.py                  # Archivo principal de ejecución
```

✨ Funcionalidades Principales
1. Gestión de Categorías (CRUD): Creación, listado, actualización total y borrado lógico.

2. Gestión de Productos (CRUD): Control detallado de productos incluyendo precio, stock y stock mínimo.

3. Relación N:M: * Un producto puede pertenecer a múltiples categorías.

    * Una categoría puede agrupar múltiples productos.

    * Endpoints dedicados para asignar y remover categorías de un producto específico.

4. Control de Stock: Endpoint específico de lógica de negocio para evaluar si un producto requiere reposición (alerta de stock bajo).

5. Borrado Lógico: Las entidades no se eliminan físicamente de la base de datos, sino que cambian su estado activo a False para mantener la integridad histórica.

