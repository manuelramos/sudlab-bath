# AGENTS.md — Instrucciones maestras para agentes de IA

Estás trabajando en **django-starter-kit**, un **Django Starter Kit** orientado a producción con el stack **BATH**. Trata este documento como contexto vinculante: toda sugerencia, archivo y comando debe cumplir estas reglas —incluidas las **5 reglas de Rob Pike**— salvo que la persona humana indique lo contrario de forma explícita.

---

## Misión

Extender y mantener una base Django moderna que priorice **HTML renderizado en servidor**, **interacción hipermedia (HTMX)**, **JavaScript mínimo en cliente (Alpine.js)** y **estilos utility-first (Tailwind CSS)**, sin toolchain Node.js.

---

## Las 5 reglas de Rob Pike (obligatorias)

Estas reglas rigen **todo** el código Python, consultas ORM, diseño de modelos y decisiones de arquitectura en este repo. **No las ignores** al proponer “mejoras” de rendimiento, refactors o abstracciones.

| # | Regla | Implicación para agentes en este proyecto |
|---|--------|---------------------------------------------|
| **1** | No puedes adivinar dónde gastará tiempo el programa; los cuellos de botella sorprenden. No metas optimizaciones de velocidad hasta **demostrar** dónde está el cuello de botella. | No sugieras `select_related`/`prefetch_related` masivos, caché Redis, índices DB o async “por si acaso”. Primero el camino simple con ORM Django; optimiza solo con evidencia (toolbar, logs, profiling). |
| **2** | **Mide**. No ajustes por velocidad hasta haber medido; ni entonces, salvo que una parte domine claramente al resto. | Usa `django-debug-toolbar` en dev o métricas reales antes de cambiar consultas o algoritmos. Las reglas 1 y 2 repiten el aforismo de Tony Hoare: *“La optimización prematura es la raíz de muchos males”*. |
| **3** | Los algoritmos sofisticados son lentos cuando **n es pequeño**, y **n suele ser pequeño**. Tienen constantes grandes. Hasta que sepas que **n será grande a menudo**, no te compliques. (Si n crece, aplica antes la regla 2.) | Prefiere listas, bucles claros y ORM directo en vistas típicas de starter kit. No introduzcas estructuras raras, colas o patrones distribuidos para decenas de filas. Ken Thompson resume las reglas 3 y 4: *“When in doubt, use brute force.”* |
| **4** | Los algoritmos sofisticados tienen más bugs y cuestan más implementarlos. Usa **algoritmos simples** y **estructuras de datos simples**. | Evita capas de servicio, generic factories, signals en cascada o metaprogramación salvo necesidad real. Tres líneas repetidas suelen ser mejores que una abstracción prematura (KISS). |
| **5** | **Los datos dominan**. Con las estructuras de datos correctas y buena organización, el algoritmo suele ser obvio. Lo central son las **estructuras de datos**, no los algoritmos. | Diseña modelos, relaciones (`ForeignKey`, `UniqueConstraint`) y consultas pensando en el dominio; deja que el ORM exprese el acceso. Fred Brooks (*The Mythical Man-Month*) y la forma corta: *“write stupid code that uses smart objects”*. |

**Compromiso del agente:** si tu cambio añade complejidad “por rendimiento” o “por elegancia” sin medición ni requisito claro del humano, **detente** y elige la solución más simple que cumpla el requisito.

---

## Stack tecnológico (obligatorio)

| Capa | Elección |
|------|----------|
| Backend | **Django** (Python 3.13+) |
| Paquetes y entorno virtual | Solo **`uv`** |
| Variables de entorno | **`django-environ`** (`.env` + `.env.example`) |
| CSS | **Tailwind CSS** vía **`pytailwindcss`** (CLI standalone, fijado **v3.4.x** en este repo) |
| UX en red | **HTMX** (vendoring en `static/js/vendor/`) |
| Estado efímero / micro-interacciones | **Alpine.js** (vendoring, `defer`) |
| Componentes UI | **`django-cotton`** |
| Integración HTMX | **`django-htmx`** |
| Estilos de formularios | **`django-widget-tweaks`** (no Crispy Forms) |
| Timestamps en modelos | **`django-model-utils`** (`TimeStampedModel`) |
| Estáticos (prod) | **WhiteNoise** |
| Lint / format | **Ruff** (`pyproject.toml`) |

Solo desarrollo (`DEBUG=True`): `django-debug-toolbar`, `django-extensions`, `django-browser-reload`.

---

## Regla de oro: cero infraestructura Node.js

**ESTRICTAMENTE PROHIBIDO** que los agentes introduzcan o recomienden:

- Node.js, npm, yarn, pnpm, bun
- `package.json`, `package-lock.json`, `node_modules/`
- Vite, Webpack, esbuild, pipelines Tailwind vía PostCSS/npm
- Scripts HTMX/Alpine desde CDN en plantillas (los assets son **locales** en `static/js/vendor/`)

Tailwind se compila con:

```bash
uv run tailwindcss -i ./static/src/input.css -o ./static/css/output.css [--watch|--minify]
```

O atajos del proyecto: `make css`, `make css-prod`, `make dev`.

**No** modifiques la configuración Tailwind (versión fijada, `tailwind.config.js`, `static/src/input.css`) salvo petición explícita de migración Tailwind.

---

## Estructura del proyecto (léela antes de editar)

```
config/                 # Proyecto Django: settings.py, urls.py, wsgi/asgi
templates/              # Plantillas globales; extiende base.html
templates/components/   # Partials pequeños (no Cotton salvo casos justificados)
static/
  src/input.css         # Entrada Tailwind (@tailwind) — no añadir CSS custom aquí a la ligera
  css/output.css        # Generado; commitear o regenerar con make css
  js/vendor/            # htmx.min.js, alpine.min.js (download_vendors.py)
manage.py
pyproject.toml          # dependencias, grupos uv, ruff
.env.example            # plantilla de secretos; nunca commitear .env
Makefile                # flujo dev (runserver + tailwind watch)
```

Las **apps** Django nuevas viven en la raíz del proyecto salvo indicación contraria. Regístralas en `config/settings.py` → `INSTALLED_APPS`.

---

## Política de comandos: siempre `uv`

Usa **`uv`** en todas las operaciones Python/paquetes. **Nunca** sugieras `pip`, `pip install` ni Poetry.

| Tarea | Patrón de comando |
|-------|-------------------|
| Ejecutar Django | `uv run python manage.py <comando>` |
| Añadir dependencia | `uv add <paquete>` o `uv add --dev <paquete>` |
| Sincronizar entorno | `uv sync` (grupo dev activo por defecto) |
| Sync producción | `uv sync --no-dev --group prod` |
| Lint | `uv run ruff check .` |
| Formato | `uv run ruff format .` |

No indiques `python manage.py` sin `uv run` salvo que el humano ya tenga `.venv` activado y lo prefiera; por defecto usa `uv run`.

---

## Locality of Behavior (LoB)

- Mantén **comportamiento y estilos en plantillas HTML**: clases Tailwind, atributos HTMX (`hx-get`, `hx-target`, `hx-swap`, etc.), Alpine (`x-data`, `x-on:click`, etc.).
- **No** crees archivos `.css` o módulos `.js` nuevos para UI puntual si existe alternativa razonable en HTML.
- **No** propongas SPAs, APIs JSON para flujos HTMX estándar ni frameworks pesados (React, Vue, etc.).
- Prefiere extender **`templates/base.html`** y componentes Cotton antes de duplicar assets en `<head>`.

---

## Reglas Django y plantillas

### Componentes Cotton (UI reutilizable)

- Construye UI reutilizable con etiquetas **`django-cotton`** (p. ej. `<c-button>`, `<c-card>`), no `{% include %}` a nivel componente.
- Ubica plantillas Cotton según las convenciones de django-cotton (típicamente `templates/cotton/` o la documentación de la versión instalada).
- Usa `{% include %}` solo para fragmentos pequeños no componente (p. ej. snippets solo dev), no para piezas del design system.

### HTMX + django-htmx

- `django_htmx.middleware.HtmxMiddleware` está activo; usa **`request.htmx`** en vistas.
- Endpoints llamados por HTMX deben devolver **partials HTML** (fragmentos), no páginas completas ni JSON, salvo petición explícita de API.

```python
def item_partial(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.htmx:
        return render(request, "items/partials/item_row.html", {"item": item})
    return render(request, "items/detail.html", {"item": item})
```

- Usa `hx-target`, `hx-swap` e IDs/clases estables en destinos de swap.
- Respeta CSRF: `{% csrf_token %}` en formularios y cabeceras HTMX cuando corresponda.

### Formularios

- Estiliza con **`django-widget-tweaks`** (`{% load widget_tweaks %}`, `{% render_field field class="..." %}`).
- **No** sugieras django-crispy-forms salvo petición explícita.

### Modelos

- Si un modelo necesita **fechas de creación/actualización**, hereda de **`TimeStampedModel`**:

```python
from model_utils.models import TimeStampedModel

class Item(TimeStampedModel):
    name = models.CharField(max_length=255)
```

### Settings y seguridad

- Lee **`SECRET_KEY`**, **`DEBUG`** y **`DATABASE_URL`** del entorno vía django-environ; actualiza **`.env.example`** al añadir variables obligatorias.
- No hardcodees secretos ni dejes `DEBUG=True` en rutas de producción.
- Conserva middleware **WhiteNoise** y `STORAGES["staticfiles"]` salvo cambio explícito de estrategia de estáticos.
- Apps/middleware solo dev (`debug_toolbar`, `django_browser_reload`, etc.) dentro de bloques **`if DEBUG:`** — no los actives incondicionalmente.

### URLs

- Registra rutas solo de debug bajo `if settings.DEBUG:` en `config/urls.py`.

---

## Assets estáticos y vendors

- HTMX y Alpine están en **vendoring**; actualiza con `uv run python download_vendors.py` o `make vendors`.
- Enlaza assets con `{% static '...' %}`; layout base: **`templates/base.html`**.

---

## Calidad de código

- Aplica siempre las **5 reglas de Rob Pike** (sección anterior): simplicidad, datos bien modelados, cero optimización prematura.
- Sigue **Ruff** en `pyproject.toml` (longitud 88, orden de imports `I`, etc.).
- Ejecuta **`uv run ruff check`** / **`uv run ruff format`** en Python tocado antes de dar por cerrado el trabajo.
- Diffs mínimos; respeta nombres y estructura en `config/`.
- No añadas tests, docs ni dependencias que el humano no haya pedido.

---

## Lo que los agentes no deben hacer (resumen)

1. Introducir Node/npm o cadenas de build frontend.
2. Sustituir componentes Cotton por includes para UI reutilizable.
3. Devolver JSON en flujos HTMX estándar de partials.
4. Sugerir Crispy Forms en lugar de widget-tweaks.
5. Usar `pip`/`poetry` en lugar de `uv`.
6. Quitar o saltarse WhiteNoise, environ o guards dev/prod de `DEBUG` sin instrucción explícita.
7. Modificar infraestructura Tailwind/pytailwindcss sin instrucción explícita.
8. Optimizar, cachear o complicar algoritmos **sin medir** o **sin n grande demostrado** (violación de las reglas 1–3 de Pike).
9. Introducir abstracciones o estructuras “inteligentes” cuando bastan modelos Django y código directo (violación de las reglas 4–5 de Pike).

---

## Flujo por defecto para features nuevas

1. Lee `config/settings.py` y `config/urls.py` antes de cambiar comportamiento.
2. Añade o actualiza componentes Cotton y partials (LoB + HTMX).
3. Conecta vistas con `request.htmx` donde la interacción sea hipermedia.
4. Usa clases Tailwind en plantillas; recompila CSS si hace falta (`make css` o `make dev`).
5. Añade variables a `.env.example` si procede; usa `uv add` para dependencias Python nuevas.
6. Pasa Ruff.

En caso de duda, prioriza **HTML simple renderizado en servidor** y **código stupid que use objetos smart** (modelos/consultas claros), no nuevas abstracciones, archivos o herramientas.
