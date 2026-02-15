import streamlit as st
import random
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Rosca Política: 189", layout="wide", page_icon="🗳️")

# --- VARIABLES GLOBALES ---
PRESUPUESTO_INICIAL = 250000
RENTA_BASE_TURNO = 250000
VOTOS_PARA_GANAR = 189

# --- AUDIO (EFECTOS) ---
SFX_WIN = "https://www.myinstants.com/media/sounds/aplausos_1.mp3"
SFX_LOSE = "https://www.myinstants.com/media/sounds/boo.mp3"

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    /* Estilo General */
    .main { background-color: #f5f5f5; }
    
    /* Botones del Mapa - FORZAR TEXTO NEGRO */
    .stButton>button { 
        width: 100%; 
        border-radius: 6px; 
        font-weight: 700; 
        text-align: left; 
        white-space: pre-wrap; 
        height: 75px !important;
        padding: 5px 8px;
        font-size: 0.8rem;
        border: 1px solid #ccc;
        background-color: white !important;
        color: #000000 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        line-height: 1.2;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        border-color: #333;
        z-index: 5;
    }
    
    /* Paneles de Reporte - TEXTO NEGRO */
    .report-card { 
        background-color: white; 
        padding: 15px; 
        border-radius: 8px; 
        border-left: 5px solid #666; 
        margin-bottom: 10px; 
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        color: #000000 !important;
    }
    .report-conflict { border-left-color: #dc3545; background-color: #fff5f5; }
    .report-invest { border-left-color: #28a745; background-color: #f0fff4; }
    .report-change { border-left-color: #ffc107; background-color: #fff9db; }
    
    /* Barra de Progreso Superior */
    .voto-bar-wrapper {
        width: 100%;
        background-color: #e0e0e0;
        border-radius: 10px;
        height: 25px;
        margin-bottom: 20px;
        position: relative;
        overflow: hidden;
    }
    .voto-bar-fill {
        height: 100%;
        border-radius: 10px;
        text-align: center;
        color: white;
        font-weight: bold;
        line-height: 25px;
        font-size: 0.9rem;
        transition: width 0.5s;
        min-width: 2%;
    }

    /* Avisos Finales */
    .win-msg {
        font-size: 35px; font-weight: 800; color: #155724; text-align: center;
        padding: 20px; border: 3px solid #c3e6cb; border-radius: 15px;
        background-color: #d4edda; margin-bottom: 20px;
    }
    .lose-msg {
        font-size: 35px; font-weight: 800; color: #721c24; text-align: center;
        padding: 20px; border: 3px solid #f5c6cb; border-radius: 15px;
        background-color: #f8d7da; margin-bottom: 20px;
    }
    
    /* Dinero */
    .money-box { background-color: #e8f5e9; padding: 10px; border-radius: 10px; border: 1px solid #28a745; color: #155724; }
    .expense-box { background-color: #ffebee; padding: 10px; border-radius: 10px; border: 1px solid #dc3545; color: #721c24; }
    </style>
""", unsafe_allow_html=True)

# --- 1. IDENTIDAD DE PARTIDOS (CORREGIDO PARA COINCIDIR CON TUS NOMBRES) ---
PARTY_COLORS = {
    "Peronismo (PJ/PJ Federal)": {"hex": "#1E88E5", "mark": "🟦", "name": "PJ"},
    "La Libertad Avanza (LLA)": {"hex": "#8E24AA", "mark": "🟪", "name": "LLA"},
    "Propuesta Republicana (PRO)": {"hex": "#FFD700", "mark": "🟨", "name": "PRO"},
    "Union Civica Radical (UCR)": {"hex": "#2E7D32", "mark": "🟩", "name": "UCR"},
    "Izquierda Argentina Unida (FIT-U/PO/Nuevo Mas y +)": {"hex": "#D32F2F", "mark": "🟥", "name": "FIT"},
    "Union de Partidos Nacionalistas (PD, ERF, FPF y +)": {"hex": "#212121", "mark": "⬛", "name": "PN"},
    "Independientes (Sin Partido/Varios Partidos)": {"hex": "#FF9800", "mark": "⚪", "name": "IND"},
    "Especiales": {"hex": "#9E9E9E", "mark": "⬜", "name": "ESP"},
    "Presidentes Históricos": {"hex": "#795548", "mark": "🟫", "name": "HIST"}
}

def get_party_from_candidate(cand_name):
    for p_key, p_data in PARTIDOS.items():
        if cand_name in p_data["candidatos"]:
            return p_key
    return None

def get_visual_id(cand_name):
    """Devuelve [Marca Color] [Emoji]"""
    if not cand_name: return "" 
    p_key = get_party_from_candidate(cand_name)
    # Fallback si no encuentra la key (aunque ahora debería encontrarla)
    mark = PARTY_COLORS[p_key]["mark"] if p_key in PARTY_COLORS else "⬜"
    
    # Buscar emoji
    emoji = "👤"
    if p_key and p_key in PARTIDOS:
        emoji = PARTIDOS[p_key]["candidatos"][cand_name].get("emoji", "👤")
    
    return f"{mark} {emoji}"

# --- 2. GRUPOS Y MAPA ---
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

PROV_TO_GROUP_RAW = {
    "Jujuy": ["PE", "EA"], "Formosa": ["PE", "CP"], "Salta": ["FG", "PC"], "Chaco": ["PE", "CP"],
    "Misiones": ["FG", "PN"], "Tucumán": ["FG", "PN", "CP"], "Santiago del Estero": ["CP"],
    "Corrientes": ["EA"], "La Rioja": ["PE", "CP"], "Catamarca": ["PN", "PE", "CP"],
    "San Juan": ["PN", "CP"], "Santa Fe": ["FG", "ET", "PN", "PC"], "Entre Ríos": ["PN", "PC"],
    "San Luis": ["PC", "CP"], "Córdoba": ["FG", "ET", "PN", "EA"], "PBA Norte": ["FG", "TR", "ET"],
    "CABA": ["FG", "TR", "ET", "EA"], "Mendoza": ["FG", "ET", "PN"], "PBA Oeste": ["FG", "PE", "CP"],
    "PBA Centro": ["ET", "PN"], "La Pampa": ["PE", "CP"], "PBA Costa": ["TR", "ET"],
    "Neuquén": ["TR", "PN", "PC"], "Río Negro": ["TR", "EA"], "Chubut": ["TR", "PN", "PC"],
    "Santa Cruz": ["PN", "PE", "CP"], "Tierra del Fuego": ["TR", "PE"]
}

COSTOS_FIJOS = {
    "Jujuy": 20000, "Formosa": 15000, "Salta": 35000, "Chaco": 25000, "Misiones": 35000,
    "Tucumán": 75000, "Santiago del Estero": 30000, "Corrientes": 30000, "La Rioja": 10000,
    "Catamarca": 12500, "San Juan": 25000, "Santa Fe": 200000, "Entre Ríos": 37500,
    "San Luis": 15000, "Córdoba": 200000, "PBA Norte": 125000, "CABA": 150000,
    "Mendoza": 75000, "PBA Oeste": 200000, "PBA Centro": 50000, "La Pampa": 12500,
    "PBA Costa": 35000, "Neuquén": 22500, "Río Negro": 25000, "Chubut": 20000,
    "Santa Cruz": 10000, "Tierra del Fuego": 10000
}

MAPA_DATA = {
    "Jujuy": {"votos": 8, "pos": (0, 1), "abbr": "JUJ"}, 
    "Formosa": {"votos": 6, "pos": (0, 3), "abbr": "FOR"},
    "Salta": {"votos": 14, "pos": (1, 1), "abbr": "SAL"}, 
    "Chaco": {"votos": 11, "pos": (1, 3), "abbr": "CHA"},
    "Misiones": {"votos": 13, "pos": (1, 4), "abbr": "MIS"}, 
    "Tucumán": {"votos": 17, "pos": (2, 1), "abbr": "TUC"},
    "Santiago del Estero": {"votos": 11, "pos": (2, 2), "abbr": "SDE"}, 
    "Corrientes": {"votos": 12, "pos": (2, 3), "abbr": "CRR"},
    "La Rioja": {"votos": 4, "pos": (3, 0), "abbr": "LRJ"}, 
    "Catamarca": {"votos": 4, "pos": (3, 1), "abbr": "CAT"},
    "San Juan": {"votos": 8, "pos": (4, 0), "abbr": "SJU"}, 
    "Santa Fe": {"votos": 36, "pos": (4, 2), "abbr": "SFE"},
    "Entre Ríos": {"votos": 14, "pos": (4, 3), "abbr": "ERI"}, 
    "San Luis": {"votos": 6, "pos": (5, 0), "abbr": "SLU"},
    "Córdoba": {"votos": 40, "pos": (5, 1), "abbr": "CBA"}, 
    "PBA Norte": {"votos": 28, "pos": (5, 2), "abbr": "PBA-N"},
    "CABA": {"votos": 31, "pos": (5, 3), "abbr": "CABA"}, 
    "Mendoza": {"votos": 20, "pos": (6, 0), "abbr": "MDZ"},
    "PBA Oeste": {"votos": 35, "pos": (6, 1), "abbr": "PBA-O"}, 
    "PBA Centro": {"votos": 15, "pos": (6, 2), "abbr": "PBA-C"},
    "La Pampa": {"votos": 4, "pos": (7, 1), "abbr": "LPA"}, 
    "PBA Costa": {"votos": 12, "pos": (7, 2), "abbr": "PBA-S"},
    "Neuquén": {"votos": 7, "pos": (8, 0), "abbr": "NQN"}, 
    "Río Negro": {"votos": 8, "pos": (8, 1), "abbr": "RNG"},
    "Chubut": {"votos": 6, "pos": (9, 1), "abbr": "CHU"}, 
    "Santa Cruz": {"votos": 3, "pos": (10, 1), "abbr": "SCR"},
    "Tierra del Fuego": {"votos": 3, "pos": (11, 1), "abbr": "TDF"}
}

# --- BASE DE DATOS DE CANDIDATOS ---
PARTIDOS = {
    "Peronismo (PJ/PJ Federal)": {"color": "🔵", "candidatos": {
        # --- LIDERES DEL PJ ---
        "Cristina Kirchner": {"emoji": "✌️", "FG": 10, "TR": 15, "ET": 15, "PN": 15, "PC": -25, "PE": 20, "EA": -45, "CP": 15, "SO": -15, "REL": -5, "JUV": -5, "EMP": -25, "PROG": 30, "PYME": 10},
        "Sergio Massa": {"emoji": "🐯", "FG": 25, "TR": -10, "ET": 20, "PN": 0, "PC": 10, "PE": 10, "EA": -25, "CP": -5, "SO": 20, "REL": 10, "JUV": 5, "EMP": 30, "PROG": 15, "PYME": 25},
        "Axel Kicillof": {"emoji": "🚗", "FG": -5, "TR": 0, "ET": 15, "PN": 0, "PC": -5, "PE": 35, "EA": -30, "CP": 5, "SO": -10, "REL": 20, "JUV": 20, "EMP": -10, "PROG": 20, "PYME": 10},
        "Alberto Fernandez": {"emoji": "🎸", "FG": 20, "TR": -25, "ET": 5, "PN": -10, "PC": 5, "PE": 15, "EA": -10, "CP": -5, "SO": -15, "REL": -15, "JUV": -25, "EMP": 5, "PROG": 30, "PYME": 10},
        "Máximo Kirchner": {"emoji": "🎮", "FG": -10, "TR": -10, "ET": 10, "PN": 5, "PC": -35, "PE": 20, "EA": -40, "CP": 5, "SO": -30, "REL": -10, "JUV": 0, "EMP": -20, "PROG": 25, "PYME": -15},
        "Wado de Pedro": {"emoji": "🚜", "FG": -10, "TR": 10, "ET": 15, "PN": 20, "PC": -30, "PE": 25, "EA": -35, "CP": 5, "SO": -10, "REL": -20, "JUV": 10, "EMP": -15, "PROG": 30, "PYME": 10},
        "Jose Mayans": {"emoji": "🐊", "FG": 25, "TR": 10, "ET": -10, "PN": 5, "PC": -30, "PE": 30, "EA": -40, "CP": 45, "SO": 10, "REL": 35, "JUV": -20, "EMP": -10, "PROG": -5, "PYME": -10},
        "Agustín Rossi": {"emoji": "🛡️", "FG": 20, "TR": 10, "ET": 10, "PN": -30, "PC": -20, "PE": 30, "EA": -50, "CP": 20, "SO": 40, "REL": 0, "JUV": -10, "EMP": -10, "PROG": 30, "PYME": 0},
        "Juan Grabois": {"emoji": "🌱", "FG": -10, "TR": 10, "ET": 30, "PN": 0, "PC": -10, "PE": 30, "EA": -25, "CP": 5, "SO": -25, "REL": 15, "JUV": 30, "EMP": -30, "PROG": 35, "PYME": -10},
        "Guillermo Moreno": {"emoji": "🌭", "FG": 10, "TR": 0, "ET": -10, "PN": 5, "PC": 0, "PE": 5, "EA": -50, "CP": 30, "SO": 10, "REL": 40, "JUV": 5, "EMP": -5, "PROG": -5, "PYME": 15},
        
        # --- GOBERNADORES Y PODER TERRITORIAL (OFICIALISMO PJ) ---
        "Gildo Insfrán": {"emoji": "🧉", "FG": 30, "TR": -15, "ET": 5, "PN": 10, "PC": -45, "PE": 50, "EA": -65, "CP": 40, "SO": 10, "REL": -15, "JUV": -25, "EMP": -20, "PROG": 0, "PYME": -5},
        "Ricardo Quintela": {"emoji": "💵", "FG": 25, "TR": 5, "ET": 10, "PN": -5, "PC": -25, "PE": 25, "EA": -25, "CP": 35, "SO": 5, "REL": 5, "JUV": -15, "EMP": -15, "PROG": 15, "PYME": 5},
        "Sergio Ziliotto": {"emoji": "🚜", "FG": 15, "TR": 5, "ET": 10, "PN": 15, "PC": 5, "PE": 45, "EA": -15, "CP": 15, "SO": -5, "REL": -5, "JUV": -15, "EMP": -15, "PROG": 20, "PYME": 10},
        "Raúl Jalil": {"emoji": "🏞️", "FG": 20, "TR": 15, "ET": 5, "PN": 15, "PC": -25, "PE": 5, "EA": -25, "CP": 10, "SO": 0, "REL": 5, "JUV": -10, "EMP": 0, "PROG": 10, "PYME": 15},
        "Osvaldo Jaldo": {"emoji": "🍊", "FG": 35, "TR": -10, "ET": -15, "PN": 30, "PC": -45, "PE": 5, "EA": -20, "CP": 30, "SO": 10, "REL": 20, "JUV": -15, "EMP": -10, "PROG": 10, "PYME": 10},
        "Gustavo Melella": {"emoji": "🏔️", "FG": 15, "TR": 30, "ET": 10, "PN": -5, "PC": -25, "PE": 25, "EA": -20, "CP": 25, "SO": -10, "REL": -5, "JUV": 10, "EMP": -10, "PROG": 20, "PYME": 5},
        "Jorge Capitanich": {"emoji": "📚", "FG": 30, "TR": 10, "ET": 10, "PN": -10, "PC": -20, "PE": 40, "EA": -40, "CP": 30, "SO": -10, "REL": 5, "JUV": -10, "EMP": -10, "PROG": 20, "PYME": -10},

        # --- JEFES DE BLOQUE Y LEGISLATIVOS ---
        "Germán Martínez": {"emoji": "📋", "FG": 10, "TR": 10, "ET": 10, "PN": -10, "PC": 20, "PE": 20, "EA": -30, "CP": 30, "SO": 0, "REL": -5, "JUV": -20, "EMP": -10, "PROG": 10, "PYME": -10},
        "Cecilia Moreau": {"emoji": "👩", "FG": 10, "TR": -20, "ET": 25, "PN": 10, "PC": -25, "PE": 20, "EA": -15, "CP": 15, "SO": 5, "REL": -10, "JUV": 20, "EMP": -10, "PROG": 30, "PYME": -10},
        
        # --- FIGURAS CLAVE Y SINDICALES ---
        "Agustín Rossi": {"emoji": "🛡️", "FG": 20, "TR": 10, "ET": 10, "PN": -30, "PC": -20, "PE": 30, "EA": -50, "CP": 20, "SO": 40, "REL": 0, "JUV": -10, "EMP": -10, "PROG": 30, "PYME": 0},
        "Hugo Moyano": {"emoji": "🚛", "FG": -30, "TR": 40, "ET": 15, "PN": 5, "PC": -40, "PE": 20, "EA": -45, "CP": 5, "SO": 10, "REL": -5, "JUV": -30, "EMP": -50, "PROG": 50, "PYME": -45},
        "Huguito Moyano": {"emoji": "⚖️", "FG": -10, "TR": 35, "ET": -25, "PN": -5, "PC": -20, "PE": 10, "EA": -30, "CP": 25, "SO": -10, "REL": 0, "JUV": 5, "EMP": -25, "PROG": 45, "PYME": -15},
        "Sergio Berni": {"emoji": "🤠", "FG": 10, "TR": 5, "ET": -5, "PN": 0, "PC": 10, "PE": 25, "EA": -35, "CP": 10, "SO": 35, "REL": 10, "JUV": -15, "EMP": -10, "PROG": -15, "PYME": 0},
        "Aníbal Fernández": {"emoji": "🧳", "FG": 30, "TR": -15, "ET": -5, "PN": -5, "PC": 15, "PE": 30, "EA": -40, "CP": 15, "SO": 35, "REL": 5, "JUV": -25, "EMP": -25, "PROG": -10, "PYME": -15},
        "Felipe Solá": {"emoji": "🌾", "FG": 35, "TR": -5, "ET": 0, "PN": 25, "PC": -20, "PE": 10, "EA": -30, "CP": 15, "SO": 10, "REL": 5, "JUV": -20, "EMP": 5, "PROG": 5, "PYME": 10},
        
        # --- GESTIÓN Y NUEVOS PERFILES ---
        "Malena Galmarini": {"emoji": "🚰", "FG": 5, "TR": 10, "ET": 15, "PN": 0, "PC": -10, "PE": 30, "EA": -30, "CP": 25, "SO": 5, "REL": 5, "JUV": 25, "EMP": 5, "PROG": 15, "PYME": 5},
        "Mayra Mendoza": {"emoji": "🦅", "FG": -20, "TR": -10, "ET": 5, "PN": -25, "PC": -30, "PE": 50, "EA": -60, "CP": 60, "SO": -20, "REL": -10, "JUV": 20, "EMP": -30, "PROG": 60, "PYME": 0},
        "Victoria Tolosa Paz": {"emoji": "👠", "FG": 5, "TR": 5, "ET": 10, "PN": -25, "PC": 15, "PE": 25, "EA": -20, "CP": 15, "SO": -5, "REL": 5, "JUV": 20, "EMP": -5, "PROG": 5, "PYME": 5},
        "Julia Strada": {"emoji": "📊", "FG": -5, "TR": 15, "ET": 30, "PN": 10, "PC": 5, "PE": 25, "EA": -25, "CP": 10, "SO": -10, "REL": -20, "JUV": 10, "EMP": 0, "PROG": 20, "PYME": 10},
        "Leandro Santoro": {"emoji": "🏙️", "FG": 10, "TR": -20, "ET": 10, "PN": 5, "PC": 10, "PE": 10, "EA": 5, "CP": 5, "SO": -5, "REL": 20, "JUV": 10, "EMP": -10, "PROG": 30, "PYME": 5},
        "Natalia Zaracho": {"emoji": "♻️", "FG": -50, "TR": 20, "ET": -30, "PN": -20, "PC": -20, "PE": 50, "EA": -50, "CP": 30, "SO": -50, "REL": 10, "JUV": 20, "EMP": -70, "PROG": 40, "PYME": -20},
        "Itai Hagman": {"emoji": "🧠", "FG": 0, "TR": 10, "ET": 40, "PN": 0, "PC": 10, "PE": 20, "EA": -20, "CP": 20, "SO": -20, "REL": -10, "JUV": 20, "EMP": -40, "PROG": 50, "PYME": 0},

        # --- PJ FEDERAL / DISIDENTES (Subgrupo dentro del PJ) ---
        "Juan Schiaretti": {"emoji": "🧱", "FG": 25, "TR": 15, "ET": -15, "PN": 15, "PC": -25, "PE": -25, "EA": 5, "CP": -5, "SO": -10, "REL": 5, "JUV": -5, "EMP": 20, "PROG": -25, "PYME": 15},
        "Martín Llaryora": {"emoji": "🏙️", "FG": 25, "TR": -10, "ET": 15, "PN": 15, "PC": -25, "PE": 5, "EA": 15, "CP": -5, "SO": 5, "REL": 0, "JUV": 5, "EMP": 5, "PROG": 5, "PYME": 20},
        "Florencio Randazzo": {"emoji": "🚆", "FG": 25, "TR": 5, "ET": -5, "PN": 10, "PC": -10, "PE": -15, "EA": 0, "CP": -10, "SO": -10, "REL": 5, "JUV": -5, "EMP": 20, "PROG": -5, "PYME": 15},
        "Gustavo Sáenz": {"emoji": "🎭", "FG": 45, "TR": -20, "ET": 15, "PN": 10, "PC": 25, "PE": 5, "EA": -5, "CP": 5, "SO": 10, "REL": 20, "JUV": 0, "EMP": 10, "PROG": -5, "PYME": 20},
        "Hugo Passalacqua": {"emoji": "🏞️", "FG": 30, "TR": 15, "ET": 10, "PN": 20, "PC": -15, "PE": 20, "EA": -10, "CP": -10, "SO": 0, "REL": 5, "JUV": -5, "EMP": 5, "PROG": 10, "PYME": 15},
        "Claudio Vidal": {"emoji": "🛢️", "FG": 15, "TR": 25, "ET": -35, "PN": -20, "PC": 50, "PE": 10, "EA": -35, "CP": -20, "SO": 10, "REL": 0, "JUV": -15, "EMP": 45, "PROG": 30, "PYME": -5},
        "Graciela Camaño": {"emoji": "🗣️", "FG": 30, "TR": 10, "ET": 20, "PN": 10, "PC": 20, "PE": -20, "EA": -10, "CP": -10, "SO": 10, "REL": 5, "JUV": -20, "EMP": -10, "PROG": -10, "PYME": 10},
        "Natalia de la Sota": {"emoji": "👔", "FG": 10, "TR": 5, "ET": -5, "PN": 10, "PC": -25, "PE": 0, "EA": 10, "CP": 5, "SO": -5, "REL": 5, "JUV": -10, "EMP": 0, "PROG": -10, "PYME": 15},
        "Juan Manuel Urtubey": {"emoji": "🤵", "FG": 20, "TR": -5, "ET": 5, "PN": 15, "PC": 25, "PE": -10, "EA": 10, "CP": -10, "SO": 5, "REL": 10, "JUV": -10, "EMP": 30, "PROG": -10, "PYME": 10},
        "José Maria Carambia": {"emoji": "🗻", "FG": 30, "TR": 10, "ET": -10, "PN": 15, "PC": 10, "PE": -10, "EA": 5, "CP": 5, "SO": 0, "REL": 0, "JUV": -10, "EMP": 5, "PROG": 5, "PYME": 5},
        "Flavia Royón": {"emoji": "⚡", "FG": 15, "TR": -5, "ET": -5, "PN": 35, "PC": 10, "PE": 10, "EA": 10, "CP": 5, "SO": 0, "REL": 0, "JUV": -10, "EMP": 20, "PROG": -10, "PYME": 10},
        "Pamela Calletti": {"emoji": "⚖️", "FG": 20, "TR": -30, "ET": 10, "PN": 10, "PC": 10, "PE": 5, "EA": 10, "CP": 5, "SO": 5, "REL": 5, "JUV": -5, "EMP": 5, "PROG": -5, "PYME": -10},
        "Fernando Gray": {"emoji": "📡", "FG": 15, "TR": -25, "ET": -10, "PN": 10, "PC": -30, "PE": 10, "EA": -55, "CP": 25, "SO": 5, "REL": 10, "JUV": -10, "EMP": 5, "PROG": -5, "PYME": 35}
    }},
    "La Libertad Avanza (LLA)": {"color": "🟣", "candidatos": {
        # --- PRINCIPALES ---
        "Javier Milei": {"emoji": "🦁", "FG": 20, "TR": 35, "ET": -20, "PN": -20, "PC": 30, "PE": -50, "EA": 30, "CP": -20, "SO": 15, "REL": 25, "JUV": 35, "EMP": 35, "PROG": -50, "PYME": -5},
        "Karina Milei": {"emoji": "🔮", "FG": 20, "TR": -5, "ET": -40, "PN": -20, "PC": 30, "PE": -20, "EA": 15, "CP": -40, "SO": 25, "REL": 5, "JUV": 35, "EMP": 35, "PROG": -25, "PYME": -5},
        "Martín Menem": {"emoji": "📜", "FG": 15, "TR": 0, "ET": -5, "PN": -20, "PC": 10, "PE": -25, "EA": 5, "CP": 0, "SO": 10, "REL": 25, "JUV": -5, "EMP": 5, "PROG": -10, "PYME": 5},
        "Manuel Adorni": {"emoji": "🎤", "FG": -15, "TR": -5, "ET": -20, "PN": 10, "PC": 30, "PE": -40, "EA": 20, "CP": -10, "SO": 5, "REL": -5, "JUV": 25, "EMP": 10, "PROG": -25, "PYME": 0},
        "Luis Caputo": {"emoji": "💰", "FG": -25, "TR": 10, "ET": -10, "PN": 5, "PC": -10, "PE": -30, "EA": 10, "CP": -30, "SO": -10, "REL": 20, "JUV": 5, "EMP": 55, "PROG": -30, "PYME": -40},
        "Patricia Bullrich": {"emoji": "🍷", "FG": 45, "TR": -10, "ET": -25, "PN": -20, "PC": 10, "PE": -30, "EA": 20, "CP": -50, "SO": 45, "REL": 30, "JUV": 5, "EMP": 20, "PROG": -40, "PYME": -10},
        "Luis Petri": {"emoji": "🪖", "FG": 15, "TR": -10, "ET": -30, "PN": 5, "PC": 15, "PE": -20, "EA": 15, "CP": -30, "SO": 30, "REL": 40, "JUV": -10, "EMP": 20, "PROG": -50, "PYME": -10},
        "F. Sturzenegger": {"emoji": "📝", "FG": 10, "TR": 0, "ET": 0, "PN": -10, "PC": -5, "PE": -45, "EA": 30, "CP": -30, "SO": -5, "REL": 20, "JUV": -30, "EMP": 65, "PROG": -30, "PYME": -35},
        "Diego Santilli": {"emoji": "👱", "FG": 10, "TR": 5, "ET": -10, "PN": -5, "PC": 5, "PE": -5, "EA": 5, "CP": -15, "SO": 10, "REL": 5, "JUV": 15, "EMP": 15, "PROG": 0, "PYME": -10},

        
        # --- MESA CHICA / ESTRATEGAS ---
        "Santiago Caputo": {"emoji": "🚬", "FG": -20, "TR": -20, "ET": -25, "PN": -20, "PC": 5, "PE": -40, "EA": 30, "CP": -40, "SO": 50, "REL": 10, "JUV": 75, "EMP": 35, "PROG": -60, "PYME": -5},
        "Guillermo Francos": {"emoji": "🤝", "FG": 25, "TR": 10, "ET": -10, "PN": -5, "PC": 15, "PE": -25, "EA": 35, "CP": -30, "SO": 10, "REL": 5, "JUV": 0, "EMP": 30, "PROG": -30, "PYME": 10},
        
        # --- PODER LEGISLATIVO ---
        "Martín Menem": {"emoji": "📜", "FG": 15, "TR": 0, "ET": -5, "PN": -20, "PC": 10, "PE": -25, "EA": 5, "CP": 0, "SO": 10, "REL": 25, "JUV": -5, "EMP": 5, "PROG": -10, "PYME": 5},
        "Gabriel Bornoroni": {"emoji": "⛽", "FG": 10, "TR": -10, "ET": 0, "PN": 20, "PC": 10, "PE": -20, "EA": 20, "CP": -20, "SO": 10, "REL": 0, "JUV": 5, "EMP": 20, "PROG": -20, "PYME": 15},
        "José Luis Espert": {"emoji": "🔫", "FG": 20, "TR": -5, "ET": -10, "PN": 10, "PC": 10, "PE": -45, "EA": 5, "CP": -35, "SO": 20, "REL": 5, "JUV": 15, "EMP": 30, "PROG": -25, "PYME": -10},
        
        # --- MINISTROS CLAVE ---
        "Sandra Pettovello": {"emoji": "📑", "FG": 5, "TR": -20, "ET": -10, "PN": 0, "PC": 20, "PE": -20, "EA": 25, "CP": -30, "SO": 30, "REL": 10, "JUV": 10, "EMP": 10, "PROG": -60, "PYME": 0},
        "Diana Mondino": {"emoji": "🌍", "FG": -10, "TR": -20, "ET": 10, "PN": 0, "PC": 10, "PE": -30, "EA": 25, "CP": -30, "SO": 5, "REL": 10, "JUV": 15, "EMP": 40, "PROG": -40, "PYME": 15},
        
        # --- LEGISLADORES / REDES ---
        "Lilia Lemoine": {"emoji": "🍋", "FG": 5, "TR": -15, "ET": -40, "PN": -10, "PC": -40, "PE": -35, "EA": 10, "CP": -30, "SO": 0, "REL": -30, "JUV": 45, "EMP": -10, "PROG": -50, "PYME": -20},
        "Agustín Romo": {"emoji": "🐦", "FG": -15, "TR": -10, "ET": -10, "PN": -25, "PC": -10, "PE": -30, "EA": 30, "CP": -40, "SO": 30, "REL": -5, "JUV": 60, "EMP": 5, "PROG": -50, "PYME": 5},
        "Benegas Lynch": {"emoji": "🦅", "FG": -10, "TR": -25, "ET": -20, "PN": -10, "PC": -15, "PE": -40, "EA": 35, "CP": -30, "SO": 10, "REL": 15, "JUV": -10, "EMP": 45, "PROG": -50, "PYME": 10},
        "Ramiro Marra": {"emoji": "📉", "FG": -15, "TR": -20, "ET": -45, "PN": -35, "PC": 20, "PE": -60, "EA": 30, "CP": -10, "SO": 20, "REL": 10, "JUV": 55, "EMP": 40, "PROG": -50, "PYME": -15},
        "Carolina Píparo": {"emoji": "👩", "FG": 10, "TR": -10, "ET": 0, "PN": 5, "PC": 15, "PE": -10, "EA": 15, "CP": -5, "SO": 40, "REL": 15, "JUV": 10, "EMP": 10, "PROG": -30, "PYME": 15},
        "Luis Juez": {"emoji": "🌭", "FG": 5, "TR": -5, "ET": -20, "PN": 10, "PC": -10, "PE": -15, "EA": 15, "CP": 0, "SO": 5, "REL": 5, "JUV": -30, "EMP": -5, "PROG": -5, "PYME": 0},
        "Tronco Figliuolo": {"emoji": "🪵", "FG": -25, "TR": -10, "ET": -5, "PN": 10, "PC": 5, "PE": -15, "EA": 20, "CP": -10, "SO": 20, "REL": 10, "JUV": 35, "EMP": 20, "PROG": -25, "PYME": 20},
        
        # --- OTROS FUNCIONARIOS ---
        "Mariano Cúneo": {"emoji": "⚖️", "FG": -15, "TR": -10, "ET": 5, "PN": 0, "PC": 30, "PE": -20, "EA": 20, "CP": -20, "SO": 45, "REL": 0, "JUV": 10, "EMP": 30, "PROG": -10, "PYME": 10}
    }},
    "Propuesta Republicana (PRO)": {"color": "🟡", "candidatos": {
        # --- PRINCIPALES ---
        "Mauricio Macri": {"emoji": "🐱", "FG": 20, "TR": 5, "ET": -20, "PN": 10, "PC": -20, "PE": -20, "EA": 45, "CP": -40, "SO": 20, "REL": 25, "JUV": 10, "EMP": 55, "PROG": -15, "PYME": -10},
        "Jorge Macri": {"emoji": "🏙️", "FG": 10, "TR": 10, "ET": -30, "PN": 0, "PC": 10, "PE": 10, "EA": 10, "CP": -55, "SO": 40, "REL": 5, "JUV": 5, "EMP": 30, "PROG": -15, "PYME": 15},
        "Ignacio Torres": {"emoji": "🐳", "FG": -10, "TR": 25, "ET": 10, "PN": 20, "PC": 10, "PE": -10, "EA": 15, "CP": -15, "SO": 10, "REL": 10, "JUV": 10, "EMP": 15, "PROG": -10, "PYME": 20},
        "H. R. Larreta": {"emoji": "👽", "FG": 15, "TR": 5, "ET": 5, "PN": 15, "PC": -30, "PE": -10, "EA": 20, "CP": -45, "SO": 15, "REL": 10, "JUV": -15, "EMP": 25, "PROG": 5, "PYME": 20},
        "Gabriela Michetti": {"emoji": "♿", "FG": 20, "TR": 5, "ET": 10, "PN": -10, "PC": 30, "PE": 10, "EA": 10, "CP": -25, "SO": 0, "REL": 50, "JUV": -20, "EMP": 10, "PROG": -5, "PYME": 10},
        "María E. Vidal": {"emoji": "🦁", "FG": 5, "TR": -15, "ET": 5, "PN": 0, "PC": -5, "PE": -5, "EA": 40, "CP": -10, "SO": 15, "REL": 5, "JUV": 10, "EMP": 20, "PROG": 10, "PYME": 10},
        "Esteban Bullrich": {"emoji": "💡", "FG": 10, "TR": -5, "ET": 40, "PN": 10, "PC": 20, "PE": 10, "EA": 15, "CP": -5, "SO": 5, "REL": 40, "JUV": 10, "EMP": 10, "PROG": 0, "PYME": 10},
        "Cristian Ritondo": {"emoji": "👮‍♂️", "FG": 10, "TR": 5, "ET": 10, "PN": 5, "PC": -10, "PE": -10, "EA": 25, "CP": -30, "SO": 45, "REL": 15, "JUV": -30, "EMP": 20, "PROG": -40, "PYME": 5},
        "Rogelio Frigerio": {"emoji": "🚜", "FG": 25, "TR": -5, "ET": 10, "PN": 20, "PC": 25, "PE": -10, "EA": 20, "CP": -15, "SO": 10, "REL": 0, "JUV": 5, "EMP": 20, "PROG": -10, "PYME": 15},
        "Marcelo Orrego": {"emoji": "🏔️", "FG": 25, "TR": -15, "ET": -10, "PN": 20, "PC": 15, "PE": -10, "EA": 20, "CP": 0, "SO": 10, "REL": 0, "JUV": 5, "EMP": 20, "PROG": -10, "PYME": 15},
        "Claudio Poggi": {"emoji": "📜", "FG": 20, "TR": 15, "ET": 10, "PN": -10, "PC": 25, "PE": -5, "EA": 10, "CP": -5, "SO": -5, "REL": -5, "JUV": 10, "EMP": 10, "PROG": -5, "PYME": 10},
        "Fernando de Andreis": {"emoji": "🤫", "FG": -10, "TR": -10, "ET": 20, "PN": 10, "PC": 40, "PE": -20, "EA": 20, "CP": -30, "SO": 10, "REL": 0, "JUV": 20, "EMP": 20, "PROG": -10, "PYME": 10},
        "Enrique Goerling Lara": {"emoji": "🔌", "FG": 25, "TR": 20, "ET": -10, "PN": 20, "PC": 10, "PE": -10, "EA": 15, "CP": -10, "SO": 5, "REL": 5, "JUV": -10, "EMP": 15, "PROG": -5, "PYME": 5},
        "Carlos Melconian": {"emoji": "🍝", "FG": -10, "TR": -10, "ET": 30, "PN": 20, "PC": 20, "PE": -15, "EA": 30, "CP": -20, "SO": 10, "REL": 5, "JUV": -20, "EMP": 50, "PROG": -30, "PYME": 15},
        # --- HALCONES / COMBATIVOS ---
        "Fernando Iglesias": {"emoji": "🥊", "FG": -20, "TR": -20, "ET": 10, "PN": 0, "PC": -20, "PE": -20, "EA": 60, "CP": -60, "SO": 20, "REL": 10, "JUV": 10, "EMP": 10, "PROG": -40, "PYME": 10},
        "R. López Murphy": {"emoji": "🐶", "FG": 5, "TR": 5, "ET": -35, "PN": 5, "PC": -20, "PE": -45, "EA": 25, "CP": -35, "SO": 5, "REL": 25, "JUV": -35, "EMP": 25, "PROG": -30, "PYME": -5},
        "Hernán Lombardi": {"emoji": "🎭", "FG": 15, "TR": -5, "ET": 30, "PN": -5, "PC": -5, "PE": -10, "EA": 25, "CP": -15, "SO": -10, "REL": -10, "JUV": -10, "EMP": 5, "PROG": -10, "PYME": 10},
        "Silvia Lospennato": {"emoji": "🗳️", "FG": -5, "TR": 5, "ET": 10, "PN": -5, "PC": -20, "PE": -25, "EA": 5, "CP": -15, "SO": 10, "REL": -5, "JUV": 5, "EMP": 5, "PROG": 25, "PYME": -10},
        "Federico Pinedo": {"emoji": "🧐", "FG": 25, "TR": -10, "ET": 10, "PN": 5, "PC": -30, "PE": -10, "EA": 20, "CP": -10, "SO": 5, "REL": 5, "JUV": -20, "EMP": 35, "PROG": -40, "PYME": 20},
        "Néstor Grindetti": {"emoji": "⚽", "FG": 10, "TR": -5, "ET": -15, "PN": -5, "PC": -20, "PE": -25, "EA": 0, "CP": -20, "SO": 25, "REL": 10, "JUV": -15, "EMP": 20, "PROG": 0, "PYME": 10}
    }},
    "Union Civica Radical (UCR)": {"color": "⚪", "candidatos": {
        # --- PRESIDENTE Y RENOVACIÓN ---
        "Leonel Chiarella": {"emoji": "🦊", "FG": 10, "TR": -5, "ET": 10, "PN": 10, "PC": 20, "PE": 10, "EA": 15, "CP": -30, "SO": 20, "REL": 5, "JUV": 30, "EMP": 5, "PROG": -5, "PYME": 5},
        "Martín Lousteau": {"emoji": "🎓", "FG": 30, "TR": -25, "ET": 25, "PN": -25, "PC": -20, "PE": 20, "EA": 5, "CP": -20, "SO": 10, "REL": -20, "JUV": 25, "EMP": 15, "PROG": 25, "PYME": 15},
        "Ricardo Alfonsín": {"emoji": "👴", "FG": 20, "TR": -20, "ET": 15, "PN": 5, "PC": -15, "PE": 20, "EA": 15, "CP": -20, "SO": -15, "REL": 10, "JUV": 0, "EMP": -15, "PROG": 30, "PYME": 5},
        "Ernesto Sanz": {"emoji": "🤠", "FG": 30, "TR": -10, "ET": 10, "PN": 5, "PC": 5, "PE": 5, "EA": 30, "CP": -40, "SO": 5, "REL": 0, "JUV": -20, "EMP": 10, "PROG": -10, "PYME": 10},
        "Gerardo Zamora": {"emoji": "🏗️", "FG": 25, "TR": 0, "ET": -15, "PN": -10, "PC": -10, "PE": 15, "EA": 30, "CP": 5, "SO": 0, "REL": -5, "JUV": -15, "EMP": 15, "PROG": -20, "PYME": 10},
        "Facundo Manes": {"emoji": "🧠", "FG": -10, "TR": 5, "ET": 35, "PN": 10, "PC": -20, "PE": 5, "EA": 5, "CP": -30, "SO": -25, "REL": 0, "JUV": 5, "EMP": -10, "PROG": 10, "PYME": 10},
        "Rodrigo de Loredo": {"emoji": "🚌", "FG": 5, "TR": 5, "ET": -10, "PN": 5, "PC": -10, "PE": -15, "EA": 5, "CP": -40, "SO": 5, "REL": -15, "JUV": 30, "EMP": 5, "PROG": 10, "PYME": 10},
        "Maximiliano Pullaro": {"emoji": "👮", "FG": 30, "TR": 20, "ET": 15, "PN": 15, "PC": 20, "PE": -5, "EA": 20, "CP": -15, "SO": 25, "REL": 0, "JUV": 10, "EMP": 10, "PROG": -10, "PYME": 15},
        "Gerardo Morales": {"emoji": "🌵", "FG": 35, "TR": -5, "ET": -10, "PN": 25, "PC": -40, "PE": 5, "EA": 5, "CP": -20, "SO": 25, "REL": 20, "JUV": -15, "EMP": 5, "PROG": -15, "PYME": 15},
        "Julio Cobos": {"emoji": "👎", "FG": 30, "TR": 5, "ET": 0, "PN": -10, "PC": -30, "PE": -5, "EA": 5, "CP": -30, "SO": 10, "REL": 25, "JUV": -20, "EMP": 10, "PROG": -15, "PYME": 15},
        "Martín Tetaz": {"emoji": "📉", "FG": 15, "TR": 5, "ET": 5, "PN": -10, "PC": 10, "PE": -15, "EA": 25, "CP": -25, "SO": 0, "REL": -5, "JUV": 15, "EMP": 25, "PROG": -20, "PYME": 10},
        "Mario Negri": {"emoji": "👴", "FG": 10, "TR": 10, "ET": 15, "PN": 5, "PC": -10, "PE": 10, "EA": 15, "CP": -20, "SO": 5, "REL": -10, "JUV": -25, "EMP": 10, "PROG": 5, "PYME": 10},
        
        # --- GOBERNADORES FUERTES ---
        "Gustavo Valdés": {"emoji": "🐊", "FG": 60, "TR": 5, "ET": -10, "PN": -15, "PC": -25, "PE": 0, "EA": 30, "CP": -20, "SO": 10, "REL": 10, "JUV": -10, "EMP": 10, "PROG": -10, "PYME": 10},
        "Alfredo Cornejo": {"emoji": "🍇", "FG": 30, "TR": 10, "ET": 10, "PN": 10, "PC": 20, "PE": 10, "EA": 25, "CP": -50, "SO": 20, "REL": -5, "JUV": -15, "EMP": 20, "PROG": -15, "PYME": 20},
        "Carlos Sadir": {"emoji": "🌄", "FG": 20, "TR": -10, "ET": -10, "PN": 5, "PC": 10, "PE": 20, "EA": 30, "CP": -10, "SO": 10, "REL": 5, "JUV": -10, "EMP": 10, "PROG": -5, "PYME": 10},
        "Leandro Zdero": {"emoji": "🌲", "FG": 15, "TR": 5, "ET": 5, "PN": -10, "PC": 10, "PE": 15, "EA": 25, "CP": -5, "SO": 0, "REL": -5, "JUV": 15, "EMP": 25, "PROG": -20, "PYME": 10},
        "Daniel Angelici": {"emoji": "🎰", "FG": -10, "TR": -10, "ET": -10, "PN": 5, "PC": -30, "PE": 10, "EA": 5, "CP": -10, "SO": 20, "REL": 10, "JUV": -10, "EMP": 50, "PROG": -40, "PYME": -10},
        
        # --- LEGISLADORES / INTERIOR ---
        "Eduardo Vischi": {"emoji": "👴🏻", "FG": 20, "TR": 10, "ET": 10, "PN": 5, "PC": 20, "PE": 10, "EA": 15, "CP": -10, "SO": -10, "REL": -10, "JUV": -20, "EMP": 5, "PROG": 5, "PYME": 5},
        "Luis Naidenoff": {"emoji": "❤︎", "FG": 25, "TR": 10, "ET": -10, "PN": 10, "PC": 20, "PE": 5, "EA": 25, "CP": -30, "SO": 15, "REL": 10, "JUV": -10, "EMP": 10, "PROG": -5, "PYME": 10},
        "Pamela Verasay": {"emoji": "🍈", "FG": 20, "TR": 5, "ET": 5, "PN": 15, "PC": -10, "PE": 10, "EA": 15, "CP": -10, "SO": -5, "REL": -10, "JUV": -10, "EMP": 5, "PROG": 0, "PYME": 15},
        "Ricardo Gil Lavedra": {"emoji": "⚖️", "FG": 40, "TR": 5, "ET": 20, "PN": 0, "PC": -15, "PE": 15, "EA": 5, "CP": -25, "SO": -10, "REL": -15, "JUV": -10, "EMP": -5, "PROG": 20, "PYME": 5},
        "Lula Levy": {"emoji": "🤳", "FG": -25, "TR": -45, "ET": 40, "PN": 5, "PC": 15, "PE": 25, "EA": 5, "CP": -35, "SO": -10, "REL": -25, "JUV": 40, "EMP": 5, "PROG": 15, "PYME": 10},
        "Juan Pablo Valdés": {"emoji": "⚡", "FG": 20, "TR": 10, "ET": 10, "PN": 5, "PC": 10, "PE": -5, "EA": 40, "CP": -10, "SO": 0, "REL": 20, "JUV": 0, "EMP": 10, "PROG": -10, "PYME": 10},
        "Elías Suárez": {"emoji": "📋", "FG": -5, "TR": 10, "ET": 10, "PN": -10, "PC": -10, "PE": -5, "EA": 30, "CP": 15, "SO": 0, "REL": -5, "JUV": -15, "EMP": 15, "PROG": -20, "PYME": 10}
    }},
    "Izquierda Argentina Unida (FIT-U/PO/Nuevo Mas y +)": {"color": "🔴", "candidatos": {
        # --- CANDIDATOS PRESIDENCIALES / LIDERAZGO ---
        "Myriam Bregman": {"emoji": "✊", "FG": -35, "TR": -5, "ET": 30, "PN": 30, "PC": 10, "PE": 30, "EA": -20, "CP": -25, "SO": -20, "REL": -10, "JUV": 50, "EMP": -30, "PROG": 25, "PYME": -20},
        "Nicolás del Caño": {"emoji": "📹", "FG": -25, "TR": 10, "ET": 25, "PN": 20, "PC": 15, "PE": 25, "EA": 0, "CP": 0, "SO": -25, "REL": -25, "JUV": 30, "EMP": -25, "PROG": 30, "PYME": -25},
        "Manuela Castañeira": {"emoji": "🚩", "FG": -65, "TR": 15, "ET": 60, "PN": 15, "PC": 30, "PE": 40, "EA": -20, "CP": -10, "SO": -35, "REL": -20, "JUV": 35, "EMP": -20, "PROG": 30, "PYME": -15},
        "Gabriel Solano": {"emoji": "📢", "FG": -40, "TR": 25, "ET": 30, "PN": 10, "PC": 0, "PE": 25, "EA": -10, "CP": -10, "SO": -30, "REL": -35, "JUV": 20, "EMP": -35, "PROG": 55, "PYME": -20},
        "Romina Del Plá": {"emoji": "🏫", "FG": -35, "TR": 20, "ET": 35, "PN": 5, "PC": 10, "PE": 30, "EA": -40, "CP": -25, "SO": -30, "REL": -25, "JUV": 15, "EMP": -25, "PROG": 50, "PYME": -25},
        "Néstor Pitrola": {"emoji": "📢", "FG": -55, "TR": 40, "ET": 20, "PN": -20, "PC": -10, "PE": 45, "EA": -30, "CP": -10, "SO": -40, "REL": -30, "JUV": 10, "EMP": -60, "PROG": 50, "PYME": -20},
        "Vanina Biasi": {"emoji": "✊", "FG": -25, "TR": 15, "ET": 25, "PN": 10, "PC": 20, "PE": 30, "EA": -10, "CP": -10, "SO": -30, "REL": -35, "JUV": 25, "EMP": -40, "PROG": 55, "PYME": -5},
        "Luca Bonfante": {"emoji": "🎓", "FG": -10, "TR": 5, "ET": 45, "PN": 5, "PC": -10, "PE": 25, "EA": -5, "CP": -5, "SO": -25, "REL": -45, "JUV": 55, "EMP": -45, "PROG": 50, "PYME": 0},
        "Christian Castillo": {"emoji": "📕", "FG": -20, "TR": 10, "ET": 15, "PN": 10, "PC": -10, "PE": 20, "EA": -30, "CP": -30, "SO": -40, "REL": -30, "JUV": 10, "EMP": -40, "PROG": 40, "PYME": -30},
        "Jorge Altamira": {"emoji": "👴", "FG": -35, "TR": 25, "ET": 30, "PN": 15, "PC": -10, "PE": 35, "EA": -10, "CP": -10, "SO": -45, "REL": -25, "JUV": 10, "EMP": -45, "PROG": 45, "PYME": -10},
        
        # --- REFERENTES TERRITORIALES / SINDICALES ---
        "Alejandro Vilca": {"emoji": "🌵", "FG": 5, "TR": 30, "ET": 10, "PN": 20, "PC": -35, "PE": 20, "EA": 5, "CP": -20, "SO": -30, "REL": -10, "JUV": 5, "EMP": -40, "PROG": 40, "PYME": -10},
        "Celeste Fierro": {"emoji": "💚", "FG": -10, "TR": 20, "ET": 20, "PN": -20, "PC": 5, "PE": 20, "EA": -15, "CP": -15, "SO": -30, "REL": -40, "JUV": 20, "EMP": -40, "PROG": 40, "PYME": 0},
        "Eduardo Belliboni": {"emoji": "🔥", "FG": -65, "TR": 50, "ET": -20, "PN": -30, "PC": -45, "PE": 30, "EA": -45, "CP": -30, "SO": -60, "REL": -40, "JUV": -20, "EMP": -70, "PROG": 60, "PYME": -40},
        "Silvia Saravia": {"emoji": "🍲", "FG": 0, "TR": 30, "ET": -5, "PN": -10, "PC": -5, "PE": 40, "EA": -20, "CP": -10, "SO": -40, "REL": -10, "JUV": 10, "EMP": -40, "PROG": 55, "PYME": -20},
        "Carlos Santillán": {"emoji": "🐕", "FG": 30, "TR": 40, "ET": -10, "PN": 0, "PC": -20, "PE": 20, "EA": 5, "CP": -30, "SO": -10, "REL": 10, "JUV": -20, "EMP": -30, "PROG": 30, "PYME": -10},
        "Mónica Schlotthauer": {"emoji": "🚂", "FG": -10, "TR": 50, "ET": 40, "PN": -20, "PC": -30, "PE": 10, "EA": -20, "CP": -20, "SO": -30, "REL": -20, "JUV": 10, "EMP": -60, "PROG": 50, "PYME": -10},
        "Vilma Ripoll": {"emoji": "⚕️", "FG": -30, "TR": 30, "ET": 30, "PN": -10, "PC": 10, "PE": 30, "EA": -20, "CP": -20, "SO": -30, "REL": -30, "JUV": -10, "EMP": -50, "PROG": 60, "PYME": -10},
        
        # --- HISTÓRICOS Y OTROS --
    
        "Luis Zamora": {"emoji": "📚", "FG": -35, "TR": 10, "ET": 50, "PN": -10, "PC": 20, "PE": 10, "EA": -10, "CP": -10, "SO": -30, "REL": -20, "JUV": 20, "EMP": -50, "PROG": 50, "PYME": 0},
        "Ailén Barbani": {"emoji": "💅", "FG": -20, "TR": 0, "ET": 10, "PN": 0, "PC": 10, "PE": 10, "EA": 0, "CP": -10, "SO": -10, "REL": -20, "JUV": 50, "EMP": -20, "PROG": 20, "PYME": 0},
        "Federico Winokur": {"emoji": "🏫", "FG": -40, "TR": 20, "ET": 50, "PN": 15, "PC": -50, "PE": 30, "EA": -50, "CP": -35, "SO": -45, "REL": -40, "JUV": 25, "EMP": -50, "PROG": 45, "PYME": -10},
        "Hugo Bodart": {"emoji": "🚩", "FG": -30, "TR": 30, "ET": 25, "PN": 15, "PC": -25, "PE": 40, "EA": -20, "CP": -35, "SO": -15, "REL": -35, "JUV": -20, "EMP": -50, "PROG": 50, "PYME": -15},
        "Juan Carlos Giordano": {"emoji": "📢", "FG": 5, "TR": 20, "ET": 20, "PN": 30, "PC": 5, "PE": 25, "EA": -5, "CP": -5, "SO": -25, "REL": -20, "JUV": -5, "EMP": -45, "PROG": 50, "PYME": 5}
    }},
    "Union de Partidos Nacionalistas (PD, ERF, FPF y +": {"color": "⚫", "candidatos": {
        # --- LIDERAZGO ---
        "Victoria Villarruel": {"emoji": "🛡️", "FG": -10, "TR": 15, "ET": -20, "PN": 5, "PC": 5, "PE": 20, "EA": 10, "CP": 5, "SO": 55, "REL": 35, "JUV": 10, "EMP": 15, "PROG": -30, "PYME": 5},
        "Miguel Ángel Pichetto": {"emoji": "👔", "FG": 20, "TR": 10, "ET": 10, "PN": 20, "PC": 20, "PE": 0, "EA": -20, "CP": -20, "SO": 25, "REL": -10, "JUV": -20, "EMP": 30, "PROG": -10, "PYME": 15},
        "Santiago Cúneo": {"emoji": "🤬", "FG": 30, "TR": -10, "ET": -35, "PN": 40, "PC": -40, "PE": 10, "EA": 5, "CP": 5, "SO": 20, "REL": 15, "JUV": 20, "EMP": -15, "PROG": -10, "PYME": 10},
        "Gómez Centurión": {"emoji": "⚔️", "FG": -10, "TR": 25, "ET": 0, "PN": 25, "PC": -15, "PE": -10, "EA": -15, "CP": -15, "SO": 50, "REL": 50, "JUV": -25, "EMP": -10, "PROG": -25, "PYME": 10},
        "Alejandro Biondini": {"emoji": "🦅", "FG": -60, "TR": 10, "ET": -20, "PN": 65, "PC": -50, "PE": 5, "EA": -30, "CP": -30, "SO": 50, "REL": 45, "JUV": -65, "EMP": -35, "PROG": -75, "PYME": -25},
        "Cesar Biondini": {"emoji": "🐣", "FG": -5, "TR": 0, "ET": 25, "PN": 35, "PC": 25, "PE": 0, "EA": -45, "CP": -5, "SO": 35, "REL": 25, "JUV": 20, "EMP": -30, "PROG": -25, "PYME": -10},
        "Aldo Rico": {"emoji": "🪖", "FG": -20, "TR": 15, "ET": -10, "PN": 20, "PC": 10, "PE": 5, "EA": -25, "CP": -5, "SO": 50, "REL": 40, "JUV": -30, "EMP": -15, "PROG": -25, "PYME": 20},
        "José Bonacci": {"emoji": "📜", "FG": -65, "TR": 25, "ET": -20, "PN": 50, "PC": -45, "PE": 5, "EA": -30, "CP": -15, "SO": 40, "REL": 30, "JUV": -25, "EMP": 20, "PROG": -60, "PYME": 20},

        # --- REFERENTES DE NICHO ---
        "Cynthia Hotton": {"emoji": "✝️", "FG": 5, "TR": 10, "ET": -20, "PN": 10, "PC": 5, "PE": 5, "EA": 10, "CP": -30, "SO": 20, "REL": 70, "JUV": -25, "EMP": 10, "PROG": -75, "PYME": 5},
        "Padre Olivera Ravasi": {"emoji": "✝️", "FG": -20, "TR": -10, "ET": 10, "PN": 20, "PC": -30, "PE": -20, "EA": 0, "CP": -20, "SO": 50, "REL": 80, "JUV": 10, "EMP": 10, "PROG": -80, "PYME": -10},
        "Marcelo Gullo": {"emoji": "🇪🇸", "FG": 10, "TR": 10, "ET": 30, "PN": 20, "PC": -10, "PE": -5, "EA": -20, "CP": 30, "SO": 10, "REL": 40, "JUV": -10, "EMP": -10, "PROG": -20, "PYME": -30},
        "Adrian Salbuchi": {"emoji": "🌍", "FG": -10, "TR": 10, "ET": 10, "PN": 30, "PC": -20, "PE": 20, "EA": -10, "CP": 10, "SO": 20, "REL": -10, "JUV": -10, "EMP": -60, "PROG": -30, "PYME": 10},
        "Chinda Brandolino": {"emoji": "⚕️", "FG": -20, "TR": 5, "ET": -20, "PN": 10, "PC": -40, "PE": 10, "EA": -30, "CP": -30, "SO": 10, "REL": 60, "JUV": -20, "EMP": -40, "PROG": -75, "PYME": 5},
        "Cecilia Pando": {"emoji": "🧣", "FG": -45, "TR": -10, "ET": -20, "PN": 20, "PC": -50, "PE": -35, "EA": 30, "CP": -50, "SO": 70, "REL": 40, "JUV": -40, "EMP": 10, "PROG": -80, "PYME": -30},
        
        # --- OTROS ---
        "Alberto Samid": {"emoji": "🥩", "FG": -35, "TR": -15, "ET": -30, "PN": 50, "PC": 5, "PE": 10, "EA": -5, "CP": 10, "SO": 10, "REL": 25, "JUV": 5, "EMP": 10, "PROG": -15, "PYME": 15},
        "Jorge Sobisch": {"emoji": "🏔️", "FG": 20, "TR": 0, "ET": -20, "PN": 25, "PC": 30, "PE": 10, "EA": -10, "CP": -25, "SO": 30, "REL": 15, "JUV": -30, "EMP": 15, "PROG": -25, "PYME": 20},
        "Eduardo Amadeo": {"emoji": "💼", "FG": 10, "TR": -10, "ET": -10, "PN": 10, "PC": 10, "PE": 10, "EA": 10, "CP": -10, "SO": 10, "REL": 10, "JUV": -10, "EMP": 10, "PROG": -10, "PYME": 10},
        "Raúl Castells": {"emoji": "🧔", "FG": -50, "TR": -30, "ET": -25, "PN": 70, "PC": 40, "PE": 0, "EA": -45, "CP": -45, "SO": 10, "REL": 30, "JUV": 50, "EMP": -50, "PROG": 30, "PYME": -50},
        "Larry de Clay": {"emoji": "🎩", "FG": -10, "TR": 5, "ET": -15, "PN": 20, "PC": -25, "PE": -5, "EA": -15, "CP": 25, "SO": 10, "REL": 25, "JUV": 30, "EMP": 5, "PROG": -30, "PYME": 10},
        "Rocío Bonacci": {"emoji": "💅", "FG": -10, "TR": 5, "ET": -30, "PN": 5, "PC": 20, "PE": -45, "EA": 10, "CP": 5, "SO": 35, "REL": 45, "JUV": -10, "EMP": 15, "PROG": -40, "PYME": 5}
    }},
    "Independientes (Sin Partido/Varios Partidos)": {"color": "⬜", "candidatos": {
        # --- TERCERA VÍA / FEDERALES ---
        "Roberto Lavagna": {"emoji": "🧦", "FG": 20, "TR": 20, "ET": 0, "PN": 15, "PC": -25, "PE": 0, "EA": 10, "CP": -20, "SO": 5, "REL": 5, "JUV": -25, "EMP": 20, "PROG": 5, "PYME": 20},
        "Daniel Scioli": {"emoji": "🚤", "FG": 5, "TR": 0, "ET": -10, "PN": -10, "PC": -15, "PE": 0, "EA": 10, "CP": 10, "SO": 15, "REL": 10, "JUV": 10, "EMP": 20, "PROG": 15, "PYME": 20},
        "Elisa Carrió": {"emoji": "✝️", "FG": 15, "TR": -5, "ET": 10, "PN": 5, "PC": 25, "PE": 5, "EA": 40, "CP": -20, "SO": -10, "REL": 25, "JUV": -10, "EMP": -15, "PROG": 20, "PYME": 0},
        "Margarita Stolbizer": {"emoji": "👜", "FG": 45, "TR": -10, "ET": 10, "PN": 5, "PC": -15, "PE": 10, "EA": 5, "CP": -35, "SO": -10, "REL": -10, "JUV": 5, "EMP": -10, "PROG": 20, "PYME": 10},
        "Graciela Ocaña": {"emoji": "🐜", "FG": 10, "TR": -30, "ET": 40, "PN": -10, "PC": 30, "PE": 10, "EA": 20, "CP": -20, "SO": 30, "REL": 10, "JUV": -10, "EMP": -5, "PROG": -10, "PYME": 10},
        "Antonio Bonfatti": {"emoji": "🌹", "FG": 40, "TR": 10, "ET": 30, "PN": 20, "PC": 15, "PE": 10, "EA": -20, "CP": -20, "SO": -10, "REL": -10, "JUV": 0, "EMP": 0, "PROG": 30, "PYME": 20},
                "Esteban Paulón": {"emoji": "🏳️‍🌈", "FG": 15, "TR": -10, "ET": 30, "PN": 15, "PC": -25, "PE": 15, "EA": -5, "CP": -5, "SO": -20, "REL": -70, "JUV": 35, "EMP": -10, "PROG": 75, "PYME": 5},

        # --- PROVINCIALES ---
        "Carlos Rovira": {"emoji": "🔇", "FG": 40, "TR": 10, "ET": 20, "PN": 20, "PC": 5, "PE": 30, "EA": -10, "CP": 0, "SO": 10, "REL": 10, "JUV": -10, "EMP": 10, "PROG": 0, "PYME": 10},
        "Alberto Weretilneck": {"emoji": "🍏", "FG": 15, "TR": 20, "ET": -10, "PN": -15, "PC": -20, "PE": 15, "EA": 5, "CP": 0, "SO": 0, "REL": 0, "JUV": -5, "EMP": 15, "PROG": 0, "PYME": 20},
        "Rolando Figueroa": {"emoji": "⛰️", "FG": 15, "TR": 25, "ET": 15, "PN": 30, "PC": -25, "PE": 0, "EA": -5, "CP": -5, "SO": -10, "REL": -10, "JUV": -15, "EMP": 10, "PROG": -15, "PYME": 20},
        "Oscar Zago": {"emoji": "👔", "FG": 20, "TR": 10, "ET": -5, "PN": -5, "PC": 20, "PE": -10, "EA": 5, "CP": 0, "SO": 5, "REL": 0, "JUV": -20, "EMP": 10, "PROG": -10, "PYME": 10},
        "Carlos Arce": {"emoji": "🧉", "FG": 30, "TR": -10, "ET": 10, "PN": 15, "PC": 5, "PE": 10, "EA": -10, "CP": -10, "SO": 5, "REL": 5, "JUV": -10, "EMP": 10, "PROG": -5, "PYME": 10},
        
        # --- OTROS ---
        "Maximiliano Ferraro": {"emoji": "📑", "FG": 10, "TR": 10, "ET": 20, "PN": 5, "PC": 20, "PE": 10, "EA": 20, "CP": -20, "SO": -10, "REL": 5, "JUV": -10, "EMP": -5, "PROG": 10, "PYME": 10},
        "Humberto Tumini": {"emoji": "✌️", "FG": 10, "TR": 10, "ET": 10, "PN": 10, "PC": -10, "PE": 30, "EA": -10, "CP": 10, "SO": 10, "REL": -30, "JUV": 10, "EMP": -30, "PROG": 30, "PYME": -10},
        "Claudio 'Turco' Garcia": {"emoji": "⚽", "FG": -25, "TR": 5, "ET": 5, "PN": -10, "PC": 10, "PE": 20, "EA": 5, "CP": 0, "SO": 0, "REL": 15, "JUV": 25, "EMP": -20, "PROG": -5, "PYME": 0},
        "Carlos Maslatón": {"emoji": "📈", "FG": 10, "TR": 0, "ET": 5, "PN": 10, "PC": 30, "PE": -35, "EA": 10, "CP": 5, "SO": 0, "REL": -5, "JUV": 35, "EMP": 35, "PROG": 25, "PYME": 20},
        "Domingo Cavallo": {"emoji": "💲", "FG": -10, "TR": -25, "ET": -35, "PN": -20, "PC": 50, "PE": -25, "EA": 35, "CP": 20, "SO": 20, "REL": 30, "JUV": 5, "EMP": 65, "PROG": -40, "PYME": 0},
        "Luis Barrionuevo": {"emoji": "🍽️", "FG": 5, "TR": 20, "ET": -10, "PN": 5, "PC": -20, "PE": 0, "EA": -25, "CP": 5, "SO": 30, "REL": -5, "JUV": -40, "EMP": -20, "PROG": 40, "PYME": -40},
        "Fernando Burlando": {"emoji": "⚖️", "FG": -20, "TR": -10, "ET": 0, "PN": -5, "PC": -5, "PE": 0, "EA": 0, "CP": -10, "SO": 25, "REL": 10, "JUV": 5, "EMP": 15, "PROG": -15, "PYME": 15},
        "Amalia Granata": {"emoji": "💙", "FG": 5, "TR": -10, "ET": 0, "PN": 25, "PC": -30, "PE": -15, "EA": -40, "CP": 5, "SO": 30, "REL": 35, "JUV": 10, "EMP": -10, "PROG": -25, "PYME": 20},
        "Fernanda Tokumoto": {"emoji": "🌸", "FG": -20, "TR": 5, "ET": -10, "PN": -30, "PC": -30, "PE": -5, "EA": 10, "CP": -10, "SO": 20, "REL": -5, "JUV": -5, "EMP": 5, "PROG": 5, "PYME": 35},
        "Sixto Christiani": {"emoji": "✝️", "FG": 30, "TR": 20, "ET": 25, "PN": 10, "PC": -15, "PE": 5, "EA": -35, "CP": -35, "SO": 5, "REL": -30, "JUV": 60, "EMP": 15, "PROG": 5, "PYME": 10},
        "Yamil Santoro": {"emoji": "🗽", "FG": 5, "TR": 0, "ET": -20, "PN": -20, "PC": 10, "PE": -45, "EA": 10, "CP": 0, "SO": -5, "REL": -5, "JUV": -10, "EMP": +50, "PROG": -15, "PYME": 5},
        "Carlos del Frade": {"emoji": "🌾", "FG": -5, "TR": 5, "ET": 5, "PN": 30, "PC": 10, "PE": 30, "EA": -20, "CP": 0, "SO": 0, "REL": -30, "JUV": -20, "EMP": -40, "PROG": 20, "PYME": -10},
        "Juan Carlos Blanco": {"emoji": "⚪", "FG": -10, "TR": 10, "ET": 5, "PN": 10, "PC": 20, "PE": 20, "EA": -20, "CP": -20, "SO": 5, "REL": 5, "JUV": -10, "EMP": -10, "PROG": 20, "PYME": -5},
        "Roberto Baradel": {"emoji": "👷", "FG": -15, "TR": 15, "ET": 30, "PN": -10, "PC": -45, "PE": 35, "EA": -40, "CP": 15, "SO": -20, "REL": -15, "JUV": 5, "EMP": -45, "PROG": 45, "PYME": -10},
        "Oscar Moscariello": {"emoji": "📜", "FG": -15, "TR": 20, "ET": 15, "PN": -15, "PC": 5, "PE": -15, "EA": 5, "CP": -10, "SO": 10, "REL": 20, "JUV": 0, "EMP": 10, "PROG": -5, "PYME": 20},
        "Luis D'Elía": {"emoji": "✊", "FG": -15, "TR": 10, "ET": 15, "PN": 10, "PC": 10, "PE": -10, "EA": 5, "CP": 5, "SO": -10, "REL": 0, "JUV": 10, "EMP": 20, "PROG": -15, "PYME": 10},
        "Turco García": {"emoji": "⚽", "FG": -10, "TR": 5, "ET": 5, "PN": -10, "PC": 10, "PE": 20, "EA": 5, "CP": 0, "SO": 0, "REL": 15, "JUV": 25, "EMP": -20, "PROG": -5, "PYME": 0},
        "R. Caruso Lombardi": {"emoji": "💨", "FG": -45, "TR": -5, "ET": 5, "PN": 5, "PC": 20, "PE": -10, "EA": 15, "CP": -20, "SO": -20, "REL": 0, "JUV": 35, "EMP": -10, "PROG": 5, "PYME": -10},
        "Leopoldo Moreau": {"emoji": "🦊", "FG": 20, "TR": 15, "ET": 20, "PN": 10, "PC": -40, "PE": 20, "EA": -10, "CP": -10, "SO": -10, "REL": -20, "JUV": -10, "EMP": 0, "PROG": 25, "PYME": 10},
        "Sergio Abrevaya": {"emoji": "👓", "FG": 20, "TR": 10, "ET": 10, "PN": 5, "PC": -30, "PE": 15, "EA": 10, "CP": -30, "SO": -10, "REL": -5, "JUV": 10, "EMP": -10, "PROG": 15, "PYME": 20},
        "Alberto Rodríguez Saá": {"emoji": "🏞️", "FG": 25, "TR": 20, "ET": -15, "PN": -20, "PC": 10, "PE": -15, "EA": 15, "CP": 15, "SO": 10, "REL": 10, "JUV": -25, "EMP": 10, "PROG": 0, "PYME": 15},
        "José Luis Ramón": {"emoji": "📢", "FG": 15, "TR": -5, "ET": 10, "PN": 5, "PC": 30, "PE": 15, "EA": -20, "CP": -20, "SO": -10, "REL": -5, "JUV": 10, "EMP": -15, "PROG": 10, "PYME": 10},
        "Luis Rosales": {"emoji": "👔", "FG": 15, "TR": 5, "ET": 10, "PN": -20, "PC": 5, "PE": -25, "EA": 5, "CP": -20, "SO": 10, "REL": 5, "JUV": -25, "EMP": 5, "PROG": -10, "PYME": 15},
        "Andres Passamonti": {"emoji": "🔵", "FG": 10, "TR": 0, "ET": 5, "PN": 5, "PC": 25, "PE": -5, "EA": 0, "CP": -10, "SO": 10, "REL": 10, "JUV": -10, "EMP": 5, "PROG": -10, "PYME": 5},
        "Monica Fein": {"emoji": "🌹", "FG": 20, "TR": 10, "ET": 25, "PN": 10, "PC": 0, "PE": 25, "EA": -20, "CP": -15, "SO": -20, "REL": -20, "JUV": 10, "EMP": -10, "PROG": 35, "PYME": 15},
        "José Bordón": {"emoji": "🍷", "FG": 30, "TR": 10, "ET": 0, "PN": 15, "PC": -15, "PE": -5, "EA": 5, "CP": 10, "SO": 10, "REL": 5, "JUV": -15, "EMP": 10, "PROG": 5, "PYME": 10},
        "Chacho Álvarez": {"emoji": "✌️", "FG": 50, "TR": -25, "ET": -15, "PN": -15, "PC": 35, "PE": 0, "EA": 25, "CP": 25, "SO": -25, "REL": -10, "JUV": -5, "EMP": -5, "PROG": 0, "PYME": 10},
        "Carlos Zapata": {"emoji": "🎩", "FG": -15, "TR": 5, "ET": 10, "PN": 15, "PC": 20, "PE": -35, "EA": 10, "CP": 5, "SO": 20, "REL": 20, "JUV": -25, "EMP": 10, "PROG": -25, "PYME": 25},
        "Alfredo Olmedo": {"emoji": "🚜", "FG": -10, "TR": 10, "ET": -15, "PN": 25, "PC": -10, "PE": -15, "EA": 10, "CP": -10, "SO": 35, "REL": 50, "JUV": -30, "EMP": 15, "PROG": -45, "PYME": 20},
        "Candidato Independiente": {"emoji": "👤", "FG": 0, "TR": 0, "ET": 0, "PN": 0, "PC": 0, "PE": 0, "EA": 0, "CP": 0, "SO": 0, "REL": 0, "JUV": 0, "EMP": 0, "PROG": 0, "PYME": 0}
    }},
    "Especiales": {"color": "#FFD700", "candidatos": {
        "Diego Maradona": {"emoji": "🔟", "FG": -10, "TR": 30, "ET": 10, "PN": 55, "PC": 20, "PE": 10, "EA": -5, "CP": 45, "SO": -50, "REL": 20, "JUV": 50, "EMP": 5, "PROG": 30, "PYME": 10},
        "Papa Francisco": {"emoji": "🇻🇦", "FG": 20, "TR": 20, "ET": 10, "PN": 0, "PC": 10, "PE": 20, "EA": 5, "CP": 10, "SO": -10, "REL": 100, "JUV": 10, "EMP": -30, "PROG": 40, "PYME": 0},
        "Manuel Belgrano": {"emoji": "🇦🇷", "FG": 50, "TR": 75, "ET": 60, "PN": 55, "PC": 100, "PE": 55, "EA": 100, "CP": 100, "SO": 50, "REL": 50, "JUV": 50, "EMP": 0, "PROG": 50, "PYME": 0},
        "José de San Martín": {"emoji": "🗡️", "FG": 100, "TR": 75, "ET": 75, "PN": 75, "PC": 75, "PE": 75, "EA": 75, "CP": 75, "SO": 100, "REL": 75, "JUV": 75, "EMP": 75, "PROG": 75, "PYME": 75},
        "Cornelio Saavedra": {"emoji": "🎩", "FG": 75, "TR": 50, "ET": 50, "PN": 50, "PC": 50, "PE": 50, "EA": 50, "CP": 50, "SO": 100, "REL": 50, "JUV": 50, "EMP": 50, "PROG": 50, "PYME": 50},
        "Juana Azurduy": {"emoji": "⚔️", "FG": 25, "TR": 30, "ET": 20, "PN": 15, "PC": 40, "PE": 40, "EA": 0, "CP": 25, "SO": 25, "REL": 0, "JUV": 50, "EMP": 0, "PROG": 75, "PYME": 0},
        "Guillermo Brown": {"emoji": "⚓", "FG": 25, "TR": 10, "ET": 15, "PN": 30, "PC": 35, "PE": 15, "EA": 10, "CP": 10, "SO": 65, "REL": 15, "JUV": -10, "EMP": 10, "PROG": 0, "PYME": 15},
        "Miguel de Güemes": {"emoji": "🐎", "FG": 35, "TR": 25, "ET": 40, "PN": 20, "PC": 40, "PE": 20, "EA": 20, "CP": 20, "SO": 55, "REL": 25, "JUV": 0, "EMP": -5, "PROG": -10, "PYME": 25},
        "Juan José Castelli": {"emoji": "🗣️", "FG": 10, "TR": 30, "ET": 35, "PN": 10, "PC": 15, "PE": 25, "EA": 5, "CP": 5, "SO": 10, "REL": -40, "JUV": 15, "EMP": -30, "PROG": 45, "PYME": -10},
        "Juan José Paso": {"emoji": "📜", "FG": 70, "TR": 30, "ET": 35, "PN": 10, "PC": 15, "PE": 25, "EA": 5, "CP": 5, "SO": 10, "REL": 10, "JUV": 15, "EMP": 0, "PROG": 45, "PYME": 0},
        "Mariano Moreno": {"emoji": "🔥", "FG": 20, "TR": 35, "ET": 40, "PN": 15, "PC": 15, "PE": 35, "EA": 15, "CP": 15, "SO": 10, "REL": 0, "JUV": 20, "EMP": -35, "PROG": 50, "PYME": -15},
        "Juan M. de Rosas": {"emoji": "🌹", "FG": 200, "TR": 10, "ET": 10, "PN": 50, "PC": 25, "PE": 25, "EA": -25, "CP": 5, "SO": 100, "REL": 100, "JUV": 25, "EMP": 0, "PROG": 10, "PYME": 0},
        "José Artigas": {"emoji": "🇺🇾", "FG": 150, "TR": 25, "ET": 10, "PN": 20, "PC": 40, "PE": 15, "EA": 5, "CP": 10, "SO": 20, "REL": 15, "JUV": 0, "EMP": -15, "PROG": 20, "PYME": 30},
        "Manuel Dorrego": {"emoji": "🎩", "FG": 50, "TR": 25, "ET": 25, "PN": 15, "PC": 30, "PE": 40, "EA": -10, "CP": 15, "SO": 20, "REL": 10, "JUV": -5, "EMP": -10, "PROG": 25, "PYME": 20},
        "Martín Rodríguez": {"emoji": "⚔️", "FG": 50, "TR": 15, "ET": 10, "PN": 50, "PC": 50, "PE": 10, "EA": 10, "CP": 10, "SO": 25, "REL": 15, "JUV": -10, "EMP": 15, "PROG": -10, "PYME": 20},
        "José Maria Paz": {"emoji": "🦾", "FG": -30, "TR": 20, "ET": 35, "PN": 10, "PC": 15, "PE": 15, "EA": 20, "CP": -15, "SO": 65, "REL": 10, "JUV": -10, "EMP": 10, "PROG": -20, "PYME": 10},
        "Gregorio Lamadrid": {"emoji": "🐎", "FG": -45, "TR": 10, "ET": 40, "PN": 5, "PC": 10, "PE": 10, "EA": 15, "CP": -10, "SO": 100, "REL": 10, "JUV": -10, "EMP": 5, "PROG": -15, "PYME": 10},
        "Charly Garcia": {"emoji": "🎹", "FG": -65, "TR": -10, "ET": 60, "PN": 40, "PC": 40, "PE": 20, "EA": 20, "CP": 40, "SO": -50, "REL": -40, "JUV": 50, "EMP": -20, "PROG": 40, "PYME": 0},
        "Indio Solari": {"emoji": "👑", "FG": -10, "TR": 20, "ET": 20, "PN": 30, "PC": 20, "PE": 20, "EA": 0, "CP": 50, "SO": -40, "REL": 10, "JUV": 80, "EMP": -40, "PROG": 60, "PYME": 10},
        "Fito Páez": {"emoji": "🎹", "FG": 10, "TR": -20, "ET": 50, "PN": 30, "PC": -10, "PE": 20, "EA": -50, "CP": 30, "SO": -30, "REL": -20, "JUV": +20, "EMP": -20, "PROG": +70, "PYME": 10},
        "Gustavo Cordera": {"emoji": "🤪", "FG": -30, "TR": 10, "ET": -30, "PN": 0, "PC": 10, "PE": -10, "EA": 25, "CP": 5, "SO": -40, "REL": -30, "JUV": -10, "EMP": -40, "PROG": -80, "PYME": 10},
        "Ricardo Iorio": {"emoji": "🤘", "FG": -30, "TR": 20, "ET": -20, "PN": 80, "PC": -30, "PE": 0, "EA": 10, "CP": 30, "SO": 50, "REL": 80, "JUV": 40, "EMP": -60, "PROG": -50, "PYME": 20},
        "Rolo Sartorio": {"emoji": "🎸", "FG": -10, "TR": -30, "ET": -10, "PN": -30, "PC": 20, "PE": -20, "EA": 35, "CP": -30, "SO": 20, "REL": 10, "JUV": 20, "EMP": 10, "PROG": -45, "PYME": 20},
        "Marcelo Tinelli": {"emoji": "📺", "FG": -20, "TR": 5, "ET": 0, "PN": 5, "PC": 40, "PE": -5, "EA": 10, "CP": 10, "SO": -10, "REL": -10, "JUV": 45, "EMP": 20, "PROG": 5, "PYME": 15},
        "Jorge Lanata": {"emoji": "🚬", "FG": 5, "TR": 0, "ET": 10, "PN": 5, "PC": -20, "PE": -10, "EA": 50, "CP": -40, "SO": 10, "REL": -10, "JUV": 20, "EMP": 10, "PROG": -30, "PYME": 5},
        "Luis Majul": {"emoji": "📖", "FG": -30, "TR": -20, "ET": -50, "PN": -25, "PC": -60, "PE": 0, "EA": 45, "CP": -35, "SO": 20, "REL": 10, "JUV": 5, "EMP": 15, "PROG": -35, "PYME": 10},
        "Eduardo Feinmann": {"emoji": "👔", "FG": -5, "TR": 0, "ET": -45, "PN": -25, "PC": 5, "PE": -35, "EA": 50, "CP": -40, "SO": 30, "REL": 50, "JUV": 10, "EMP": 15, "PROG": -50, "PYME": 10},
        "Baby Etchecopar": {"emoji": "🎙️", "FG": 10, "TR": 0, "ET": -25, "PN": 10, "PC": 5, "PE": -20, "EA": 15, "CP": -50, "SO": 55, "REL": 45, "JUV": -50, "EMP": 25, "PROG": -85, "PYME": 15},
        "Marcelo Longobardi": {"emoji": "📻", "FG": 10, "TR": 0, "ET": 5, "PN": 10, "PC": 15, "PE": -10, "EA": 35, "CP": -30, "SO": 15, "REL": 5, "JUV": 10, "EMP": 20, "PROG": -30, "PYME": 15},
        "Cinthia Fernández": {"emoji": "🤸‍♀️", "FG": -20, "TR": -5, "ET": -5, "PN": -10, "PC": 10, "PE": -25, "EA": 5, "CP": 5, "SO": -20, "REL": -30, "JUV": 60, "EMP": 10, "PROG": 10, "PYME": 0},
        "Juan S. Verón": {"emoji": "🧙‍♂️", "FG": 20, "TR": -30, "ET": 10, "PN": 25, "PC": 15, "PE": -40, "EA": 0, "CP": -25, "SO": 15, "REL": 0, "JUV": 20, "EMP": 30, "PROG": -25, "PYME": 20},
        "Juan R. Riquelme": {"emoji": "🔟", "FG": -15, "TR": 10, "ET": 35, "PN": 0, "PC": 25, "PE": 35, "EA": -45, "CP": 25, "SO": -20, "REL": 0, "JUV": 15, "EMP": 5, "PROG": 25, "PYME": 5},
        "Chiqui Tapia": {"emoji": "🏆", "FG": 10, "TR": 30, "ET": -30, "PN": 20, "PC": -20, "PE": 35, "EA": -20, "CP": 5, "SO": -25, "REL": -5, "JUV": -45, "EMP": 20, "PROG": 35, "PYME": 15},
        "El Gordo Dan": {"emoji": "🐦", "FG": -20, "TR": -35, "ET": -40, "PN": -25, "PC": -40, "PE": -35, "EA": 15, "CP": -45, "SO": 10, "REL": 5, "JUV": 55, "EMP": 5, "PROG": -65, "PYME": -5},
        "El Dipy": {"emoji": "🎵", "FG": -15, "TR": 10, "ET": -10, "PN": 0, "PC": 50, "PE": -20, "EA": 10, "CP": 0, "SO": -15, "REL": -20, "JUV": 60, "EMP": 5, "PROG": -10, "PYME": 5},
        "Nancy Pazos": {"emoji": "👚", "FG": -15, "TR": 0, "ET": 15, "PN": 0, "PC": -25, "PE": 25, "EA": -25, "CP": 5, "SO": -20, "REL": -35, "JUV": 15, "EMP": -15, "PROG": 45, "PYME": 5},
        "Chino Luna": {"emoji": "⚽", "FG": 15, "TR": 5, "ET": -20, "PN": 5, "PC": 10, "PE": -5, "EA": 25, "CP": -40, "SO": 5, "REL": 0, "JUV": 20, "EMP": 10, "PROG": -25, "PYME": -20},
        "Alejandro Fantino": {"emoji": "⚔️", "FG": 15, "TR": 5, "ET": -20, "PN": 10, "PC": 25, "PE": -30, "EA": 0, "CP": -10, "SO": 5, "REL": 0, "JUV": 35, "EMP": 35, "PROG": -25, "PYME": -20},
        "Michelo": {"emoji": "🕺", "FG": -45, "TR": -50, "ET": -10, "PN": -10, "PC": 20, "PE": 30, "EA": -60, "CP": 40, "SO": -30, "REL": -20, "JUV": 70, "EMP": -30, "PROG": 30, "PYME": -10},
        "El Presto": {"emoji": "🧢", "FG": -50, "TR": -20, "ET": -20, "PN": -10, "PC": 30, "PE": -60, "EA": 70, "CP": -70, "SO": 60, "REL": 10, "JUV": 60, "EMP": 10, "PROG": -90, "PYME": 20},
        "Santi Maratea": {"emoji": "📲", "FG": -20, "TR": -10, "ET": -40, "PN": 0, "PC": -40, "PE": -50, "EA": 10, "CP": -10, "SO": 0, "REL": 0, "JUV": 80, "EMP": 10, "PROG": 5, "PYME": 30},
        "Iñaki Gutiérrez": {"emoji": "📱", "FG": -40, "TR": -30, "ET": -10, "PN": -20, "PC": -10, "PE": -40, "EA": 20, "CP": -40, "SO": 10, "REL": -10, "JUV": 80, "EMP": 0, "PROG": -50, "PYME": 0},
        "Marcos Aramburu": {"emoji": "🍮", "FG": -20, "TR": -10, "ET": 10, "PN": 10, "PC": 10, "PE": 10, "EA": -30, "CP": 30, "SO": -10, "REL": -20, "JUV": 60, "EMP": -10, "PROG": 40, "PYME": 0},
        "Pedro Rosemblat": {"emoji": "🗳️", "FG": -10, "TR": -10, "ET": 20, "PN": 10, "PC": -10, "PE": 20, "EA": -40, "CP": 50, "SO": -20, "REL": -20, "JUV": 50, "EMP": -20, "PROG": 40, "PYME": -10},
        "Lali Espósito": {"emoji": "💃", "FG": -20, "TR": -10, "ET": 20, "PN": 20, "PC": 20, "PE": 10, "EA": -30, "CP": 10, "SO": -20, "REL": -40, "JUV": 70, "EMP": -10, "PROG": 45, "PYME": 10},
        "Ricardo Fort": {"emoji": "🍫", "FG": -10, "TR": -20, "ET": 10, "PN": -20, "PC": 40, "PE": -40, "EA": 20, "CP": 20, "SO": -20, "REL": -10, "JUV": 80, "EMP": 60, "PROG": 25, "PYME": -10},
        "Moria Casán": {"emoji": "👠", "FG": 5, "TR": 10, "ET": 20, "PN": 0, "PC": 50, "PE": 10, "EA": -20, "CP": 20, "SO": -10, "REL": -50, "JUV": 30, "EMP": 10, "PROG": 40, "PYME": 10},
        "Beto Casella": {"emoji": "📺", "FG": 10, "TR": 10, "ET": 10, "PN": 10, "PC": 60, "PE": -5, "EA": 0, "CP": 10, "SO": -10, "REL": -10, "JUV": 20, "EMP": 0, "PROG": 10, "PYME": 30},
        "Mario Pergolini": {"emoji": "🕶️", "FG": -10, "TR": -30, "ET": 40, "PN": 10, "PC": 20, "PE": -40, "EA": 25, "CP": 20, "SO": 10, "REL": -30, "JUV": 45, "EMP": 30, "PROG": -40, "PYME": 20},
        "Alfredo Casero": {"emoji": "🍮", "FG": -40, "TR": -20, "ET": -10, "PN": 10, "PC": 30, "PE": -30, "EA": 60, "CP": -60, "SO": 30, "REL": -5, "JUV": 10, "EMP": 5, "PROG": -40, "PYME": 10},
        "Tato Bores": {"emoji": "📞", "FG": 10, "TR": 10, "ET": 50, "PN": 10, "PC": 40, "PE": 0, "EA": 10, "CP": 10, "SO": 0, "REL": 5, "JUV": 20, "EMP": -5, "PROG": 10, "PYME": 20},
        "Enrique Pinti": {"emoji": "🎭", "FG": 10, "TR": 10, "ET": 40, "PN": 10, "PC": 30, "PE": 5, "EA": 10, "CP": 10, "SO": -5, "REL": -15, "JUV": 10, "EMP": 0, "PROG": 35, "PYME": 10},
        "Ernesto 'Che' Guevara": {"emoji": "⭐️", "FG": -80, "TR": 40, "ET": 20, "PN": 55, "PC": -40, "PE": 100, "EA": -60, "CP": -20, "SO": -70, "REL": -50, "JUV": 90, "EMP": -100, "PROG": 80, "PYME": -50},
        "Mago sin Dientes": {"emoji": "🎩", "FG": -20, "TR": -10, "ET": -10, "PN": -10, "PC": 0, "PE": -20, "EA": 25, "CP": -30, "SO": 10, "REL": 10, "JUV": 20, "EMP": -10, "PROG": -30, "PYME": 5},
        "Jorge Porcel Jr": {"emoji": "🍝", "FG": -30, "TR": -50, "ET": -20, "PN": -30, "PC": -20, "PE": 10, "EA": 0, "CP": 0, "SO": -30, "REL": -10, "JUV": 10, "EMP": -50, "PROG": 0, "PYME": -30},
        "Alberto Pandemia": {"emoji": "😷", "FG": 25, "TR": 25, "ET": 25, "PN": 25, "PC": 25, "PE": 25, "EA": 0, "CP": 25, "SO": 25, "REL": 25, "JUV": 25, "EMP": 25, "PROG": 25, "PYME": 25},
        "Cobos Vice": {"emoji": "🚫", "FG": 20, "TR": 20, "ET": 15, "PN": 75, "PC": 20, "PE": -25, "EA": 50, "CP": 15, "SO": 0, "REL": 10, "JUV": 0, "EMP": 25, "PROG": -25, "PYME": 25},
        "Lavagna Ministro": {"emoji": "🧦", "FG": 15, "TR": 50, "ET": 10, "PN": 50, "PC": 10, "PE": 25, "EA": 50, "CP": 50, "SO": 10, "REL": 25, "JUV": 0, "EMP": 50, "PROG": 0, "PYME": 50},
        "Cavallo 1 a 1": {"emoji": "💵", "FG": -5, "TR": 10, "ET": -50, "PN": -50, "PC": 20, "PE": -150, "EA": 50, "CP": 50, "SO": 10, "REL": 10, "JUV": 10, "EMP": 150, "PROG": -25, "PYME": -50},
        "Perón 3er Mandato": {"emoji": "👑", "FG": 20, "TR": 45, "ET": -25, "PN": 50, "PC": 10, "PE": 5, "EA": -50, "CP": 50, "SO": 150, "REL": 50, "JUV": -1574, "EMP": 15, "PROG": -1574, "PYME": 30},
        "Lousteau 125": {"emoji": "📉", "FG": -20, "TR": -50, "ET": 10, "PN": -150, "PC": 10, "PE": 35, "EA": -20, "CP": -30, "SO": 0, "REL": -20, "JUV": 10, "EMP": -50, "PROG": 25, "PYME": -50},
        "Cristina Presa": {"emoji": "⛓️", "FG": -30, "TR": -30, "ET": -30, "PN": -30, "PC": -30, "PE": -30, "EA": -30, "CP": -30, "SO": -30, "REL": -30, "JUV": -30, "EMP": -30, "PROG": -30, "PYME": -30},
        "Perón Exilio": {"emoji": "✈️", "FG": -72, "TR": 72, "ET": 72, "PN": 72, "PC": -72, "PE": 72, "EA": -72, "CP": 72, "SO": -72, "REL": -72, "JUV": 72, "EMP": -72, "PROG": 72, "PYME": 72},
        "PDBCEM": {"emoji": "🎲", "FG": 45, "TR": 15, "ET": 35, "PN": 50, "PC": 40, "PE": 20, "EA": 5, "CP": 5, "SO": 30, "REL": -5, "JUV": 30, "EMP": -10, "PROG": 60, "PYME": 15},
        "MILICHO CHORRO": {"emoji": "👮", "FG": -50, "TR": -50, "ET": -50, "PN": -50, "PC": -50, "PE": -50, "EA": -50, "CP": -50, "SO": -50, "REL": -50, "JUV": -50, "EMP": -50, "PROG": -50, "PYME": -50},
        "Scioli Presidente": {"emoji": "🦾", "FG": 30, "TR": 10, "ET": 25, "PN": 25, "PC": 50, "PE": 25, "EA": -5, "CP": 50, "SO": 5, "REL": 25, "JUV": 25, "EMP": -10, "PROG": 25, "PYME": -10},
        "Bullrich Montonera": {"emoji": "💣", "FG": -50, "TR": 5, "ET": 10, "PN": 5, "PC": -35, "PE": 15, "EA": -10, "CP": -5, "SO": 50, "REL": -10, "JUV": 15, "EMP": -45, "PROG": 10, "PYME": -20},
        "Luis Juez (Mix)": {"emoji": "🌭", "FG": 5, "TR": -5, "ET": 5, "PN": -5, "PC": 5, "PE": -5, "EA": 5, "CP": 5, "SO": -5, "REL": 5, "JUV": 0, "EMP": 5, "PROG": 5, "PYME": -5}
    }},
    "Presidentes Históricos": {"color": "#DAA520", "candidatos": {
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
        "Ramón Puerta": {"emoji": "🚪", "FG": -50, "TR": 25, "ET": 10, "PN": 20, "PC": 5, "PE": 20, "EA": -15, "CP": 35, "SO": 10, "REL": 20, "JUV": -20, "EMP": 15, "PROG": 20, "PYME": 20},
        "Eduardo Camaño": {"emoji": "🕰️", "FG": -60, "TR": 25, "ET": 10, "PN": 20, "PC": 5, "PE": 20, "EA": -15, "CP": 35, "SO": 10, "REL": 20, "JUV": -20, "EMP": 15, "PROG": 20, "PYME": 20},
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
    for g in SOCIAL_GROUPS:
        slots = st.session_state.social_slots[g]
        mx = max(slots.values()) if slots else 0
        if mx >= 3:
            lideres = [c for c, q in slots.items() if q == mx]
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
            if st.session_state.slots[p].get(nombre, 0) >= 10: st.session_state.hard_locked[p] = False
            if nombre in st.session_state.slots[p]: del st.session_state.slots[p][nombre]
    for g in SOCIAL_GROUPS:
        if nombre in st.session_state.social_slots[g]:
            if st.session_state.social_slots[g].get(nombre, 0) >= 10: st.session_state.hard_locked[g] = False
            if nombre in st.session_state.social_slots[g]: del st.session_state.social_slots[g][nombre]
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
    reporte = {"inversiones": [], "conflictos": [], "cambios": [], "balance": []}
    mi_nombre = next(c for c, i in st.session_state.p.items() if not i["is_ia"])
    inversiones_turno = {p: {} for p in MAPA_DATA}
    inv_social = {g: {} for g in SOCIAL_GROUPS}
    
    if 'ai_conflict_memory' not in st.session_state:
        st.session_state.ai_conflict_memory = {c: {} for c in st.session_state.p}

    is_late_game = st.session_state.turno >= 15
    fuerza_grupos, total_votos_group = calcular_control_grupos()

    for cand, info in st.session_state.p.items():
        if info["is_ia"]:
            dinero_actual = get_total_money(cand)
            stats = get_candidate_stats(cand)
            oportunidades = []
            grupos_deseados = []
            for g, data in STATE_GROUPS.items():
                if stats.get(g, 0) > 0:
                    votos_mios = fuerza_grupos[g][cand]
                    total = total_votos_group[g]
                    distancia = (total * 0.51) - votos_mios
                    prioridad = stats.get(g, 0) + (1000 if distancia <= 0 else 0)
                    grupos_deseados.append((prioridad, g))
            grupos_deseados.sort(reverse=True)
            top_grupos = [x[1] for x in grupos_deseados[:3]]

            for p in MAPA_DATA:
                fichas_mias = st.session_state.slots[p].get(cand, 0)
                if fichas_mias >= 10: continue
                if st.session_state.hard_locked[p]: continue
                lider_enemigo = 0
                for c, q in st.session_state.slots[p].items():
                    if c != cand and q > lider_enemigo: lider_enemigo = q
                afinidad = calcular_afinidad(cand, "PROVINCIA", p)
                votos = MAPA_DATA[p]["votos"]
                score = votos * 50 + afinidad * 5 
                prov_grupos = PROV_TO_GROUP_RAW.get(p, [])
                for g_code in top_grupos:
                    if g_code in prov_grupos: score += 2000
                conflict_count = st.session_state.ai_conflict_memory[cand].get(p, 0)
                if conflict_count >= 2: score -= 500000 
                elif conflict_count == 1: score -= 1000
                score *= random.uniform(0.9, 1.15)
                oportunidades.append({"tipo": "PROVINCIA", "id": p, "score": score, "costo": COSTOS_FIJOS[p]})

            for g in SOCIAL_GROUPS:
                fichas_mias = st.session_state.social_slots[g].get(cand, 0)
                if fichas_mias >= 10: continue
                if st.session_state.hard_locked.get(g, False): continue
                afinidad = calcular_afinidad(cand, "SOCIAL", g)
                social_score = (SOCIAL_GROUPS[g]["renta"] / 20) + (afinidad * 50)
                oportunidades.append({"tipo": "SOCIAL", "id": g, "score": social_score, "costo": SOCIAL_GROUPS[g]["costo"]})
            
            oportunidades.sort(key=lambda x: x["score"], reverse=True)
            umbral_ahorro = 20000 
            if any(v >= 2 for v in st.session_state.ai_conflict_memory[cand].values()):
                umbral_ahorro = 80000 

            for op in oportunidades:
                if dinero_actual < umbral_ahorro: break
                if dinero_actual >= op["costo"] and op["score"] > 0:
                    target = op["id"]
                    if op["tipo"] == "PROVINCIA":
                        curr = st.session_state.slots[target].get(cand, 0)
                        landed = cand in st.session_state.landed_status.get(target, [])
                    else:
                        curr = st.session_state.social_slots[target].get(cand, 0)
                        landed = cand in st.session_state.landed_status.get(target, [])
                    limit = 2 if (curr == 0 and not landed) else (10-curr)
                    qty = 1
                    if op["score"] >= 4000: qty = min(limit, int(dinero_actual / op["costo"]))
                    elif op["score"] > 2000: qty = min(limit, 2)
                    if qty > 0 and check_solvencia(cand, target, qty, op["tipo"] == "SOCIAL"):
                        if op["tipo"] == "PROVINCIA":
                            inversiones_turno[target][cand] = inversiones_turno[target].get(cand, 0) + qty
                            if target not in st.session_state.landed_status: st.session_state.landed_status[target] = []
                            if cand not in st.session_state.landed_status[target]: st.session_state.landed_status[target].append(cand)
                            reporte["inversiones"].append(f"{cand} invirtió en {target} (+{qty})")
                        else:
                            inv_social[target][cand] = qty
                            if target not in st.session_state.landed_status: st.session_state.landed_status[target] = []
                            if cand not in st.session_state.landed_status[target]: st.session_state.landed_status[target].append(cand)
                            reporte["inversiones"].append(f"{cand} apoyó a {SOCIAL_GROUPS[target]['nombre']} (+{qty})")
                        gastar_dinero(cand, target, qty, op["tipo"] == "SOCIAL")
                        dinero_actual -= (op["costo"] * qty)

    for ent, cant in st.session_state.pending_user.items():
        if cant > 0:
            if ent in SOCIAL_GROUPS:
                inv_social[ent][mi_nombre] = cant
                gastar_dinero(mi_nombre, ent, cant, True)
                reporte["inversiones"].append(f"TÚ invirtiste en {SOCIAL_GROUPS[ent]['nombre']} (+{cant})")
            else:
                inversiones_turno[ent][mi_nombre] = cant
                gastar_dinero(mi_nombre, ent, cant, False)
                reporte["inversiones"].append(f"TÚ invirtiste en {ent} (+{cant})")
            if ent not in st.session_state.landed_status: st.session_state.landed_status[ent] = []
            if mi_nombre not in st.session_state.landed_status[ent]: st.session_state.landed_status[ent].append(mi_nombre)

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
                    reporte["conflictos"].append(f"⚔️ **{ent}**: Choque entre {nombres} por llegar a {total_obj} fichas.")
                    for c in candidatos:
                        if is_prov and c in memory_dict: memory_dict[c][ent] = memory_dict[c].get(ent, 0) + 1
                        if ent not in st.session_state.landed_status: st.session_state.landed_status[ent] = []
                        if c not in st.session_state.landed_status[ent]: st.session_state.landed_status[ent].append(c)
                else:
                    unico_cand = candidatos[0]
                    cant_inv = invs[unico_cand]
                    estado_slots[ent][unico_cand] = estado_slots[ent].get(unico_cand, 0) + cant_inv
                    if is_prov and unico_cand in memory_dict: memory_dict[unico_cand][ent] = 0 
                    if estado_slots[ent][unico_cand] >= 10: 
                        hard_lock_dict[ent] = True
                        reporte["cambios"].append(f"🔒 {ent} ha sido BLOQUEADO por {unico_cand}.")
                    if ent not in st.session_state.landed_status: st.session_state.landed_status[ent] = []
                    if unico_cand not in st.session_state.landed_status[ent]: st.session_state.landed_status[ent].append(unico_cand)

    resolver(inversiones_turno, st.session_state.slots, st.session_state.hard_locked, st.session_state.ai_conflict_memory, True)
    resolver(inv_social, st.session_state.social_slots, st.session_state.hard_locked, st.session_state.ai_conflict_memory, False)
    
    old_owners = st.session_state.owners.copy()
    update_owners()
    for p in MAPA_DATA:
        if st.session_state.owners[p] != old_owners[p] and st.session_state.owners[p] is not None:
             reporte["cambios"].append(f"🚩 **{p}** ahora es territorio de {st.session_state.owners[p]}")

    fuerza_grupos, total_votos_group = calcular_control_grupos()
    for c in st.session_state.p:
        st.session_state.p[c]["wallets"]["base"] += RENTA_BASE_TURNO
        income = RENTA_BASE_TURNO
        stats = get_candidate_stats(c)
        for g, data in STATE_GROUPS.items():
            if fuerza_grupos[g][c] > (total_votos_group[g] * 0.5):
                mod = stats.get(g, 0) / 100.0
                monto = int(data["renta"] * (1 + mod))
                st.session_state.p[c]["wallets"][g] = st.session_state.p[c]["wallets"].get(g, 0) + monto
                income += monto
        for g, data in SOCIAL_GROUPS.items():
            if st.session_state.social_owners[g] == c:
                mod = stats.get(g, 0) / 100.0
                monto = int(data["renta"] * (1 + mod))
                st.session_state.p[c]["wallets"]["base"] += monto
                income += monto

    st.session_state.last_report = reporte
    st.session_state.pending_user = {}
    st.session_state.turno += 1
    mapa_completo = check_election_readiness()
    if mapa_completo:
        if not st.session_state.get('election_pending', False):
            st.session_state.election_pending = True
            st.toast("⚠️ MAPA COMPLETO: ELECCIÓN PRÓXIMO TURNO", icon="🗳️")
        else:
            st.session_state.modo_eleccion = True
            st.session_state.election_pending = False
    else:
        st.session_state.election_pending = False

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
        st.markdown(f"""
            <div class='win-msg'>
            🎉 ¡FELICIDADES {mi_nombre.upper()}! 🎉<br>
            ERES EL NUEVO PRESIDENTE/A 🇦🇷
            </div>
            <audio autoplay src="{SFX_WIN}"></audio>
        """, unsafe_allow_html=True)
        st.balloons()
    else:
        ganador_real = st.session_state.winner if st.session_state.winner else "NADIE"
        st.markdown(f"""
            <div class='lose-msg'>
            💀 PERDISTE...<br>
            Ganó {ganador_real}.
            </div>
            <audio autoplay src="{SFX_LOSE}"></audio>
        """, unsafe_allow_html=True)
    
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
            st.session_state.last_report = None
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
    if len(sorted_v) > 1:
        st.error(f"{eliminado} eliminado.")
    
    if st.button("SIGUIENTE"):
        mi_name = next(c for c, i in st.session_state.p.items() if not i["is_ia"])
        if sorted_v[0][1] >= VOTOS_PARA_GANAR:
            if sorted_v[0][0] == mi_name: st.session_state.winner = mi_name
            else: st.session_state.winner = sorted_v[0][0]; st.session_state.loser = mi_name
        elif len(sorted_v) == 1: # Solo queda uno
             st.session_state.winner = sorted_v[0][0]
             if sorted_v[0][0] != mi_name: st.session_state.loser = mi_name
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

    # --- SIMULACIÓN DE GASTO ---
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
        votos_sorted = sorted(st.session_state.votos_resolved.items(), key=lambda x: x[1], reverse=True)
        for c, v in votos_sorted:
            d = get_total_money(c)
            color = get_party_from_candidate(c)
            hex_c = PARTY_COLORS[color]["hex"] if color else "#ccc"
            st.markdown(f"<span style='color:{hex_c}'><b>{c}</b></span><br>🗳️ {v} | 💵 ${d:,}", unsafe_allow_html=True)
            st.progress(min(v/VOTOS_PARA_GANAR, 1.0))
            
    with tab_spy:
        target = st.selectbox("Objetivo:", list(st.session_state.p.keys()))
        stats = get_candidate_stats(target)
        st.markdown(f"**Perfil de {target}**")
        for k, v in stats.items():
            if k != "emoji":
                name = STATE_GROUPS.get(k, {}).get("nombre", SOCIAL_GROUPS.get(k, {}).get("nombre", k))
                col = "green" if v > 0 else "red"
                st.markdown(f":{col}[{name}: {v:+}%]")
        
        st.markdown("---")
        st.markdown("**Inversiones Activas:**")
        found_inv = False
        st.markdown("*Provincias:*")
        for p_name, slots in st.session_state.slots.items():
            fichas = slots.get(target, 0)
            is_landed = target in st.session_state.landed_status.get(p_name, [])
            if fichas > 0 or is_landed:
                found_inv = True
                estado = f"{fichas} fichas"
                if fichas == 0 and is_landed: estado = "0 (Pie en el territorio)"
                if st.session_state.hard_locked[p_name] and fichas >= 10:
                    estado = "🔒 CERRADO (10 fichas)"
                st.write(f"- **{p_name}**: {estado}")

        st.markdown("*Grupos Sociales:*")
        for g_code, slots in st.session_state.social_slots.items():
            fichas = slots.get(target, 0)
            is_landed = target in st.session_state.landed_status.get(g_code, [])
            if fichas > 0 or is_landed:
                found_inv = True
                g_name = SOCIAL_GROUPS[g_code]["nombre"]
                estado = f"{fichas} fichas"
                if fichas == 0 and is_landed: estado = "0 (Pie en el territorio)"
                if st.session_state.hard_locked.get(g_code, False) and fichas >= 10:
                    estado = "🔒 CERRADO (10 fichas)"
                st.write(f"- **{g_name}**: {estado}")
                
        if not found_inv: st.caption("No tiene inversiones activas.")

    with tab_terr:
        fuerza_grupos, total_votos_g = calcular_control_grupos()
        for g_code, data in STATE_GROUPS.items():
            with st.expander(f"{data['color']} {data['nombre']}"):
                provs = [p for p, grps in PROV_TO_GROUP_RAW.items() if g_code in grps]
                for p in provs:
                    own = st.session_state.owners[p]
                    visual = get_visual_id(own)
                    st.caption(f"{visual} **{p}**")
                st.divider()
                total = total_votos_g[g_code]
                if total > 0:
                    ranking = sorted(fuerza_grupos[g_code].items(), key=lambda x: x[1], reverse=True)
                    for c, f in ranking:
                        if f > 0:
                            pct = f / total
                            st.write(f"{c}: {int(pct*100)}%")
                            st.progress(min(pct, 1.0))

    try: st.image("rosca politica.jpg", use_container_width=True)
    except: pass
    
    my_votes = st.session_state.votos_resolved.get(mi_nombre, 0)
    pct_win = min(my_votes / VOTOS_PARA_GANAR * 100, 100)
    st.markdown(f"""
        <div class="voto-bar-wrapper">
            <div class="voto-bar-fill" style="width: {max(pct_win, 2)}%; background-color: {PARTY_COLORS[get_party_from_candidate(mi_nombre)]["hex"]};">
                {my_votes} / {VOTOS_PARA_GANAR}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.get('election_pending', False):
        st.markdown("<div class='warning-msg'>🗳️ ¡ATENCIÓN! MAPA COMPLETO. VOTACIÓN INMINENTE.</div>", unsafe_allow_html=True)
    
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
        st.write("") 
        st.write("") 
        if st.button("JUGAR TURNO", type="primary", use_container_width=True):
            if total_gasto_display > dinero_disp: st.error("No alcanza")
            else: procesar_turno(); st.rerun()

    tab1, tab2 = st.tabs(["🗺️ Mapa Electoral", "🗣️ Grupos Sociales"])

    with tab1:
        if st.session_state.selected_prov is None:
            for r in range(12):
                cols = st.columns(5)
                for c in range(5):
                    p_name = next((n for n, d in MAPA_DATA.items() if d["pos"] == (r, c)), None)
                    with cols[c]:
                        if p_name:
                            data = MAPA_DATA[p_name]
                            own = st.session_state.owners[p_name]
                            visual_id = get_visual_id(own)
                            v = data['votos']
                            label = f"{visual_id} {p_name}\n🗳️ {v} | 💲{int(COSTOS_FIJOS[p_name]/1000)}k"
                            if st.button(label, key=f"btn_{p_name}"):
                                st.session_state.selected_prov = p_name
                                st.rerun()
                        else: st.write("")
        else:
            p = st.session_state.selected_prov
            st.button("🔙 Volver", on_click=lambda: setattr(st.session_state, 'selected_prov', None))
            own = st.session_state.owners[p]
            color_hex = PARTY_COLORS[get_party_from_candidate(own)]["hex"] if own else "#333"
            st.markdown(f"<h2 style='border-bottom: 5px solid {color_hex}'>{p}</h2>", unsafe_allow_html=True)
            st.caption(f"Dueño actual: {own if own else 'Nadie'}")
            valid_groups = PROV_TO_GROUP_RAW.get(p, [])
            st.info(f"Grupos de Interés: {', '.join(valid_groups)}")
            curr = st.session_state.slots[p].get(mi_nombre, 0)
            pend = st.session_state.pending_user.get(p, 0)
            landed = mi_nombre in st.session_state.landed_status.get(p, [])
            
            if st.session_state.hard_locked.get(p, False):
                 st.error("🔒 PROVINCIA CERRADA")
            else:
                limit = 10 - curr
                if curr == 0 and not landed: limit = min(limit, 2)
                c1, c2 = st.columns(2)
                if c1.button("➕ Comprar") and pend < limit:
                    st.session_state.pending_user[p] = pend + 1
                    st.rerun()
                if c2.button("➖ Vender") and pend > 0:
                    st.session_state.pending_user[p] -= 1
                    st.rerun()
                st.write(f"Inversión Turno: {pend}")
            st.divider()
            
            active_cands = set(st.session_state.slots[p].keys()) | set(st.session_state.landed_status.get(p, []))
            display_list = []
            for c in active_cands:
                chips = st.session_state.slots[p].get(c, 0)
                display_list.append((c, chips))
            sorted_slots = sorted(display_list, key=lambda x: x[1], reverse=True)

            for c, q in sorted_slots:
                is_landed = c in st.session_state.landed_status.get(p, [])
                if q > 0 or is_landed:
                    visual_id = get_visual_id(c)
                    status_txt = f"{q} fichas"
                    if q == 0 and is_landed: status_txt = "0 (Pie en el territorio)"
                    st.write(f"{visual_id} **{c}**: {status_txt}")
                    st.progress(q/10)

    with tab2:
        for g_code, data in SOCIAL_GROUPS.items():
            with st.container():
                c_img, c_info, c_act = st.columns([1, 4, 2])
                c_img.markdown(f"## {data['color']}")
                with c_info:
                    own = st.session_state.social_owners[g_code]
                    visual_id = get_visual_id(own)
                    st.markdown(f"**{data['nombre']}** {visual_id}")
                    st.caption(f"Renta: ${data['renta']:,} | Costo: ${data['costo']:,}")
                    slots = st.session_state.social_slots[g_code]
                    if slots:
                        for c, q in slots.items():
                            if q > 0:
                                st.write(f"{c}: {q}")
                                st.progress(q/10)
                with c_act:
                    if st.session_state.hard_locked.get(g_code, False): st.write("🔒")
                    else:
                        curr = st.session_state.social_slots[g_code].get(mi_nombre, 0)
                        pend = st.session_state.pending_user.get(g_code, 0)
                        landed = mi_nombre in st.session_state.landed_status.get(g_code, [])
                        limit = 10 - curr
                        if curr == 0 and not landed: limit = min(limit, 2)
                        if st.button("➕", key=f"s_add_{g_code}") and pend < limit:
                            st.session_state.pending_user[g_code] = pend + 1
                            st.rerun()
                        if st.button("➖", key=f"s_rem_{g_code}") and pend > 0:
                            st.session_state.pending_user[g_code] -= 1
                            st.rerun()
                        if pend > 0: st.write(f"Add: {pend}")
                st.divider()

    if st.session_state.last_report:
        st.markdown("### 📰 Reporte del Turno")
        log = st.session_state.last_report
        with st.expander("💸 Inversiones", expanded=True):
            for l in log["inversiones"]: st.markdown(f"<div class='report-card report-invest'>{l}</div>", unsafe_allow_html=True)
        with st.expander("⚔️ Conflictos", expanded=True):
            if log["conflictos"]:
                for l in log["conflictos"]: st.markdown(f"<div class='report-card report-conflict'>{l}</div>", unsafe_allow_html=True)
            else: st.write("Sin conflictos.")
        with st.expander("🚩 Cambios de Mando", expanded=True):
             if log["cambios"]:
                for l in log["cambios"]: st.markdown(f"<div class='report-card report-change'>{l}</div>", unsafe_allow_html=True)
             else: st.write("El mapa se mantiene estable.")


