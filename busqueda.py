# app_dashboard_moderno.py
import streamlit as st
import folium
from streamlit_folium import st_folium
import math
import heapq
import pandas as pd
import time
from typing import Dict, List, Tuple, Optional

# ---------------- CONFIGURACIÓN GLOBAL ----------------
st.set_page_config(
    page_title="🗺️ Rutas Inteligentes - Cuenca",
    page_icon="🌿",
    layout="wide",
)

# Estilo CSS personalizado
st.markdown("""
    <style>
        /* Fondo general */
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: #f5f5f5;
        }

        [data-testid="stSidebar"] {
            background-color: #111927;
            color: white;
        }

        h1, h2, h3, h4, h5, h6 {
            color: #00b4d8 !important;
        }

        .stButton button {
            background-color: #00b4d8 !important;
            color: white !important;
            border-radius: 12px !important;
            border: none !important;
            font-weight: 600;
            padding: 0.6rem 1rem;
        }
        .stButton button:hover {
            background-color: #0077b6 !important;
        }

        .metric-card {
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 1rem;
            text-align: center;
            color: white;
        }

        .metric-value {
            font-size: 1.5rem;
            font-weight: bold;
            color: #90e0ef;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------- NODOS ----------------
CUENCA_NODES = {
    "Catedral Nueva": {"lat": -2.8975, "lon": -79.005, "descripcion": "Centro histórico", "tipo": "Otro"},
    "Parque Calderón": {"lat": -2.89741, "lon": -79.00438, "descripcion": "Corazón de Cuenca", "tipo": "Parque"},
    "Puente Roto": {"lat": -2.90423, "lon": -79.00142, "descripcion": "Monumento histórico", "tipo": "Otro"},
    "Museo Pumapungo": {"lat": -2.90607, "lon": -78.99681, "descripcion": "Museo de antropología", "tipo": "Museo"},
    "Terminal Terrestre": {"lat": -2.89222, "lon": -78.99277, "descripcion": "Terminal de buses", "tipo": "Otro"},
    "Mirador de Turi": {"lat": -2.92583, "lon": -79.0040, "descripcion": "Mirador panorámico", "tipo": "Parque"},
    "Parque de la Madre": {"lat": -2.902, "lon": -79.006, "descripcion": "Parque popular", "tipo": "Parque"},
    "El Vergel": {"lat": -2.915, "lon": -79.008, "descripcion": "Zona comercial", "tipo": "Otro"},
    "Parque Infantil": {"lat": -2.898, "lon": -79.003, "descripcion": "Parque para niños", "tipo": "Parque"},
    "Plaza Abdon Calderón": {"lat": -2.8965, "lon": -79.0035, "descripcion": "Plaza principal", "tipo": "Otro"},
    "Puente de Otorongo": {"lat": -2.903, "lon": -79.002, "descripcion": "Puente histórico", "tipo": "Otro"},
    "Museo del Banco Central": {"lat": -2.905, "lon": -78.995, "descripcion": "Museo cultural", "tipo": "Museo"},
    "Universidad de Cuenca": {"lat": -2.897, "lon": -79.006, "descripcion": "Institución educativa", "tipo": "Universidad"},
    "Hospital Vicente Corral Moscoso": {"lat": -2.898, "lon": -78.991, "descripcion": "Hospital público", "tipo": "Hospital"},
    "Parque Miraflores": {"lat": -2.907, "lon": -79.002, "descripcion": "Zona verde", "tipo": "Parque"},
    "Calle Larga": {"lat": -2.8985, "lon": -79.002, "descripcion": "Zona comercial", "tipo": "Otro"},
    "Iglesia del Carmen": {"lat": -2.899, "lon": -79.0045, "descripcion": "Iglesia histórica", "tipo": "Iglesia"},
    "Biblioteca Municipal": {"lat": -2.8978, "lon": -79.003, "descripcion": "Biblioteca pública", "tipo": "Otro"},
    "Estadio Alejandro Serrano": {"lat": -2.910, "lon": -79.003, "descripcion": "Estadio deportivo", "tipo": "Otro"},
    "Plaza San Francisco": {"lat": -2.9035, "lon": -79.004, "descripcion": "Plaza histórica", "tipo": "Otro"},
}

GRAPH_EDGES = {
    "Catedral Nueva": ["Parque Calderón", "Museo Pumapungo", "Parque Infantil", "Plaza Abdon Calderón", "Parque de la Madre"],
    "Parque Calderón": ["Catedral Nueva", "Terminal Terrestre", "Puente Roto", "Plaza Abdon Calderón"],
    "Puente Roto": ["Catedral Nueva", "Parque Calderón", "Museo Pumapungo", "Mirador de Turi", "El Vergel", "Plaza San Francisco"],
    "Museo Pumapungo": ["Catedral Nueva", "Puente Roto", "Terminal Terrestre", "Museo del Banco Central"],
    "Terminal Terrestre": ["Parque Calderón", "Museo Pumapungo", "Mirador de Turi", "Hospital Vicente Corral Moscoso"],
    "Mirador de Turi": ["Puente Roto", "Terminal Terrestre", "El Vergel"],
    "Parque de la Madre": ["Catedral Nueva", "Parque Infantil"],
    "El Vergel": ["Puente Roto", "Mirador de Turi", "Calle Larga"],
    "Parque Infantil": ["Catedral Nueva", "Parque de la Madre", "Plaza Abdon Calderón"],
    "Plaza Abdon Calderón": ["Catedral Nueva", "Parque Infantil", "Parque Calderón", "Iglesia del Carmen"],
    "Puente de Otorongo": ["Plaza San Francisco", "Parque Miraflores"],
    "Museo del Banco Central": ["Museo Pumapungo", "Biblioteca Municipal"],
    "Universidad de Cuenca": ["Calle Larga", "Biblioteca Municipal"],
    "Hospital Vicente Corral Moscoso": ["Terminal Terrestre", "Calle Larga"],
    "Parque Miraflores": ["Puente de Otorongo", "Estadio Alejandro Serrano"],
    "Calle Larga": ["El Vergel", "Universidad de Cuenca", "Hospital Vicente Corral Moscoso"],
    "Iglesia del Carmen": ["Plaza Abdon Calderón", "Biblioteca Municipal"],
    "Biblioteca Municipal": ["Museo del Banco Central", "Universidad de Cuenca", "Iglesia del Carmen"],
    "Estadio Alejandro Serrano": ["Parque Miraflores", "Plaza San Francisco"],
    "Plaza San Francisco": ["Puente Roto", "Puente de Otorongo", "Estadio Alejandro Serrano"],
}

# ---------------- FUNCIONES ----------------
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1_rad, lat2_rad = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad)*math.cos(lat2_rad)*math.sin(dlon/2)**2
    c = 2*math.asin(math.sqrt(a))
    return R * c

class AStarPathFinder:
    def __init__(self, nodes: Dict, edges: Dict):
        self.nodes = nodes
        self.edges = edges

    def heuristic(self, node: str, goal: str) -> float:
        n, g = self.nodes[node], self.nodes[goal]
        return haversine_distance(n["lat"], n["lon"], g["lat"], g["lon"])

    def get_distance(self, node1: str, node2: str) -> float:
        n1, n2 = self.nodes[node1], self.nodes[node2]
        return haversine_distance(n1["lat"], n1["lon"], n2["lat"], n2["lon"])

    def find_path(self, start: str, goal: str) -> Tuple[Optional[List[str]], float, List[str]]:
        frontier = []
        heapq.heappush(frontier, (0, start, [start], 0))
        visited = set()
        explored_nodes = set()
        while frontier:
            f, current, path, g_score = heapq.heappop(frontier)
            explored_nodes.add(current)
            if current == goal:
                return path, g_score, list(explored_nodes)
            visited.add(current)
            for neighbor in self.edges.get(current, []):
                if neighbor not in visited:
                    g = g_score + self.get_distance(current, neighbor)
                    h = self.heuristic(neighbor, goal)
                    heapq.heappush(frontier, (g + h, neighbor, path + [neighbor], g))
        return None, float("inf"), list(explored_nodes)

pathfinder = AStarPathFinder(CUENCA_NODES, GRAPH_EDGES)

# ---------------- SESSION STATE ----------------
for key, val in {"ruta": [], "distancia": 0.0, "explorados": [], "tiempo": 0.0}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ---------------- INTERFAZ ----------------
with st.sidebar:
    st.title("🚦 Rutas Inteligentes Cuenca")
    inicio = st.selectbox("📍 Punto de inicio", list(CUENCA_NODES.keys()))
    destino = st.selectbox("🏁 Punto de destino", list(CUENCA_NODES.keys()))
    mostrar_no_vistos = st.checkbox("👁️ Mostrar nodos no explorados", value=False)
    calcular_btn = st.button("🔍 Buscar ruta óptima")
    limpiar_btn = st.button("🧹 Limpiar ruta")

    st.markdown("---")
    st.markdown("### 📊 Datos de Cuenca")
    st.info("""
    - **Población:** ~400,000  
    - **Clima:** 12°C - 25°C  
    - **Turismo:** Turi, Calderón, Pumapungo  
    - **Educación:** Univ. de Cuenca, Univ. del Azuay
    """)

# ---------------- BOTONES ----------------
if limpiar_btn:
    for key in ["ruta", "distancia", "explorados", "tiempo"]:
        st.session_state[key] = 0.0 if key == "distancia" or key == "tiempo" else []

if calcular_btn:
    start_time = time.time()
    ruta, distancia, explorados = pathfinder.find_path(inicio, destino)
    st.session_state.tiempo = time.time() - start_time
    if ruta:
        st.session_state.ruta, st.session_state.distancia, st.session_state.explorados = ruta, distancia, explorados
    else:
        st.error("❌ No se encontró una ruta válida.")

# ---------------- INFORMACIÓN ----------------
st.title("🌐 Sistema de Rutas Óptimas de Cuenca")

if st.session_state.ruta:
    col1, col2, col3 = st.columns(3)
    col1.markdown('<div class="metric-card"><p>Distancia total</p><p class="metric-value">'
                  f'{st.session_state.distancia:.2f} km</p></div>', unsafe_allow_html=True)
    col2.markdown('<div class="metric-card"><p>Tiempo de ejecución</p><p class="metric-value">'
                  f'{st.session_state.tiempo:.4f} s</p></div>', unsafe_allow_html=True)
    col3.markdown('<div class="metric-card"><p>Nodos explorados</p><p class="metric-value">'
                  f'{len(st.session_state.explorados)}</p></div>', unsafe_allow_html=True)

    st.markdown(f"**🗺️ Ruta:** {' → '.join(st.session_state.ruta)}")

    df = pd.DataFrame({
        "Nodo": st.session_state.ruta,
        "Latitud": [CUENCA_NODES[n]["lat"] for n in st.session_state.ruta],
        "Longitud": [CUENCA_NODES[n]["lon"] for n in st.session_state.ruta],
        "Descripción": [CUENCA_NODES[n]["descripcion"] for n in st.session_state.ruta]
    })
    st.download_button("⬇️ Descargar CSV de ruta", df.to_csv(index=False), "ruta_cuenca.csv", "text/csv")

# ---------------- MAPA ----------------
st.subheader("🗺️ Visualización de la ruta")
mapa = folium.Map(location=[-2.8975, -79.005], zoom_start=14, tiles="CartoDB dark_matter")
tipo_color = {"Museo": "purple", "Parque": "green", "Iglesia": "darkred",
              "Hospital": "red", "Universidad": "blue", "Otro": "gray"}

for nodo, info in CUENCA_NODES.items():
    color = tipo_color.get(info["tipo"], "gray")
    if mostrar_no_vistos and nodo not in st.session_state.explorados:
        color = "orange"
    if nodo in st.session_state.ruta:
        color = "lightblue"
    folium.Marker(
        [info["lat"], info["lon"]],
        popup=f"<b>{nodo}</b><br>{info['descripcion']}<br><i>{info['tipo']}</i>",
        icon=folium.Icon(color=color)
    ).add_to(mapa)

if st.session_state.ruta:
    coords = [[CUENCA_NODES[n]["lat"], CUENCA_NODES[n]["lon"]] for n in st.session_state.ruta]
    folium.PolyLine(coords, color="cyan", weight=6, opacity=0.7).add_to(mapa)

st_folium(mapa, width=1000, height=600)
