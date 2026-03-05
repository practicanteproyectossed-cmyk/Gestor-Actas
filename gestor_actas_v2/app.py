import streamlit as st
import streamlit.components.v1 as components
from jinja2 import Environment, FileSystemLoader
from datetime import datetime, date
import json
import os
import base64
import locale
from uuid import uuid4


# intentar poner la localización en español para que strftime devuelva
# nombres de mes en español (Windows usa etiquetas como 'Spanish_Spain').
# si falla no importa, el texto quedará en inglés como antes.
for loc in ('es_ES.UTF-8','es_ES','Spanish_Spain','Spanish'):
    try:
        locale.setlocale(locale.LC_TIME, loc)
        break
    except locale.Error:
        continue


#  Intentar importar WeasyPrint 
try:
    from weasyprint import HTML as WeasyprintHTML
    WEASYPRINT_OK = True
except ImportError:
    WEASYPRINT_OK = False

#  Configuración de página 
st.set_page_config(
    page_title="Gestor de Actas",
    layout="wide",
    initial_sidebar_state="expanded",
)

#  CSS global 
st.markdown("""
<style>

/* 
   FUENTE
 */
@import url('https://fonts.googleapis.com/css2family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* 
   FONDO GENERAL CLARO
 */
.stApp {
    background-color: #f4f6f8 !important;
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

@keyframes pageFadeIn {
    from { opacity: 0; transform: translateY(4px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes elementRiseIn {
    from { opacity: 0; transform: translateY(6px) scale(0.995); }
    to { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes previewGlowIn {
    from { opacity: 0; transform: translateY(4px); box-shadow: 0 0 0 rgba(29,78,216,0); }
    to { opacity: 1; transform: translateY(0); box-shadow: 0 10px 24px rgba(15,23,42,0.08); }
}
.page-fade {
    animation: pageFadeIn 150ms ease-out;
}

/* Asegurar que los títulos sean oscuros en cualquier contexto */
h1, h2, h3, h4, h5, h6 {
    color: #1f2933 !important;
}

/* Asegurar que los títulos en el área principal sean oscuros también (redundante pero seguro) */
.main .block-container h1,
.main .block-container h2,
.main .block-container h3,
.main .block-container h4,
.main .block-container h5,
.main .block-container h6 {
    color: #1f2933 !important;
}

/* 
   SIDEBAR CORPORATIVO
 */

[data-testid="stSidebar"] {
    background:
      radial-gradient(120% 90% at 15% -10%, rgba(59,130,246,0.18) 0%, rgba(59,130,246,0) 45%),
      linear-gradient(180deg, #0b1220 0%, #0f1a2a 52%, #0c1522 100%) !important;
    border-right: 1px solid rgba(148,163,184,0.2) !important;
    box-shadow: 2px 0 22px rgba(2,6,23,0.35) !important;
    transition: width 0.28s ease, min-width 0.28s ease, transform 0.28s ease, box-shadow 0.28s ease !important;
    will-change: width, transform;
}

[data-testid="stSidebar"] > div:first-child {
    transition: width 0.28s ease, min-width 0.28s ease, transform 0.28s ease !important;
}

[data-testid="stSidebarUserContent"] {
    padding-top: 0 !important;
    transition: opacity 0.22s ease, transform 0.22s ease !important;
}

[data-testid="stSidebar"] .sidebar-logo-wrap {
    position: static;
    margin: 0 !important;
    margin-top: -32px !important;
    margin-bottom: 0.2rem !important;
}

[data-testid="stSidebar"] .sidebar-logo {
    width: 98px;
    height: auto;
    display: block;
    margin: 0;
}

[data-testid="stSidebar"] h1 {
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 1.6rem !important;
    margin-bottom: 0.5rem !important;
    padding-bottom: 0.5rem !important;
    border-bottom: 2px solid #1d4ed8 !important;
    letter-spacing: -0.01em !important;
}

[data-testid="stSidebar"] .stCaption {
    color: #aab7c7 !important;
    font-size: 0.75rem !important;
    margin-top: -0.2rem !important;
    margin-bottom: 1rem !important;
}

/* Textos generales del sidebar */
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {
    color: #d8e2ee !important;
}

[data-testid="stSidebar"] hr {
    border-color: rgba(148,163,184,0.28) !important;
    margin: 1.5rem 0 !important;
}

/*  BOTONES DEL SIDEBAR  */
[data-testid="stSidebar"] .stButton button,
[data-testid="stSidebar"] [data-testid="stButton"] button {
    border-radius: 6px !important;
    padding: 0.5rem 1rem !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
    text-align: left !important;
    border: 1px solid transparent;
}

[data-testid="stSidebar"] .stButton button[kind="secondary"],
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"] {
    background-color: rgba(255,255,255,0.07) !important;
    color: #e7eef8 !important;
    border: 1px solid rgba(148,163,184,0.35) !important;
}

[data-testid="stSidebar"] .stButton button[kind="secondary"]:hover,
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"]:hover {
    background-color: rgba(255,255,255,0.14) !important;
    color: #ffffff !important;
    border-color: rgba(191,219,254,0.55) !important;
    box-shadow: 0 4px 12px rgba(15,23,42,0.3) !important;
}

[data-testid="stSidebar"] .stButton button[kind="primary"],
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] {
    background-color: #1d4ed8 !important;
    color: white !important;
    border: 1px solid #1d4ed8 !important;
}

[data-testid="stSidebar"] .stButton button[kind="primary"]:hover,
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"]:hover {
    background-color: #1e40af !important;
    border-color: #1e40af !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
}

[data-testid="stSidebar"] .stMarkdown p {
    color: #e4e7eb !important;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

/* 
   TÍTULOS PRINCIPALES
 */
h1, h2, h3 {
    color: #1f2933 !important;
    font-weight: 600 !important;
}

/* Ocultar icono de ancla/enlace junto a títulos */
[data-testid="stHeaderActionElements"] {
    display: none !important;
}

/* 
   BOTONES GENERALES
 */
.stButton button,
[data-testid="stButton"] button {
    border-radius: 6px !important;
    font-weight: 500 !important;
    padding: 0.45rem 1rem !important;
    transition: transform 0.14s ease, box-shadow 0.18s ease, background-color 0.18s ease, border-color 0.18s ease !important;
}
.stButton button:active,
[data-testid="stButton"] button:active {
    transform: translateY(1px) scale(0.995);
}
.stButton button:focus-visible,
[data-testid="stButton"] button:focus-visible {
    outline: 2px solid rgba(29, 78, 216, 0.32) !important;
    outline-offset: 1px !important;
}

.stButton button[kind="primary"],
[data-testid="stButton"] button[kind="primary"] {
    background-color: #1d4ed8 !important;
    color: white !important;
    border: none !important;
}

.stButton button[kind="primary"]:hover,
[data-testid="stButton"] button[kind="primary"]:hover {
    background-color: #1e40af !important;
}

.stButton button[kind="secondary"],
[data-testid="stButton"] button[kind="secondary"] {
    background-color: white !important;
    border: 1px solid #cbd5e1 !important;
    color: #1f2933 !important;
}

.stButton button[kind="secondary"]:hover,
[data-testid="stButton"] button[kind="secondary"]:hover {
    background-color: #f1f5f9 !important;
}

/* 
   INPUTS
 */
.stTextInput input,
.stTextArea textarea,
.stSelectbox select,
.stDateInput input {
    border-radius: 6px !important;
    border: 1px solid #d1d5db !important;
    background-color: white !important;
    font-size: 0.9rem !important;
    color: #111827 !important;
    caret-color: #111827 !important;
    cursor: text !important;
    outline: none !important;
    box-shadow: none !important;
    transition: border-color 0.16s ease, box-shadow 0.16s ease !important;
}
.stTextInput input:focus,
.stTextArea textarea:focus,
.stDateInput input:focus {
    border-color: #93c5fd !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.14) !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: #cbd5e1 !important;
    border-width: 1px !important;
    outline: none !important;
    box-shadow: none !important;
}

/* BaseWeb (Streamlit moderno): quitar anillo morado y usar borde sutil */
[data-baseweb="input"],
[data-baseweb="textarea"],
[data-baseweb="select"] > div {
    color: #111827 !important;
    caret-color: #111827 !important;
    border-color: #d1d5db !important;
    box-shadow: none !important;
    outline: none !important;
}
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea,
[data-baseweb="input"] textarea {
    color: #111827 !important;
    caret-color: #111827 !important;
    cursor: text !important;
    -webkit-text-fill-color: #111827 !important;
}
.stTextInput input:hover,
.stTextInput input:focus,
.stTextInput input:active,
.stTextArea textarea:hover,
.stTextArea textarea:focus,
.stTextArea textarea:active,
[data-baseweb="input"] input:hover,
[data-baseweb="input"] input:focus,
[data-baseweb="input"] input:active,
[data-baseweb="textarea"] textarea:hover,
[data-baseweb="textarea"] textarea:focus,
[data-baseweb="textarea"] textarea:active {
    caret-color: #111827 !important;
    cursor: text !important;
    color: #111827 !important;
    -webkit-text-fill-color: #111827 !important;
    opacity: 1 !important;
}
[data-baseweb="input"]:focus-within,
[data-baseweb="textarea"]:focus-within,
[data-baseweb="select"] > div:focus-within {
    border-color: #cbd5e1 !important;
    border-width: 1px !important;
    box-shadow: none !important;
    outline: none !important;
}
.stTextInput input:focus-visible,
.stTextArea textarea:focus-visible,
.stDateInput input:focus-visible {
    outline: none !important;
    box-shadow: none !important;
    border-color: #cbd5e1 !important;
    border-width: 1px !important;
}
/* DateInput: suavizar segmento derecho (icono/calendario) */
[data-testid="stDateInput"] [data-baseweb="input"] {
    background: #ffffff !important;
    border: 1px solid #d1d5db !important;
    box-shadow: none !important;
}
[data-testid="stDateInput"] [data-baseweb="input"] > div {
    background: #ffffff !important;
}
[data-testid="stDateInput"] [data-baseweb="input"] [role="button"],
[data-testid="stDateInput"] [data-baseweb="input"] button {
    background-color: #d1d5db !important;
    border-left: 1px solid #cbd5e1 !important;
    color: #64748b !important;
    box-shadow: none !important;
}
[data-testid="stDateInput"] [data-baseweb="input"] [role="button"] *,
[data-testid="stDateInput"] [data-baseweb="input"] button * {
    background-color: #d1d5db !important;
}
[data-testid="stDateInput"] [data-baseweb="input"] [role="button"]:hover,
[data-testid="stDateInput"] [data-baseweb="input"] button:hover {
    background-color: #cbd5e1 !important;
    color: #475569 !important;
}
[data-testid="stDateInput"] [data-baseweb="input"] [role="button"]:hover *,
[data-testid="stDateInput"] [data-baseweb="input"] button:hover * {
    background-color: #cbd5e1 !important;
}
[data-testid="stDateInput"] button svg,
[data-testid="stDateInput"] [role="button"] svg,
[data-testid="stDateInput"] [data-testid="stIconMaterial"] {
    color: #64748b !important;
    fill: #64748b !important;
}
/* Fallback para navegadores con indicador nativo de fecha */
[data-testid="stDateInput"] input::-webkit-calendar-picker-indicator {
    filter: grayscale(100%) brightness(65%) !important;
    opacity: 0.8 !important;
}

/* Navegador (Chrome/Edge): evitar fondo oscuro al previsualizar/autocompletar sugerencias */
input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus,
textarea:-webkit-autofill,
textarea:-webkit-autofill:hover,
textarea:-webkit-autofill:focus {
    -webkit-text-fill-color: #111827 !important;
    -webkit-box-shadow: 0 0 0 1000px #ffffff inset !important;
    box-shadow: 0 0 0 1000px #ffffff inset !important;
    border: 1px solid #e5e7eb !important;
    transition: background-color 9999s ease-out 0s !important;
}

/* Input de búsqueda (Mis Actas): estilo limpio */
div[class*="st-key-busqueda_mis_actas"] [data-baseweb="input"] {
    border: 1px solid #d1d5db !important;
    border-radius: 8px !important;
    box-shadow: none !important;
    background: #ffffff !important;
}
div[class*="st-key-busqueda_mis_actas"] [data-baseweb="input"]:focus-within {
    border: 1px solid #cbd5e1 !important;
    box-shadow: none !important;
}
/* Selects puntuales (Nueva Acta + Mis Actas): campo cerrado en claro */
div[class*="st-key-tipo_acta_select"] [data-baseweb="select"],
div[class*="st-key-filtro_mis_actas_ui_select"] [data-baseweb="select"],
div[class*="st-key-orden_mis_actas"] [data-baseweb="select"] {
    color-scheme: light !important;
}
div[class*="st-key-tipo_acta_select"] [data-baseweb="select"] > div,
div[class*="st-key-filtro_mis_actas_ui_select"] [data-baseweb="select"] > div,
div[class*="st-key-orden_mis_actas"] [data-baseweb="select"] > div {
    background: #ffffff !important;
    color: #111827 !important;
    border-color: #d1d5db !important;
}
div[class*="st-key-tipo_acta_select"] [data-baseweb="select"] [role="combobox"],
div[class*="st-key-filtro_mis_actas_ui_select"] [data-baseweb="select"] [role="combobox"],
div[class*="st-key-orden_mis_actas"] [data-baseweb="select"] [role="combobox"],
div[class*="st-key-tipo_acta_select"] [data-baseweb="select"] [role="button"],
div[class*="st-key-filtro_mis_actas_ui_select"] [data-baseweb="select"] [role="button"],
div[class*="st-key-orden_mis_actas"] [data-baseweb="select"] [role="button"],
div[class*="st-key-tipo_acta_select"] [data-baseweb="select"] [aria-haspopup="listbox"],
div[class*="st-key-filtro_mis_actas_ui_select"] [data-baseweb="select"] [aria-haspopup="listbox"],
div[class*="st-key-orden_mis_actas"] [data-baseweb="select"] [aria-haspopup="listbox"] {
    background: #ffffff !important;
    color: #111827 !important;
    border-color: #d1d5db !important;
    box-shadow: none !important;
}
div[class*="st-key-tipo_acta_select"] [data-baseweb="select"] [role="combobox"]:focus,
div[class*="st-key-filtro_mis_actas_ui_select"] [data-baseweb="select"] [role="combobox"]:focus,
div[class*="st-key-orden_mis_actas"] [data-baseweb="select"] [role="combobox"]:focus,
div[class*="st-key-tipo_acta_select"] [data-baseweb="select"] [role="button"]:focus,
div[class*="st-key-filtro_mis_actas_ui_select"] [data-baseweb="select"] [role="button"]:focus,
div[class*="st-key-orden_mis_actas"] [data-baseweb="select"] [role="button"]:focus {
    border-color: #cbd5e1 !important;
    box-shadow: none !important;
    outline: none !important;
}
/* Menu desplegable (portal) en claro */
div[role="listbox"],
li[role="option"],
[data-baseweb="menu"] [role="option"] {
    background: #ffffff !important;
    color: #111827 !important;
}
div[role="listbox"] [role="option"][aria-selected="true"],
li[role="option"][aria-selected="true"],
[data-baseweb="menu"] [role="option"][aria-selected="true"] {
    background: #eaf2ff !important;
    color: #1d4ed8 !important;
}

.stTextInput label,
.stTextArea label,
.stSelectbox label,
.stDateInput label {
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    color: #475569 !important;
}

.main .block-container p,
.main .block-container li {
    line-height: 1.5 !important;
}

/* 
   DOWNLOAD BUTTON
 */
.stDownloadButton button,
[data-testid="stDownloadButton"] button {
    background: #0f172a !important;
    color: white !important;
    border-radius: 6px !important;
    border: none !important;
}

.stDownloadButton button:hover,
[data-testid="stDownloadButton"] button:hover {
    background: #1e293b !important;
}

/* 
   DIVISORES
 */
hr {
    border-color: #e2e8f0 !important;
}

/* 
   BADGES
 */
.badge {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
}

.badge-inicio_requerimiento { background: #dbeafe; color: #1d4ed8; }
.badge-inicio  { background: #dbeafe; color: #1d4ed8; }
.badge-cierre  { background: #fee2e2; color: #dc2626; }
.badge-cierre_proyecto { background: #ffedd5; color: #c2410c; }
.badge-reunion { background: #dcfce7; color: #15803d; }

.acta-card-head {
    border-left: 4px solid transparent;
    padding-left: 10px;
    margin-bottom: 10px;
}
.acta-card-head.accent-inicio_requerimiento { border-left-color: #1d4ed8; }
.acta-card-head.accent-cierre { border-left-color: #dc2626; }
.acta-card-head.accent-cierre_proyecto { border-left-color: #c2410c; }
.acta-card-head.accent-reunion { border-left-color: #15803d; }
.acta-meta-row {
    display: flex;
    gap: 6px;
    align-items: center;
    margin-bottom: 6px;
    flex-wrap: wrap;
}
.meta-chip {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 600;
    line-height: 1.35;
    border: 1px solid #cbd5e1;
    background: #f8fafc;
    color: #334155;
}
.acta-card-shell {
    padding: 0.25rem 0.1rem 0.05rem 0.1rem;
    transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
    border-radius: 10px;
    animation: elementRiseIn 170ms ease-out both;
}
.acta-card-shell:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 18px rgba(15, 23, 42, 0.08);
}
.acta-card-title {
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: -0.01em;
    color: #0f172a;
}
.empty-state-card {
    border: 1px dashed #cbd5e1;
    border-radius: 12px;
    background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    padding: 1.2rem 1rem;
    text-align: center;
    color: #334155;
}
.empty-state-card .icon {
    font-size: 1.15rem;
    opacity: 0.8;
    margin-bottom: 0.3rem;
}
.empty-state-card .title {
    font-size: 0.98rem;
    font-weight: 600;
    margin-bottom: 0.2rem;
}
.empty-state-card .desc {
    font-size: 0.86rem;
    color: #64748b;
}

div[class*="st-key-edit_"] .stButton button,
div[class*="st-key-edit_"] [data-testid="stButton"] button,
div[class*="st-key-ver_"] .stButton button,
div[class*="st-key-ver_"] [data-testid="stButton"] button,
div[class*="st-key-del_"] .stButton button,
div[class*="st-key-del_"] [data-testid="stButton"] button,
div[class*="st-key-dl_html_"] .stDownloadButton button,
div[class*="st-key-dl_html_"] [data-testid="stDownloadButton"] button,
div[class*="st-key-dl_pdf_"] .stDownloadButton button,
div[class*="st-key-dl_pdf_"] [data-testid="stDownloadButton"] button {
    height: 34px !important;
    border-radius: 8px !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.01em;
    transition: transform 0.16s ease, box-shadow 0.16s ease, background-color 0.16s ease, border-color 0.16s ease !important;
}
div[class*="st-key-edit_"] .stButton button:hover,
div[class*="st-key-edit_"] [data-testid="stButton"] button:hover,
div[class*="st-key-ver_"] .stButton button:hover,
div[class*="st-key-ver_"] [data-testid="stButton"] button:hover,
div[class*="st-key-dl_html_"] .stDownloadButton button:hover,
div[class*="st-key-dl_html_"] [data-testid="stDownloadButton"] button:hover,
div[class*="st-key-dl_pdf_"] .stDownloadButton button:hover,
div[class*="st-key-dl_pdf_"] [data-testid="stDownloadButton"] button:hover {
    transform: translateY(-1px);
    box-shadow: 0 5px 14px rgba(15, 23, 42, 0.12) !important;
}

div[class*="st-key-del_"] .stButton button,
div[class*="st-key-del_"] [data-testid="stButton"] button {
    background-color: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #cbd5e1 !important;
    transition: background-color 0.55s ease-in-out, color 0.55s ease-in-out, border-color 0.55s ease-in-out, box-shadow 0.55s ease-in-out, transform 0.55s ease-in-out !important;
}
div[class*="st-key-del_"] .stButton button[kind="secondary"],
div[class*="st-key-del_"] [data-testid="stButton"] button[kind="secondary"],
div[class*="st-key-del_"] .stButton button:focus,
div[class*="st-key-del_"] [data-testid="stButton"] button:focus,
div[class*="st-key-del_"] .stButton button:active,
div[class*="st-key-del_"] [data-testid="stButton"] button:active {
    background-color: #ffffff !important;
    color: #111827 !important;
    border-color: #cbd5e1 !important;
}
div[class*="st-key-del_"] .stButton button:hover,
div[class*="st-key-del_"] [data-testid="stButton"] button:hover {
    background-color: #dc2626 !important;
    color: #ffffff !important;
    border-color: #dc2626 !important;
    box-shadow: 0 4px 12px rgba(220, 38, 38, 0.25) !important;
    transform: translateY(-1px);
}
div[class*="st-key-del_"] button[kind="secondary"]:hover,
div[class*="st-key-del_"] button:hover {
    background-color: #dc2626 !important;
    color: #ffffff !important;
    border-color: #dc2626 !important;
    box-shadow: 0 4px 12px rgba(220, 38, 38, 0.25) !important;
}

div[class*="st-key-dl_html_"] .stDownloadButton button,
div[class*="st-key-dl_html_"] [data-testid="stDownloadButton"] button {
    white-space: nowrap !important;
    font-size: 0.74rem !important;
    padding: 0.4rem 0.62rem !important;
}

div[class*="st-key-dl_html_prev_"],
div[class*="st-key-dl_pdf_prev_"],
div[class*="st-key-close_prev_"] {
    position: sticky;
    top: 0.45rem;
    z-index: 12;
    padding-top: 0.2rem;
    background: #f4f6f8;
}

div[class*="st-key-close_prev_lista"] .stButton button,
div[class*="st-key-close_prev_lista"] [data-testid="stButton"] button {
    white-space: nowrap !important;
    min-width: max-content !important;
    margin-right: 0.12rem !important;
}

div[class*="st-key-dl_pdf_prev_lista_"] .stDownloadButton button,
div[class*="st-key-dl_pdf_prev_lista_"] [data-testid="stDownloadButton"] button {
    margin-left: 0.12rem !important;
}

/* 
   PREVIEW WRAPPER
 */
.preview-wrap {
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    overflow: hidden;
    background: white;
    margin-top: 16px;
    animation: previewGlowIn 190ms ease-out both;
}

/* Ocultar menú Streamlit */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }

/* 
   BOTN DE COLAPSO  SOLUCIN DEFINITIVA
 */

/* Forzar visibilidad permanente en todos los niveles */
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebarCollapseButton"] span {
    visibility: visible !important;
    opacity: 1 !important;
    display: inline-flex !important;
}

/* Color blanco  sidebar abierto, fondo oscuro */
[data-testid="stSidebarCollapseButton"] span[data-testid="stIconMaterial"] {
    color: #ffffff !important;
}

/*  Para el botón que aparece cuando el sidebar está CERRADO  */
/* Streamlit usa stSidebarCollapsedControl cuando está cerrado   */
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarCollapsedControl"] button,
[data-testid="stSidebarCollapsedControl"] span {
    visibility: visible !important;
    opacity: 1 !important;
    display: inline-flex !important;
}

[data-testid="stSidebarCollapsedControl"] span[data-testid="stIconMaterial"] {
    color: #000000 !important;
}

</style>
""", unsafe_allow_html=True)

#  Jinja2 
env = Environment(loader=FileSystemLoader(
    os.path.join(os.path.dirname(__file__), "templates")
))

def _normalizar_tipo(tipo: str) -> str:
    return "inicio_requerimiento" if tipo == "inicio_clasica" else tipo

def _fecha_es_capitalizada(fecha: datetime) -> str:
    meses_es = (
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
    )
    mes = meses_es[fecha.month - 1]
    return f"{fecha.day:02d} de {mes} de {fecha.year}"

@st.cache_data(show_spinner=False)
def obtener_logo_data_uri() -> str:
    """Carga el logo desde static y lo devuelve como data URI para HTML/PDF."""
    logo_path = os.path.join(os.path.dirname(__file__), "static", "SED Normal.jpg")
    if not os.path.exists(logo_path):
        return ""
    with open(logo_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"

def _templates_fingerprint() -> tuple:
    """Firma liviana de templates para invalidar caché al editar HTML."""
    tpl_dir = os.path.join(os.path.dirname(__file__), "templates")
    firma = []
    try:
        for nombre in sorted(os.listdir(tpl_dir)):
            if not nombre.endswith(".html"):
                continue
            ruta = os.path.join(tpl_dir, nombre)
            try:
                firma.append((nombre, int(os.path.getmtime(ruta))))
            except OSError:
                continue
    except OSError:
        return tuple()
    return tuple(firma)

@st.cache_data(show_spinner=False)
def _renderizar_acta_cache(
    tipo: str,
    datos_json: str,
    fecha_generacion: str,
    numero: str,
    templates_fp: tuple,
) -> str:
    datos = json.loads(datos_json)
    if tipo == "cierre":
        tpl_name = "acta_cierre_requerimiento.html"
    elif tipo == "cierre_proyecto":
        tpl_name = "acta_cierre_proyecto.html"
    elif tipo == "reunion":
        tpl_name = "acta_reunion.html"
    elif tipo == "inicio_requerimiento":
        tpl_name = "acta_inicio_requerimiento.html"
    else:
        tpl_name = f"acta_{tipo}.html"
    tpl = env.get_template(tpl_name)
    return tpl.render(
        datos=datos,
        tipo=tipo,
        fecha_generacion=fecha_generacion,
        numero=numero,
        logo_data_uri=obtener_logo_data_uri(),
    )

def renderizar_acta(tipo: str, datos: dict) -> str:
    """Renderiza la plantilla Jinja2 y devuelve HTML como string."""
    tipo_norm = _normalizar_tipo(tipo)
    return _renderizar_acta_cache(
        tipo=tipo_norm,
        datos_json=json.dumps(datos, ensure_ascii=False, sort_keys=True),
        fecha_generacion=_fecha_es_capitalizada(datetime.now()),
        numero=str(datos.get("id", 1)).zfill(4),
        templates_fp=_templates_fingerprint(),
    )

@st.cache_data(show_spinner=False)
def html_a_pdf(html: str) -> bytes:
    """Convierte HTML renderizado por Jinja2 a PDF usando WeasyPrint.
    Utiliza la carpeta `static` como base_url para resolver recursos.
    """
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    return WeasyprintHTML(string=html, base_url=static_dir).write_pdf()

#  Persistencia en JSON 
DATOS_FILE = os.path.join(os.path.dirname(__file__), "actas.json")

def cargar_actas():
    if os.path.exists(DATOS_FILE):
        with open(DATOS_FILE, "r", encoding="utf-8") as f:
            actas = json.load(f)
        # migración de tipo antiguo
        for a in actas:
            if a.get("tipo") == "inicio_clasica":
                a["tipo"] = "inicio_requerimiento"
        return actas
    return []

def guardar_actas(actas):
    with open(DATOS_FILE, "w", encoding="utf-8") as f:
        json.dump(actas, f, ensure_ascii=False, indent=2)

def _sanear_actas(actas: list[dict]) -> bool:
    """
    Corrige datos heredados para evitar colisiones:
    - asegura uid único por acta (para keys de widgets)
    - normaliza tipo antiguo
    - repara IDs inválidos o duplicados
    """
    changed = False
    usados_uid = set()
    usados_id = set()
    max_id = 0

    # calcular máximo id válido existente
    for a in actas:
        aid = a.get("id")
        if isinstance(aid, int) and aid > max_id:
            max_id = aid

    for a in actas:
        if a.get("tipo") == "inicio_clasica":
            a["tipo"] = "inicio_requerimiento"
            changed = True

        uid = str(a.get("uid", "")).strip()
        if not uid or uid in usados_uid:
            a["uid"] = uuid4().hex
            changed = True
        usados_uid.add(a["uid"])

        aid = a.get("id")
        if not isinstance(aid, int) or aid <= 0 or aid in usados_id:
            max_id += 1
            a["id"] = max_id
            changed = True
        usados_id.add(a["id"])

    return changed

#  Helper: dos botones de descarga 
def botones_descarga(html: str, tipo: str, acta_id: int, key_suffix: str, close_key: str | None = None) -> bool:
    """
    Muestra botones en una fila:
      - Descargar HTML  (siempre disponible, Jinja2)
      - Descargar PDF   (requiere WeasyPrint)
      - Cerrar vista previa (opcional)
    """
    nombre_base = f"acta_{tipo}_{str(acta_id).zfill(4)}"
    cerrada = False
    col_html, col_pdf, col_close, _ = st.columns([1.3, 1.3, 1.0, 3.4])

    # HTML
    col_html.download_button(
        label     = "Descargar HTML",
        data      = html,
        file_name = f"{nombre_base}.html",
        mime      = "text/html",
        key       = f"dl_html_{key_suffix}",
    )

    # PDF
    if WEASYPRINT_OK:
        try:
            pdf_bytes = html_a_pdf(html)
            col_pdf.download_button(
                label     = "Descargar PDF",
                data      = pdf_bytes,
                file_name = f"{nombre_base}.pdf",
                mime      = "application/pdf",
                key       = f"dl_pdf_{key_suffix}",
            )
        except Exception as e:
            set_feedback("error", "No se pudo generar el PDF", ":material/error:")
            col_pdf.warning(f"Error PDF: {e}")
    else:
        col_pdf.info("PDF: `pip install weasyprint`")

    if close_key:
        cerrada = col_close.button("Cerrar", key=close_key, use_container_width=True, help="Cerrar vista previa")

    return cerrada

def cerrar_preview():
    st.session_state.preview_html = None
    st.session_state.preview_datos = {}

def set_feedback(kind: str, message: str, icon: str = ":material/info:"):
    st.session_state.flash = {"kind": kind, "message": message, "icon": icon}

def render_feedback():
    flash = st.session_state.get("flash")
    if not flash:
        return

    kind = flash.get("kind", "info")
    message = flash.get("message", "")
    icon = flash.get("icon", ":material/info:")
    fn = {
        "success": st.success,
        "warning": st.warning,
        "error": st.error,
        "info": st.info,
    }.get(kind, st.info)
    fn(message, icon=icon)
    st.session_state.flash = None

def render_control_vinetas_js():
    components.html(
        """
        <div style="display:flex; justify-content:flex-start; margin-top:0.1rem;">
          <button id="vineta-toggle-btn" type="button" aria-pressed="false"
            style="
              width:138px;
              height:34px;
              border-radius:6px;
              border:1px solid rgba(148,163,184,0.35);
              background:rgba(255,255,255,0.07);
              color:#e7eef8;
              font:500 13px Inter, sans-serif;
              cursor:pointer;
              display:inline-flex;
              align-items:center;
              justify-content:center;
              gap:6px;
              transition:all .2s ease;
            ">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <circle cx="5.5" cy="7" r="1.5" fill="currentColor"></circle>
              <circle cx="5.5" cy="12" r="1.5" fill="currentColor"></circle>
              <circle cx="5.5" cy="17" r="1.5" fill="currentColor"></circle>
              <rect x="8.5" y="6" width="10" height="2" rx="1" fill="currentColor"></rect>
              <rect x="8.5" y="11" width="10" height="2" rx="1" fill="currentColor"></rect>
              <rect x="8.5" y="16" width="10" height="2" rx="1" fill="currentColor"></rect>
            </svg>
            <span id="vineta-label">Vi&ntilde;eta OFF</span>
          </button>
        </div>
        <script>
          (() => {
            const doc = window.parent.document;
            const btn = document.getElementById("vineta-toggle-btn");
            const label = document.getElementById("vineta-label");
            if (!doc || !btn || !label) return;

            if (!window.parent.__gestorVineta) {
              window.parent.__gestorVineta = {
                active: false,
                lastTextarea: null,
                initialized: false
              };
            }
            const state = window.parent.__gestorVineta;
            const BULLET = "\\u2022\\u00A0\\u00A0";

            function setTextareaValue(el, value, caretPos) {
              const setter = Object.getOwnPropertyDescriptor(
                window.parent.HTMLTextAreaElement.prototype,
                "value"
              )?.set;
              if (setter) setter.call(el, value);
              else el.value = value;
              if (typeof caretPos === "number") {
                el.selectionStart = caretPos;
                el.selectionEnd = caretPos;
              }
              el.dispatchEvent(new Event("input", { bubbles: true }));
            }

            function insertAtCursor(el, text) {
              const start = el.selectionStart ?? el.value.length;
              const end = el.selectionEnd ?? start;
              const next = el.value.slice(0, start) + text + el.value.slice(end);
              setTextareaValue(el, next, start + text.length);
              el.focus({ preventScroll: true });
            }

            function insertBullet(el, prependNewline) {
              if (!(el instanceof window.parent.HTMLTextAreaElement)) return;
              const insert = (prependNewline ? "\\n" : "") + BULLET;
              insertAtCursor(el, insert);
            }

            function updateButton() {
              label.textContent = state.active ? "Vi\\u00f1eta ON" : "Vi\\u00f1eta OFF";
              btn.setAttribute("aria-pressed", state.active ? "true" : "false");
              btn.style.background = state.active ? "rgba(29,78,216,0.22)" : "rgba(255,255,255,0.07)";
              btn.style.borderColor = state.active ? "rgba(147,197,253,0.9)" : "rgba(148,163,184,0.35)";
              btn.style.boxShadow = state.active ? "0 0 0 1px rgba(147,197,253,0.35) inset" : "none";
            }

            function rememberTarget(ev) {
              if (!(ev.target instanceof Element)) return;
              const t = ev.target.closest("textarea");
              if (t instanceof window.parent.HTMLTextAreaElement) {
                state.lastTextarea = t;
              }
            }

            function handleEnter(ev) {
              if (!state.active || ev.key !== "Enter" || ev.shiftKey) return;
              const t = ev.target;
              if (!(t instanceof window.parent.HTMLTextAreaElement)) return;
              ev.preventDefault();
              insertBullet(t, true);
            }

            if (!state.initialized) {
              doc.addEventListener("focusin", rememberTarget, true);
              doc.addEventListener("click", rememberTarget, true);
              doc.addEventListener("keydown", handleEnter, true);
              state.initialized = true;
            }

            btn.addEventListener("mousedown", (ev) => ev.preventDefault());
            btn.addEventListener("click", (ev) => {
              ev.preventDefault();
              const active = doc.activeElement;
              if (active instanceof window.parent.HTMLTextAreaElement) {
                state.lastTextarea = active;
              }
              state.active = !state.active;
              updateButton();
              if (state.active && state.lastTextarea instanceof window.parent.HTMLTextAreaElement) {
                insertBullet(state.lastTextarea, false);
              }
            });

            updateButton();
          })();
        </script>
        """,
        height=50,
    )

if "actas"         not in st.session_state: st.session_state.actas         = cargar_actas()
if "preview_html"  not in st.session_state: st.session_state.preview_html  = None
if "preview_datos" not in st.session_state: st.session_state.preview_datos = {}
if "pagina"        not in st.session_state: st.session_state.pagina        = "nueva"
if "acta_editando" not in st.session_state: st.session_state.acta_editando = None
if "borradores"    not in st.session_state: st.session_state.borradores    = {}
if "filtro_mis_actas" not in st.session_state: st.session_state.filtro_mis_actas = "Todas"
if "flash"         not in st.session_state: st.session_state.flash         = None
if "page_transition" not in st.session_state: st.session_state.page_transition = False
# migrar selección de tipo antigua (antes: inicio_clasica)
if st.session_state.get("tipo_seleccionado") == "inicio_clasica":
    st.session_state.tipo_seleccionado = "inicio_requerimiento"
if _sanear_actas(st.session_state.actas):
    guardar_actas(st.session_state.actas)

TIPOS = {
    "inicio_requerimiento": {"label": "Acta de Inicio de Requerimiento", "color": "#d71920"},
    # hay ahora dos variantes de cierre (requerimiento y proyecto)
    "cierre": {"label": "Acta de Cierre de Requerimiento", "color": "#c23b2e"},
    "cierre_proyecto": {"label": "Acta de Cierre de Proyecto", "color": "#c23b2e"},
    "reunion": {"label": "Acta de Reunión", "color": "#1e7a4e"},
}

#  SIDEBAR 
with st.sidebar:
    sidebar_logo = os.path.join(os.path.dirname(__file__), "static", "SED sin fondo.png")
    if os.path.exists(sidebar_logo):
        with open(sidebar_logo, "rb") as f:
            sidebar_logo_b64 = base64.b64encode(f.read()).decode("utf-8")
        st.markdown(
            f'<div class="sidebar-logo-wrap"><img src="data:image/png;base64,{sidebar_logo_b64}" class="sidebar-logo"></div>',
            unsafe_allow_html=True,
        )

    st.markdown("# Gestor Actas")
    st.caption("Sistema Documental")
    
    st.divider()

    st.markdown("**Navegación**")
    if st.button("Nueva Acta", use_container_width=True,
                 type="primary" if st.session_state.pagina == "nueva" else "secondary"):
        cerrar_preview()
        st.session_state.page_transition = st.session_state.pagina != "nueva"
        st.session_state.pagina = "nueva"
        st.session_state.acta_editando = None
        st.rerun()

    total = len(st.session_state.actas)
    if st.button(f"Mis Actas ({total})" if total else "Mis Actas", use_container_width=True,
                 type="primary" if st.session_state.pagina == "lista" else "secondary"):
        cerrar_preview()
        st.session_state.page_transition = st.session_state.pagina != "lista"
        st.session_state.pagina = "lista"
        st.rerun()

    st.divider()
    st.markdown("**Acceso rápido**")
    for tid, tinfo in TIPOS.items():
        if st.button(tinfo["label"], use_container_width=True, key=f"sb_{tid}"):
            cerrar_preview()
            st.session_state.page_transition = st.session_state.pagina != "nueva"
            st.session_state.pagina           = "nueva"
            st.session_state.tipo_seleccionado = tid
            st.session_state.acta_editando    = None
            st.rerun()

    st.divider()
    st.markdown("**Herramientas**")
    if st.session_state.pagina == "nueva":
        render_control_vinetas_js()

render_feedback()

page_fade_class = "page-fade" if st.session_state.page_transition else ""
st.markdown(f'<div class="{page_fade_class}">', unsafe_allow_html=True)


# 
# PÁGINA: NUEVA / EDITAR ACTA
# 
if st.session_state.pagina == "nueva":

    editando      = st.session_state.acta_editando
    datos_previos = editando["data"] if editando else {}

    st.markdown("## " + ("Editar Acta" if editando else "Nueva Acta"))

    tipos_disponibles = list(TIPOS.keys())
    if editando:
        tipo_default = editando["tipo"]
        st.session_state.tipo_acta_select = tipo_default
    else:
        tipo_default = st.session_state.get("tipo_acta_select") or st.session_state.get("tipo_seleccionado", tipos_disponibles[0])
        if st.session_state.get("tipo_acta_select") is None:
            st.session_state.tipo_acta_select = tipo_default
    tipo = st.selectbox(
        "Tipo de acta",
        tipos_disponibles,
        index=tipos_disponibles.index(tipo_default),
        format_func=lambda x: TIPOS[x]["label"],
        key="tipo_acta_select",
        disabled=bool(editando),
    )
    if not editando:
        st.session_state.tipo_seleccionado = tipo
        datos_previos = st.session_state.borradores.get(tipo, {})
    if st.session_state.preview_html and st.session_state.preview_datos.get("tipo") != tipo:
        cerrar_preview()

    st.divider()
    datos = {}


    #  INICIO (clásica) 
    if tipo == "inicio_requerimiento":
        st.markdown("## Acta de Inicio de Requerimiento")

        # sección 1: información general
        st.markdown("#### 1. Información General")
        col1, col2 = st.columns(2)
        datos["cl_nombreRequerimiento"] = col1.text_input("Nombre del Requerimiento",  value=datos_previos.get("cl_nombreRequerimiento",""))
        datos["cl_areasSolicitantes"]   = col2.text_input("Áreas Solicitantes",       value=datos_previos.get("cl_areasSolicitantes",""))

        col1, col2 = st.columns(2)
        datos["cl_tipoRequerimiento"]   = col1.text_input("Tipo de Requerimiento",     value=datos_previos.get("cl_tipoRequerimiento",""))
        fe_val = datos_previos.get("cl_fechaElaboracion", "")
        fe_date = datetime.strptime(fe_val, "%d/%m/%Y").date() if fe_val else date.today()
        datos["cl_fechaElaboracion"] = col2.date_input("Fecha de Elaboración", value=fe_date, format="DD/MM/YYYY").strftime("%d/%m/%Y")

        col1, col2 = st.columns(2)
        datos["cl_responsableFuncional"]  = col1.text_input("Responsable Funcional",      value=datos_previos.get("cl_responsableFuncional",""))
        datos["cl_liderRequerimiento"]    = col2.text_input("Líder del Requerimiento",    value=datos_previos.get("cl_liderRequerimiento",""))
        datos["cl_responsableTecnico"]    = st.text_input("Responsable Técnico",       value=datos_previos.get("cl_responsableTecnico",""))

        # sección 2
        st.markdown("#### 2. Antecedentes y Justificación")
        datos["cl_antecedentesJustificacion"] = st.text_area(
            "",
            value=datos_previos.get("cl_antecedentesJustificacion",""),
            height=120,
            key="ia_cl_ant_just"
        )

        # sección 3
        st.markdown("#### 3. Objetivo del Requerimiento")
        datos["cl_objetivoRequerimiento"] = st.text_area(
            "",
            value=datos_previos.get("cl_objetivoRequerimiento",""),
            height=100,
            key="ia_cl_obj_req"
        )

        # sección 4
        st.markdown("#### 4. Alcance del Proyecto")
        datos["cl_alcanceProyecto"] = st.text_area(
            "",
            value=datos_previos.get("cl_alcanceProyecto",""),
            height=100,
            key="ia_cl_alc_proy"
        )

        # sección 5
        st.markdown("#### 5. Alcance Funcional")
        datos["cl_alcance_5"] = st.text_area(
            "",
            value=datos_previos.get("cl_alcance_5",""),
            height=120,
            key="ia_cl_alc_5"
        )

        # secciones 6 a 11
        st.markdown("#### 6. Vistas por Rol")
        datos["cl_vistasPorRol"] = st.text_area("", value=datos_previos.get("cl_vistasPorRol",""), height=80, key="ia_cl_vistasRol")
        st.markdown("#### 7. Medición y Control")
        datos["cl_medicionControl"] = st.text_area("", value=datos_previos.get("cl_medicionControl",""), height=80, key="ia_cl_med_control")
        st.markdown("#### 8. Notificaciones Automáticas")
        datos["cl_notificaciones"] = st.text_area("", value=datos_previos.get("cl_notificaciones",""), height=80, key="ia_cl_notificaciones")
        st.markdown("#### 9. Trazabilidad y Auditoría")
        datos["cl_trazabilidadAuditoria"] = st.text_area("", value=datos_previos.get("cl_trazabilidadAuditoria",""), height=80, key="ia_cl_traz_aud")
        st.markdown("#### 10. Alcance Técnico")
        datos["cl_alcanceTecnico"] = st.text_area("", value=datos_previos.get("cl_alcanceTecnico",""), height=80, key="ia_cl_alc_tecnico")
        st.markdown("#### 11. Exclusiones")
        datos["cl_exclusiones"] = st.text_area("", value=datos_previos.get("cl_exclusiones",""), height=80, key="ia_cl_exclusiones")


    #  CIERRE 
    elif tipo == "cierre":
        st.markdown("## Acta de Cierre de Requerimiento")

        # Información general
        st.markdown("#### Información General")
        col1, col2 = st.columns(2)
        datos["nombreRequerimiento"]   = col1.text_input("Nombre del Requerimiento", value=datos_previos.get("nombreRequerimiento",""))
        datos["solicitadoPor"]         = col2.text_input("Solicitado por",            value=datos_previos.get("solicitadoPor",""))

        col1, col2 = st.columns(2)
        datos["areaSolicitante"]       = col1.text_input("Área Solicitante",          value=datos_previos.get("areaSolicitante",""))
        fe_val = datos_previos.get("fechaEntrega", "")
        fe_date = datetime.strptime(fe_val, "%d/%m/%Y").date() if fe_val else date.today()
        datos["fechaEntrega"]          = col2.date_input("Fecha de Entrega",        value=fe_date, format="DD/MM/YYYY").strftime("%d/%m/%Y")

        datos["ejecutorRequerimiento"] = st.text_input("Ejecutor del Requerimiento", value=datos_previos.get("ejecutorRequerimiento",""))

        # Objetivo
        st.markdown("#### Objetivo del Requerimiento")
        datos["objetivoCierre"] = st.text_area("", value=datos_previos.get("objetivoCierre",""), height=100, key="ocierre")

        # Desarrollo
        st.markdown("#### Desarrollo del Requerimiento")
        datos["desarrolloRequerimiento"] = st.text_area("", value=datos_previos.get("desarrolloRequerimiento",""), height=120, key="desarrollo_req")

        # Entregables
        st.markdown("#### Entregables")
        datos["entregablesCierre"] = st.text_area("", value=datos_previos.get("entregablesCierre",""), height=100, key="entregables_cierre")

        # Lecciones aprendidas
        st.markdown("#### Lecciones Aprendidas")
        datos["leccionesAprendidas"] = st.text_area("", value=datos_previos.get("leccionesAprendidas",""), height=100, key="lecciones_cierre")

        # firmas de aprobación
        st.markdown("#### Firmas de Aprobación")
        col1, col2 = st.columns(2)
        datos["firmaGerente"] = col1.text_input("Gerente de Proyecto", value=datos_previos.get("firmaGerente",""))
        datos["firmaCliente"] = col2.text_input("Cliente / Patrocinador", value=datos_previos.get("firmaCliente",""))

    #  CIERRE PROYECTO 
    elif tipo == "cierre_proyecto":
        st.markdown("## Acta de Cierre de Proyecto")

        # Información general
        st.markdown("#### Información General")
        col1, col2 = st.columns(2)
        datos["empresa"]           = col1.text_input("Empresa",               value=datos_previos.get("empresa",""))
        datos["proyecto"]          = col2.text_input("Proyecto",              value=datos_previos.get("proyecto",""))

        col1, col2 = st.columns(2)
        datos["liderProyecto"]     = col1.text_input("Líder de Proyecto",     value=datos_previos.get("liderProyecto",""))
        fe_val = datos_previos.get("fechaCierre", "")
        fe_date = datetime.strptime(fe_val, "%d/%m/%Y").date() if fe_val else date.today()
        datos["fechaCierre"]       = col2.date_input("Fecha de Cierre",      value=fe_date, format="DD/MM/YYYY").strftime("%d/%m/%Y")

        datos["areaSolicitante"]   = st.text_input("Área Solicitante",      value=datos_previos.get("areaSolicitante",""))

        # secciones de texto
        st.markdown("#### Resumen del Proyecto")
        datos["resumenProyecto"]   = st.text_area("", value=datos_previos.get("resumenProyecto",""), height=120, key="resumen_proj")

        st.markdown("#### Participantes")
        datos["participantesProyecto"] = st.text_area("", value=datos_previos.get("participantesProyecto",""), height=100, key="part_proj")

        st.markdown("#### Entregables")
        datos["entregablesProyecto"] = st.text_area("", value=datos_previos.get("entregablesProyecto",""), height=100, key="entreg_proj")

        st.markdown("#### Documentación")
        datos["documentacion"]      = st.text_area("", value=datos_previos.get("documentacion",""), height=100, key="doc_proj")

        # firmas de aprobación
        st.markdown("#### Firmas de Aprobación")
        col1, col2 = st.columns(2)
        datos["firmaGerente"] = col1.text_input("Gerente de Proyecto", value=datos_previos.get("firmaGerente",""))
        datos["firmaCliente"] = col2.text_input("Cliente / Patrocinador", value=datos_previos.get("firmaCliente",""))

    #  REUNIN 
    elif tipo == "reunion":
        st.markdown("## Acta de Reunión")
        # campos iniciales de metadatos
        col1, col2 = st.columns(2)
        datos["nombreReunion"] = col1.text_input("Proyecto / Tema", value=datos_previos.get("nombreReunion",""), placeholder="Ej: Seguimiento semanal")

        fr_val  = datos_previos.get("fechaReunion","")
        fr_date = datetime.strptime(fr_val, "%d/%m/%Y").date() if fr_val else date.today()
        datos["fechaReunion"]  = col2.date_input("Fecha de la Reunión",  value=fr_date, format="DD/MM/YYYY").strftime("%d/%m/%Y")
        datos["horaInicio"]    = col1.text_input("Hora Inicio",       value=datos_previos.get("horaInicio",""),  placeholder="09:00")
        datos["horaFin"]       = col2.text_input("Hora Fin",          value=datos_previos.get("horaFin",""),    placeholder="10:30")

        datos["lugar"]         = st.text_input("Lugar / Medio",       value=datos_previos.get("lugar",""))
        datos["liderReunion"]  = st.text_input("Líder de la Reunión", value=datos_previos.get("liderReunion",""))
        datos["elaboro"]       = st.text_input("Elaboró",            value=datos_previos.get("elaboro",""))

        st.markdown("#### Participantes y Agenda")
        datos["asistentes"] = st.text_area("Participantes (una por línea)", value=datos_previos.get("asistentes",""), height=100, key="asistentes_reu")
        datos["agenda"]     = st.text_area("Agenda / Puntos a Tratar",           value=datos_previos.get("agenda",""),     height=90, key="agenda_reu")

        st.markdown("#### Objetivo de la Reunión")
        datos["objetivo"]  = st.text_area("Objetivo de la reunión", value=datos_previos.get("objetivo",""), height=100, key="objetivo_reu", label_visibility="collapsed")

        st.markdown("#### Desarrollo y Temas Tratados")
        datos["desarrollo"] = st.text_area("Desarrollo y temas tratados", value=datos_previos.get("desarrollo",""), height=120, key="desarrollo_reu", label_visibility="collapsed")

        st.markdown("#### Compromisos y Plan de Acción")
        datos["compromisos"] = st.text_area(
            "Compromiso|Responsable|Fecha Compromiso|Estado (una fila por línea)",
            value=datos_previos.get("compromisos",""),
            height=120,
            key="compromisos_reu"
        )

        st.markdown("#### Observaciones")
        datos["observaciones"] = st.text_area("Observaciones", value=datos_previos.get("observaciones",""), height=90, key="obs_reu", label_visibility="collapsed")

    #  Barra de acciones 
    if not editando:
        # Borrador en memoria por tipo de acta: se conserva al navegar entre páginas.
        st.session_state.borradores[tipo] = dict(datos)

    st.divider()
    col_g, col_p, col_c, _ = st.columns([1.2, 1.2, 1.2, 2])

    if col_g.button("Guardar acta", type="primary", use_container_width=True):
        titulo = (
            datos.get("cl_nombreRequerimiento")
            or datos.get("nombreRequerimiento")
            or datos.get("proyecto")
            or datos.get("nombreReunion")
            or "Sin título"
        )
        if editando:
            for i, a in enumerate(st.session_state.actas):
                if a.get("uid") == editando.get("uid") or (
                    not a.get("uid") and not editando.get("uid") and a.get("id") == editando.get("id")
                ):
                    st.session_state.actas[i]["data"]   = datos
                    st.session_state.actas[i]["titulo"] = titulo
                    break
            guardar_actas(st.session_state.actas)
            set_feedback("success", f"Acta actualizada: {titulo}", ":material/check_circle:")
            st.session_state.acta_editando = None
            st.rerun()
        else:
            next_id = (max((a.get("id", 0) for a in st.session_state.actas), default=0) + 1)
            nueva = {
                "id":        next_id,
                "uid":       uuid4().hex,
                "tipo":      tipo,
                "titulo":    titulo,
                "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "data":      datos,
            }
            st.session_state.actas.append(nueva)
            guardar_actas(st.session_state.actas)
            st.session_state.borradores.pop(tipo, None)
            set_feedback("success", f"Acta guardada: {titulo}", ":material/check_circle:")
            st.rerun()

    if col_p.button("Previsualizar", use_container_width=True):
        datos["id"] = editando["id"] if editando else len(st.session_state.actas) + 1
        st.session_state.preview_html  = renderizar_acta(tipo, datos)
        st.session_state.preview_datos = {"tipo": tipo, "id": datos["id"]}

    if editando and col_c.button("Cancelar", use_container_width=True):
        cerrar_preview()
        st.session_state.acta_editando = None
        st.session_state.page_transition = st.session_state.pagina != "lista"
        st.session_state.pagina = "lista"
        st.rerun()

    #  Vista previa + descarga 
    if st.session_state.preview_html:
        st.divider()
        st.markdown("##### Vista previa - Descargas")

        pdata = st.session_state.preview_datos
        cerrar_prev = botones_descarga(
            html       = st.session_state.preview_html,
            tipo       = pdata.get("tipo", tipo),
            acta_id    = pdata.get("id", 0),
            key_suffix = "prev_nueva",
            close_key  = "close_prev_nueva",
        )

        if cerrar_prev:
            cerrar_preview()
            set_feedback("info", "Vista previa cerrada", ":material/visibility_off:")
            st.rerun()

        st.markdown('<div class="preview-wrap">', unsafe_allow_html=True)
        components.html(st.session_state.preview_html, height=920, scrolling=True)
        st.markdown('</div>', unsafe_allow_html=True)


# 
# PÁGINA: MIS ACTAS
# 
elif st.session_state.pagina == "lista":

    st.markdown("## Mis Actas")
    actas = st.session_state.actas

    if not actas:
        st.markdown(
            """
            <div class="empty-state-card">
              <div class="icon">&#128196;</div>
              <div class="title">No hay actas registradas</div>
              <div class="desc">Empieza creando tu primera acta para verla aquí y exportarla a HTML/PDF.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<div style="height: 0.55rem;"></div>', unsafe_allow_html=True)
        if st.button("Crear nueva acta", type="primary", key="crear_primera_acta"):
            st.session_state.page_transition = st.session_state.pagina != "nueva"
            st.session_state.pagina = "nueva"
            st.rerun()
    else:
        opciones_filtro = [
            "Todas",
            "Acta de Inicio de Requerimiento",
            "Acta de Cierre de Requerimiento",
            "Acta de Cierre de Proyecto",
            "Acta de Reunión",
        ]
        filtro = st.selectbox(
            "Filtrar por tipo de acta",
            options=opciones_filtro,
            index=opciones_filtro.index(st.session_state.filtro_mis_actas) if st.session_state.filtro_mis_actas in opciones_filtro else 0,
            key="filtro_mis_actas_ui_select",
        )
        st.session_state.filtro_mis_actas = filtro
        mapa_filtro = {
            "Acta de Inicio de Requerimiento": "inicio_requerimiento",
            "Acta de Cierre de Requerimiento": "cierre",
            "Acta de Cierre de Proyecto": "cierre_proyecto",
            "Acta de Reunión": "reunion",
        }
        actas_filtradas = actas if filtro == "Todas" else [a for a in actas if a["tipo"] == mapa_filtro[filtro]]

        col_busq, col_orden = st.columns([2.2, 1.2])
        with col_busq:
            busqueda_raw = st.text_input(
                "Buscar acta",
                placeholder="Buscar por título, tipo o ID (ej: 0004)",
                key="busqueda_mis_actas",
            )
        busqueda = (busqueda_raw or "").strip().lower()
        orden = col_orden.selectbox(
            "Ordenar por",
            [
                "Más recientes",
                "Más antiguas",
                "ID ascendente",
                "ID descendente",
                "Título A-Z",
                "Título Z-A",
            ],
            key="orden_mis_actas",
        )

        if busqueda:
            def _coincide_busqueda(a: dict) -> bool:
                id_txt = str(a.get("id", "")).zfill(4)
                tipo_txt = TIPOS.get(a.get("tipo", ""), {}).get("label", "")
                titulo_txt = a.get("titulo", "")
                campos = [id_txt.lower(), tipo_txt.lower(), titulo_txt.lower()]
                # búsqueda precisa por prefijo: cada token debe empezar por el texto buscado
                return any(
                    token.startswith(busqueda)
                    for campo in campos
                    for token in campo.split()
                )

            actas_filtradas = [a for a in actas_filtradas if _coincide_busqueda(a)]

        if orden == "Más recientes":
            actas_filtradas = sorted(actas_filtradas, key=lambda a: a.get("createdAt", ""), reverse=True)
        elif orden == "Más antiguas":
            actas_filtradas = sorted(actas_filtradas, key=lambda a: a.get("createdAt", ""))
        elif orden == "ID ascendente":
            actas_filtradas = sorted(actas_filtradas, key=lambda a: a.get("id", 0))
        elif orden == "ID descendente":
            actas_filtradas = sorted(actas_filtradas, key=lambda a: a.get("id", 0), reverse=True)
        elif orden == "Título A-Z":
            actas_filtradas = sorted(actas_filtradas, key=lambda a: a.get("titulo", "").lower())
        elif orden == "Título Z-A":
            actas_filtradas = sorted(actas_filtradas, key=lambda a: a.get("titulo", "").lower(), reverse=True)

        st.divider()
        if not actas_filtradas:
            st.markdown(
                """
                <div class="empty-state-card">
                  <div class="icon">&#128269;</div>
                  <div class="title">Sin resultados</div>
                  <div class="desc">No hay actas que coincidan con el filtro y la búsqueda actual.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        for acta in actas_filtradas:
            with st.container(border=True):
                st.markdown('<div class="acta-card-shell">', unsafe_allow_html=True)
                acta_uid = str(acta.get("uid") or f"id_{acta.get('id', 0)}")
                tipo_label  = TIPOS[acta["tipo"]]["label"]
                nombre_base = f"acta_{acta['tipo']}_{str(acta['id']).zfill(4)}"

                st.markdown(
                    f'<div class="acta-card-head accent-{acta["tipo"]}">'
                    f'<div class="acta-meta-row">'
                    f'<span class="badge badge-{acta["tipo"]}">{tipo_label}</span>'
                    f'<span class="meta-chip">ID {str(acta["id"]).zfill(4)}</span>'
                    f'<span class="meta-chip">{acta["createdAt"]}</span>'
                    f'</div>'
                    f'<div class="acta-card-title">{acta["titulo"]}</div></div>',
                    unsafe_allow_html=True,
                )

                col_e, col_d, col_v, col_h, col_p = st.columns([1.0, 0.8, 1.0, 1.25, 1.25])
                html_reporte = renderizar_acta(acta["tipo"], acta["data"] | {"id": acta["id"]})

                if col_e.button("Editar", key=f"edit_{acta_uid}", use_container_width=True):
                    cerrar_preview()
                    st.session_state.acta_editando = acta
                    st.session_state.page_transition = st.session_state.pagina != "nueva"
                    st.session_state.pagina = "nueva"
                    st.rerun()

                if col_d.button("", key=f"del_{acta_uid}", use_container_width=True, help="Eliminar acta"):
                    titulo_eliminado = acta.get("titulo", "Sin título")
                    st.session_state.actas = [
                        a for a in actas
                        if str(a.get("uid") or f"id_{a.get('id', 0)}") != acta_uid
                    ]
                    guardar_actas(st.session_state.actas)
                    set_feedback("warning", f"Acta eliminada: {titulo_eliminado}", ":material/delete:")
                    st.rerun()

                if col_v.button("Ver", key=f"ver_{acta_uid}", use_container_width=True):
                    st.session_state.preview_html  = html_reporte
                    st.session_state.preview_datos = {"tipo": acta["tipo"], "id": acta["id"]}

                col_h.download_button(
                    label     = "Descargar HTML",
                    data      = html_reporte,
                    file_name = f"{nombre_base}.html",
                    mime      = "text/html",
                    key       = f"dl_html_{acta_uid}",
                    use_container_width=True,
                )

                if WEASYPRINT_OK:
                    try:
                        col_p.download_button(
                            label     = "Descargar PDF",
                            data      = html_a_pdf(html_reporte),
                            file_name = f"{nombre_base}.pdf",
                            mime      = "application/pdf",
                            key       = f"dl_pdf_{acta_uid}",
                            use_container_width=True,
                        )
                    except Exception:
                        set_feedback("error", "No se pudo generar el PDF", ":material/error:")
                        col_p.warning("Error")
                else:
                    col_p.caption("pip install\nweasyprint")
                st.markdown('</div>', unsafe_allow_html=True)

        # Vista previa desde lista
        if st.session_state.preview_html:
            st.divider()
            st.markdown("##### Vista previa")
            pdata = st.session_state.preview_datos or {}
            tipo_prev = _normalizar_tipo(pdata.get("tipo", "acta"))
            acta_id_prev = pdata.get("id", 0)
            nombre_base_prev = f"acta_{tipo_prev}_{str(acta_id_prev).zfill(4)}"

            col_close_prev, col_pdf_prev, _ = st.columns([1.25, 1.35, 4.4])
            if col_close_prev.button("Cerrar vista previa", key="close_prev_lista", use_container_width=True):
                cerrar_preview()
                set_feedback("info", "Vista previa cerrada", ":material/visibility_off:")
                st.rerun()

            if WEASYPRINT_OK:
                try:
                    col_pdf_prev.download_button(
                        label="Descargar PDF",
                        data=html_a_pdf(st.session_state.preview_html),
                        file_name=f"{nombre_base_prev}.pdf",
                        mime="application/pdf",
                        key=f"dl_pdf_prev_lista_{tipo_prev}_{acta_id_prev}",
                        use_container_width=True,
                    )
                except Exception:
                    set_feedback("error", "No se pudo generar el PDF de la vista previa", ":material/error:")
                    col_pdf_prev.warning("Error PDF")
            else:
                col_pdf_prev.info("PDF: `pip install weasyprint`")

            st.markdown('<div class="preview-wrap">', unsafe_allow_html=True)
            components.html(st.session_state.preview_html, height=920, scrolling=True)
            st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
if st.session_state.page_transition:
    st.session_state.page_transition = False
