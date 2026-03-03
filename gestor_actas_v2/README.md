# GestorActas — Streamlit + Jinja2

Sistema de gestión de actas de proyecto con generación de reportes HTML.

## Estructura

```
gestor_actas/
├── app.py                     # App principal Streamlit
├── requirements.txt
├── actas.json                 # Persistencia automática (se crea al guardar)
└── templates/
    ├── base.html              # Plantilla base con estilos y layout
    ├── acta_inicio.html       # Acta de Inicio de Proyecto
    ├── acta_cierre.html       # Acta de Cierre de Proyecto
    └── acta_reunion.html      # Acta de Reunión
```

## Instalación y uso

```bash
# Instalar dependencias
pip install -r requirements.txt

# Correr la app
streamlit run app.py
```

La app queda disponible en http://localhost:8501

## Exportar a PDF (opcional)

### Opción A — WeasyPrint (recomendado, sin dependencias de sistema)
```bash
pip install weasyprint
```
Agrega en app.py donde quieras el botón PDF:
```python
from weasyprint import HTML as WeasyprintHTML

pdf_bytes = WeasyprintHTML(string=html_reporte).write_pdf()
st.download_button("Descargar PDF", data=pdf_bytes,
                   file_name="acta.pdf", mime="application/pdf")
```

### Opción B — pdfkit + wkhtmltopdf
```bash
pip install pdfkit
# Ubuntu/Debian:
sudo apt install wkhtmltopdf
# macOS:
brew install wkhtmltopdf
```
```python
import pdfkit
pdf_bytes = pdfkit.from_string(html_reporte, False)
```

## Personalizar plantillas

Las plantillas Jinja2 están en `templates/`. Cada acta extiende `base.html`.
Variables disponibles en todas las plantillas:
- `datos`            → dict con todos los campos del formulario
- `tipo`             → "inicio" | "cierre" | "reunion"
- `numero`           → ID del acta con padding (0001, 0002...)
- `fecha_generacion` → Fecha actual en formato largo
