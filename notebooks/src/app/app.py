"""
Generador de Dietas Sostenibles
Basado en el Análisis de Desperdicios Alimentarios Domésticos
TFM – Máster de Inteligencia Artificial – VIU
Alumna: Carmen Carrera Rodríguez
"""

import streamlit as st
from PIL import Image
import datetime

# Tabla maestra con datos reales de USDA FoodData Central + huella de carbono
# (Tabla 5.8 de la memoria). El campo "riesgo" sigue la categorización del
# Apéndice B.2: las 6 categorías del corpus (frutas y verduras frescas) se
# etiquetan como riesgo "Alto", en línea con los datos de Eurostat (2024)
# citados en la sección 2.1 (frutas 27 %, verduras 20 % del desperdicio UE).
TABLA_MAESTRA_USDA = {
    "manzana":   {"kcal": 58.2, "proteinas": 0.15, "carbohidratos": 15.65, "grasas": 0.16, "fibra": 2.08, "co2": 0.43, "riesgo": "Alto"},
    "zanahoria": {"kcal": 41.0, "proteinas": 0.93, "carbohidratos": 9.58,  "grasas": 0.24, "fibra": 2.80, "co2": 0.43, "riesgo": "Alto"},
    "limon":     {"kcal": 29.0, "proteinas": 1.10, "carbohidratos": 9.32,  "grasas": 0.30, "fibra": 2.80, "co2": 0.40, "riesgo": "Alto"},
    "naranja":   {"kcal": 46.0, "proteinas": 0.70, "carbohidratos": 11.54, "grasas": 0.21, "fibra": 2.40, "co2": 0.45, "riesgo": "Alto"},
    "pimiento":  {"kcal": 26.0, "proteinas": 0.99, "carbohidratos": 6.03,  "grasas": 0.30, "fibra": 2.10, "co2": 0.53, "riesgo": "Alto"},
    "tomate":    {"kcal": 18.0, "proteinas": 0.88, "carbohidratos": 3.89,  "grasas": 0.20, "fibra": 1.20, "co2": 1.44, "riesgo": "Alto"},
}

def buscar_datos_cientificos(nombre_ingrediente):
    """Busca el ingrediente en la tabla maestra USDA. Si no está, devuelve None."""
    clave = nombre_ingrediente.strip().lower()
    return TABLA_MAESTRA_USDA.get(clave)

# ── Motor de decisión: función de puntuación multiobjetivo ────────────────────
# Implementación fiel a la ecuación 4.2 de la memoria:
#   Score(i) = alpha * N(i) + beta * S(i) + gamma * U(i)
# con N(i) y S(i) definidos por las ecuaciones 4.3-4.4 (normalización
# min-max sobre el corpus presente en el inventario) y U(i) calculada
# mediante la función escalonada del Apéndice B.3.

def calcular_urgencia(dias, riesgo="Alto"):
    """Réplica exacta de la función escalonada del Apéndice B.3."""
    mult = {"Alto": 1.0, "Medio": 0.75, "Bajo": 0.50}.get(riesgo, 0.75)
    if dias <= 2:
        base = 1.00
    elif dias <= 5:
        base = 0.75
    elif dias <= 10:
        base = 0.50
    elif dias <= 20:
        base = 0.25
    else:
        base = 0.10
    return base * mult

def calcular_nutriscore(datos):
    """
    Puntuación nutricional compuesta (sección 4.2.4), calculada a partir de
    densidad calórica, contenido proteico y fibra: favorece proteína y
    fibra, penaliza densidad calórica. Se normaliza después mediante
    escalado min-max sobre el corpus del inventario (ecuación 4.3).
    """
    return (2 * datos["proteinas"]) + (2 * datos["fibra"]) - (datos["kcal"] / 50)

def calcular_scores(ingredientes, alpha, beta, gamma):
    """
    Calcula Score(i) para cada ingrediente del inventario según la ecuación
    4.2 de la memoria. N(i) y S(i) solo se calculan para ingredientes
    presentes en la tabla maestra verificada (TABLA_MAESTRA_USDA); para
    ingredientes añadidos manualmente fuera del corpus de 6 clases, se
    aplica únicamente el componente de urgencia U(i), marcándose como
    estimación parcial (sin datos científicos verificados).
    Se aplica además la penalización del 50 % al ingrediente en el decil
    superior de CO2 del corpus presente, como restricción dura RESTRINGIDO,
    y se marca como OBLIGATORIO todo ingrediente con caducidad <= 2 días.
    """
    con_datos = []
    for ing in ingredientes:
        datos = buscar_datos_cientificos(ing["nombre"])
        if datos:
            con_datos.append({"nutriscore": calcular_nutriscore(datos), "co2": datos["co2"]})

    n_min = n_max = c_min = c_max = None
    co2_maximo = None
    if con_datos:
        nutriscores = [c["nutriscore"] for c in con_datos]
        co2s = [c["co2"] for c in con_datos]
        n_min, n_max = min(nutriscores), max(nutriscores)
        c_min, c_max = min(co2s), max(co2s)
        if len(co2s) > 1:
            co2_maximo = max(co2s)

    resultados = []
    for ing in ingredientes:
        datos = buscar_datos_cientificos(ing["nombre"])
        dias = (ing["caducidad"] - datetime.date.today()).days
        riesgo = datos["riesgo"] if datos else "Medio"
        u = calcular_urgencia(dias, riesgo)
        obligatorio = dias <= 2
        restringido = False

        if datos:
            nutriscore = calcular_nutriscore(datos)
            n = (nutriscore - n_min) / (n_max - n_min) if n_max > n_min else 1.0
            s = 1 - ((datos["co2"] - c_min) / (c_max - c_min)) if c_max > c_min else 1.0
            score = alpha * n + beta * s + gamma * u
            if co2_maximo is not None and datos["co2"] == co2_maximo:
                score *= 0.5
                restringido = True
        else:
            # Fuera del corpus verificado: solo se pondera la urgencia.
            score = gamma * u

        resultados.append({
            **ing,
            "datos": datos,
            "score": round(score, 3),
            "obligatorio": obligatorio,
            "restringido": restringido,
        })

    resultados.sort(key=lambda x: x["score"], reverse=True)
    return resultados

# ── Configuración de la página ────────────────────────────────────────────────
st.set_page_config(
    page_title="Generador de Dietas Sostenibles",
    page_icon="🥦",
    layout="wide",
)

# ── Estilos ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title { font-size: 2rem; font-weight: 700; color: #D64616; }
    .subtitle { font-size: 1rem; color: #555; margin-bottom: 1.5rem; }
    .ingredient-card {
        background-color: #fff4f0;
        border-left: 4px solid #D64616;
        border-radius: 6px;
        padding: 0.6rem 1rem;
        margin-bottom: 0.5rem;
    }
    .recipe-box {
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1.2rem;
        margin-top: 1rem;
    }
    .warning-caducidad { color: #D64616; font-weight: bold; }
    .section-title {
        font-size: 1.2rem; font-weight: 600; color: #333;
        margin-top: 1.5rem; margin-bottom: 0.5rem;
        border-bottom: 2px solid #D64616; padding-bottom: 0.3rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Cabecera ──────────────────────────────────────────────────────────────────
st.markdown('<p class="main-title">🥦 Generador de Dietas Sostenibles</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Basado en el análisis de desperdicios alimentarios domésticos · VIU 2025–2026</p>', unsafe_allow_html=True)

# ── Carga del modelo YOLOv8 ───────────────────────────────────────────────────
@st.cache_resource
def cargar_modelo():
    try:
        from ultralytics import YOLO
        modelo = YOLO("best_fruits.pt")
        return modelo, None
    except FileNotFoundError:
        return None, "No se encontró best.pt. Asegúrate de que está en la misma carpeta que app.py."
    except Exception as e:
        return None, f"Error al cargar el modelo: {str(e)}"

modelo, error_modelo = cargar_modelo()

if error_modelo:
    st.error(f"⚠️ {error_modelo}")

# ── Layout en dos columnas ────────────────────────────────────────────────────
col_izq, col_der = st.columns([1, 1], gap="large")

# ═══════════════════════════════════════════════════════════════════════════════
# COLUMNA IZQUIERDA – Subida de imagen e inventario
# ═══════════════════════════════════════════════════════════════════════════════
with col_izq:

    st.markdown('<p class="section-title">📷 Imagen de la nevera o despensa</p>', unsafe_allow_html=True)
    imagen = st.file_uploader(
        "Sube una foto de tu nevera o despensa",
        type=["jpg", "jpeg", "png"],
    )

    if imagen:
        img = Image.open(imagen)
        ingredientes_detectados = []

        # ── Detección real con YOLOv8 ─────────────────────────────────────────
        # NOTA (ver memoria TFM, sección de limitaciones): la matriz de confusión
        # del modelo reveló un sesgo hacia la clase "Pimiento" (falsos positivos
        # sobre fondo en el 51% de los casos), probablemente por el bajo número
        # de épocas de entrenamiento (15) y la ausencia de ejemplos negativos.
        # Como mitigación a corto plazo se usan umbrales de confianza distintos
        # por clase en lugar de un único conf=0.25 global.
        UMBRAL_POR_CLASE = {
            "Manzana": 0.25,
            "Tomate": 0.25,
            "Pimiento": 0.60,   # clase con sesgo detectado -> más exigente
            "Naranja": 0.25,
            "Limon": 0.25,
            "Zanahoria": 0.20,
        }
        UMBRAL_POR_DEFECTO = 0.25
        MAX_DETECCIONES_POR_CLASE = 3  # evita que un sesgo puntual "inunde" el resultado

        if modelo is not None:
            with st.spinner("🔍 Detectando ingredientes con YOLOv8..."):
                # Umbral bajo aquí: filtramos nosotros después clase a clase
                resultados = modelo.predict(img, conf=0.05)
                img_anotada = Image.fromarray(resultados[0].plot()[:, :, ::-1])
                st.image(img_anotada, caption="Ingredientes detectados por YOLOv8 (umbral bajo, sin filtrar)", use_container_width=True)

                nombres_clases = modelo.names
                detecciones = resultados[0].boxes
                clases_vistas = set()
                conteo_por_clase = {}

                if detecciones is not None and len(detecciones) > 0:
                    # Ordenamos por confianza descendente para quedarnos primero
                    # con las mejores detecciones de cada clase
                    cajas_ordenadas = sorted(detecciones, key=lambda b: float(b.conf[0]), reverse=True)

                    for box in cajas_ordenadas:
                        clase_id = int(box.cls[0])
                        confianza = float(box.conf[0])
                        nombre = nombres_clases[clase_id]

                        umbral = UMBRAL_POR_CLASE.get(nombre, UMBRAL_POR_DEFECTO)
                        if confianza < umbral:
                            continue

                        if conteo_por_clase.get(nombre, 0) >= MAX_DETECCIONES_POR_CLASE:
                            continue

                        conteo_por_clase[nombre] = conteo_por_clase.get(nombre, 0) + 1

                        if nombre not in clases_vistas:
                            clases_vistas.add(nombre)
                            ingredientes_detectados.append({
                                "nombre": nombre.capitalize(),
                                "confianza": confianza,
                                "cantidad": "1 unidad",
                                "caducidad": datetime.date.today() + datetime.timedelta(days=5)
                            })

                if ingredientes_detectados:
                    st.success(f"✅ {len(ingredientes_detectados)} ingrediente(s) detectados.")
                else:
                    st.warning("No se detectaron ingredientes con suficiente confianza. Añádelos manualmente.")
        else:
            st.image(img, caption="Imagen cargada", use_container_width=True)

        # Mostrar confianza
        if ingredientes_detectados:
            st.markdown('<p class="section-title">🔍 Resultado de la detección</p>', unsafe_allow_html=True)
            for ing in ingredientes_detectados:
                pct = int(ing["confianza"] * 100)
                color = "#2ecc71" if pct >= 70 else "#e67e22"
                st.markdown(
                    f'<div class="ingredient-card"><b>{ing["nombre"]}</b> '
                    f'<span style="color:{color}; font-size:0.85rem;">({pct}% confianza)</span></div>',
                    unsafe_allow_html=True
                )

        # ── Corrección manual ─────────────────────────────────────────────────
        st.markdown('<p class="section-title">✏️ Corrección manual del inventario</p>', unsafe_allow_html=True)
        st.caption("Revisa los ingredientes detectados. Puedes modificar nombre, cantidad y fecha de caducidad.")

        if "ingredientes" not in st.session_state:
            st.session_state.ingredientes = ingredientes_detectados

        if st.button("🔄 Recargar desde detección") and ingredientes_detectados:
            st.session_state.ingredientes = ingredientes_detectados
            st.rerun()

        ingredientes_editados = []
        for i, ing in enumerate(st.session_state.ingredientes):
            with st.expander(f"🥗 {ing['nombre']}", expanded=False):
                c1, c2, c3 = st.columns([2, 2, 2])
                nombre    = c1.text_input("Nombre",   value=ing["nombre"],   key=f"nombre_{i}")
                cantidad  = c2.text_input("Cantidad", value=ing["cantidad"], key=f"cant_{i}")
                caducidad = c3.date_input("Caducidad", value=ing["caducidad"], key=f"cad_{i}")
                dias = (caducidad - datetime.date.today()).days
                if dias <= 2:
                    st.markdown(f'<p class="warning-caducidad">⚠️ Caduca en {dias} día(s) — prioridad alta</p>', unsafe_allow_html=True)
                ingredientes_editados.append({"nombre": nombre, "cantidad": cantidad, "caducidad": caducidad})

        # Añadir manualmente
        st.markdown("**➕ Añadir ingrediente manualmente**")
        nc1, nc2, nc3 = st.columns([2, 2, 2])
        nuevo_nombre    = nc1.text_input("Nombre",   key="nuevo_nombre",   placeholder="Ej: Zanahoria")
        nueva_cantidad  = nc2.text_input("Cantidad", key="nueva_cantidad", placeholder="Ej: 2 unidades")
        nueva_caducidad = nc3.date_input("Caducidad", key="nueva_cad",
                                          value=datetime.date.today() + datetime.timedelta(days=7))
        if st.button("Añadir ingrediente"):
            if nuevo_nombre:
                st.session_state.ingredientes.append({
                    "nombre": nuevo_nombre,
                    "cantidad": nueva_cantidad,
                    "caducidad": nueva_caducidad
                })
                st.rerun()

        st.session_state.ingredientes = ingredientes_editados

# ═══════════════════════════════════════════════════════════════════════════════
# COLUMNA DERECHA – Preferencias y receta
# ═══════════════════════════════════════════════════════════════════════════════
with col_der:

    st.markdown('<p class="section-title">⚖️ Preferencias y criterios de optimización</p>', unsafe_allow_html=True)

    dieta = st.selectbox(
        "Tipo de dieta",
        ["Sin restricciones", "Vegetariana", "Vegana", "Sin gluten", "Sin lactosa", "Baja en calorías"],
    )
    comensales = st.slider("Número de comensales", 1, 8, 2)

    st.markdown("**Prioridades de optimización**")
    pc1, pc2, pc3 = st.columns(3)
    peso_caducidad = pc1.slider("🗓️ Caducidad",  0, 10, 8)
    peso_nutricion = pc2.slider("🥗 Nutrición",  0, 10, 6)
    peso_carbono   = pc3.slider("🌿 Huella CO₂", 0, 10, 5)

    st.markdown('<p class="section-title">🔑 Clave API de Groq (gratis)</p>', unsafe_allow_html=True)
    api_key = st.text_input(
        "Introduce tu clave de Groq",
        type="password",
        help="Obtenla gratis en console.groq.com → API Keys · Se usa solo localmente, no se guarda."
    )

    st.markdown('<p class="section-title">🍽️ Receta generada</p>', unsafe_allow_html=True)

    if st.button("✨ Generar receta sostenible", type="primary", use_container_width=True):
        if not imagen:
            st.warning("Sube primero una imagen.")
        elif not st.session_state.get("ingredientes"):
            st.warning("No hay ingredientes en el inventario.")
        elif not api_key:
            st.warning("Introduce tu clave de API de Groq.")
        else:
            with st.spinner("Generando receta con IA..."):

                # α, β, γ ajustables por el usuario mediante los sliders,
                # mapeados a los componentes de la ecuación 4.2 de la
                # memoria: nutrición → alpha, huella CO2 → beta,
                # caducidad/urgencia → gamma. Los valores por defecto de los
                # sliders (8, 6, 5) normalizan a (≈0.42, ≈0.32, ≈0.26),
                # próximos a los coeficientes usados en la validación
                # experimental de la sección 5.5 (0.40, 0.35, 0.25).
                total = peso_caducidad + peso_nutricion + peso_carbono or 1
                alpha = round(peso_nutricion / total, 2)   # nutrición -> N(i)
                beta  = round(peso_carbono   / total, 2)   # sostenibilidad -> S(i)
                gamma = round(peso_caducidad / total, 2)   # urgencia -> U(i)

                ingredientes_puntuados = calcular_scores(
                    st.session_state.ingredientes, alpha, beta, gamma
                )

                # Se muestra la tabla de puntuaciones para que el
                # funcionamiento del motor de decisión (sección 4.2.4) sea
                # visible en la interfaz, no solo su resultado en la receta.
                st.markdown("**⚖️ Puntuación multiobjetivo Score(i) = α·N(i) + β·S(i) + γ·U(i)**")
                st.dataframe(
                    [{
                        "Ingrediente": i["nombre"],
                        "Score": i["score"],
                        "Caduca": i["caducidad"].strftime("%d/%m/%Y"),
                        "Obligatorio": "✅" if i["obligatorio"] else "",
                        "Restringido": "⚠️" if i["restringido"] else "",
                        "Datos verificados": "✅" if i["datos"] else "—",
                    } for i in ingredientes_puntuados],
                    use_container_width=True,
                    hide_index=True,
                )

                def formatear_ingrediente(i):
                    etiquetas = []
                    if i["obligatorio"]:
                        etiquetas.append("OBLIGATORIO: caduca en ≤2 días")
                    if i["restringido"]:
                        etiquetas.append("RESTRINGIDO: huella de carbono muy elevada, usar con moderación")
                    sufijo_etiquetas = f" [{'; '.join(etiquetas)}]" if etiquetas else ""

                    base = (f"- {i['nombre']} ({i['cantidad']}) — Score={i['score']} — "
                            f"caduca el {i['caducidad'].strftime('%d/%m/%Y')}{sufijo_etiquetas}")
                    if i["datos"]:
                        d = i["datos"]
                        base += (f"\n  [Datos USDA verificados: {d['kcal']} kcal, "
                        f"{d['proteinas']}g proteína, {d['fibra']}g fibra, "
                          f"huella de carbono {d['co2']} kg CO2eq/kg]")
                    else:
                        base += "\n  [Sin datos científicos verificados; Score parcial basado solo en urgencia]"
                    return base

                lista_ing = "\n".join([formatear_ingrediente(i) for i in ingredientes_puntuados])

                prompt = f"""Eres un nutricionista experto en sostenibilidad alimentaria y reducción del desperdicio.

Genera una receta para {comensales} persona(s) usando los siguientes ingredientes,
ya ordenados de mayor a menor prioridad según la función de puntuación
Score(i) = {alpha}·N(i) + {beta}·S(i) + {gamma}·U(i), donde N(i) es el valor
nutricional normalizado, S(i) la sostenibilidad ambiental (huella de carbono
invertida) y U(i) la urgencia de consumo por caducidad.

Ingredientes disponibles (ordenados por Score, de mayor a menor prioridad):
{lista_ing}

RESTRICCIONES DURAS que debes respetar:
- Todo ingrediente marcado [OBLIGATORIO] debe incluirse en la receta.
- Todo ingrediente marcado [RESTRINGIDO] debe evitarse o usarse en cantidad mínima, salvo que sea también OBLIGATORIO.

IMPORTANTE: cuando un ingrediente incluya "Datos USDA verificados", usa esos
valores exactos para los cálculos nutricionales y de huella de carbono de la
receta, en lugar de estimarlos tú mismo.

Restricción dietética: {dieta}

Responde con esta estructura exacta:
**Nombre del plato:** ...
**Ingredientes utilizados:** lista con cantidades
**Preparación:** pasos numerados
**Valor nutricional aproximado por persona:** calorías, proteínas, grasas, carbohidratos
**Huella de carbono estimada:** kg CO₂eq por ración
**Puntuación de sostenibilidad:** X/10
**Ingredientes próximos a caducar aprovechados:** N de M
"""
                try:
                    import openai
                    # Groq expone una API compatible con la de OpenAI: mismo
                    # cliente/librería, solo cambia la URL base y el modelo.
                    # Free tier sin coste (ver console.groq.com).
                    client = openai.OpenAI(
                        api_key=api_key,
                        base_url="https://api.groq.com/openai/v1",
                    )
                    respuesta = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7,
                        max_tokens=1800,
                        reasoning_effort="low",
                    )
                    receta_texto = respuesta.choices[0].message.content

                    if not receta_texto or not receta_texto.strip():
                        st.error("Groq devolvió una respuesta vacía (probablemente se quedó sin tokens razonando). Intenta pulsar el botón de nuevo.")
                        st.stop()

                    st.markdown('<div class="recipe-box">', unsafe_allow_html=True)
                    st.markdown(receta_texto)
                    st.markdown('</div>', unsafe_allow_html=True)

                    # Métricas resumen
                    st.markdown('<p class="section-title">📊 Resumen</p>', unsafe_allow_html=True)
                    m1, m2, m3, m4 = st.columns(4)
                    urgentes = sum(1 for i in ingredientes_puntuados if i["obligatorio"])
                    m1.metric("🗓️ Ingredientes OBLIGATORIOS (Score)", urgentes)
                    m2.metric("👥 Comensales", comensales)
                    m3.metric("🥗 Dieta", dieta)
                    m4.metric("⚖️ Pesos (α,β,γ)", f"{alpha}/{beta}/{gamma}")

                except Exception as e:
                    st.error(f"Error al conectar con Groq: {str(e)}")
                    st.info("Comprueba que tu clave API de Groq es correcta (console.groq.com → API Keys).")
    else:
        st.markdown("""
        <div class="recipe-box" style="color:#aaa; text-align:center; padding: 3rem;">
            Sube una imagen y pulsa <b>Generar receta sostenible</b>
        </div>
        """, unsafe_allow_html=True)

# ── Pie ───────────────────────────────────────────────────────────────────────
st.divider()
st.caption("TFM · Máster de Inteligencia Artificial · Universidad Internacional de Valencia · Carmen Carrera Rodríguez · 2025–2026")