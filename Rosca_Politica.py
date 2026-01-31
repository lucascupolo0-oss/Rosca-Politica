import streamlit as st
import random
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Rosca Política: 136", layout="wide", page_icon="🇦🇷")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .stButton>button { 
        width: 100%; 
        border-radius: 5px; 
        font-weight: bold; 
        text-align: left; 
        white-space: pre-wrap; 
        height: auto !important;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .metric-card { background-color: #f0f2f6; padding: 10px; border-radius: 10px; border-left: 5px solid #333; }
    div[data-testid="stMetricValue"] { font-size: 1.1rem; }
    </style>
""", unsafe_allow_html=True)

# --- DATOS ESTRUCTURALES ---

STATE_GROUPS = {
    "FG": {"nombre": "Federalismo y Gob.", "renta": 100000, "color": "🟢"},
    "TR": {"nombre": "Trabajo", "renta": 80000, "color": "🟠"},
    "ET": {"nombre": "Educación y Transp.", "renta": 75000, "color": "🔵"},
    "PN": {"nombre": "Producción Nac.", "renta": 75000, "color": "🟣"},
    "PC": {"nombre": "Prov. Cambiantes", "renta": 65000, "color": "⚪"},
    "PE": {"nombre": "Presencia Estatal", "renta": 45000, "color": "🟡"},
    "EA": {"nombre": "Eternos Anti-PJ", "renta": 40000, "color": "⬛"},
    "CP": {"nombre": "Clásicos Peronistas", "renta": 40000, "color": "🟦"}
}

SOCIAL_GROUPS = {
    "SO": {"nombre": "Seguridad y Orden", "costo": 75000, "renta": 37500, "color": "👮"},
    "REL": {"nombre": "Tradición y Religión", "costo": 50000, "renta": 25000, "color": "✝️"},
    "JUV": {"nombre": "Juventud y Redes", "costo": 50000, "renta": 25000, "color": "📱"},
    "EMP": {"nombre": "Banca Empresarial", "costo": 100000, "renta": 50000, "color": "💼"},
    "PROG": {"nombre": "Progresismo y Sind.", "costo": 100000, "renta": 50000, "color": "✊"},
    "PYME": {"nombre": "Comerciantes y PyMEs", "costo": 75000, "renta": 37500, "color": "🏪"}
}

PROV_TO_GROUP_RAW = {
    "Jujuy": ["PE"], "Formosa": ["PE", "CP"], "Salta": ["FG"], "Chaco": ["PE", "CP"],
    "Misiones": ["PC"], "Tucumán": ["FG", "CP"], "Santiago del Estero": ["PE", "CP"],
    "Corrientes": ["EA"], "La Rioja": ["PE", "CP"], "Catamarca": ["PE", "CP"],
    "San Juan": ["PN", "CP"], "Santa Fe": ["TR", "ET", "PN", "FG", "PC"],
    "Entre Ríos": ["PN", "ET", "FG", "PC"], "San Luis": ["EA"],
    "Córdoba": ["TR", "ET", "PN", "FG", "EA"], "PBA Norte": ["TR", "ET", "PN", "FG", "PC"],
    "CABA": ["TR", "ET", "FG", "EA"], "Mendoza": ["TR", "ET", "PN", "FG", "EA"],
    "PBA Oeste": ["TR", "PE", "FG", "CP"], "PBA Centro": ["TR", "PN", "FG", "PC"],
    "La Pampa": ["PN", "CP"], "PBA Costa": ["TR", "PN"],
    "Neuquén": ["TR", "PN", "PC"], "Río Negro": ["PN", "PC"],
    "Chubut": ["PN"], "Santa Cruz": ["PE", "CP"], "Tierra del Fuego": ["PE", "PN"]
}

MAPA_DATA = {
    "Jujuy": {"votos": 8, "pos": (0, 1)}, "Salta": {"votos": 10, "pos": (1, 1)},
    "Formosa": {"votos": 7, "pos": (0, 2)}, "Chaco": {"votos": 9, "pos": (1, 2)},
    "Misiones": {"votos": 9, "pos": (1, 3)}, "Tucumán": {"votos": 12, "pos": (2, 1)},
    "Santiago del Estero":{"votos": 10, "pos": (2, 2)}, "Corrientes": {"votos": 10, "pos": (2, 3)},
    "La Rioja": {"votos": 6, "pos": (3, 0)}, "Catamarca": {"votos": 6, "pos": (3, 1)},
    "Santa Fe": {"votos": 25, "pos": (4, 2)}, "Entre Ríos": {"votos": 15, "pos": (4, 3)},
    "San Juan": {"votos": 8, "pos": (4, 0)}, "Córdoba": {"votos": 25, "pos": (5, 1)},
    "San Luis": {"votos": 8, "pos": (5, 0)}, "Mendoza": {"votos": 18, "pos": (6, 0)},
    "PBA Norte": {"votos": 20, "pos": (5, 2)}, "PBA Oeste": {"votos": 18, "pos": (6, 1)},
    "PBA Centro": {"votos": 18, "pos": (6, 2)}, "CABA": {"votos": 30, "pos": (5, 3)},
    "PBA Costa": {"votos": 18, "pos": (7, 3)}, "La Pampa": {"votos": 8, "pos": (7, 1)},
    "Neuquén": {"votos": 10, "pos": (8, 0)}, "Río Negro": {"votos": 10, "pos": (8, 1)},
    "Chubut": {"votos": 12, "pos": (9, 1)}, "Santa Cruz": {"votos": 8, "pos": (10, 1)},
    "Tierra del Fuego": {"votos": 5, "pos": (11, 1)},
}

COSTOS_FIJOS = {
    "Jujuy": 15000, "Formosa": 17500, "Salta": 22500, "Chaco": 25000,
    "Misiones": 20000, "Tucumán": 40000, "Santiago del Estero": 25000,
    "Corrientes": 22500, "La Rioja": 10000, "Catamarca": 12500,
    "San Juan": 20000, "Santa Fe": 200000, "Entre Ríos": 100000,
    "San Luis": 15000, "Córdoba": 175000, "PBA Norte": 175000,
    "CABA": 200000, "Mendoza": 150000, "PBA Oeste": 100000,
    "PBA Centro": 125000, "La Pampa": 25000, "PBA Costa": 75000,
    "Neuquén": 40000, "Río Negro": 35000, "Chubut": 30000,
    "Santa Cruz": 20000, "Tierra del Fuego": 17500
}

# --- CANDIDATOS ---
PARTIDOS = {
    "PJ": {"color": "#1f77b4", "candidatos": {
        "Cristina Kirchner": {"emoji": "✌️", "FG": 10, "TR": 15, "ET": 15, "PN": 15, "PC": -25, "PE": 20, "EA": -45, "CP": 15, "SO": -15, "REL": -5, "JUV": -5, "EMP": -25, "PROG": 30, "PYME": 10},
        "Juan Schiaretti": {"emoji": "🧱", "FG": 20, "TR": 0, "ET": -5, "PN": 5, "PC": 10, "PE": -10, "EA": -5, "CP": 10, "SO": 10, "REL": 5, "JUV": -5, "EMP": 20, "PROG": -15, "PYME": 35},
        "Juan Grabois": {"emoji": "🌱", "FG": -10, "TR": 10, "ET": 30, "PN": 0, "PC": -10, "PE": 30, "EA": -25, "CP": 5, "SO": -25, "REL": 15, "JUV": 30, "EMP": -30, "PROG": 35, "PYME": -10},
        "Guillermo Moreno": {"emoji": "🌭", "FG": 10, "TR": 0, "ET": -10, "PN": 5, "PC": 0, "PE": 5, "EA": -50, "CP": 30, "SO": 10, "REL": 40, "JUV": 5, "EMP": -5, "PROG": -5, "PYME": 15},
        "Axel Kicillof": {"emoji": "🚗", "FG": -5, "TR": 0, "ET": 15, "PN": 0, "PC": -5, "PE": 35, "EA": -30, "CP": 5, "SO": -10, "REL": 20, "JUV": 20, "EMP": -10, "PROG": 20, "PYME": 10},
        "Máximo Kirchner": {"emoji": "🎮", "FG": -10, "TR": -10, "ET": 10, "PN": 5, "PC": -35, "PE": 20, "EA": -40, "CP": 5, "SO": -30, "REL": -10, "JUV": 0, "EMP": -20, "PROG": 25, "PYME": -15},
        "Sergio Massa": {"emoji": "🐯", "FG": 25, "TR": -10, "ET": 20, "PN": 0, "PC": -40, "PE": 15, "EA": -10, "CP": 0, "SO": 20, "REL": 10, "JUV": -10, "EMP": 30, "PROG": 15, "PYME": 25},
        "Florencio Randazzo": {"emoji": "🚆", "FG": 15, "TR": 0, "ET": -10, "PN": 5, "PC": 10, "PE": 5, "EA": -10, "CP": 0, "SO": 15, "REL": 10, "JUV": -10, "EMP": 20, "PROG": 5, "PYME": 15},
        "Alberto Fernandez": {"emoji": "🎸", "FG": 20, "TR": -10, "ET": 5, "PN": -10, "PC": 5, "PE": 30, "EA": -10, "CP": -5, "SO": -15, "REL": 5, "JUV": -25, "EMP": 5, "PROG": 30, "PYME": 10},
        "Leandro Santoro": {"emoji": "🏙️", "FG": 10, "TR": -20, "ET": 10, "PN": 10, "PC": 10, "PE": 10, "EA": 5, "CP": 5, "SO": -5, "REL": 20, "JUV": 10, "EMP": -10, "PROG": 30, "PYME": 5},
        "Fernando Gray": {"emoji": "📡", "FG": 15, "TR": -10, "ET": 0, "PN": 0, "PC": -30, "PE": 10, "EA": -55, "CP": 30, "SO": 5, "REL": 15, "JUV": -10, "EMP": 10, "PROG": 0, "PYME": 20},
        "Aníbal Fernández": {"emoji": "🧳", "FG": 20, "TR": 10, "ET": 5, "PN": 5, "PC": 15, "PE": 30, "EA": -40, "CP": 25, "SO": 35, "REL": 5, "JUV": -25, "EMP": -25, "PROG": 10, "PYME": 5},
        "Wado de Pedro": {"emoji": "🚜", "FG": 20, "TR": 10, "ET": 15, "PN": 5, "PC": -30, "PE": 25, "EA": -35, "CP": 5, "SO": -10, "REL": -20, "JUV": 10, "EMP": -15, "PROG": 20, "PYME": 10}
    }},
    "LLA": {"color": "#9467bd", "candidatos": {
        "Javier Milei": {"emoji": "🦁", "FG": 20, "TR": 20, "ET": -20, "PN": -20, "PC": 30, "PE": -45, "EA": 30, "CP": -10, "SO": 20, "REL": 25, "JUV": 35, "EMP": 35, "PROG": -45, "PYME": -5},
        "Patricia Bullrich": {"emoji": "🍷", "FG": 35, "TR": -20, "ET": -10, "PN": -40, "PC": 0, "PE": -30, "EA": 20, "CP": -20, "SO": 35, "REL": 30, "JUV": 5, "EMP": 20, "PROG": -40, "PYME": -10},
        "Ramiro Marra": {"emoji": "📉", "FG": 20, "TR": -10, "ET": -30, "PN": -30, "PC": 40, "PE": -50, "EA": 10, "CP": -5, "SO": 20, "REL": 10, "JUV": 30, "EMP": 40, "PROG": -20, "PYME": -15},
        "Manuel Adorni": {"emoji": "🎤", "FG": 5, "TR": 5, "ET": -20, "PN": -10, "PC": 30, "PE": -30, "EA": 20, "CP": -10, "SO": 5, "REL": -5, "JUV": 25, "EMP": 10, "PROG": -15, "PYME": 0},
        "Lilia Lemoine": {"emoji": "🍋", "FG": 5, "TR": -15, "ET": -40, "PN": -10, "PC": -40, "PE": 5, "EA": 0, "CP": -30, "SO": 5, "REL": -20, "JUV": 35, "EMP": -10, "PROG": -10, "PYME": -20},
        "Martín Menem": {"emoji": "📜", "FG": 15, "TR": 0, "ET": -5, "PN": -20, "PC": 10, "PE": -15, "EA": 5, "CP": 0, "SO": 10, "REL": 5, "JUV": -5, "EMP": 5, "PROG": -10, "PYME": 5},
        "Luis Petri": {"emoji": "🪖", "FG": 25, "TR": -15, "ET": -5, "PN": 0, "PC": 5, "PE": 5, "EA": 25, "CP": -35, "SO": 30, "REL": 20, "JUV": 5, "EMP": 10, "PROG": -10, "PYME": -5},
        "José Luis Espert": {"emoji": "🔫", "FG": 20, "TR": -5, "ET": -10, "PN": -20, "PC": 10, "PE": -30, "EA": 5, "CP": -35, "SO": 30, "REL": 5, "JUV": 15, "EMP": 30, "PROG": -25, "PYME": -10},
        "Karina Milei": {"emoji": "🔮", "FG": 25, "TR": 0, "ET": -20, "PN": -10, "PC": -10, "PE": -5, "EA": 10, "CP": -30, "SO": 10, "REL": -15, "JUV": 10, "EMP": 10, "PROG": -5, "PYME": -30},
        "Luis Caputo": {"emoji": "💰", "FG": 10, "TR": 10, "ET": -10, "PN": -20, "PC": -10, "PE": -30, "EA": 10, "CP": -30, "SO": -10, "REL": 20, "JUV": 5, "EMP": 35, "PROG": -30, "PYME": -40},
        "F. Sturzenegger": {"emoji": "📝", "FG": 10, "TR": 0, "ET": 0, "PN": -10, "PC": -5, "PE": -15, "EA": 30, "CP": -30, "SO": -5, "REL": 20, "JUV": -30, "EMP": 45, "PROG": -30, "PYME": -35},
        "Diego Santilli": {"emoji": "👱", "FG": 20, "TR": 15, "ET": -10, "PN": -20, "PC": -10, "PE": -5, "EA": 0, "CP": -30, "SO": 20, "REL": 25, "JUV": 10, "EMP": 25, "PROG": 0, "PYME": -10}
    }},
    "PRO": {"color": "#ff7f0e", "candidatos": {
        "Mauricio Macri": {"emoji": "🐱", "FG": 20, "TR": 25, "ET": -20, "PN": -30, "PC": -20, "PE": -20, "EA": 45, "CP": -40, "SO": 20, "REL": 20, "JUV": -35, "EMP": 50, "PROG": -20, "PYME": 15},
        "H. R. Larreta": {"emoji": "👽", "FG": 30, "TR": 5, "ET": 5, "PN": -30, "PC": -30, "PE": -10, "EA": 20, "CP": -45, "SO": 15, "REL": 10, "JUV": -15, "EMP": 25, "PROG": 5, "PYME": 20},
        "R. López Murphy": {"emoji": "bulldog", "FG": 5, "TR": 5, "ET": -35, "PN": -25, "PC": -20, "PE": -45, "EA": 25, "CP": -35, "SO": 5, "REL": 25, "JUV": -35, "EMP": 25, "PROG": -30, "PYME": -5},
        "María E. Vidal": {"emoji": "🦁", "FG": 5, "TR": -15, "ET": 5, "PN": 0, "PC": -5, "PE": -5, "EA": 40, "CP": -10, "SO": 15, "REL": 5, "JUV": 10, "EMP": 20, "PROG": 10, "PYME": 10},
        "Jorge Macri": {"emoji": "🏙️", "FG": 10, "TR": -20, "ET": 0, "PN": -40, "PC": 10, "PE": 10, "EA": 10, "CP": -55, "SO": 30, "REL": 15, "JUV": 10, "EMP": 30, "PROG": -10, "PYME": 15},
        "Silvia Lospennato": {"emoji": "🗳️", "FG": -5, "TR": 5, "ET": 10, "PN": -5, "PC": -20, "PE": -5, "EA": 5, "CP": -15, "SO": 10, "REL": -5, "JUV": 5, "EMP": 5, "PROG": 10, "PYME": -10},
        "Néstor Grindetti": {"emoji": "⚽", "FG": 10, "TR": -5, "ET": -15, "PN": -5, "PC": -20, "PE": 5, "EA": 0, "CP": -20, "SO": 15, "REL": 10, "JUV": -15, "EMP": 20, "PROG": 0, "PYME": 10},
        "Luis Juez": {"emoji": "🌭", "FG": 25, "TR": -25, "ET": -20, "PN": -10, "PC": 20, "PE": 5, "EA": 5, "CP": 0, "SO": 5, "REL": 5, "JUV": -30, "EMP": -5, "PROG": -5, "PYME": 0}
    }},
    "UCR": {"color": "#d3d3d3", "candidatos": {
        "Martín Lousteau": {"emoji": "🎓", "FG": 30, "TR": -25, "ET": 10, "PN": 5, "PC": -20, "PE": 10, "EA": 0, "CP": -10, "SO": 10, "REL": -15, "JUV": 25, "EMP": 15, "PROG": 25, "PYME": 15},
        "Roberto Lavagna": {"emoji": "🧦", "FG": 10, "TR": 20, "ET": 0, "PN": -5, "PC": -15, "PE": 5, "EA": 10, "CP": -40, "SO": 5, "REL": 10, "JUV": -10, "EMP": 20, "PROG": 5, "PYME": 20},
        "Facundo Manes": {"emoji": "🧠", "FG": 20, "TR": -10, "ET": 5, "PN": 0, "PC": -20, "PE": 5, "EA": 0, "CP": -30, "SO": -10, "REL": 5, "JUV": 20, "EMP": 10, "PROG": 10, "PYME": 10},
        "Gerardo Morales": {"emoji": "🌵", "FG": 25, "TR": 0, "ET": -10, "PN": 5, "PC": -40, "PE": 5, "EA": 5, "CP": -20, "SO": 25, "REL": 20, "JUV": -15, "EMP": 15, "PROG": 0, "PYME": 15},
        "Julio Cobos": {"emoji": "👎", "FG": 20, "TR": 5, "ET": 0, "PN": -10, "PC": -30, "PE": 5, "EA": 0, "CP": -20, "SO": 10, "REL": 20, "JUV": -20, "EMP": 5, "PROG": 5, "PYME": 15},
        "Rodrigo de Loredo": {"emoji": "🚌", "FG": 5, "TR": 5, "ET": 30, "PN": 0, "PC": -10, "PE": -5, "EA": 5, "CP": -40, "SO": 5, "REL": -15, "JUV": 30, "EMP": 5, "PROG": 10, "PYME": 10},
        "Ricardo Alfonsín": {"emoji": "👴", "FG": 0, "TR": -10, "ET": 15, "PN": 5, "PC": 5, "PE": 15, "EA": 5, "CP": -20, "SO": -15, "REL": 15, "JUV": 0, "EMP": -15, "PROG": 30, "PYME": 5},
        "Lula Levy": {"emoji": "🤳", "FG": 25, "TR": -45, "ET": 30, "PN": 5, "PC": 15, "PE": 10, "EA": 10, "CP": -5, "SO": -10, "REL": -10, "JUV": 40, "EMP": 5, "PROG": 15, "PYME": 10}
    }},
    "FIT-U": {"color": "#d62728", "candidatos": {
        "Myriam Bregman": {"emoji": "✊", "FG": -35, "TR": 15, "ET": 40, "PN": 10, "PC": 10, "PE": 30, "EA": -20, "CP": -15, "SO": -20, "REL": -10, "JUV": 50, "EMP": -30, "PROG": 25, "PYME": -20},
        "Nicolás del Caño": {"emoji": "📹", "FG": -25, "TR": 10, "ET": 25, "PN": 10, "PC": 15, "PE": 25, "EA": 0, "CP": 0, "SO": -25, "REL": -25, "JUV": 30, "EMP": -25, "PROG": 30, "PYME": -25},
        "Gabriel Solano": {"emoji": "📢", "FG": -40, "TR": 25, "ET": 30, "PN": 10, "PC": 0, "PE": 25, "EA": -10, "CP": -10, "SO": -30, "REL": -35, "JUV": 20, "EMP": -35, "PROG": 35, "PYME": -20},
        "Manuela Castañeira": {"emoji": "🚩", "FG": -45, "TR": 15, "ET": 60, "PN": 15, "PC": 20, "PE": 30, "EA": -20, "CP": 0, "SO": -35, "REL": -20, "JUV": 35, "EMP": -20, "PROG": 30, "PYME": -15},
        "Christian Castillo": {"emoji": "📕", "FG": -20, "TR": 10, "ET": 15, "PN": 10, "PC": -10, "PE": 20, "EA": -30, "CP": -30, "SO": -40, "REL": -30, "JUV": 10, "EMP": -40, "PROG": 60, "PYME": -30},
        "Romina Del Plá": {"emoji": "🏫", "FG": -35, "TR": 20, "ET": 35, "PN": 5, "PC": 10, "PE": 30, "EA": -40, "CP": -25, "SO": -30, "REL": -25, "JUV": 15, "EMP": -25, "PROG": 20, "PYME": -25},
        "Federico Winokur": {"emoji": "🏫", "FG": -40, "TR": 20, "ET": 50, "PN": 15, "PC": -50, "PE": 30, "EA": -50, "CP": -35, "SO": -45, "REL": -40, "JUV": 25, "EMP": -50, "PROG": 45, "PYME": -10},
        "Luca Bonfante": {"emoji": "🎓", "FG": -10, "TR": 25, "ET": 30, "PN": 10, "PC": 10, "PE": 25, "EA": -5, "CP": -5, "SO": -25, "REL": -30, "JUV": 35, "EMP": -35, "PROG": 40, "PYME": 0}
    }},
    "PN": {"color": "#2c3e50", "candidatos": {
        "Victoria Villarruel": {"emoji": "🛡️", "FG": 0, "TR": 15, "ET": -20, "PN": 20, "PC": 5, "PE": -30, "EA": 10, "CP": 5, "SO": 35, "REL": 35, "JUV": 10, "EMP": 15, "PROG": -30, "PYME": 5},
        "Santiago Cúneo": {"emoji": "📺", "FG": 10, "TR": 0, "ET": -35, "PN": 40, "PC": -20, "PE": 0, "EA": -5, "CP": 0, "SO": 20, "REL": 15, "JUV": 20, "EMP": -15, "PROG": 10, "PYME": 10},
        "Gómez Centurión": {"emoji": "⚔️", "FG": -10, "TR": 25, "ET": 0, "PN": 25, "PC": -5, "PE": -10, "EA": -5, "CP": -5, "SO": 40, "REL": 40, "JUV": -25, "EMP": -10, "PROG": -25, "PYME": 10},
        "Alejandro Biondini": {"emoji": "🦅", "FG": -50, "TR": 10, "ET": 0, "PN": 65, "PC": -20, "PE": -5, "EA": -20, "CP": -20, "SO": 50, "REL": 45, "JUV": -55, "EMP": -20, "PROG": -40, "PYME": -25},
        "Cesar Biondini": {"emoji": "🐣", "FG": -20, "TR": 5, "ET": -5, "PN": 20, "PC": 10, "PE": 0, "EA": -10, "CP": 10, "SO": 35, "REL": 20, "JUV": 10, "EMP": -30, "PROG": -30, "PYME": -10},
        "Alberto Samid": {"emoji": "🥩", "FG": -35, "TR": 15, "ET": -20, "PN": 30, "PC": 5, "PE": 0, "EA": -5, "CP": 0, "SO": 10, "REL": 15, "JUV": 5, "EMP": 10, "PROG": 5, "PYME": 15},
        "Larry de Clay": {"emoji": "🎩", "FG": -10, "TR": 10, "ET": -5, "PN": 10, "PC": -15, "PE": -5, "EA": -15, "CP": 25, "SO": 10, "REL": 15, "JUV": 40, "EMP": 5, "PROG": -10, "PYME": 10},
        "José Bonacci": {"emoji": "📜", "FG": -65, "TR": 25, "ET": -20, "PN": 20, "PC": -45, "PE": 5, "EA": -30, "CP": -15, "SO": 40, "REL": 30, "JUV": -55, "EMP": 20, "PROG": -60, "PYME": 20}
    }},
    "INDEPENDIENTES": {"color": "#eeeeee", "candidatos": {
        "Elisa Carrió": {"emoji": "✝️", "FG": 15, "TR": -5, "ET": 10, "PN": -10, "PC": 25, "PE": -5, "EA": 40, "CP": -10, "SO": 10, "REL": 25, "JUV": -10, "EMP": -15, "PROG": 20, "PYME": -10},
        "Daniel Scioli": {"emoji": "🚤", "FG": 5, "TR": 0, "ET": -10, "PN": -10, "PC": -15, "PE": 0, "EA": 10, "CP": 10, "SO": 15, "REL": 10, "JUV": 10, "EMP": 20, "PROG": 15, "PYME": 20},
        "R. Caruso Lombardi": {"emoji": "💨", "FG": -25, "TR": 15, "ET": 5, "PN": 5, "PC": 20, "PE": -10, "EA": 15, "CP": -20, "SO": -20, "REL": 0, "JUV": 35, "EMP": -10, "PROG": 5, "PYME": -10},
        "Turco García": {"emoji": "⚽", "FG": -10, "TR": 5, "ET": 5, "PN": -10, "PC": 10, "PE": 20, "EA": 5, "CP": 0, "SO": 0, "REL": 15, "JUV": 25, "EMP": -20, "PROG": -5, "PYME": 0},
        "Fernanda Tokumoto": {"emoji": "🌸", "FG": 5, "TR": 5, "ET": -10, "PN": -30, "PC": -10, "PE": -15, "EA": 10, "CP": -10, "SO": -30, "REL": 20, "JUV": -20, "EMP": -25, "PROG": -20, "PYME": -20},
        "Fernando Burlando": {"emoji": "⚖️", "FG": -10, "TR": 10, "ET": 0, "PN": -15, "PC": 5, "PE": -25, "EA": 5, "CP": -10, "SO": 5, "REL": 10, "JUV": 5, "EMP": 15, "PROG": 15, "PYME": 15},
        "Sixto Christiani": {"emoji": "✝️", "FG": -20, "TR": 0, "ET": 25, "PN": 15, "PC": 10, "PE": 30, "EA": -25, "CP": -25, "SO": -25, "REL": -10, "JUV": 60, "EMP": -30, "PROG": 25, "PYME": 5},
        "Carlos Maslatón": {"emoji": "📈", "FG": 10, "TR": 0, "ET": 5, "PN": 20, "PC": 30, "PE": -25, "EA": 10, "CP": 5, "SO": 0, "REL": -5, "JUV": 35, "EMP": 35, "PROG": -5, "PYME": 20},
        "Esteban Paulón": {"emoji": "🏳️‍🌈", "FG": -5, "TR": 10, "ET": 30, "PN": 5, "PC": -25, "PE": 15, "EA": 0, "CP": 5, "SO": -20, "REL": -70, "JUV": 35, "EMP": -10, "PROG": 65, "PYME": 5},
        "Yamil Santoro": {"emoji": "🗽", "FG": 0, "TR": 0, "ET": 0, "PN": 0, "PC": 0, "PE": 0, "EA": 0, "CP": 0, "SO": 0, "REL": 0, "JUV": 0, "EMP": 0, "PROG": 0, "PYME": 0},
        "Luis Barrionuevo": {"emoji": "🍽️", "FG": 5, "TR": -20, "ET": 10, "PN": 5, "PC": -20, "PE": 20, "EA": -15, "CP": 25, "SO": 30, "REL": 0, "JUV": -20, "EMP": 10, "PROG": 40, "PYME": 0},
        "Domingo Cavallo": {"emoji": "💲", "FG": -10, "TR": -25, "ET": -35, "PN": -20, "PC": 50, "PE": -25, "EA": 35, "CP": 20, "SO": 20, "REL": 30, "JUV": 5, "EMP": 65, "PROG": -40, "PYME": 0}
    }},
    "ESPECIALES": {"color": "#FFD700", "candidatos": {
        "Palito Ortega": {"emoji": "🎤", "FG": 15, "TR": 20, "ET": 10, "PN": 15, "PC": 25, "PE": 10, "EA": -20, "CP": 30, "SO": 5, "REL": 20, "JUV": -15, "EMP": 5, "PROG": 15, "PYME": 20},
        "Marcelo Tinelli": {"emoji": "📺", "FG": -10, "TR": 5, "ET": 0, "PN": 5, "PC": 40, "PE": -5, "EA": 10, "CP": 10, "SO": -10, "REL": -10, "JUV": 45, "EMP": 20, "PROG": 5, "PYME": 15},
        "Carlos Reutemann": {"emoji": "🏎️", "FG": 25, "TR": 15, "ET": 10, "PN": 20, "PC": 10, "PE": 10, "EA": 10, "CP": 10, "SO": 25, "REL": 20, "JUV": -30, "EMP": 25, "PROG": -5, "PYME": 20},
        "Florencia Peña": {"emoji": "🎭", "FG": -5, "TR": 10, "ET": 15, "PN": 5, "PC": 20, "PE": 20, "EA": -30, "CP": 20, "SO": -20, "REL": -25, "JUV": 30, "EMP": -10, "PROG": 40, "PYME": 0},
        "Gerardo Romano": {"emoji": "🎬", "FG": -5, "TR": 15, "ET": 10, "PN": 10, "PC": 15, "PE": 25, "EA": -25, "CP": 25, "SO": -10, "REL": -20, "JUV": 10, "EMP": -10, "PROG": 35, "PYME": 5},
        "Luis Brandoni": {"emoji": "🎥", "FG": 5, "TR": -5, "ET": 5, "PN": 0, "PC": 15, "PE": -10, "EA": 45, "CP": -35, "SO": 10, "REL": 10, "JUV": 5, "EMP": 20, "PROG": -30, "PYME": 5},
        "Héctor Baldassi": {"emoji": "⚽", "FG": 15, "TR": 10, "ET": 10, "PN": 5, "PC": -30, "PE": 5, "EA": -20, "CP": 0, "SO": 35, "REL": 15, "JUV": -10, "EMP": 10, "PROG": -25, "PYME": -15},
        "Jorge Lanata": {"emoji": "🚬", "FG": 5, "TR": 0, "ET": 10, "PN": 5, "PC": -20, "PE": -10, "EA": 50, "CP": -40, "SO": 10, "REL": -10, "JUV": 20, "EMP": 10, "PROG": -30, "PYME": 5},
        "Luis Majul": {"emoji": "📖", "FG": 0, "TR": -20, "ET": -50, "PN": -25, "PC": -60, "PE": 0, "EA": 45, "CP": -35, "SO": 20, "REL": 10, "JUV": 5, "EMP": 15, "PROG": -35, "PYME": 10},
        "Eduardo Feinmann": {"emoji": "👔", "FG": 0, "TR": 0, "ET": -45, "PN": -25, "PC": 5, "PE": -35, "EA": 50, "CP": -40, "SO": 30, "REL": 50, "JUV": 10, "EMP": 15, "PROG": -50, "PYME": 10},
        "Baby Etchecopar": {"emoji": "🎙️", "FG": 10, "TR": 0, "ET": -25, "PN": 10, "PC": 5, "PE": -20, "EA": 15, "CP": -50, "SO": 55, "REL": 45, "JUV": -50, "EMP": 25, "PROG": -85, "PYME": 15},
        "Marcelo Longobardi": {"emoji": "📻", "FG": 10, "TR": 0, "ET": 5, "PN": 10, "PC": 15, "PE": -10, "EA": 35, "CP": -30, "SO": 15, "REL": 5, "JUV": 10, "EMP": 20, "PROG": -30, "PYME": 15},
        "Cinthia Fernández": {"emoji": "🤸‍♀️", "FG": -20, "TR": -5, "ET": -5, "PN": -10, "PC": 10, "PE": -25, "EA": 5, "CP": 5, "SO": -20, "REL": -30, "JUV": 60, "EMP": 10, "PROG": 10, "PYME": 0},
        "Juan S. Verón": {"emoji": "🧙‍♂️", "FG": 20, "TR": -30, "ET": 10, "PN": 25, "PC": 15, "PE": -40, "EA": 0, "CP": -25, "SO": 15, "REL": 0, "JUV": 20, "EMP": 30, "PROG": -25, "PYME": 20},
        "Chiqui Tapia": {"emoji": "🏆", "FG": 10, "TR": 30, "ET": -30, "PN": 20, "PC": -20, "PE": 35, "EA": -20, "CP": 5, "SO": -25, "REL": -5, "JUV": -45, "EMP": 20, "PROG": 35, "PYME": 15},
        "Alejandro Kim": {"emoji": "🇰🇷", "FG": -30, "TR": 15, "ET": 10, "PN": 15, "PC": -40, "PE": 10, "EA": -35, "CP": 15, "SO": 10, "REL": 5, "JUV": 35, "EMP": 10, "PROG": 5, "PYME": 15},
        "Tomás Rebord": {"emoji": "👓", "FG": 5, "TR": 10, "ET": 15, "PN": 5, "PC": 35, "PE": 15, "EA": 0, "CP": 10, "SO": -10, "REL": -10, "JUV": 45, "EMP": -5, "PROG": 15, "PYME": 5},
        "El Gordo Dan": {"emoji": "🐦", "FG": -20, "TR": -35, "ET": -40, "PN": -25, "PC": -40, "PE": -35, "EA": 15, "CP": -45, "SO": 10, "REL": 5, "JUV": 55, "EMP": 5, "PROG": -65, "PYME": -5},
        "Ramón Puerta": {"emoji": "🚪", "FG": -50, "TR": 25, "ET": 10, "PN": 20, "PC": 5, "PE": 20, "EA": -15, "CP": 35, "SO": 10, "REL": 20, "JUV": -20, "EMP": 15, "PROG": 20, "PYME": 20},
        "Eduardo Camaño": {"emoji": "🕰️", "FG": -60, "TR": 25, "ET": 10, "PN": 20, "PC": 5, "PE": 20, "EA": -15, "CP": 35, "SO": 10, "REL": 20, "JUV": -20, "EMP": 15, "PROG": 20, "PYME": 20},
        "El Dipy": {"emoji": "🎵", "FG": -15, "TR": 10, "ET": -10, "PN": 0, "PC": 50, "PE": -20, "EA": 10, "CP": 0, "SO": -15, "REL": -20, "JUV": 60, "EMP": 5, "PROG": -10, "PYME": 5},
        "Nancy Pazos": {"emoji": "👚", "FG": -15, "TR": 0, "ET": 15, "PN": 0, "PC": -25, "PE": 25, "EA": -25, "CP": 5, "SO": -20, "REL": -35, "JUV": 15, "EMP": -15, "PROG": 45, "PYME": 5},
        "Juan R. Riquelme": {"emoji": "🔟", "FG": -15, "TR": 10, "ET": 35, "PN": 0, "PC": 25, "PE": 35, "EA": -45, "CP": 25, "SO": -20, "REL": 0, "JUV": 15, "EMP": 5, "PROG": 25, "PYME": 5},
        "Chino Luna": {"emoji": "⚽", "FG": 15, "TR": 5, "ET": -20, "PN": 5, "PC": 10, "PE": -5, "EA": 25, "CP": -40, "SO": 5, "REL": 0, "JUV": 20, "EMP": 10, "PROG": -25, "PYME": -20},
        "Scioli Presidente": {"emoji": "🦾", "FG": 30, "TR": 10, "ET": 25, "PN": 25, "PC": 50, "PE": 25, "EA": -5, "CP": 50, "SO": 5, "REL": 25, "JUV": 25, "EMP": -10, "PROG": 25, "PYME": -10},
        "Bullrich Montonera": {"emoji": "💣", "FG": 0, "TR": 0, "ET": 0, "PN": 0, "PC": 0, "PE": 0, "EA": 0, "CP": 0, "SO": 0, "REL": 0, "JUV": 0, "EMP": 0, "PROG": 0, "PYME": 0},
        "Luis Juez (Mix)": {"emoji": "🌭", "FG": 5, "TR": -5, "ET": 5, "PN": -5, "PC": 5, "PE": -5, "EA": 5, "CP": 5, "SO": -5, "REL": 5, "JUV": 0, "EMP": 5, "PROG": 5, "PYME": -5},
        "Alberto Pandemia": {"emoji": "😷", "FG": 25, "TR": 25, "ET": 25, "PN": 25, "PC": 25, "PE": 25, "EA": 0, "CP": 25, "SO": 25, "REL": 25, "JUV": 25, "EMP": 25, "PROG": 25, "PYME": 25},
        "Cobos Vice": {"emoji": "🚫", "FG": 20, "TR": 20, "ET": 15, "PN": 75, "PC": 20, "PE": -25, "EA": 50, "CP": 15, "SO": 0, "REL": 10, "JUV": 0, "EMP": 25, "PROG": -25, "PYME": 25},
        "Lavagna Ministro": {"emoji": "🧦", "FG": 15, "TR": 50, "ET": 10, "PN": 50, "PC": 10, "PE": 25, "EA": 50, "CP": 50, "SO": 10, "REL": 25, "JUV": 0, "EMP": 50, "PROG": 0, "PYME": 50},
        "Cavallo 1 a 1": {"emoji": "💵", "FG": -5, "TR": 10, "ET": -50, "PN": -50, "PC": 20, "PE": -150, "EA": 50, "CP": 50, "SO": 10, "REL": 10, "JUV": 10, "EMP": 150, "PROG": -25, "PYME": -50},
        "Perón 3er Mandato": {"emoji": "👑", "FG": 20, "TR": 45, "ET": -25, "PN": 50, "PC": 10, "PE": 5, "EA": -50, "CP": 50, "SO": 150, "REL": 50, "JUV": -1574, "EMP": 15, "PROG": -1574, "PYME": 30},
        "Lousteau 125": {"emoji": "📉", "FG": -20, "TR": -50, "ET": 10, "PN": -150, "PC": 10, "PE": 35, "EA": -20, "CP": -30, "SO": 0, "REL": -20, "JUV": 10, "EMP": -50, "PROG": 25, "PYME": -50},
        "Cristina Presa": {"emoji": "⛓️", "FG": -30, "TR": -30, "ET": -30, "PN": -30, "PC": -30, "PE": -30, "EA": -30, "CP": -30, "SO": -30, "REL": -30, "JUV": -30, "EMP": -30, "PROG": -30, "PYME": -30},
        "Perón Exilio": {"emoji": "✈️", "FG": -72, "TR": 72, "ET": 72, "PN": 72, "PC": -72, "PE": 72, "EA": -72, "CP": 72, "SO": -72, "REL": -72, "JUV": 72, "EMP": -72, "PROG": 72, "PYME": 72},
        "Manuel Belgrano": {"emoji": "🇦🇷", "FG": 50, "TR": 75, "ET": 60, "PN": 55, "PC": 100, "PE": 55, "EA": 100, "CP": 100, "SO": 50, "REL": 50, "JUV": 50, "EMP": 0, "PROG": 50, "PYME": 0},
        "José de San Martín": {"emoji": "🗡️", "FG": 100, "TR": 75, "ET": 75, "PN": 75, "PC": 75, "PE": 75, "EA": 75, "CP": 75, "SO": 100, "REL": 75, "JUV": 75, "EMP": 75, "PROG": 75, "PYME": 75},
        "Cornelio Saavedra": {"emoji": "🎩", "FG": 75, "TR": 50, "ET": 50, "PN": 50, "PC": 50, "PE": 50, "EA": 50, "CP": 50, "SO": 100, "REL": 50, "JUV": 50, "EMP": 50, "PROG": 50, "PYME": 50},
        "Juana Azurduy": {"emoji": "⚔️", "FG": 25, "TR": 30, "ET": 20, "PN": 15, "PC": 40, "PE": 40, "EA": 0, "CP": 25, "SO": 25, "REL": 0, "JUV": 50, "EMP": 0, "PROG": 75, "PYME": 0},
        "Juan M. de Rosas": {"emoji": "🌹", "FG": 200, "TR": 10, "ET": 10, "PN": 50, "PC": 25, "PE": 25, "EA": -25, "CP": 5, "SO": 100, "REL": 100, "JUV": 25, "EMP": 0, "PROG": 10, "PYME": 0}
    }},
    "HIST": {"color": "#DAA520", "candidatos": {
        "Bernardino Rivadavia": {"emoji": "🪑", "FG": -50, "TR": 0, "ET": 25, "PN": -5, "PC": 35, "PE": 10, "EA": 20, "CP": -10, "SO": 20, "REL": 25, "JUV": 0, "EMP": 40, "PROG": -20, "PYME": 0},
        "Vicente López": {"emoji": "🎶", "FG": 10, "TR": 0, "ET": 10, "PN": 0, "PC": 5, "PE": 5, "EA": 5, "CP": 0, "SO": 5, "REL": 10, "JUV": -20, "EMP": 5, "PROG": 0, "PYME": 5},
        "Justo José de Urquiza": {"emoji": "🚜", "FG": 40, "TR": -15, "ET": 10, "PN": 20, "PC": 35, "PE": 20, "EA": 5, "CP": -5, "SO": 25, "REL": 15, "JUV": -30, "EMP": 0, "PROG": 0, "PYME": 15},
        "Santiago Derqui": {"emoji": "📉", "FG": 10, "TR": 0, "ET": 5, "PN": 0, "PC": -10, "PE": -5, "EA": 0, "CP": 0, "SO": -10, "REL": 5, "JUV": -25, "EMP": 0, "PROG": 0, "PYME": 0},
        "Juan E. Pedernera": {"emoji": "⚔️", "FG": -15, "TR": 5, "ET": 5, "PN": 5, "PC": 10, "PE": 10, "EA": 5, "CP": -5, "SO": 5, "REL": 5, "JUV": -20, "EMP": 0, "PROG": 0, "PYME": 5},
        "Bartolomé Mitre": {"emoji": "📰", "FG": -20, "TR": 10, "ET": 25, "PN": 30, "PC": 5, "PE": 20, "EA": 25, "CP": -15, "SO": 15, "REL": 20, "JUV": -25, "EMP": 15, "PROG": 10, "PYME": 20},
        "Domingo Sarmiento": {"emoji": "📚", "FG": -10, "TR": 20, "ET": 75, "PN": 30, "PC": -5, "PE": 15, "EA": 45, "CP": -10, "SO": 25, "REL": -10, "JUV": -15, "EMP": 10, "PROG": 20, "PYME": 15},
        "Nicolás Avellaneda": {"emoji": "🌾", "FG": -15, "TR": 20, "ET": 10, "PN": 25, "PC": 0, "PE": 10, "EA": 25, "CP": -10, "SO": 20, "REL": 20, "JUV": -20, "EMP": 25, "PROG": 5, "PYME": 15},
        "Julio A. Roca": {"emoji": "🦊", "FG": -15, "TR": 30, "ET": 20, "PN": 10, "PC": -30, "PE": -5, "EA": 15, "CP": 5, "SO": 65, "REL": 35, "JUV": -30, "EMP": 50, "PROG": -15, "PYME": 40},
        "Miguel Juárez Celman": {"emoji": "💸", "FG": -25, "TR": -10, "ET": -10, "PN": -30, "PC": 20, "PE": -10, "EA": 30, "CP": -15, "SO": -5, "REL": 20, "JUV": -25, "EMP": 30, "PROG": -20, "PYME": 10},
        "Carlos Pellegrini": {"emoji": "🏦", "FG": 10, "TR": 20, "ET": 25, "PN": 50, "PC": -20, "PE": 30, "EA": 0, "CP": 5, "SO": 10, "REL": 10, "JUV": 10, "EMP": 30, "PROG": 40, "PYME": 30},
        "Luis Sáenz Peña": {"emoji": "🛌", "FG": -15, "TR": -5, "ET": -10, "PN": -10, "PC": 20, "PE": -5, "EA": 20, "CP": -10, "SO": -45, "REL": 20, "JUV": -20, "EMP": 20, "PROG": 0, "PYME": 10},
        "José Uriburu": {"emoji": "🎩", "FG": 5, "TR": 0, "ET": -15, "PN": -10, "PC": 10, "PE": 20, "EA": 20, "CP": -5, "SO": 35, "REL": 35, "JUV": -10, "EMP": 30, "PROG": -15, "PYME": 5},
        "Manuel Quintana": {"emoji": "👴", "FG": -20, "TR": 5, "ET": 10, "PN": 10, "PC": 10, "PE": 10, "EA": 10, "CP": 10, "SO": 10, "REL": -20, "JUV": 10, "EMP": 10, "PROG": 10, "PYME": 10},
        "Figueroa Alcorta": {"emoji": "🏛️", "FG": -5, "TR": 20, "ET": 30, "PN": 25, "PC": -15, "PE": 5, "EA": -20, "CP": -5, "SO": 10, "REL": 0, "JUV": -40, "EMP": 15, "PROG": 5, "PYME": 25},
        "Roque Sáenz Peña": {"emoji": "🗳️", "FG": 10, "TR": 25, "ET": 35, "PN": 10, "PC": 10, "PE": 10, "EA": 10, "CP": 10, "SO": 0, "REL": 5, "JUV": -5, "EMP": 10, "PROG": 15, "PYME": 15},
        "Victorino de la Plaza": {"emoji": "🇬🇧", "FG": -10, "TR": 15, "ET": 15, "PN": 20, "PC": -5, "PE": 15, "EA": 20, "CP": -20, "SO": 15, "REL": 20, "JUV": -40, "EMP": 20, "PROG": 10, "PYME": 5},
        "Hipólito Yrigoyen": {"emoji": "🤠", "FG": 25, "TR": 35, "ET": 30, "PN": 25, "PC": 20, "PE": 30, "EA": 15, "CP": -5, "SO": -20, "REL": 10, "JUV": 20, "EMP": 10, "PROG": 15, "PYME": 5},
        "Marcelo T. de Alvear": {"emoji": "🎭", "FG": 0, "TR": 5, "ET": 10, "PN": -5, "PC": 15, "PE": 10, "EA": 30, "CP": -10, "SO": 5, "REL": 0, "JUV": 5, "EMP": 10, "PROG": 20, "PYME": 15},
        "Agustín P. Justo": {"emoji": "🌉", "FG": -10, "TR": 5, "ET": 10, "PN": 20, "PC": -10, "PE": 10, "EA": 25, "CP": -15, "SO": 20, "REL": 10, "JUV": -25, "EMP": 25, "PROG": -10, "PYME": 20},
        "Roberto Ortiz": {"emoji": "🤒", "FG": 10, "TR": -10, "ET": 15, "PN": 10, "PC": -25, "PE": 10, "EA": 15, "CP": -30, "SO": 5, "REL": 0, "JUV": -20, "EMP": 10, "PROG": 10, "PYME": 5},
        "Ramón Castillo": {"emoji": "⛴️", "FG": -15, "TR": -10, "ET": -10, "PN": 20, "PC": -20, "PE": 10, "EA": 30, "CP": -20, "SO": 25, "REL": 25, "JUV": -35, "EMP": 15, "PROG": -15, "PYME": 5},
        "Juan D. Perón": {"emoji": "✌️", "FG": 20, "TR": 45, "ET": 20, "PN": 40, "PC": 10, "PE": 40, "EA": -50, "CP": 75, "SO": 10, "REL": 10, "JUV": 10, "EMP": 10, "PROG": 50, "PYME": 25},
        "Arturo Frondizi": {"emoji": "🛢️", "FG": 15, "TR": 10, "ET": 15, "PN": 50, "PC": -10, "PE": 10, "EA": 5, "CP": 0, "SO": 5, "REL": -5, "JUV": -20, "EMP": 20, "PROG": 5, "PYME": 20},
        "José María Guido": {"emoji": "🖊️", "FG": -15, "TR": -10, "ET": -5, "PN": -5, "PC": -10, "PE": 5, "EA": 40, "CP": -25, "SO": 20, "REL": 20, "JUV": -25, "EMP": 10, "PROG": -10, "PYME": 5},
        "Arturo Illia": {"emoji": "🐢", "FG": 30, "TR": 5, "ET": 25, "PN": -5, "PC": 10, "PE": 15, "EA": 30, "CP": -15, "SO": -10, "REL": 0, "JUV": -15, "EMP": -5, "PROG": 20, "PYME": 15},
        "Héctor Cámpora": {"emoji": "🦷", "FG": -25, "TR": 10, "ET": 5, "PN": 10, "PC": -10, "PE": 10, "EA": -50, "CP": 30, "SO": 5, "REL": -10, "JUV": 35, "EMP": -10, "PROG": 20, "PYME": 10},
        "Raúl Lastiri": {"emoji": "👔", "FG": -20, "TR": 5, "ET": 5, "PN": 5, "PC": 0, "PE": 10, "EA": -40, "CP": 30, "SO": 0, "REL": 5, "JUV": -15, "EMP": 5, "PROG": 15, "PYME": 10},
        "Isabel Perón": {"emoji": "💃", "FG": -35, "TR": -10, "ET": -10, "PN": -10, "PC": 10, "PE": 15, "EA": -45, "CP": 30, "SO": -25, "REL": 10, "JUV": -25, "EMP": -10, "PROG": 10, "PYME": 5},
        "Raúl Alfonsín": {"emoji": "🗣️", "FG": 40, "TR": 10, "ET": 25, "PN": 5, "PC": 30, "PE": 5, "EA": 20, "CP": -5, "SO": -20, "REL": -10, "JUV": -15, "EMP": -5, "PROG": 20, "PYME": 15},
        "Carlos Menem": {"emoji": "🚀", "FG": 25, "TR": -15, "ET": -20, "PN": -40, "PC": 30, "PE": -20, "EA": 10, "CP": 20, "SO": 10, "REL": 5, "JUV": -10, "EMP": 40, "PROG": -25, "PYME": 15},
        "Fernando de la Rúa": {"emoji": "📉", "FG": 15, "TR": -30, "ET": 0, "PN": -10, "PC": 25, "PE": -15, "EA": 15, "CP": -5, "SO": -10, "REL": 0, "JUV": -30, "EMP": 15, "PROG": -20, "PYME": -10},
        "A. Rodriguez Saa": {"emoji": "🏞️", "FG": -5, "TR": -35, "ET": 5, "PN": 30, "PC": -15, "PE": 10, "EA": -30, "CP": 5, "SO": 15, "REL": 10, "JUV": -25, "EMP": 5, "PROG": 5, "PYME": 10},
        "Eduardo Duhalde": {"emoji": "♟️", "FG": 10, "TR": 5, "ET": -15, "PN": 5, "PC": 10, "PE": 5, "EA": -30, "CP": 5, "SO": 30, "REL": 5, "JUV": -30, "EMP": 15, "PROG": 10, "PYME": 10},
        "Néstor Kirchner": {"emoji": "🐧", "FG": 15, "TR": 20, "ET": 20, "PN": 20, "PC": -20, "PE": 25, "EA": -45, "CP": 25, "SO": -10, "REL": -5, "JUV": 15, "EMP": -10, "PROG": 15, "PYME": 10}
    }}
}

PRESUPUESTO_INICIAL = 250000
RENTA_BASE_TURNO = 250000

# --- LÓGICA DE JUEGO ---

def get_candidate_stats(cand_name):
    for p in PARTIDOS.values():
        if cand_name in p["candidatos"]:
            return p["candidatos"][cand_name]
    return {}

def get_total_money(cand):
    if cand in st.session_state.p:
        w = st.session_state.p[cand]["wallets"]
        return sum(w.values())
    return 0

def update_owners():
    # Provincias
    for p in MAPA_DATA:
        slots = st.session_state.slots[p]
        max_fichas = max(slots.values()) if slots else 0
        if max_fichas > 0:
            lideres = [c for c, q in slots.items() if q == max_fichas]
            curr = st.session_state.owners[p]
            if curr not in lideres:
                st.session_state.owners[p] = lideres[0]
        else:
            st.session_state.owners[p] = None
            
    # Grupos Sociales
    for g in SOCIAL_GROUPS:
        slots = st.session_state.social_slots[g]
        max_f = max(slots.values()) if slots else 0
        if max_f >= 3:
            lideres = [c for c, q in slots.items() if q == max_f]
            curr = st.session_state.social_owners[g]
            if curr not in lideres:
                st.session_state.social_owners[g] = lideres[0]
        else:
            st.session_state.social_owners[g] = None

def update_votos():
    update_owners()
    votos = {c: 0 for c in st.session_state.p}
    for p, owner in st.session_state.owners.items():
        if owner and owner in votos: votos[owner] += MAPA_DATA[p]["votos"]
    st.session_state.votos_resolved = votos

def check_solvencia(cand, entity, cantidad, is_social=False):
    if is_social:
        costo = SOCIAL_GROUPS[entity]["costo"] * cantidad
        wallets = st.session_state.p[cand]["wallets"]
        return wallets["base"] >= costo
    else:
        costo_total = COSTOS_FIJOS[entity] * cantidad
        wallets = st.session_state.p[cand]["wallets"]
        disponible = wallets["base"]
        for g in PROV_TO_GROUP_RAW.get(entity, []):
            disponible += wallets.get(g, 0)
        return disponible >= costo_total

def gastar_dinero(cand, entity, cantidad, is_social=False):
    wallets = st.session_state.p[cand]["wallets"]
    if is_social:
        costo = SOCIAL_GROUPS[entity]["costo"] * cantidad
        wallets["base"] -= costo
    else:
        costo_total = COSTOS_FIJOS[entity] * cantidad
        grupos_prov = PROV_TO_GROUP_RAW.get(entity, [])
        for g in grupos_prov:
            if costo_total <= 0: break
            if wallets.get(g, 0) > 0:
                deduccion = min(costo_total, wallets[g])
                wallets[g] -= deduccion
                costo_total -= deduccion
        if costo_total > 0:
            wallets["base"] -= costo_total

def check_election_readiness():
    for p in MAPA_DATA:
        if sum(st.session_state.slots[p].values()) == 0:
            return False
    return True

def eliminar_candidato(nombre):
    if nombre in st.session_state.p:
        del st.session_state.p[nombre]
    for p in MAPA_DATA:
        if nombre in st.session_state.slots[p]: del st.session_state.slots[p][nombre]
    for g in SOCIAL_GROUPS:
        if nombre in st.session_state.social_slots[g]: del st.session_state.social_slots[g][nombre]
    update_owners()

def calcular_control_grupos():
    fuerza_grupos = {code: {c: 0 for c in st.session_state.p} for code in STATE_GROUPS}
    total_votos_grupo = {code: 0 for code in STATE_GROUPS}

    for p_name, p_data in MAPA_DATA.items():
        grupos_prov = PROV_TO_GROUP_RAW.get(p_name, [])
        for g in grupos_prov:
            total_votos_grupo[g] += p_data["votos"]

    for p_name, owner in st.session_state.owners.items():
        if not owner or owner not in st.session_state.p: continue
        
        grupos_prov = PROV_TO_GROUP_RAW.get(p_name, [])
        fichas = st.session_state.slots[p_name][owner]
        if fichas < 3: continue
        
        multiplicador = 1.5 if fichas >= 8 else 1.0
        fuerza = MAPA_DATA[p_name]["votos"] * multiplicador
        
        for g in grupos_prov:
            fuerza_grupos[g][owner] += fuerza

    return fuerza_grupos, total_votos_grupo

def procesar_turno():
    reporte = []
    mi_nombre = next(c for c, i in st.session_state.p.items() if not i["is_ia"])
    
    inversiones_turno = {p: {} for p in MAPA_DATA}
    inv_social = {g: {} for g in SOCIAL_GROUPS}
    
    # 1. IA
    for cand, info in st.session_state.p.items():
        if info["is_ia"]:
            # SOCIAL
            for g in SOCIAL_GROUPS:
                curr = st.session_state.social_slots[g].get(cand, 0)
                should_buy = (curr > 0 and curr < 3) or (curr == 0 and (get_total_money(cand) > 350000 or st.session_state.turno < 8))
                
                if should_buy and curr < 3:
                    needed = 3 - curr
                    if check_solvencia(cand, g, needed, True):
                        inv_social[g][cand] = needed
                        gastar_dinero(cand, g, needed, True)

            # PROVINCIAS
            attempts = 0
            while get_total_money(cand) > 15000 and attempts < 30:
                posibles = [p for p in MAPA_DATA if not st.session_state.hard_locked[p] and st.session_state.slots[p].get(cand, 0) < 10]
                if not posibles: break
                
                weights = [MAPA_DATA[p]["votos"] for p in posibles]
                target = random.choices(posibles, weights=weights, k=1)[0]
                
                curr = st.session_state.slots[target].get(cand, 0)
                has_landed = cand in st.session_state.landed_status.get(target, [])
                
                limit = 2 if (curr==0 and not has_landed) else (10-curr)
                qty = 0
                for q in range(limit, 0, -1):
                    prev = inversiones_turno[target].get(cand, 0)
                    if (curr + prev + q) <= 10 and check_solvencia(cand, target, q, False):
                        qty = q
                        break
                
                if qty > 0:
                    inversiones_turno[target][cand] = inversiones_turno[target].get(cand, 0) + qty
                    gastar_dinero(cand, target, qty, False)
                    if target not in st.session_state.landed_status: st.session_state.landed_status[target] = []
                    if cand not in st.session_state.landed_status[target]: st.session_state.landed_status[target].append(cand)
                
                attempts += 1

    # 2. USUARIO
    for ent, cant in st.session_state.pending_user.items():
        if cant > 0:
            if ent in SOCIAL_GROUPS:
                inv_social[ent][mi_nombre] = cant
                gastar_dinero(mi_nombre, ent, cant, True)
            else:
                inversiones_turno[ent][mi_nombre] = cant
                gastar_dinero(mi_nombre, ent, cant, False)
                if ent not in st.session_state.landed_status: st.session_state.landed_status[ent] = []
                if mi_nombre not in st.session_state.landed_status[ent]: st.session_state.landed_status[ent].append(mi_nombre)

    # 3. RESOLUCIÓN
    def resolver(target_dict, slots_state, hard_lock=False):
        for ent, invs in target_dict.items():
            if not invs: continue
            by_qty = {}
            for c, q in invs.items():
                if q not in by_qty: by_qty[q] = []
                by_qty[q].append(c)
            
            for q, cands in by_qty.items():
                if len(cands) == 1:
                    winner = cands[0]
                    slots_state[ent][winner] = slots_state[ent].get(winner, 0) + q
                    if hard_lock and slots_state[ent][winner] >= 10:
                        st.session_state.hard_locked[ent] = True
                else:
                    reporte.append(f"💥 **{ent}**: Choque de {q} fichas.")
                    if ent in MAPA_DATA:
                        for c in cands:
                            if ent not in st.session_state.landed_status: st.session_state.landed_status[ent] = []
                            if c not in st.session_state.landed_status[ent]: st.session_state.landed_status[ent].append(c)

    resolver(inversiones_turno, st.session_state.slots, True)
    resolver(inv_social, st.session_state.social_slots, False)
    update_owners()

    # 4. RENTAS
    fuerza_grupos, total_votos_group = calcular_control_grupos()
    
    for c in st.session_state.p:
        st.session_state.p[c]["wallets"]["base"] += RENTA_BASE_TURNO
        stats = get_candidate_stats(c)
        for g, data in STATE_GROUPS.items():
            if fuerza_grupos[g][c] > (total_votos_group[g] * 0.5):
                mod = stats.get(g, 0) / 100.0
                monto = int(data["renta"] * (1 + mod))
                st.session_state.p[c]["wallets"][g] = st.session_state.p[c]["wallets"].get(g, 0) + monto
                reporte.append(f"💰 {c} recibe ${monto:,} de **{data['nombre']}**")
        for g, data in SOCIAL_GROUPS.items():
            if st.session_state.social_owners[g] == c:
                mod = stats.get(g, 0) / 100.0
                monto = int(data["renta"] * (1 + mod))
                st.session_state.p[c]["wallets"]["base"] += monto
                reporte.append(f"🗣️ {c} recibe ${monto:,} de **{data['nombre']}**")

    st.session_state.last_report = reporte
    st.session_state.pending_user = {}
    st.session_state.turno += 1
    
    if check_election_readiness() and st.session_state.turno % 4 == 0:
        st.session_state.modo_eleccion = True

# --- 3. INICIALIZACIÓN ---
if 'p' not in st.session_state:
    st.session_state.p = {}
    st.session_state.game_started = False

# --- 4. INTERFAZ UI ---
if not st.session_state.game_started:
    st.title("Rosca Política: 136")
    try: st.image("rosca politica.jpg", use_container_width=True)
    except: pass
    
    c1, c2 = st.columns(2)
    p_sel = c1.selectbox("Partido", list(PARTIDOS.keys()))
    c_sel = c1.selectbox("Candidato", list(PARTIDOS[p_sel]["candidatos"].keys()))
    all_cands = [c for p in PARTIDOS.values() for c in p["candidatos"] if c != c_sel]
    ias = c2.multiselect("Rivales (Máx 4)", all_cands, max_selections=4)
    
    st.markdown(f"### 📊 Estadísticas de {c_sel}")
    stats = get_candidate_stats(c_sel)
    
    col_t, col_s = st.columns(2)
    with col_t:
        st.subheader("Territoriales")
        for k, v in stats.items():
            if k in STATE_GROUPS:
                st.metric(STATE_GROUPS[k]["nombre"], f"{v:+}%")
    with col_s:
        st.subheader("Sociales")
        for k, v in stats.items():
            if k in SOCIAL_GROUPS:
                st.metric(SOCIAL_GROUPS[k]["nombre"], f"{v:+}%")

    if st.button("JUGAR"):
        if not ias: st.error("Faltan rivales")
        else:
            jugadores = [c_sel] + ias
            st.session_state.p = {c: {"is_ia": c!=c_sel, "wallets": {"base": PRESUPUESTO_INICIAL}} for c in jugadores}
            st.session_state.slots = {p: {} for p in MAPA_DATA}
            st.session_state.owners = {p: None for p in MAPA_DATA}
            st.session_state.social_slots = {g: {} for g in SOCIAL_GROUPS}
            st.session_state.social_owners = {g: None for g in SOCIAL_GROUPS}
            st.session_state.hard_locked = {p: False for p in MAPA_DATA}
            st.session_state.landed_status = {p: [] for p in MAPA_DATA}
            st.session_state.pending_user = {}
            st.session_state.turno = 1
            st.session_state.modo_eleccion = False
            st.session_state.winner = None
            st.session_state.loser = None
            st.session_state.last_report = []
            st.session_state.selected_prov = None
            st.session_state.game_started = True
            st.rerun()

elif st.session_state.modo_eleccion:
    st.title("🗳️ ELECCIONES")
    update_votos()
    votos = st.session_state.votos_resolved
    sorted_v = sorted(votos.items(), key=lambda x: x[1], reverse=True)
    
    for c, v in sorted_v:
        st.write(f"**{c}**: {v} votos")
        st.progress(min(v/130, 1.0))
        
    eliminado = sorted_v[-1][0]
    st.error(f"{eliminado} eliminado.")
    
    if st.button("SIGUIENTE"):
        mi_name = next(c for c, i in st.session_state.p.items() if not i["is_ia"])
        if sorted_v[0][1] >= 129:
            if sorted_v[0][0] == mi_name: st.session_state.winner = "GANASTE"
            else: st.session_state.loser = "PERDISTE"
        elif eliminado == mi_name:
            st.session_state.loser = "ELIMINADO"
        else:
            eliminar_candidato(eliminado)
            st.session_state.modo_eleccion = False
        st.rerun()

elif st.session_state.winner or st.session_state.loser:
    st.title(st.session_state.winner or st.session_state.loser)
    if st.button("REINICIAR"):
        st.session_state.game_started = False
        st.rerun()

else:
    mi_nombre = next(c for c, i in st.session_state.p.items() if not i["is_ia"])
    
    # SIDEBAR
    st.sidebar.title(f"Turno {st.session_state.turno}")
    
    tab_rank, tab_spy, tab_terr = st.sidebar.tabs(["📊 Ranking", "🕵️ Espionaje", "🏳️ Territorio"])
    
    with tab_rank:
        update_votos()
        for c in st.session_state.p:
            v = st.session_state.votos_resolved.get(c, 0)
            d = get_total_money(c)
            st.write(f"**{c}**: {v} votos | ${d:,}")
            
    with tab_spy:
        target = st.sidebar.selectbox("Ver:", list(st.session_state.p.keys()))
        stats = get_candidate_stats(target)
        for k, v in stats.items():
            if k != "emoji":
                name = STATE_GROUPS.get(k, {}).get("nombre", SOCIAL_GROUPS.get(k, {}).get("nombre", k))
                col = "green" if v > 0 else "red"
                st.sidebar.markdown(f":{col}[{name}: {v:+}%]")

    with tab_terr:
        fuerza_grupos, total_votos_g = calcular_control_grupos()
        for g, data in STATE_GROUPS.items():
            with st.sidebar.expander(f"{data['color']} {data['nombre']}"):
                total = total_votos_g[g]
                if total > 0:
                    for c, f in sorted(fuerza_grupos[g].items(), key=lambda x: x[1], reverse=True):
                        if f > 0:
                            pct = f / total
                            st.write(f"{c}: {int(pct*100)}%")
                            st.progress(min(pct, 1.0))

    # MAIN
    try: st.image("rosca politica.jpg", use_container_width=True)
    except: pass
    
    gasto_total = 0
    for ent, cant in st.session_state.pending_user.items():
        if ent in MAPA_DATA:
            gasto_total += COSTOS_FIJOS[ent] * cant
        else:
            gasto_total += SOCIAL_GROUPS[ent]["costo"] * cant
            
    dinero_disp = get_total_money(mi_nombre)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("CAJA", f"${dinero_disp:,}")
    c2.metric("GASTO", f"${gasto_total:,}", delta_color="inverse")
    if c3.button("JUGAR TURNO", type="primary"):
        if gasto_total > dinero_disp: st.error("No alcanza")
        else: procesar_turno(); st.rerun()

    tab1, tab2 = st.tabs(["🗺️ Mapa", "🗣️ Grupos Sociales"])

    with tab1:
        if st.session_state.selected_prov is None:
            for r in range(12):
                cols = st.columns(5)
                for c in range(5):
                    p_n = next((n for n, d in MAPA_DATA.items() if d["pos"] == (r, c)), None)
                    if p_n:
                        own = st.session_state.owners[p_n]
                        e = get_candidate_stats(own)["emoji"] if own else "⬜"
                        grps = PROV_TO_GROUP_RAW.get(p_n, [])
                        dots = "".join([STATE_GROUPS[g]["color"] for g in grps])
                        cost_k = int(COSTOS_FIJOS[p_n]/1000)
                        if cols[c].button(f"{dots} {e} {p_n}\n${cost_k}k", key=p_n):
                            st.session_state.selected_prov = p_n; st.rerun()
        else:
            p = st.session_state.selected_prov
            st.button("🔙", on_click=lambda: setattr(st.session_state, 'selected_prov', None))
            st.header(p)
            
            my_w = st.session_state.p[mi_nombre]["wallets"]
            st.write(f"Base: ${my_w['base']:,}")
            valid_groups = PROV_TO_GROUP_RAW.get(p, [])
            disp_prov = my_w['base']
            for g in valid_groups:
                if my_w.get(g, 0) > 0:
                    st.write(f"+ {g}: ${my_w[g]:,}")
                    disp_prov += my_w[g]
                
            curr = st.session_state.slots[p].get(mi_nombre, 0)
            pend = st.session_state.pending_user.get(p, 0)
            landed = mi_nombre in st.session_state.landed_status[p]
            costo = COSTOS_FIJOS[p]
            
            limit_add = 10 - curr
            if curr == 0 and not landed: limit_add = min(limit_add, 2)
            
            can_afford = (disp_prov - (gasto_total - (costo*pend) if p in st.session_state.pending_user else gasto_total)) >= costo

            if st.button("➕") and pend < limit_add:
                if can_afford:
                    st.session_state.pending_user[p] = pend + 1
                    st.rerun()
                else: st.error("Sin fondos")
            
            if st.button("➖") and pend > 0:
                st.session_state.pending_user[p] -= 1; st.rerun()
                
            st.write(f"Inversión: {pend} (Total futura: {curr+pend})")
            st.divider()
            for c, q in st.session_state.slots[p].items():
                st.write(f"{c}: {q}")
                st.progress(q/10)

    with tab2:
        for g_code, data in SOCIAL_GROUPS.items():
            with st.container():
                c_img, c_info, c_act = st.columns([1, 3, 2])
                c_img.write(f"## {data['color']}")
                with c_info:
                    st.write(f"**{data['nombre']}**")
                    st.caption(f"Renta: ${data['renta']:,} | Costo: ${data['costo']:,}")
                    own = st.session_state.social_owners[g_code]
                    st.write(f"Líder: **{own if own else 'Nadie'}**")
                    
                    has_fichas = False
                    for c, q in st.session_state.social_slots[g_code].items():
                        if q > 0:
                            has_fichas = True
                            plus = f"(+{st.session_state.pending_user.get(g_code,0)})" if c == mi_nombre else ""
                            st.write(f"{c}: {q} {plus}")
                            st.progress(q/10)
                    if not has_fichas: st.write("-")

                with c_act:
                    curr = st.session_state.social_slots[g_code].get(mi_nombre, 0)
                    pend = st.session_state.pending_user.get(g_code, 0)
                    costo = data['costo']
                    
                    has_landed = mi_nombre in st.session_state.landed_status.get(g_code, [])
                    limit_add = 10 - curr
                    if curr == 0 and not has_landed: limit_add = min(limit_add, 2)
                    
                    can_afford = (st.session_state.p[mi_nombre]["wallets"]["base"] - (gasto_total - costo*pend)) >= costo

                    if st.button("➕", key=f"add_{g_code}") and pend < limit_add:
                        if can_afford:
                            st.session_state.pending_user[g_code] = pend + 1
                            st.rerun()
                        else: st.error("No alcanza")
                            
                    if st.button("➖", key=f"rem_{g_code}") and pend > 0:
                        st.session_state.pending_user[g_code] -= 1
                        st.rerun()
                st.divider()

    st.divider()
    st.subheader("🌐 Panorama Nacional")
    cols_global = st.columns(len(st.session_state.p))
    update_votos()
    sorted_global = sorted(st.session_state.votos_resolved.items(), key=lambda x: x[1], reverse=True)
    
    for i, (c, v) in enumerate(sorted_global):
        if c in st.session_state.p:
            with cols_global[i]:
                st.metric(f"{get_candidate_stats(c)['emoji']} {c}", f"{v} Votos", f"${get_total_money(c):,}")

    if st.session_state.last_report:
        with st.expander("Reporte"):
            for l in st.session_state.last_report: st.write(l)