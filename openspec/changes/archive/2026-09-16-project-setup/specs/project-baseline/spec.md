## Purpose

Baseline del repositorio de la plataforma: estructura hexagonal heredada por todo el código futuro, núcleo puro sin dependencias de interfaz, empaquetado instalable, configuración válida de OpenSpec y documentación de referencia.

## ADDED Requirements

### Requirement: Estructura hexagonal del repositorio

El proyecto SHALL organizar su código fuente bajo `src/` en tres paquetes Python importables — `core`, `infrastructure` y `entrypoints` — y las pruebas bajo `tests/`.

#### Scenario: Los paquetes de las tres capas son importables

- **WHEN** se ejecuta `python -c "import core, infrastructure, entrypoints"`
- **THEN** la sentencia termina sin errores de importación

#### Scenario: La estructura de directorios existe

- **WHEN** se inspecciona la raíz del repositorio
- **THEN** existen los directorios `src/core/`, `src/infrastructure/`, `src/entrypoints/` y `tests/`

### Requirement: Núcleo puro sin dependencias de interfaz

La capa `src/core` SHALL permanecer en Python puro: ningún módulo de `core` SHALL importar Streamlit, Gradio ni FastAPI. La suite de pruebas SHALL verificar esta regla automáticamente.

#### Scenario: Guard de pureza del núcleo

- **WHEN** se ejecuta la suite de pruebas
- **THEN** una prueba se ejecuta y comprueba que ningún archivo bajo `src/core/` importa `streamlit`, `gradio` o `fastapi`

#### Scenario: Dependencias de interfaz ausentes del núcleo

- **WHEN** se ejecuta la prueba de pureza en un `src/core` que contenga un import prohibido de `streamlit`, `gradio` o `fastapi`
- **THEN** la prueba falla e identifica el archivo infractor

### Requirement: Empaquetado e instalación del proyecto

El proyecto SHALL ser instalable con `pip` desde el repositorio, requiriendo Python 3.11 o superior, y declarando las dependencias de runtime (Pandas, Polars, PyArrow, Pydantic) y las de desarrollo (Pytest).

#### Scenario: Instalación editable con extras de desarrollo

- **WHEN** se ejecuta `pip install -e ".[dev]"`
- **THEN** el paquete se instala en modo editable y `pytest` queda disponible en el entorno

#### Scenario: Requisito de versión mínima de Python

- **WHEN** se inspecta `pyproject.toml`
- **THEN** `requires-python` es `>=3.11`

### Requirement: Configuración de OpenSpec válida

`openspec/config.yaml` SHALL ser un documento YAML válido que defina las secciones `context` (stack técnico, dominio y arquitectura), `rules` (reglas por artefacto) y `operations` (guía para `apply` y `archive`).

#### Scenario: La configuración es legible por OpenSpec

- **WHEN** se ejecuta `openspec doctor`
- **THEN** la configuración se lee como YAML válido sin errores de parseo

#### Scenario: Reglas y operaciones definidas

- **WHEN** se lee `openspec/config.yaml`
- **THEN** `rules` contiene la regla de cerrar cada tarea con un commit y `operations.apply` contiene la guía de ejecutar `pytest` antes de marcar tareas como completadas

### Requirement: Documentación de referencia

`README.md` SHALL documentar el propósito del proyecto, el stack técnico, la arquitectura (incluida la regla de núcleo puro), la estructura del repositorio y los pasos de arranque rápido.

#### Scenario: Contenido esencial del README

- **WHEN** se lee `README.md`
- **THEN** incluye propósito, stack, regla de núcleo puro y una sección de instalación/running rápida

### Requirement: Suite de pruebas ejecutable

Los tests SHALL ejecutarse con `pytest` e incluir al menos una prueba de humo de importación y el guard de pureza del núcleo.

#### Scenario: Pytest en verde sobre la baseline

- **WHEN** se ejecuta `pytest` en la raíz del repositorio
- **THEN** la suite completa pasa sin errores