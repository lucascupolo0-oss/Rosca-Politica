import streamlit as st
import random

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Rosca Política: 189", layout="wide", page_icon="🇦🇷")

# --- VARIABLES GLOBALES ---
PRESUPUESTO_INICIAL = 250000
RENTA_BASE_TURNO = 250000
VOTOS_PARA_GANAR = 189 

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
    
    /* Pantallas Finales y Avisos */
    .win-msg {
        font-size: 40px; font-weight: 800; color: #155724; text-align: center;
        padding: 30px; border: 3px solid #c3e6cb; border-radius: 15px;
        background-color: #d4edda; margin-bottom: 20px;
    }
    .lose-msg {
        font-size: 40px; font-weight: 800; color: #721c24; text-align: center;
        padding: 30px; border: 3px solid #f5c6cb; border-radius: 15px;
        background-color: #f8d7da; margin-bottom: 20px;
    }
    .warning-msg {
        font-size: 30px; font-weight: 700; color: #856404; text-align: center;
        padding: 20px; border: 3px solid #ffeeba; border-radius: 15px;
        background-color: #fff3cd; margin-bottom: 20px;
    }
    /* Estilos para Caja y Gastos */
    .money-box {
        background-color: #e8f5e9;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #c8e6c9;
    }
    .expense-box {
        background-color: #ffebee;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #ffcdd2;
    }
    .money-title { font-weight: bold; font-size: 1.2rem; margin-bottom: 5px; }
    .money-item { font-family: monospace; font-size: 1rem; }
    </style>
""", unsafe_allow_html=True)

# --- 1. GRUPOS ---
STATE_GROUPS = {
    "FG": {"nombre": "Federalismo y Gob.", "renta": 50000, "color": "🟢"},
    "TR": {"nombre": "Trabajo", "renta": 100000, "color": "🟠"},
    "ET": {"nombre": "Educación y Transp.", "renta": 50000, "color": "🔵"},
    "PN": {"nombre": "Producción Nac.", "renta": 100000, "color": "🟣"},
    "PC": {"nombre": "Prov. Cambiantes", "renta": 75000, "color": "⚪"},
    "PE": {"nombre": "Presencia Estatal", "renta": 75000, "color": "🟡"},
    "EA": {"nombre": "Eternos Anti-PJ", "renta": 100000, "color": "⬛"},
    "CP": {"nombre": "Clásicos Peronistas", "renta": 75000, "color": "🟦"}
}

SOCIAL_GROUPS = {
    "SO": {"nombre": "Seguridad y Orden", "costo": 75000, "renta": 37500, "color": "👮"},
    "REL": {"nombre": "Tradición y Religión", "costo": 50000, "renta": 25000, "color": "✝️"},
    "JUV": {"nombre": "Juventud y Redes", "costo": 50000, "renta": 25000, "color": "📱"},
    "EMP": {"nombre": "Banca Empresarial", "costo": 100000, "renta": 50000, "color": "💼"},
    "PROG": {"nombre": "Progresismo y Sind.", "costo": 100000, "renta": 50000, "color": "✊"},
    "PYME": {"nombre": "Comerciantes y PyMEs", "costo": 75000, "renta": 37500, "color": "🏪"}
}

# --- 2. MAPA DE GRUPOS ---
PROV_TO_GROUP_RAW = {
    "Jujuy": ["PE", "EA"],
    "Formosa": ["PE", "CP"],
    "Salta": ["FG", "PC"],
    "Chaco": ["PE", "CP"],
    "Misiones": ["FG", "PN"],
    "Tucumán": ["FG", "PN", "CP"],
    "Santiago del Estero": ["CP"],
    "Corrientes": ["EA"],
    "La Rioja": ["PE", "CP"],
    "Catamarca": ["PN", "PE", "CP"],
    "San Juan": ["PN", "CP"],
    "Santa Fe": ["FG", "ET", "PN", "PC"],
    "Entre Ríos": ["PN", "PC"],
    "San Luis": ["PC", "CP"], 
    "Córdoba": ["FG", "ET", "PN", "EA"],
    "PBA Norte": ["FG", "TR", "ET"],
    "CABA": ["FG", "TR", "ET", "EA"],
    "Mendoza": ["FG", "ET", "PN"],
    "PBA Oeste": ["FG", "PE", "CP"],
    "PBA Centro": ["ET", "PN"], 
    "La Pampa": ["PE", "CP"],
    "PBA Costa": ["TR", "ET"],
    "Neuquén": ["TR", "PN", "PC"], 
    "Río Negro": ["TR", "EA"],
    "Chubut": ["TR", "PN", "PC"], 
    "Santa Cruz": ["PN", "PE", "CP"],
    "Tierra del Fuego": ["TR", "PE"]
}

# --- 3. COSTOS FIJOS ---
COSTOS_FIJOS = {
    "Jujuy": 20000, "Formosa": 15000, "Salta": 35000, "Chaco": 25000,
    "Misiones": 35000, "Tucumán": 75000, "Santiago del Estero": 30000,
    "Corrientes": 30000, "La Rioja": 10000, "Catamarca": 12500,
    "San Juan": 25000, "Santa Fe": 200000, "Entre Ríos": 37500,
    "San Luis": 15000, "Córdoba": 200000, "PBA Norte": 125000,
    "CABA": 150000, "Mendoza": 75000, "PBA Oeste": 200000,
    "PBA Centro": 50000, "La Pampa": 12500, "PBA Costa": 35000,
    "Neuquén": 22500, "Río Negro": 25000, "Chubut": 20000,
    "Santa Cruz": 10000, "Tierra del Fuego": 10000
}

# --- 4. MAPA DE VOTOS Y POSICIONES ---
MAPA_DATA = {
    "Jujuy": {"votos": 8, "pos": (0, 1)}, 
    "Formosa": {"votos": 6, "pos": (0, 3)},
    "Salta": {"votos": 14, "pos": (1, 1)}, 
    "Chaco": {"votos": 11, "pos": (1, 3)},
    "Misiones": {"votos": 13, "pos": (1, 4)}, 
    "Tucumán": {"votos": 17, "pos": (2, 1)},
    "Santiago del Estero": {"votos": 11, "pos": (2, 2)}, 
    "Corrientes": {"votos": 12, "pos": (2, 3)},
    "La Rioja": {"votos": 4, "pos": (3, 0)}, 
    "Catamarca": {"votos": 4, "pos": (3, 1)},
    "San Juan": {"votos": 8, "pos": (4, 0)}, 
    "Santa Fe": {"votos": 36, "pos": (4, 2)},
    "Entre Ríos": {"votos": 14, "pos": (4, 3)}, 
    "San Luis": {"votos": 6, "pos": (5, 0)},
    "Córdoba": {"votos": 40, "pos": (5, 1)}, 
    "PBA Norte": {"votos": 28, "pos": (5, 2)},
    "CABA": {"votos": 31, "pos": (5, 3)}, 
    "Mendoza": {"votos": 20, "pos": (6, 0)},
    "PBA Oeste": {"votos": 35, "pos": (6, 1)}, 
    "PBA Centro": {"votos": 15, "pos": (6, 2)},
    "La Pampa": {"votos": 4, "pos": (7, 1)}, 
    "PBA Costa": {"votos": 12, "pos": (7, 2)},
    "Neuquén": {"votos": 7, "pos": (8, 0)}, 
    "Río Negro": {"votos": 8, "pos": (8, 1)},
    "Chubut": {"votos": 6, "pos": (9, 1)}, 
    "Santa Cruz": {"votos": 3, "pos": (10, 1)},
    "Tierra del Fuego": {"votos": 3, "pos": (11, 1)}
}

# --- CANDIDATOS ---
PARTIDOS = {
    "PJ": {"color": "🔵", "candidatos": {
        "Cristina Kirchner": {"emoji": "✌️", "FG": 10, "TR": 15, "ET": 15, "PN": 15, "PC": -25, "PE": 20, "EA": -45, "CP": 15, "SO": -15, "REL": -5, "JUV": -5, "EMP": -25, "PROG": 30, "PYME": 10},
        "Juan Schiaretti": {"emoji": "🧱", "FG": 20, "TR": 0, "ET": -5, "PN": 5, "PC": 10, "PE": -10, "EA": -5, "CP": 10, "SO": 10, "REL": 5, "JUV": -5, "EMP": 20, "PROG": -15, "PYME": 35},
        "Juan Grabois": {"emoji": "🌱", "FG": -10, "TR": 10, "ET": 30, "PN": 0, "PC": -10, "PE": 30, "EA": -25, "CP": 5, "SO": -25, "REL": 15, "JUV": 30, "EMP": -30, "PROG": 35, "PYME": -10},
        "Guillermo Moreno": {"emoji": "🌭", "FG": 10, "TR": 0, "ET": -10, "PN": 5, "PC": 0, "PE": 5, "EA": -50, "CP": 30, "SO": 10, "REL": 40, "JUV": 5, "EMP": -5, "PROG": -5, "PYME": 15},
        "Axel Kicillof": {"emoji": "🚗", "FG": -5, "TR": 0, "ET": 15, "PN": 0, "PC": -5, "PE": 35, "EA": -30, "CP": 5, "SO": -10, "REL": 20, "JUV": 20, "EMP": -10, "PROG": 20, "PYME": 10},
        "Máximo Kirchner": {"emoji": "🎮", "FG": -10, "TR": -10, "ET": 10, "PN": 5, "PC": -35, "PE": 20, "EA": -40, "CP": 5, "SO": -30, "REL": -10, "JUV": 0, "EMP": -20, "PROG": 25, "PYME": -15},
        "Sergio Massa": {"emoji": "🐯", "FG": 25, "TR": -10, "ET": 20, "PN": 0, "PC": 10, "PE": 10, "EA": -25, "CP": -5, "SO": 20, "REL": 10, "JUV": 5, "EMP": 30, "PROG": 15, "PYME": 25},
        "Florencio Randazzo": {"emoji": "🚆", "FG": 15, "TR": 5, "ET": -5, "PN": 10, "PC": -10, "PE": -15, "EA": 0, "CP": -10, "SO": -10, "REL": 5, "JUV": -5, "EMP": 20, "PROG": -5, "PYME": 15},
        "Alberto Fernandez": {"emoji": "🎸", "FG": 20, "TR": -25, "ET": 5, "PN": -10, "PC": 5, "PE": 15, "EA": -10, "CP": -5, "SO": -15, "REL": -15, "JUV": -25, "EMP": 5, "PROG": 30, "PYME": 10},
        "Leandro Santoro": {"emoji": "🏙️", "FG": 10, "TR": -20, "ET": 10, "PN": 5, "PC": 10, "PE": 10, "EA": 5, "CP": 5, "SO": -5, "REL": 20, "JUV": 10, "EMP": -10, "PROG": 30, "PYME": 5},
        "Fernando Gray": {"emoji": "📡", "FG": 15, "TR": -25, "ET": -10, "PN": 10, "PC": -30, "PE": 10, "EA": -55, "CP": 25, "SO": 5, "REL": 10, "JUV": -10, "EMP": 5, "PROG": -5, "PYME": 35},
        "Aníbal Fernández": {"emoji": "🧳", "FG": 30, "TR": -15, "ET": -5, "PN": -5, "PC": 15, "PE": 30, "EA": -40, "CP": 15, "SO": 35, "REL": 5, "JUV": -25, "EMP": -25, "PROG": -10, "PYME": -15},
        "Wado de Pedro": {"emoji": "🚜", "FG": -10, "TR": 10, "ET": 15, "PN": 20, "PC": -30, "PE": 25, "EA": -35, "CP": 5, "SO": -10, "REL": -20, "JUV": 10, "EMP": -15, "PROG": 30, "PYME": 10}
    }},
    "LLA": {"color": "🟣", "candidatos": {
        "Javier Milei": {"emoji": "🦁", "FG": 20, "TR": 35, "ET": -20, "PN": -20, "PC": 30, "PE": -50, "EA": 30, "CP": -20, "SO": 15, "REL": 25, "JUV": 35, "EMP": 35, "PROG": -50, "PYME": -5},
        "Patricia Bullrich": {"emoji": "🍷", "FG": 45, "TR": -10, "ET": -25, "PN": -20, "PC": 10, "PE": -30, "EA": 20, "CP": -50, "SO": 45, "REL": 30, "JUV": 5, "EMP": 20, "PROG": -40, "PYME": -10},
        "Ramiro Marra": {"emoji": "📉", "FG": -15, "TR": -20, "ET": -45, "PN": -35, "PC": 20, "PE": -60, "EA": 30, "CP": -10, "SO": 20, "REL": 10, "JUV": 55, "EMP": 40, "PROG": -50, "PYME": -15},
        "Manuel Adorni": {"emoji": "🎤", "FG": -15, "TR": -5, "ET": -20, "PN": 10, "PC": 30, "PE": -40, "EA": 20, "CP": -10, "SO": 5, "REL": -5, "JUV": 25, "EMP": 10, "PROG": -25, "PYME": 0},
        "Lilia Lemoine": {"emoji": "🍋", "FG": 5, "TR": -15, "ET": -40, "PN": -10, "PC": -40, "PE": -35, "EA": 10, "CP": -30, "SO": 0, "REL": -30, "JUV": 45, "EMP": -10, "PROG": -50, "PYME": -20},
        "Martín Menem": {"emoji": "📜", "FG": 15, "TR": 0, "ET": -5, "PN": -20, "PC": 10, "PE": -25, "EA": 5, "CP": 0, "SO": 10, "REL": 25, "JUV": -5, "EMP": 5, "PROG": -10, "PYME": 5},
        "Luis Petri": {"emoji": "🪖", "FG": 15, "TR": -10, "ET": -30, "PN": 5, "PC": 15, "PE": -20, "EA": 15, "CP": -30, "SO": 30, "REL": 40, "JUV": -10, "EMP": 20, "PROG": -50, "PYME": -10},
        "José Luis Espert": {"emoji": "🔫", "FG": 20, "TR": -5, "ET": -10, "PN": 10, "PC": 10, "PE": -45, "EA": 5, "CP": -35, "SO": 20, "REL": 5, "JUV": 15, "EMP": 30, "PROG": -25, "PYME": -10},
        "Karina Milei": {"emoji": "🔮", "FG": 20, "TR": -5, "ET": -40, "PN": -20, "PC": 30, "PE": -20, "EA": 15, "CP": -40, "SO": 25, "REL": 5, "JUV": 35, "EMP": 35, "PROG": -25, "PYME": -5},
        "Luis Caputo": {"emoji": "💰", "FG": -25, "TR": 10, "ET": -10, "PN": 5, "PC": -10, "PE": -30, "EA": 10, "CP": -30, "SO": -10, "REL": 20, "JUV": 5, "EMP": 55, "PROG": -30, "PYME": -40},
        "F. Sturzenegger": {"emoji": "📝", "FG": 10, "TR": 0, "ET": 0, "PN": -10, "PC": -5, "PE": -45, "EA": 30, "CP": -30, "SO": -5, "REL": 20, "JUV": -30, "EMP": 65, "PROG": -30, "PYME": -35},
        "Diego Santilli": {"emoji": "👱", "FG": 10, "TR": 5, "ET": -10, "PN": -5, "PC": 5, "PE": -5, "EA": 5, "CP": -15, "SO": 10, "REL": 5, "JUV": 15, "EMP": 15, "PROG": 0, "PYME": -10}
    }},
    "PRO": {"color": "🟡", "candidatos": {
        "Mauricio Macri": {"emoji": "🐱", "FG": 20, "TR": 5, "ET": -20, "PN": 10, "PC": -20, "PE": -20, "EA": 45, "CP": -40, "SO": 20, "REL": 25, "JUV": 10, "EMP": 55, "PROG": -15, "PYME": -10},
        "H. R. Larreta": {"emoji": "👽", "FG": 15, "TR": 5, "ET": 5, "PN": 15, "PC": -30, "PE": -10, "EA": 20, "CP": -45, "SO": 15, "REL": 10, "JUV": -15, "EMP": 25, "PROG": 5, "PYME": 20},
        "R. López Murphy": {"emoji": "bulldog", "FG": 5, "TR": 5, "ET": -35, "PN": 5, "PC": -20, "PE": -45, "EA": 25, "CP": -35, "SO": 5, "REL": 25, "JUV": -35, "EMP": 25, "PROG": -30, "PYME": -5},
        "María E. Vidal": {"emoji": "🦁", "FG": 5, "TR": -15, "ET": 5, "PN": 0, "PC": -5, "PE": -5, "EA": 40, "CP": -10, "SO": 15, "REL": 5, "JUV": 10, "EMP": 20, "PROG": 10, "PYME": 10},
        "Jorge Macri": {"emoji": "🏙️", "FG": 10, "TR": 10, "ET": -30, "PN": 0, "PC": 10, "PE": 10, "EA": 10, "CP": -55, "SO": 40, "REL": 5, "JUV": 5, "EMP": 30, "PROG": -15, "PYME": 15},
        "Silvia Lospennato": {"emoji": "🗳️", "FG": -5, "TR": 5, "ET": 10, "PN": -5, "PC": -20, "PE": -25, "EA": 5, "CP": -15, "SO": 10, "REL": -5, "JUV": 5, "EMP": 5, "PROG": 25, "PYME": -10},
        "Néstor Grindetti": {"emoji": "⚽", "FG": 10, "TR": -5, "ET": -15, "PN": -5, "PC": -20, "PE": -25, "EA": 0, "CP": -20, "SO": 25, "REL": 10, "JUV": -15, "EMP": 20, "PROG": 0, "PYME": 10},
        "Luis Juez": {"emoji": "🌭", "FG": 5, "TR": -5, "ET": -20, "PN": 10, "PC": -10, "PE": -15, "EA": 15, "CP": 0, "SO": 5, "REL": 5, "JUV": -30, "EMP": -5, "PROG": -5, "PYME": 0}
    }},
    "UCR": {"color": "⚪", "candidatos": {
        "Martín Lousteau": {"emoji": "🎓", "FG": 30, "TR": -25, "ET": 25, "PN": -25, "PC": -20, "PE": 20, "EA": 5, "CP": -20, "SO": 10, "REL": -20, "JUV": 25, "EMP": 15, "PROG": 25, "PYME": 15},
        "Roberto Lavagna": {"emoji": "🧦", "FG": 20, "TR": 20, "ET": 0, "PN": 15, "PC": -25, "PE": 0, "EA": 10, "CP": -20, "SO": 5, "REL": 5, "JUV": -25, "EMP": 20, "PROG": 5, "PYME": 20},
        "Facundo Manes": {"emoji": "🧠", "FG": -10, "TR": 5, "ET": 35, "PN": 10, "PC": -20, "PE": 5, "EA": 5, "CP": -30, "SO": -25, "REL": 0, "JUV": 5, "EMP": -10, "PROG": 10, "PYME": 10},
        "Gerardo Morales": {"emoji": "🌵", "FG": 35, "TR": -5, "ET": -10, "PN": 25, "PC": -40, "PE": 5, "EA": 5, "CP": -20, "SO": 25, "REL": 20, "JUV": -15, "EMP": 5, "PROG": -15, "PYME": 15},
        "Julio Cobos": {"emoji": "👎", "FG": 30, "TR": 5, "ET": 0, "PN": -10, "PC": -30, "PE": -5, "EA": 5, "CP": -30, "SO": 10, "REL": 25, "JUV": -20, "EMP": 10, "PROG": -15, "PYME": 15},
        "Rodrigo de Loredo": {"emoji": "🚌", "FG": 5, "TR": 5, "ET": -10, "PN": 5, "PC": -10, "PE": -15, "EA": 5, "CP": -40, "SO": 5, "REL": -15, "JUV": 30, "EMP": 5, "PROG": 10, "PYME": 10},
        "Ricardo Alfonsín": {"emoji": "👴", "FG": 20, "TR": -20, "ET": 15, "PN": 5, "PC": -15, "PE": 20, "EA": 15, "CP": -20, "SO": -15, "REL": 10, "JUV": 0, "EMP": -15, "PROG": 30, "PYME": 5},
        "Lula Levy": {"emoji": "🤳", "FG": -25, "TR": -45, "ET": 40, "PN": 5, "PC": 15, "PE": 25, "EA": 5, "CP": -35, "SO": -10, "REL": -25, "JUV": 40, "EMP": 5, "PROG": 15, "PYME": 10}
    }},
    "FIT-U": {"color": "🔴", "candidatos": {
        "Myriam Bregman": {"emoji": "✊", "FG": -35, "TR": -5, "ET": 30, "PN": 30, "PC": 10, "PE": 30, "EA": -20, "CP": -25, "SO": -20, "REL": -10, "JUV": 50, "EMP": -30, "PROG": 25, "PYME": -20},
        "Nicolás del Caño": {"emoji": "📹", "FG": -25, "TR": 10, "ET": 25, "PN": 20, "PC": 15, "PE": 25, "EA": 0, "CP": 0, "SO": -25, "REL": -25, "JUV": 30, "EMP": -25, "PROG": 30, "PYME": -25},
        "Gabriel Solano": {"emoji": "📢", "FG": -40, "TR": 25, "ET": 30, "PN": 10, "PC": 0, "PE": 25, "EA": -10, "CP": -10, "SO": -30, "REL": -35, "JUV": 20, "EMP": -35, "PROG": 55, "PYME": -20},
        "Manuela Castañeira": {"emoji": "🚩", "FG": -65, "TR": 15, "ET": 60, "PN": 15, "PC": 30, "PE": 40, "EA": -20, "CP": -10, "SO": -35, "REL": -20, "JUV": 35, "EMP": -20, "PROG": 30, "PYME": -15},
        "Christian Castillo": {"emoji": "📕", "FG": -20, "TR": 10, "ET": 15, "PN": 10, "PC": -10, "PE": 20, "EA": -30, "CP": -30, "SO": -40, "REL": -30, "JUV": 10, "EMP": -40, "PROG": 40, "PYME": -30},
        "Romina Del Plá": {"emoji": "🏫", "FG": -35, "TR": 20, "ET": 35, "PN": 5, "PC": 10, "PE": 30, "EA": -40, "CP": -25, "SO": -30, "REL": -25, "JUV": 15, "EMP": -25, "PROG": 50, "PYME": -25},
        "Federico Winokur": {"emoji": "🏫", "FG": -40, "TR": 20, "ET": 50, "PN": 15, "PC": -50, "PE": 30, "EA": -50, "CP": -35, "SO": -45, "REL": -40, "JUV": 25, "EMP": -50, "PROG": 45, "PYME": -10},
        "Luca Bonfante": {"emoji": "🎓", "FG": -10, "TR": 5, "ET": 45, "PN": 5, "PC": -10, "PE": 25, "EA": -5, "CP": -5, "SO": -25, "REL": -45, "JUV": 55, "EMP": -45, "PROG": 50, "PYME": 0}
    }},
    "PN": {"color": "⚫", "candidatos": {
        "Victoria Villarruel": {"emoji": "🛡️", "FG": -10, "TR": 15, "ET": -20, "PN": 5, "PC": 5, "PE": 20, "EA": 10, "CP": 5, "SO": 55, "REL": 35, "JUV": 10, "EMP": 15, "PROG": -30, "PYME": 5},
        "Santiago Cúneo": {"emoji": "🤬", "FG": 30, "TR": -10, "ET": -35, "PN": 40, "PC": -40, "PE": 10, "EA": 5, "CP": 5, "SO": 20, "REL": 15, "JUV": 20, "EMP": -15, "PROG": -10, "PYME": 10},
        "Gómez Centurión": {"emoji": "⚔️", "FG": -10, "TR": 25, "ET": 0, "PN": 25, "PC": -15, "PE": -10, "EA": -15, "CP": -15, "SO": 50, "REL": 50, "JUV": -25, "EMP": -10, "PROG": -25, "PYME": 10},
        "Alejandro Biondini": {"emoji": "🦅", "FG": -60, "TR": 10, "ET": -20, "PN": 65, "PC": -50, "PE": 5, "EA": -30, "CP": -30, "SO": 50, "REL": 45, "JUV": -65, "EMP": -35, "PROG": -75, "PYME": -25},
        "Cesar Biondini": {"emoji": "🐣", "FG": 5, "TR": 0, "ET": -25, "PN": 35, "PC": 5, "PE": 10, "EA": -45, "CP": -35, "SO": 35, "REL": 15, "JUV": 20, "EMP": -30, "PROG": -25, "PYME": -10},
        "Alberto Samid": {"emoji": "🥩", "FG": -35, "TR": -15, "ET": -30, "PN": 50, "PC": 5, "PE": 10, "EA": -5, "CP": 10, "SO": 10, "REL": 25, "JUV": 5, "EMP": 10, "PROG": -15, "PYME": 15},
        "Larry de Clay": {"emoji": "🎩", "FG": -10, "TR": 5, "ET": -15, "PN": 20, "PC": -25, "PE": -5, "EA": -15, "CP": 25, "SO": 10, "REL": 25, "JUV": 30, "EMP": 5, "PROG": -30, "PYME": 10},
        "José Bonacci": {"emoji": "📜", "FG": -65, "TR": 25, "ET": -20, "PN": 50, "PC": -45, "PE": 5, "EA": -30, "CP": -15, "SO": 40, "REL": 30, "JUV": -25, "EMP": 20, "PROG": -60, "PYME": 20}
    }},
    "INDEPENDIENTES": {"color": "⬜", "candidatos": {
        "Elisa Carrió": {"emoji": "✝️", "FG": 15, "TR": -5, "ET": 10, "PN": 5, "PC": 25, "PE": 5, "EA": 40, "CP": -20, "SO": -10, "REL": 25, "JUV": -10, "EMP": -15, "PROG": 20, "PYME": 0},
        "Daniel Scioli": {"emoji": "🚤", "FG": 5, "TR": 0, "ET": -10, "PN": -10, "PC": -15, "PE": 0, "EA": 10, "CP": 10, "SO": 15, "REL": 10, "JUV": 10, "EMP": 20, "PROG": 15, "PYME": 20},
        "Fernanda Tokumoto": {"emoji": "🌸", "FG": -20, "TR": 5, "ET": -10, "PN": -30, "PC": -30, "PE": -5, "EA": 10, "CP": -10, "SO": 20, "REL": -5, "JUV": -5, "EMP": 5, "PROG": 5, "PYME": 35},
        "Sixto Christiani": {"emoji": "✝️", "FG": 30, "TR": 20, "ET": 25, "PN": 10, "PC": -15, "PE": 5, "EA": -35, "CP": -35, "SO": 5, "REL": -30, "JUV": 60, "EMP": 15, "PROG": 5, "PYME": 10},
        "Fernando Burlando": {"emoji": "⚖️", "FG": -20, "TR": -10, "ET": 0, "PN": -5, "PC": -5, "PE": 0, "EA": 0, "CP": -10, "SO": 25, "REL": 10, "JUV": 5, "EMP": 15, "PROG": -15, "PYME": 15},
        "Carlos Maslatón": {"emoji": "📈", "FG": 10, "TR": 0, "ET": 5, "PN": 10, "PC": 30, "PE": -35, "EA": 10, "CP": 5, "SO": 0, "REL": -5, "JUV": 35, "EMP": 35, "PROG": 25, "PYME": 20},
        "Esteban Paulón": {"emoji": "🏳️‍🌈", "FG": -5, "TR": 10, "ET": 30, "PN": 5, "PC": -25, "PE": 15, "EA": 0, "CP": 5, "SO": -20, "REL": -70, "JUV": 35, "EMP": -10, "PROG": 65, "PYME": 5},
        "Yamil Santoro": {"emoji": "🗽", "FG": 0, "TR": 0, "ET": 0, "PN": 0, "PC": 0, "PE": 0, "EA": 0, "CP": 0, "SO": 0, "REL": 0, "JUV": 0, "EMP": 0, "PROG": 0, "PYME": 0},
        "Luis Barrionuevo": {"emoji": "🍽️", "FG": 5, "TR": 20, "ET": -10, "PN": 5, "PC": -20, "PE": 0, "EA": -25, "CP": 5, "SO": 30, "REL": -5, "JUV": -40, "EMP": -20, "PROG": 40, "PYME": -40},
        "Domingo Cavallo": {"emoji": "💲", "FG": -10, "TR": -25, "ET": -35, "PN": -20, "PC": 50, "PE": -25, "EA": 35, "CP": 20, "SO": 20, "REL": 30, "JUV": 5, "EMP": 65, "PROG": -40, "PYME": 0},
        "Claudio Vidal": {"emoji": "🛢️", "FG": 15, "TR": 25, "ET": -35, "PN": -20, "PC": 50, "PE": 10, "EA": -35, "CP": -20, "SO": 10, "REL": 0, "JUV": -15, "EMP": 45, "PROG": 30, "PYME": -5},
        "Carlos del Frade": {"emoji": "🌾", "FG": -5, "TR": 5, "ET": 5, "PN": 30, "PC": 10, "PE": 30, "EA": -20, "CP": 0, "SO": 0, "REL": -30, "JUV": -20, "EMP": -40, "PROG": 20, "PYME": -10},
        "Juan Carlos Blanco": {"emoji": "⚪", "FG": -10, "TR": 10, "ET": 5, "PN": 10, "PC": 20, "PE": 20, "EA": -20, "CP": -20, "SO": 5, "REL": 5, "JUV": -10, "EMP": -10, "PROG": 20, "PYME": -5}
    }},
    "ESPECIALES": {"color": "#FFD700", "candidatos": {
        "Palito Ortega": {"emoji": "🎤", "FG": 15, "TR": 20, "ET": 10, "PN": 15, "PC": 25, "PE": 10, "EA": -20, "CP": 30, "SO": 5, "REL": 20, "JUV": -15, "EMP": 5, "PROG": 15, "PYME": 20},
        "Marcelo Tinelli": {"emoji": "📺", "FG": -20, "TR": 5, "ET": 0, "PN": 5, "PC": 40, "PE": -5, "EA": 10, "CP": 10, "SO": -10, "REL": -10, "JUV": 45, "EMP": 20, "PROG": 5, "PYME": 15},
        "Carlos Reutemann": {"emoji": "🏎️", "FG": 25, "TR": 15, "ET": 10, "PN": 20, "PC": 10, "PE": 10, "EA": 10, "CP": 10, "SO": 25, "REL": 20, "JUV": -30, "EMP": 25, "PROG": -5, "PYME": 20},
        "Florencia Peña": {"emoji": "🎭", "FG": -15, "TR": 10, "ET": 15, "PN": 5, "PC": 20, "PE": 20, "EA": -30, "CP": 20, "SO": -20, "REL": -25, "JUV": 30, "EMP": -10, "PROG": 40, "PYME": 0},
        "Gerardo Romano": {"emoji": "🎬", "FG": -5, "TR": 15, "ET": 10, "PN": 10, "PC": 15, "PE": 25, "EA": -25, "CP": 25, "SO": -10, "REL": -20, "JUV": 10, "EMP": -10, "PROG": 35, "PYME": 5},
        "Luis Brandoni": {"emoji": "🎥", "FG": 5, "TR": -5, "ET": 5, "PN": 0, "PC": 15, "PE": -10, "EA": 45, "CP": -35, "SO": 10, "REL": 10, "JUV": 5, "EMP": 20, "PROG": -30, "PYME": 5},
        "Héctor Baldassi": {"emoji": "⚽", "FG": 15, "TR": 10, "ET": 10, "PN": 5, "PC": -30, "PE": 5, "EA": -20, "CP": 0, "SO": 35, "REL": 15, "JUV": -10, "EMP": 10, "PROG": -25, "PYME": -15},
        "Jorge Lanata": {"emoji": "🚬", "FG": 5, "TR": 0, "ET": 10, "PN": 5, "PC": -20, "PE": -10, "EA": 50, "CP": -40, "SO": 10, "REL": -10, "JUV": 20, "EMP": 10, "PROG": -30, "PYME": 5},
        "Luis Majul": {"emoji": "📖", "FG": -30, "TR": -20, "ET": -50, "PN": -25, "PC": -60, "PE": 0, "EA": 45, "CP": -35, "SO": 20, "REL": 10, "JUV": 5, "EMP": 15, "PROG": -35, "PYME": 10},
        "Eduardo Feinmann": {"emoji": "👔", "FG": -5, "TR": 0, "ET": -45, "PN": -25, "PC": 5, "PE": -35, "EA": 50, "CP": -40, "SO": 30, "REL": 50, "JUV": 10, "EMP": 15, "PROG": -50, "PYME": 10},
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
        "Ricardo Caruso Lombardi": {"emoji": "💨", "FG": -45, "TR": -5, "ET": 5, "PN": 5, "PC": 20, "PE": -5, "EA": 15, "CP": -20, "SO": -20, "REL": 0, "JUV": 35, "EMP": -10, "PROG": 5, "PYME": -10},
        "Claudio 'Turco' Garcia": {"emoji": "⚽", "FG": -25, "TR": 5, "ET": 5, "PN": -10, "PC": 10, "PE": 20, "EA": 5, "CP": 0, "SO": 0, "REL": 15, "JUV": 25, "EMP": -20, "PROG": -5, "PYME": 0},
        "Scioli Presidente": {"emoji": "🦾", "FG": 30, "TR": 10, "ET": 25, "PN": 25, "PC": 50, "PE": 25, "EA": -5, "CP": 50, "SO": 5, "REL": 25, "JUV": 25, "EMP": -10, "PROG": 25, "PYME": -10},
        "Bullrich Montonera": {"emoji": "💣", "FG": -50, "TR": 5, "ET": 10, "PN": 5, "PC": -35, "PE": 15, "EA": -10, "CP": -5, "SO": 50, "REL": -10, "JUV": 15, "EMP": -45, "PROG": 10, "PYME": -20},
        "Luis Juez (Mix)": {"emoji": "🌭", "FG": 5, "TR": -5, "ET": 5, "PN": -5, "PC": 5, "PE": -5, "EA": 5, "CP": 5, "SO": -5, "REL": 5, "JUV": 0, "EMP": 5, "PROG": 5, "PYME": -5},
        "Alberto Pandemia": {"emoji": "😷", "FG": 25, "TR": 25, "ET": 25, "PN": 25, "PC": 25, "PE": 25, "EA": 0, "CP": 25, "SO": 25, "REL": 25, "JUV": 25, "EMP": 25, "PROG": 25, "PYME": 25},
        "Cobos Vice": {"emoji": "🚫", "FG": 20, "TR": 20, "ET": 15, "PN": 75, "PC": 20, "PE": -25, "EA": 50, "CP": 15, "SO": 0, "REL": 10, "JUV": 0, "EMP": 25, "PROG": -25, "PYME": 25},
        "Lavagna Ministro": {"emoji": "🧦", "FG": 15, "TR": 50, "ET": 10, "PN": 50, "PC": 10, "PE": 25, "EA": 50, "CP": 50, "SO": 10, "REL": 25, "JUV": 0, "EMP": 50, "PROG": 0, "PYME": 50},
        "Cavallo 1 a 1": {"emoji": "💵", "FG": -5, "TR": 10, "ET": -50, "PN": -50, "PC": 20, "PE": -150, "EA": 50, "CP": 50, "SO": 10, "REL": 10, "JUV": 10, "EMP": 150, "PROG": -25, "PYME": -50},
        "Perón 3er Mandato": {"emoji": "👑", "FG": 20, "TR": 45, "ET": -25, "PN": 50, "PC": 10, "PE": 5, "EA": -50, "CP": 50, "SO": 150, "REL": 50, "JUV": -1574, "EMP": 15, "PROG": -1574, "PYME": 30},
        "Lousteau 125": {"emoji": "📉", "FG": -20, "TR": -50, "ET": 10, "PN": -150, "PC": 10, "PE": 35, "EA": -20, "CP": -30, "SO": 0, "REL": -20, "JUV": 10, "EMP": -50, "PROG": 25, "PYME": -50},
        "Cristina Presa": {"emoji": "⛓️", "FG": -30, "TR": -30, "ET": -30, "PN": -30, "PC": -30, "PE": -30, "EA": -30, "CP": -30, "SO": -30, "REL": -30, "JUV": -30, "EMP": -30, "PROG": -30, "PYME": -30},
        "Perón Exilio": {"emoji": "✈️", "FG": -72, "TR": 72, "ET": 72, "PN": 72, "PC": -72, "PE": 72, "EA": -72, "CP": 72, "SO": -72, "REL": -72, "JUV": 72, "EMP": -72, "PROG": 72, "PYME": 72},
        "Cornelio Saavedra": {"emoji": "🎩", "FG": 75, "TR": 50, "ET": 50, "PN": 50, "PC": 50, "PE": 50, "EA": 50, "CP": 50, "SO": 100, "REL": 50, "JUV": 50, "EMP": 50, "PROG": 50, "PYME": 50},
        "Juana Azurduy": {"emoji": "⚔️", "FG": 25, "TR": 30, "ET": 20, "PN": 15, "PC": 40, "PE": 40, "EA": 0, "CP": 25, "SO": 25, "REL": 0, "JUV": 50, "EMP": 0, "PROG": 75, "PYME": 0},
        "Juan M. de Rosas": {"emoji": "🌹", "FG": 200, "TR": 10, "ET": 10, "PN": 50, "PC": 25, "PE": 25, "EA": -25, "CP": 5, "SO": 100, "REL": 100, "JUV": 25, "EMP": 0, "PROG": 10, "PYME": 0},
        "Manuel Belgrano": {"emoji": "🇦🇷", "FG": 80, "TR": 20, "ET": 50, "PN": 50, "PC": 50, "PE": 50, "EA": 20, "CP": 20, "SO": 50, "REL": 50, "JUV": 50, "EMP": 20, "PROG": 50, "PYME": 20},
        "San Martín": {"emoji": "⚔️", "FG": 100, "TR": 20, "ET": 20, "PN": 20, "PC": 50, "PE": 50, "EA": 20, "CP": 20, "SO": 100, "REL": 50, "JUV": 20, "EMP": 20, "PROG": 50, "PYME": 20}
    }},
    "HIST": {"color": "#DAA520", "candidatos": {
        "Bernardino Rivadavia": {"emoji": "🪑", "FG": -50, "TR": 0, "ET": 25, "PN": -5, "PC": 35, "PE": 10, "EA": 20, "CP": -10, "SO": 20, "REL": 25, "JUV": 0, "EMP": 40, "PROG": -20, "PYME": 0},
        "Vicente López": {"emoji": "🎶", "FG": 10, "TR": 0, "ET": 10, "PN": 0, "PC": 5, "PE": 5, "EA": 5, "CP": 0, "SO": 5, "REL": 10, "JUV": -20, "EMP": 5, "PROG": 0, "PYME": 5},
        "Justo José de Urquiza": {"emoji": "🚜", "FG": 20, "TR": -15, "ET": 10, "PN": 20, "PC": 35, "PE": 20, "EA": 15, "CP": -5, "SO": 45, "REL": 15, "JUV": -30, "EMP": 0, "PROG": 0, "PYME": 15},
        "Santiago Derqui": {"emoji": "📉", "FG": 10, "TR": 0, "ET": 5, "PN": 0, "PC": -10, "PE": -5, "EA": 0, "CP": 0, "SO": -10, "REL": 5, "JUV": -25, "EMP": 0, "PROG": 0, "PYME": 0},
        "Juan E. Pedernera": {"emoji": "⚔️", "FG": -15, "TR": 5, "ET": 5, "PN": 5, "PC": 10, "PE": 10, "EA": 5, "CP": -5, "SO": 5, "REL": 5, "JUV": -20, "EMP": 0, "PROG": 0, "PYME": 5},
        "Bartolomé Mitre": {"emoji": "📰", "FG": -20, "TR": 10, "ET": 25, "PN": 30, "PC": 5, "PE": 20, "EA": 25, "CP": -15, "SO": 15, "REL": 20, "JUV": -25, "EMP": 15, "PROG": 10, "PYME": 20},
        "Domingo Sarmiento": {"emoji": "📚", "FG": -20, "TR": 20, "ET": 100, "PN": 30, "PC": -25, "PE": 15, "EA": 25, "CP": 0, "SO": 25, "REL": -10, "JUV": -15, "EMP": -10, "PROG": -20, "PYME": 15},
        "Nicolás Avellaneda": {"emoji": "🌾", "FG": -15, "TR": 20, "ET": 10, "PN": 25, "PC": 0, "PE": 10, "EA": 25, "CP": -10, "SO": 20, "REL": 20, "JUV": -20, "EMP": 25, "PROG": 5, "PYME": 15},
        "Julio A. Roca": {"emoji": "🦊", "FG": -15, "TR": 30, "ET": 20, "PN": 20, "PC": -30, "PE": 5, "EA": 15, "CP": 5, "SO": 65, "REL": 35, "JUV": -30, "EMP": 50, "PROG": -35, "PYME": 40},
        "Miguel Juárez Celman": {"emoji": "💸", "FG": -25, "TR": -10, "ET": -10, "PN": -30, "PC": 20, "PE": -40, "EA": 10, "CP": -25, "SO": -5, "REL": 20, "JUV": -25, "EMP": 30, "PROG": -20, "PYME": 10},
        "Carlos Pellegrini": {"emoji": "🏦", "FG": 10, "TR": 20, "ET": 25, "PN": 50, "PC": -20, "PE": 30, "EA": 5, "CP": 5, "SO": 0, "REL": 10, "JUV": -10, "EMP": 30, "PROG": 20, "PYME": 30},
        "Luis Sáenz Peña": {"emoji": "🛌", "FG": -15, "TR": -5, "ET": -10, "PN": -10, "PC": 20, "PE": -5, "EA": 20, "CP": -10, "SO": -45, "REL": 20, "JUV": -20, "EMP": 20, "PROG": 0, "PYME": 10},
        "José Uriburu": {"emoji": "🎩", "FG": 5, "TR": 0, "ET": -15, "PN": -10, "PC": 10, "PE": 20, "EA": 20, "CP": -5, "SO": 35, "REL": 35, "JUV": -10, "EMP": 30, "PROG": -15, "PYME": 5},
        "Manuel Quintana": {"emoji": "👴", "FG": -20, "TR": 5, "ET": 10, "PN": 10, "PC": 10, "PE": 10, "EA": 10, "CP": 10, "SO": 10, "REL": -20, "JUV": 10, "EMP": 10, "PROG": 10, "PYME": 10},
        "Figueroa Alcorta": {"emoji": "🏛️", "FG": 15, "TR": 20, "ET": 30, "PN": 25, "PC": -15, "PE": 5, "EA": -20, "CP": -5, "SO": 10, "REL": 0, "JUV": -40, "EMP": 15, "PROG": 5, "PYME": 25},
        "Roque Sáenz Peña": {"emoji": "🗳️", "FG": 10, "TR": 25, "ET": 35, "PN": 10, "PC": 10, "PE": 10, "EA": 10, "CP": 10, "SO": 0, "REL": 5, "JUV": -5, "EMP": 10, "PROG": 15, "PYME": 15},
        "Victorino de la Plaza": {"emoji": "🇬🇧", "FG": -10, "TR": 15, "ET": 15, "PN": 20, "PC": -5, "PE": 15, "EA": 20, "CP": -20, "SO": 15, "REL": 20, "JUV": -40, "EMP": 20, "PROG": 10, "PYME": 5},
        "Hipólito Yrigoyen": {"emoji": "🤠", "FG": 25, "TR": 35, "ET": 30, "PN": 25, "PC": 20, "PE": 30, "EA": 15, "CP": -5, "SO": -20, "REL": 10, "JUV": 20, "EMP": 10, "PROG": 15, "PYME": 5},
        "Marcelo T. de Alvear": {"emoji": "🎭", "FG": 0, "TR": 5, "ET": 10, "PN": -5, "PC": 15, "PE": 10, "EA": 30, "CP": -10, "SO": 5, "REL": 0, "JUV": 5, "EMP": 10, "PROG": 20, "PYME": 15},
        "Agustín P. Justo": {"emoji": "🌉", "FG": -10, "TR": 5, "ET": 10, "PN": 20, "PC": -10, "PE": 10, "EA": 25, "CP": -15, "SO": 20, "REL": 10, "JUV": -25, "EMP": 25, "PROG": -10, "PYME": 20},
        "Roberto Ortiz": {"emoji": "🤒", "FG": 10, "TR": -10, "ET": 15, "PN": 10, "PC": -25, "PE": 10, "EA": 15, "CP": -30, "SO": 5, "REL": 0, "JUV": -20, "EMP": 10, "PROG": 10, "PYME": 5},
        "Ramón Castillo": {"emoji": "⛴️", "FG": -15, "TR": -10, "ET": -10, "PN": 20, "PC": -20, "PE": 10, "EA": 30, "CP": -20, "SO": 25, "REL": 25, "JUV": -35, "EMP": 15, "PROG": -15, "PYME": 5},
        "Juan D. Perón": {"emoji": "✌️", "FG": 30, "TR": 45, "ET": 20, "PN": 50, "PC": 10, "PE": 40, "EA": -100, "CP": 100, "SO": 10, "REL": 10, "JUV": 10, "EMP": -10, "PROG": 50, "PYME": 25},
        "Arturo Frondizi": {"emoji": "🛢️", "FG": 15, "TR": 10, "ET": 15, "PN": 50, "PC": -10, "PE": -10, "EA": 5, "CP": 0, "SO": -15, "REL": -5, "JUV": -20, "EMP": 40, "PROG": 5, "PYME": 20},
        "José María Guido": {"emoji": "🖊️", "FG": -15, "TR": -10, "ET": -5, "PN": -5, "PC": -10, "PE": 5, "EA": 40, "CP": -25, "SO": 20, "REL": 20, "JUV": -25, "EMP": 10, "PROG": -10, "PYME": 5},
        "Arturo Illia": {"emoji": "🐢", "FG": 30, "TR": 5, "ET": 25, "PN": 0, "PC": 10, "PE": 15, "EA": 30, "CP": 0, "SO": -10, "REL": 0, "JUV": -15, "EMP": -5, "PROG": 20, "PYME": 15},
        "Héctor Cámpora": {"emoji": "🦷", "FG": -45, "TR": 10, "ET": 5, "PN": 10, "PC": -10, "PE": 10, "EA": -50, "CP": 30, "SO": 5, "REL": -10, "JUV": 35, "EMP": -10, "PROG": 20, "PYME": 10},
        "Raúl Lastiri": {"emoji": "👔", "FG": -20, "TR": 5, "ET": 5, "PN": 5, "PC": 0, "PE": 10, "EA": -40, "CP": 30, "SO": 0, "REL": 5, "JUV": -15, "EMP": 5, "PROG": 15, "PYME": 10},
        "Isabel Perón": {"emoji": "💃", "FG": -35, "TR": -10, "ET": -10, "PN": -10, "PC": 10, "PE": 15, "EA": -45, "CP": 10, "SO": 25, "REL": 10, "JUV": -25, "EMP": -10, "PROG": -10, "PYME": -5},
        "Raúl Alfonsín": {"emoji": "🗣️", "FG": 40, "TR": 10, "ET": 25, "PN": 5, "PC": 30, "PE": 5, "EA": 20, "CP": -5, "SO": -20, "REL": -10, "JUV": -15, "EMP": -5, "PROG": 20, "PYME": 15},
        "Carlos Menem": {"emoji": "🚀", "FG": 25, "TR": -15, "ET": -20, "PN": -40, "PC": 30, "PE": -20, "EA": 10, "CP": 20, "SO": 10, "REL": 5, "JUV": -10, "EMP": 40, "PROG": -25, "PYME": 15},
        "Fernando de la Rúa": {"emoji": "📉", "FG": 15, "TR": -30, "ET": 0, "PN": -10, "PC": 25, "PE": -15, "EA": 15, "CP": -5, "SO": -10, "REL": 0, "JUV": -30, "EMP": 15, "PROG": -20, "PYME": -10},
        "A. Rodriguez Saa": {"emoji": "🏞️", "FG": 15, "TR": -5, "ET": -15, "PN": -5, "PC": -10, "PE": 15, "EA": 10, "CP": 10, "SO": 20, "REL": 10, "JUV": -30, "EMP": 15, "PROG": -15, "PYME": 10},
        "Eduardo Duhalde": {"emoji": "♟️", "FG": 25, "TR": -5, "ET": -25, "PN": -5, "PC": -30, "PE": 15, "EA": -10, "CP": 5, "SO": 30, "REL": 5, "JUV": -30, "EMP": 15, "PROG": -25, "PYME": 10},
        "Néstor Kirchner": {"emoji": "🐧", "FG": 15, "TR": 20, "ET": 20, "PN": 10, "PC": -20, "PE": 25, "EA": -45, "CP": 25, "SO": -10, "REL": -5, "JUV": 15, "EMP": 0, "PROG": 15, "PYME": 10}
    }}
}

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

def calcular_afinidad(cand, tipo, nombre_entidad):
    stats = get_candidate_stats(cand)
    score = 0
    if tipo == "SOCIAL":
        score = stats.get(nombre_entidad, 0)
    elif tipo == "PROVINCIA":
        grupos = PROV_TO_GROUP_RAW.get(nombre_entidad, [])
        for g in grupos:
            score += stats.get(g, 0)
    return score

def update_owners():
    # Provincias
    for p in MAPA_DATA:
        slots = st.session_state.slots[p]
        mx = max(slots.values()) if slots else 0
        if mx > 0:
            lideres = [c for c, q in slots.items() if q == mx]
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
            if wallets["base"] < 0: wallets["base"] = 0 

def check_election_readiness():
    for p in MAPA_DATA:
        if sum(st.session_state.slots[p].values()) == 0:
            return False
    return True

def eliminar_candidato(nombre):
    if nombre in st.session_state.p:
        del st.session_state.p[nombre]
    
    for p in MAPA_DATA:
        if nombre in st.session_state.slots[p]:
            if st.session_state.slots[p][nombre] >= 10:
                st.session_state.hard_locked[p] = False
            del st.session_state.slots[p][nombre]

    for g in SOCIAL_GROUPS:
        if nombre in st.session_state.social_slots[g]:
            if st.session_state.social_slots[g][nombre] >= 10:
                st.session_state.hard_locked[g] = False
            del st.session_state.social_slots[g][nombre]
    
    if nombre in st.session_state.ai_conflict_memory:
        del st.session_state.ai_conflict_memory[nombre]

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
        
        fichas_owner = st.session_state.slots[p_name].get(owner, 0)
        if fichas_owner < 3: continue 
        
        grupos_prov = PROV_TO_GROUP_RAW.get(p_name, [])
        fuerza = MAPA_DATA[p_name]["votos"] 
        
        for g in grupos_prov:
            fuerza_grupos[g][owner] += fuerza

    return fuerza_grupos, total_votos_grupo

def procesar_turno():
    reporte = []
    mi_nombre = next(c for c, i in st.session_state.p.items() if not i["is_ia"])
    
    inversiones_turno = {p: {} for p in MAPA_DATA}
    inv_social = {g: {} for g in SOCIAL_GROUPS}
    
    if 'ai_conflict_memory' not in st.session_state:
        st.session_state.ai_conflict_memory = {c: {} for c in st.session_state.p}

    is_late_game = st.session_state.turno >= 15

    # 1. GENERAR OBJETIVOS DE IA (Estrategia de Grupos)
    fuerza_grupos, total_votos_group = calcular_control_grupos()

    for cand, info in st.session_state.p.items():
        if info["is_ia"]:
            dinero_actual = get_total_money(cand)
            stats = get_candidate_stats(cand)
            
            # --- ESTRATEGIA TERRITORIAL (Grand Strategy) ---
            # Identificar qué grupos quiere dominar la IA
            grupos_deseados = []
            for g, data in STATE_GROUPS.items():
                if stats.get(g, 0) > 0: # Si tiene afinidad positiva
                    # Calcular cuan cerca esta de ganar el grupo
                    votos_mios = fuerza_grupos[g][cand]
                    total = total_votos_group[g]
                    distancia = (total * 0.51) - votos_mios
                    prioridad = stats.get(g, 0) + (1000 if distancia <= 0 else 0) # Prioriza mantener lo ganado
                    grupos_deseados.append((prioridad, g))
            grupos_deseados.sort(reverse=True)
            
            objetivos_prov = []
            for p in MAPA_DATA:
                fichas_mias = st.session_state.slots[p].get(cand, 0)
                if fichas_mias >= 10: continue
                if st.session_state.hard_locked[p]: continue

                lider_enemigo = 0
                total_fichas_prov = 0
                for c, q in st.session_state.slots[p].items():
                    total_fichas_prov += q
                    if c != cand and q > lider_enemigo: lider_enemigo = q
                
                # --- Puntuación Base ---
                afinidad = calcular_afinidad(cand, "PROVINCIA", p)
                votos = MAPA_DATA[p]["votos"]
                score = votos * 50 + afinidad * 5 
                
                # --- Bonus por Estrategia de Grupo ---
                prov_grupos = PROV_TO_GROUP_RAW.get(p, [])
                for prio, g_code in grupos_deseados[:3]: # Mira sus top 3 grupos
                    if g_code in prov_grupos:
                        score += 2000 # Gran incentivo para completar grupos
                
                # --- Lógica de Conflicto y Retirada ---
                conflict_count = st.session_state.ai_conflict_memory[cand].get(p, 0)
                if conflict_count >= 2: score -= 500000 
                elif conflict_count == 1: score -= 1000
                
                # Retirada si el enemigo es muy fuerte
                if lider_enemigo >= 7 and fichas_mias < 3: score -= 10000

                # --- Oportunismo ---
                if total_fichas_prov == 0: score += 3000 # Agarrar tierra de nadie
                if fichas_mias > lider_enemigo and fichas_mias >= 3: score += 5000 # Cerrar puerta
                if lider_enemigo >= 8: score += 2000 # Intentar bloquear al rival (arriesgado)
                
                # --- Personalidad Random ---
                score *= random.uniform(0.9, 1.15)

                objetivos_prov.append((score, p))
            
            objetivos_prov.sort(reverse=True)
            
            # --- LISTA UNIFICADA DE OPORTUNIDADES ---
            # Vamos a mezclar provincias y grupos sociales
            oportunidades = []

            # Agregar Provincias a la lista
            for score, p in objetivos_prov:
                oportunidades.append({
                    "tipo": "PROVINCIA",
                    "id": p,
                    "score": score,
                    "costo": COSTOS_FIJOS[p]
                })

            # Agregar Grupos Sociales a la lista
            for g in SOCIAL_GROUPS:
                fichas_mias = st.session_state.social_slots[g].get(cand, 0)
                if fichas_mias >= 10: continue
                if st.session_state.hard_locked.get(g, False): continue
                
                fichas_enemigo = 0
                for c_rival, q in st.session_state.social_slots[g].items():
                    if c_rival != cand and q > fichas_enemigo: fichas_enemigo = q

                afinidad = calcular_afinidad(cand, "SOCIAL", g)
                
                # Score base social
                social_score = (SOCIAL_GROUPS[g]["renta"] / 20) + (afinidad * 50)
                
                if fichas_enemigo >= 8 and fichas_mias > 0: social_score += 1500 
                elif fichas_mias >= 8: social_score += 1000 
                elif fichas_enemigo > fichas_mias: social_score += 500
                
                # Personalidad
                social_score *= random.uniform(0.9, 1.15)

                oportunidades.append({
                    "tipo": "SOCIAL",
                    "id": g,
                    "score": social_score,
                    "costo": SOCIAL_GROUPS[g]["costo"]
                })
            
            # Ordenar todo por score descendente
            oportunidades.sort(key=lambda x: x["score"], reverse=True)

            # --- EJECUCIÓN DE COMPRAS ---
            # Umbral de Ahorro Dinámico
            umbral_ahorro = 20000 
            if any(v >= 2 for v in st.session_state.ai_conflict_memory[cand].values()):
                umbral_ahorro = 80000 

            for op in oportunidades:
                if dinero_actual < umbral_ahorro: break

                if dinero_actual >= op["costo"] and op["score"] > 0:
                    target = op["id"]
                    
                    # Calcular limite de compra
                    if op["tipo"] == "PROVINCIA":
                        curr = st.session_state.slots[target].get(cand, 0)
                        landed = cand in st.session_state.landed_status.get(target, [])
                    else:
                        curr = st.session_state.social_slots[target].get(cand, 0)
                        landed = cand in st.session_state.landed_status.get(target, [])
                    
                    limit = 2 if (curr == 0 and not landed) else (10-curr)
                    
                    # Decisión de cantidad
                    qty = 1
                    if op["score"] >= 4000: qty = min(limit, int(dinero_actual / op["costo"]))
                    elif op["score"] > 2000: qty = min(limit, 2)
                    
                    # Ejecutar
                    if qty > 0 and check_solvencia(cand, target, qty, op["tipo"] == "SOCIAL"):
                        if op["tipo"] == "PROVINCIA":
                            inversiones_turno[target][cand] = inversiones_turno[target].get(cand, 0) + qty
                            if target not in st.session_state.landed_status: st.session_state.landed_status[target] = []
                            if cand not in st.session_state.landed_status[target]: st.session_state.landed_status[target].append(cand)
                        else:
                            inv_social[target][cand] = qty
                            if target not in st.session_state.landed_status: st.session_state.landed_status[target] = []
                            if cand not in st.session_state.landed_status[target]: st.session_state.landed_status[target].append(cand)

                        gastar_dinero(cand, target, qty, op["tipo"] == "SOCIAL")
                        dinero_actual -= (op["costo"] * qty)

    # 2. PROCESAR JUGADOR REAL
    for ent, cant in st.session_state.pending_user.items():
        if cant > 0:
            if ent in SOCIAL_GROUPS:
                inv_social[ent][mi_nombre] = cant
                gastar_dinero(mi_nombre, ent, cant, True)
                if ent not in st.session_state.landed_status: st.session_state.landed_status[ent] = []
                if mi_nombre not in st.session_state.landed_status[ent]: st.session_state.landed_status[ent].append(mi_nombre)
            else:
                inversiones_turno[ent][mi_nombre] = cant
                gastar_dinero(mi_nombre, ent, cant, False)
                if ent not in st.session_state.landed_status: st.session_state.landed_status[ent] = []
                if mi_nombre not in st.session_state.landed_status[ent]: st.session_state.landed_status[ent].append(mi_nombre)

    # 3. RESOLUCIÓN
    def resolver(inversiones_dict, estado_slots, hard_lock_dict, memory_dict, is_prov=True):
        for ent, invs in inversiones_dict.items():
            if not invs: continue
            proyecciones = {}
            for cand, cantidad in invs.items():
                actual = estado_slots[ent].get(cand, 0)
                total_proyectado = actual + cantidad
                if total_proyectado > 10: total_proyectado = 10
                if total_proyectado not in proyecciones: proyecciones[total_proyectado] = []
                proyecciones[total_proyectado].append(cand)
            
            for total_obj, candidatos in proyecciones.items():
                if len(candidatos) > 1:
                    nombres = ", ".join(candidatos)
                    reporte.append(f"💥 **{ent}**: Choque entre {nombres} intentando llegar a {total_obj} fichas.")
                    for c in candidatos:
                        # IA: Aprende del choque (solo en provincias para no complicar)
                        if is_prov and c in memory_dict: memory_dict[c][ent] = memory_dict[c].get(ent, 0) + 1
                        
                        if ent not in st.session_state.landed_status: st.session_state.landed_status[ent] = []
                        if c not in st.session_state.landed_status[ent]: st.session_state.landed_status[ent].append(c)
                else:
                    unico_cand = candidatos[0]
                    cant_inv = invs[unico_cand]
                    estado_slots[ent][unico_cand] = estado_slots[ent].get(unico_cand, 0) + cant_inv
                    
                    if is_prov and unico_cand in memory_dict: memory_dict[unico_cand][ent] = 0 
                    
                    if estado_slots[ent][unico_cand] >= 10: hard_lock_dict[ent] = True
                    if ent not in st.session_state.landed_status: st.session_state.landed_status[ent] = []
                    if unico_cand not in st.session_state.landed_status[ent]: st.session_state.landed_status[ent].append(unico_cand)

    resolver(inversiones_turno, st.session_state.slots, st.session_state.hard_locked, st.session_state.ai_conflict_memory, True)
    resolver(inv_social, st.session_state.social_slots, st.session_state.hard_locked, st.session_state.ai_conflict_memory, False)
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
    
    # --- LÓGICA DE ELECCIÓN AVISADA ---
    mapa_completo = check_election_readiness()
    
    if mapa_completo:
        if not st.session_state.get('election_pending', False):
            st.session_state.election_pending = True
            st.session_state.last_report.append("⚠️ ¡ATENCIÓN! Todas las provincias tienen presencia. VOTACIÓN EL PRÓXIMO TURNO.")
        else:
            st.session_state.modo_eleccion = True
            st.session_state.election_pending = False
    else:
        st.session_state.election_pending = False

    cond_classic = st.session_state.turno > 1 and st.session_state.turno % 4 == 0 and mapa_completo
    cond_time_limit = len(st.session_state.p) >= 3 and st.session_state.turno >= 20 and mapa_completo 
    
    if cond_classic or cond_time_limit:
       pass 

# --- 3. INICIALIZACIÓN ---
if 'p' not in st.session_state:
    st.session_state.p = {}
    st.session_state.game_started = False
    st.session_state.winner = None
    st.session_state.loser = None
    st.session_state.election_pending = False

# --- 4. INTERFAZ UI ---

if st.session_state.winner or st.session_state.loser:
    mi_nombre = next(c for c, i in st.session_state.p.items() if not i["is_ia"])
    
    if st.session_state.winner == mi_nombre:
        st.markdown(f"<div class='win-msg'>🎉 ¡FELICIDADES {mi_nombre.upper()}! 🎉<br>ERES EL NUEVO PRESIDENTE 🇦🇷</div>", unsafe_allow_html=True)
        st.balloons()
    else:
        ganador_real = st.session_state.winner if st.session_state.winner else "OTRO CANDIDATO"
        st.markdown(f"<div class='lose-msg'>💀 Lo siento {mi_nombre}...<br>Ganó {ganador_real}. Vuelve a intentarlo 📉</div>", unsafe_allow_html=True)
    
    if st.button("🔄 REINICIAR CAMPAÑA"):
        st.session_state.game_started = False
        st.session_state.winner = None
        st.session_state.loser = None
        st.session_state.election_pending = False
        st.rerun()

elif not st.session_state.game_started:
    st.title("Rosca Política: 189")
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
            st.session_state.hard_locked = {k: False for k in list(MAPA_DATA.keys()) + list(SOCIAL_GROUPS.keys())}
            st.session_state.landed_status = {k: [] for k in list(MAPA_DATA.keys()) + list(SOCIAL_GROUPS.keys())}
            st.session_state.ai_conflict_memory = {c: {} for c in jugadores}
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
        st.progress(min(v/VOTOS_PARA_GANAR, 1.0))
        
    eliminado = sorted_v[-1][0]
    st.error(f"{eliminado} eliminado.")
    
    if st.button("SIGUIENTE"):
        mi_name = next(c for c, i in st.session_state.p.items() if not i["is_ia"])
        if sorted_v[0][1] >= VOTOS_PARA_GANAR:
            if sorted_v[0][0] == mi_name: st.session_state.winner = mi_name
            else: st.session_state.winner = sorted_v[0][0]; st.session_state.loser = mi_name
        elif eliminado == mi_name:
            st.session_state.loser = mi_name
        else:
            eliminar_candidato(eliminado)
            st.session_state.modo_eleccion = False
        st.rerun()

else:
    mi_nombre = next(c for c, i in st.session_state.p.items() if not i["is_ia"])
    
    # SIDEBAR
    st.sidebar.title(f"Turno {st.session_state.turno}")
    
    if st.session_state.get('election_pending', False):
        st.sidebar.markdown("<div class='warning-msg'>⚠️ ELECCIÓN PRÓXIMO TURNO</div>", unsafe_allow_html=True)

    # --- SIMULACIÓN DE GASTO PARA VISUALIZACIÓN ---
    sim_wallets = st.session_state.p[mi_nombre]["wallets"].copy()
    gasto_breakdown = {"General": 0}
    
    for ent, cant in st.session_state.pending_user.items():
        if ent in SOCIAL_GROUPS:
            costo = SOCIAL_GROUPS[ent]["costo"] * cant
            gasto_breakdown["General"] = gasto_breakdown.get("General", 0) + costo
            if sim_wallets["base"] >= costo: sim_wallets["base"] -= costo
        else:
            costo_total = COSTOS_FIJOS[ent] * cant
            grupos_prov = PROV_TO_GROUP_RAW.get(ent, [])
            for g in grupos_prov:
                if costo_total <= 0: break
                if sim_wallets.get(g, 0) > 0:
                    deduccion = min(costo_total, sim_wallets[g])
                    sim_wallets[g] -= deduccion
                    costo_total -= deduccion
                    gasto_breakdown[g] = gasto_breakdown.get(g, 0) + deduccion
            if costo_total > 0:
                gasto_breakdown["General"] = gasto_breakdown.get("General", 0) + costo_total
                if sim_wallets["base"] >= costo_total: sim_wallets["base"] -= costo_total

    total_gasto_display = sum(gasto_breakdown.values())
    dinero_disp = get_total_money(mi_nombre)

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
    
    if st.session_state.get('election_pending', False):
        st.markdown("<div class='warning-msg'>🗳️ ¡ATENCIÓN! EL MAPA ESTÁ COMPLETO. LA VOTACIÓN SERÁ AL FINALIZAR ESTE TURNO.</div>", unsafe_allow_html=True)

    
    # --- VISUALIZACIÓN DE CAJA Y GASTOS ---
    col_caja, col_gasto, col_btn = st.columns(3)
    
    with col_caja:
        st.markdown("<div class='money-box'>", unsafe_allow_html=True)
        st.markdown("<div class='money-title'>🏦 Caja</div>", unsafe_allow_html=True)
        real_wallets = st.session_state.p[mi_nombre]["wallets"]
        st.markdown(f"<div class='money-item'>- General: ${real_wallets['base']:,}</div>", unsafe_allow_html=True)
        for k, v in real_wallets.items():
            if k != 'base' and v > 0:
                st.markdown(f"<div class='money-item'>- {k}: ${v:,}</div>", unsafe_allow_html=True)
        st.markdown(f"<hr style='margin:5px 0'><b>Total: ${dinero_disp:,}</b>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_gasto:
        st.markdown("<div class='expense-box'>", unsafe_allow_html=True)
        st.markdown("<div class='money-title'>💸 Gastos</div>", unsafe_allow_html=True)
        if total_gasto_display == 0:
            st.markdown("<div class='money-item'>- Sin gastos</div>", unsafe_allow_html=True)
        else:
            if gasto_breakdown["General"] > 0:
                st.markdown(f"<div class='money-item'>- General: -${gasto_breakdown['General']:,}</div>", unsafe_allow_html=True)
            for k, v in gasto_breakdown.items():
                if k != "General" and v > 0:
                    st.markdown(f"<div class='money-item'>- {k}: -${v:,}</div>", unsafe_allow_html=True)
            st.markdown(f"<hr style='margin:5px 0'><b>Total: -${total_gasto_display:,}</b>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_btn:
        st.write("") # Spacer
        st.write("") # Spacer
        if st.button("JUGAR TURNO", type="primary", use_container_width=True):
            if total_gasto_display > dinero_disp: st.error("No alcanza")
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
                        
                        votos_display = MAPA_DATA[p_n]["votos"]
                        btn_label = f"{dots} {e} {p_n} ({votos_display}v)\n${cost_k}k"
                        
                        if cols[c].button(btn_label, key=p_n):
                            st.session_state.selected_prov = p_n; st.rerun()
        else:
            p = st.session_state.selected_prov
            st.button("🔙", on_click=lambda: setattr(st.session_state, 'selected_prov', None))
            st.header(p)
            
            # Info detallada de la provincia seleccionada
            my_w = st.session_state.p[mi_nombre]["wallets"]
            valid_groups = PROV_TO_GROUP_RAW.get(p, [])
            
            st.info(f"Grupos: {', '.join(valid_groups)}")
                
            curr = st.session_state.slots[p].get(mi_nombre, 0)
            pend = st.session_state.pending_user.get(p, 0)
            landed = mi_nombre in st.session_state.landed_status.get(p, [])
            costo = COSTOS_FIJOS[p]
            
            if st.session_state.hard_locked.get(p, False):
                st.error("🔒 ESTA PROVINCIA ESTÁ CERRADA (10 Fichas Alcanzadas)")
            else:
                limit_add = 10 - curr
                if curr == 0 and not landed: limit_add = min(limit_add, 2)
                
                # Check simple de solvencia (total) para habilitar botones
                can_afford = (get_total_money(mi_nombre) - total_gasto_display + (costo if p in st.session_state.pending_user else 0)) >= costo

                c_add, c_rem = st.columns(2)
                if c_add.button("➕ Comprar Ficha") and pend < limit_add:
                    if can_afford:
                        st.session_state.pending_user[p] = pend + 1
                        st.rerun()
                    else: st.error("Sin fondos")
                
                if c_rem.button("➖ Vender Ficha") and pend > 0:
                    st.session_state.pending_user[p] -= 1; st.rerun()
                    
                st.write(f"Inversión pendiente: {pend} (Total futura: {curr+pend})")
            
            st.divider()
            for c, q in st.session_state.slots[p].items():
                st.write(f"{c}: {q}")
                st.progress(min(q/10, 1.0))

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
                            st.progress(min(q/10, 1.0))
                    if not has_fichas: st.write("-")

                with c_act:
                    if st.session_state.hard_locked.get(g_code, False):
                        st.error("🔒 CERRADO")
                    else:
                        curr = st.session_state.social_slots[g_code].get(mi_nombre, 0)
                        pend = st.session_state.pending_user.get(g_code, 0)
                        costo = data['costo']
                        
                        has_landed = mi_nombre in st.session_state.landed_status.get(g_code, [])
                        limit_add = 10 - curr 
                        if curr == 0 and not has_landed: limit_add = min(limit_add, 2)
                        
                        # --- CORRECCIÓN AQUÍ: Usar total_gasto_display ---
                        can_afford = (get_total_money(mi_nombre) - total_gasto_display + (costo if g_code in st.session_state.pending_user else 0)) >= costo

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
