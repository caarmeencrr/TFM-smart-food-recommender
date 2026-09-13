# TFM — Smart Food Recommendation System

Sistema inteligente para reducir el desperdicio alimentario doméstico mediante visión artificial y generación automática de recetas.

## Descripción

El sistema detecta alimentos a partir de una imagen de nevera o despensa, los enriquece con información nutricional (USDA FoodData Central) y de huella de carbono (SU-EATABLE LIFE), aplica una función de optimización multiobjetivo y genera una receta personalizada mediante un modelo de lenguaje.

## Arquitectura del sistema

```
Imagen
  ↓
YOLOv8 (detección de alimentos)
  ↓
USDA FoodData Central (nutrición) + SU-EATABLE LIFE (huella de CO2)
  ↓
Motor de decisión multiobjetivo — Score(i) = α·N(i) + β·S(i) + γ·U(i)
  ↓
Generación de receta (LLM openai/gpt-oss-120b vía Groq API)
```

## Estructura del repositorio

```
TFM-smart-food-recommender/
└── notebooks/
    ├── 01_exploracion_uec256.ipynb
    ├── 02_exploracion_fruits360.ipynb
    ├── 03_experimento_fruits360_yolov8n_1.ipynb
    ├── 04_entrenamiento_yolov8_uec256.ipynb
    ├── 05_pruebas_usda_api.ipynb
    ├── 06_tabla_maestra_nutricional.ipynb
    ├── 07_validacion_yolov8_nevera.ipynb
    ├── src/
    │   ├── detection/                # Detección con YOLOv8 (experimento sobre UEC Food-256)
    │   ├── nutrition/                # Consulta USDA API
    │   ├── recommendation/           # Scoring multiobjetivo (versión de referencia simplificada)
    │   └── app/                      # Aplicación Streamlit (demo funcional)
    │       ├── app.py
    │       └── best_fruits.pt        # Modelo YOLOv8n final, entrenado sobre Fruits-360
    ├── configs/                      # Configuración YOLO
    ├── data/                         # No incluido en el repositorio
    ├── models/                       # No incluido en el repositorio (salvo best_fruits.pt en src/app/)
    └── results/
        └── figures/                  # Métricas y figuras
```

> **Nota sobre `src/`:** los módulos de `src/detection/`, `src/nutrition/` y `src/recommendation/`
> son implementaciones de referencia, más simples y didácticas, usadas en las fases exploratorias
> del proyecto. La aplicación final (`src/app/app.py`) integra su propia lógica —consistente con
> la memoria— directamente en el archivo, en lugar de importar estos módulos.

## Cómo ejecutar la demo

```bash
git clone https://github.com/caarmeencrr/TFM-smart-food-recommender.git
cd TFM-smart-food-recommender
pip install -r requirements.txt
cd notebooks/src/app
streamlit run app.py
```

Al abrir la app en el navegador, sube una foto de tu nevera o despensa e introduce una clave de
la API de Groq (gratuita en [console.groq.com](https://console.groq.com) → API Keys) para generar
la receta. La clave solo se usa localmente durante la sesión y no se guarda en ningún sitio.

## Tecnologías

- Python 3.12
- YOLOv8 (Ultralytics)
- PyTorch
- OpenCV
- Streamlit
- Groq API (endpoint compatible con OpenAI, modelo `openai/gpt-oss-120b`)
- USDA FoodData Central API

## Datasets

- **UEC Food-256** — 256 categorías de platos preparados. Se evaluó al inicio del proyecto como
  candidato para el entrenamiento del detector, pero fue descartado: sus categorías corresponden
  mayoritariamente a platos cocinados, no a ingredientes crudos (véase la memoria, Capítulo 5).
- **Fruits-360** — dataset finalmente empleado. El modelo final (`best_fruits.pt`) se entrena sobre
  un subconjunto de 6 categorías de ingredientes crudos: manzana, zanahoria, limón, naranja,
  pimiento y tomate.

Los datos originales no se incluyen en este repositorio.

## Entrenamiento

Los experimentos de detección y clasificación (notebooks 01-04) se ejecutaron en **Kaggle Notebooks** con GPU NVIDIA Tesla P100/Tesla T4. Los experimentos de la fase de nutrición y validación (notebooks 05-07) se ejecutaron en **Google Colab**.

## Autor

Carmen Carrera Rodríguez — TFM, Máster de Inteligencia Artificial, Universidad Internacional de Valencia (VIU), 2025–2026
