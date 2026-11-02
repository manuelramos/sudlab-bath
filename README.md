# Django Starter Kit (BATH)

Starter kit de Django con el stack **BATH**:

- **B**ase Django
- **A**lpine.js
- **T**ailwind CSS (vía [pytailwindcss](https://github.com/timonweb/pytailwindcss), sin Node.js)
- **H**TMX

Las dependencias y el entorno virtual se gestionan con **[uv](https://docs.astral.sh/uv/)**. No hay `package.json`, npm ni `node_modules` en este repositorio.

## Estructura del proyecto

```
django_starter_kit/
├── config/                 # Proyecto Django (settings.py, urls.py, wsgi.py)
├── templates/              # Plantillas globales
│   ├── base.html           # Layout base BATH
│   └── components/         # Fragmentos reutilizables
├── static/                 # Estáticos en desarrollo (STATICFILES_DIRS)
│   ├── src/input.css       # Entrada Tailwind (directivas @tailwind)
│   ├── css/output.css      # CSS compilado (generado)
│   └── js/vendor/          # HTMX y Alpine locales (vendoring)
├── staticfiles/            # Salida de collectstatic (producción; en .gitignore)
├── tailwind.config.js      # Rutas content de Tailwind
├── download_vendors.py     # Descarga HTMX y Alpine a static/js/vendor/
├── Makefile                # Atajos de desarrollo (runserver + watch Tailwind)
├── Procfile.dev            # Opcional: honcho/overmind
├── manage.py
└── pyproject.toml          # Metadatos y dependencias uv
```

### ¿Por qué uv + pytailwindcss?

- **uv** ofrece instalaciones rápidas y reproducibles (`uv sync`) y un flujo único para desarrollo y producción (`uv run`, `uv add`).
- **pytailwindcss** empaqueta el CLI standalone oficial de Tailwind, así puedes usar `@tailwind` y `tailwind.config.js` sin toolchain JavaScript.
- **HTMX** y **Alpine.js** viven en `static/js/vendor/` para funcionar sin CDN y sin conexión externa en runtime.
- **WhiteNoise** sirve estáticos comprimidos y con caché en producción tras `collectstatic`.

Este proyecto fija **Tailwind CSS v3.4.x** (`TAILWINDCSS_VERSION=v3.4.17`) para que las directivas `@tailwind base/components/utilities` en `static/src/input.css` coincidan con `tailwind.config.js`.

## Requisitos

- Python 3.13+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) en el PATH

## Instalación y desarrollo local

### 1. Clonar e instalar dependencias

```bash
cd django_starter_kit
uv sync
```

`uv sync` instala dependencias de runtime y, por defecto, el grupo **dev** (incluye `django-browser-reload`). El grupo **prod** añade Gunicorn para los ejemplos de despliegue.

### 2. Descargar vendors de frontend (HTMX + Alpine)

```bash
uv run python download_vendors.py
```

O con Make:

```bash
make vendors
```

Genera:

- `static/js/vendor/htmx.min.js`
- `static/js/vendor/alpine.min.js`

### 3. Instalar el binario del CLI de Tailwind (solo la primera vez)

En el primer uso, `pytailwindcss` puede descargar el binario automáticamente. Para fijar v3 explícitamente (recomendado en este repo):

```bash
export TAILWINDCSS_VERSION=v3.4.17
uv run tailwindcss_install
```

El `Makefile` exporta `TAILWINDCSS_VERSION=v3.4.17` en los targets de watch/build.

Si la descarga falla (p. ej. SSL corporativo), coloca manualmente el asset `tailwindcss-macos-arm64` del release v3.4.17 renombrado como `tailwindcss` en:

`.venv/lib/python3.13/site-packages/pytailwindcss/bin/v3.4.17/tailwindcss`

En macOS puede hacer falta: `xattr -cr` sobre ese binario y `chmod +x`.

### 4. Migraciones de base de datos

```bash
uv run python manage.py migrate
```

### 5. Compilar CSS una vez (opcional antes del primer arranque)

```bash
make css
```

### 6. Ejecutar Django y Tailwind watch a la vez

**Recomendado (Make):**

```bash
make dev
```

Ejecuta en paralelo:

- `uv run python manage.py runserver`
- `uv run tailwindcss -i ./static/src/input.css -o ./static/css/output.css --watch`

**Alternativa (Procfile.dev):** con [honcho](https://github.com/nickstenning/honcho) u [overmind](https://github.com/DarthSim/overmind):

```bash
honcho start -f Procfile.dev
```

### 7. Extender plantillas

En tus apps, extiende el layout base:

```django
{% extends "base.html" %}

{% block title %}Mi página{% endblock %}

{% block body %}
  <main class="p-8">
    <h1 class="text-2xl font-bold">Hola BATH</h1>
  </main>
{% endblock %}
```

Los partials pequeños pueden ir en `templates/components/` con `{% include "components/tu_partial.html" %}`. Para UI reutilizable del design system, usa **django-cotton** (ver `AGENTS.md`).

### Variables de entorno

Copia `.env.example` a `.env` y ajusta valores locales:

```bash
cp .env.example .env
```

### Recarga automática del navegador (solo desarrollo)

Con `DEBUG=True`:

- `django_browser_reload` se añade a `INSTALLED_APPS` y al middleware.
- `config/urls.py` monta `__reload__/`.
- `templates/base.html` incluye el snippet de recarga solo cuando `debug` es verdadero en el contexto.

Instala dependencias de desarrollo con `uv sync` (por defecto). Para un entorno tipo producción sin herramientas dev:

```bash
uv sync --no-dev --group prod
```

## Build y producción

Define `DEBUG=False`, configura `ALLOWED_HOSTS` y usa un `SECRET_KEY` seguro (variable de entorno) antes de desplegar.

### 1. Instalar dependencias de producción

```bash
uv sync --no-dev --group prod
```

### 2. Compilar y minificar CSS

```bash
export TAILWINDCSS_VERSION=v3.4.17
uv run tailwindcss -i ./static/src/input.css -o ./static/css/output.css --minify
```

O:

```bash
make css-prod
```

### 3. Recolectar archivos estáticos

WhiteNoise usa `CompressedManifestStaticFilesStorage`:

```bash
uv run python manage.py collectstatic --noinput
```

La salida va a `staticfiles/`.

### 4. Servidor de aplicación

**Gunicorn** (grupo de dependencias `prod`):

```bash
uv run gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

**Uvicorn** (añade el paquete si prefieres ASGI):

```bash
uv add --group prod uvicorn
uv run uvicorn config.asgi:application --host 0.0.0.0 --port 8000
```

Aplica migraciones en el entorno destino:

```bash
uv run python manage.py migrate
```

## Targets útiles del Makefile

| Target               | Descripción                          |
|----------------------|--------------------------------------|
| `make dev`           | Runserver + Tailwind `--watch`       |
| `make css`           | Build único de Tailwind              |
| `make css-prod`      | Build minificado de Tailwind         |
| `make vendors`       | Descargar HTMX y Alpine              |
| `make migrate`       | Ejecutar migraciones Django          |
| `make collectstatic` | Ejecutar `collectstatic`             |

## Añadir apps Django

Al crear apps en la raíz del proyecto, Tailwind ya escanea:

- `./templates/**/*.html`
- `./*/templates/**/*.html` y carpetas anidadas (ver `tailwind.config.js`).

Tras añadir clases en plantillas nuevas, el watch regenera `static/css/output.css` en desarrollo.

## Licencia

Usa y adapta libremente en tus propios proyectos.
