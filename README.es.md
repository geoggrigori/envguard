<!-- ══════════════════════════ PORTADA ══════════════════════════ -->
<div align="center">
  <img src="docs/title-banner.svg" width="100%" alt="envguard"/>
</div>

<br/>

<!-- ══════════════════════ IDIOMAS / LANGUAGES ══════════════════════ -->
<div align="center">
<a href="README.md"><img src="https://img.shields.io/badge/Português-555555?style=for-the-badge" alt="Português"/></a>
<a href="README.en.md"><img src="https://img.shields.io/badge/English-555555?style=for-the-badge" alt="English"/></a>
<a href="README.es.md"><img src="https://img.shields.io/badge/Español-1987F0?style=for-the-badge" alt="Español"/></a>
</div>

<br/>

<div align="center">
<img src="https://img.shields.io/badge/Python_3.11%2B-6B2FB5?style=flat-square&logo=python&logoColor=white" alt="python"/>
<img src="https://img.shields.io/badge/dependencies-zero-4A1E86?style=flat-square" alt="zero deps"/>
<img src="https://img.shields.io/badge/tests-pytest-2E7D32?style=flat-square" alt="pytest"/>
<img src="https://img.shields.io/badge/License-MIT-2E7D32?style=flat-square" alt="license"/>
</div>

<div align="center">
<a href="#acerca-de"><img src="https://img.shields.io/badge/▸_ACERCA_DE-1987F0?style=for-the-badge" alt="acerca"/></a>
<a href="#cómo-funciona"><img src="https://img.shields.io/badge/▸_CÓMO_FUNCIONA-000000?style=for-the-badge" alt="funciona"/></a>
<a href="#uso"><img src="https://img.shields.io/badge/▸_USO-1987F0?style=for-the-badge" alt="uso"/></a>
<a href="#schema"><img src="https://img.shields.io/badge/▸_SCHEMA-000000?style=for-the-badge" alt="schema"/></a>
</div>

<br/>

> 🐍 **Solo standard library.** Cero dependencias de terceros que instalar, auditar o mantener actualizadas.

## Acerca de

**envguard** es una herramienta de línea de comandos que valida tus variables de entorno contra un schema declarativo. Apúntala a un `envguard.toml`, córrela en tu pipeline de CI o entrypoint del contenedor, y recibe un reporte claro de pass/fail antes de que tu aplicación siquiera inicie.

**Destacados:**
- **Schema declarativo** en TOML puro (parseado con `tomllib` de la stdlib).
- **Chequeos de tipo ricos**: `string`, `int`, `float`, `bool`, `url`, `email`, `enum`, `regex`.
- Variables **obligatorias vs. opcionales**, con **valores por defecto**.
- Soporte de archivo **`.env`** vía `--env-file`, sobrepuesto por el entorno real del proceso.
- **Tabla de resultados** alineada con filas `OK`/`MISSING`/`INVALID`.
- **Salida JSON** vía `--format json` para consumo por CI.
- **Exit codes CI-friendly**: `0` cuando todo pasa, `1` en cualquier falla.

## Cómo funciona

```mermaid
flowchart TD
    A[Carga schema<br/>envguard.toml] --> B[Lee entorno<br/>archivo .env + entorno del proceso]
    B --> C{Valida cada<br/>variable}
    C -->|presente y válida| D[OK]
    C -->|obligatoria y ausente| E[MISSING]
    C -->|presente y errónea| F[INVALID]
    C -->|ausente con default| D
    D --> G[Imprime tabla de resultados]
    E --> G
    F --> G
    G --> H{¿Alguna falla?}
    H -->|no| I[Exit 0]
    H -->|sí| J[Exit 1]
```

## Uso

```bash
git clone https://github.com/geoggrigori/envguard.git
cd envguard
pip install .
```

Escribe un schema describiendo las variables que tu app espera:

```toml
# envguard.toml
[DATABASE_URL]
required = true
type = "url"

[PORT]
required = true
type = "int"

[LOG_LEVEL]
type = "enum"
values = ["debug", "info", "warning", "error"]
default = "info"
```

```bash
envguard --schema envguard.toml
envguard --schema envguard.toml --env-file .env
envguard --schema envguard.toml --format json
```

**Salida de ejemplo:**
```text
VARIABLE         STATUS   DETAIL
---------------  -------  ----------------------------
DATABASE_URL     OK       url
PORT             OK       int
ADMIN_EMAIL      MISSING  required but not set
RELEASE_TAG      INVALID  value '1.4.2' does not match /v\d+\.\d+\.\d+/

6 ok, 2 failed, 8 total
```

## Schema

| Campo | Significado |
|---|---|
| `required` | `true` si la variable debe estar presente (por defecto `false`) |
| `type` | `string`, `int`, `float`, `bool`, `url`, `email`, `enum`, `regex` (por defecto `string`) |
| `values` | Lista de valores permitidos; obligatorio cuando `type = "enum"` |
| `pattern` | Regex que el valor debe coincidir; obligatorio cuando `type = "regex"` |
| `default` | Valor usado cuando la variable está ausente; reportado como `OK` |

**Pruebas:**
```bash
pip install -e ".[dev]"
python -m pytest
```

## Licencia

[MIT](LICENSE).

<div align="center">
  <img src="https://file.loading.io/color/feature/thumb/Blues-8.png?" width="100%" height="10px" alt="divider"/>
</div>

<p align="center"><sub>Desarrollado por <strong><a href="https://github.com/geoggrigori">Grigori</a></strong> · 2026</sub></p>
