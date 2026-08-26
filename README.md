# TFM — Smart Food Recommendation System

Sistema inteligente para reducir el desperdicio alimentario doméstico mediante visión artificial y generación automática de recetas.

## Descripción

El sistema detecta alimentos a partir de imágenes, los enriquece con información nutricional y ambiental, aplica una función de optimización multiobjetivo y genera recetas personalizadas.

## Arquitectura del sistema

```
Imagen
  ↓
YOLOv8 (detección de alimentos)
  ↓
USDA FoodData Central (información nutricional)
  ↓
Motor de decisión multiobjetivo
  ↓
Generación de receta (OpenAI API)
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
    │   ├── detection/                # Detección con YOLOv8
    │   ├── nutrition/                # Consulta USDA API
    │   ├── recommendation/           # Scoring multiobjetivo
    │   └── app/                      # Interfaz Streamlit (pendiente)
    ├── configs/                      # Configuración YOLO
    ├── data/                         # No incluido en el repositorio
    ├── models/                       # No incluido en el repositorio
    └── results/
        └── figures/                  # Métricas y figuras
```

> `src/app/` con la interfaz Streamlit está pendiente de desarrollo — todavía no existe en el repositorio.

## Tecnologías

- Python 3.12
- YOLOv8 (Ultralytics)
- PyTorch
- OpenCV
- Streamlit
- OpenAI API
- USDA FoodData Central API

## Datasets

- **UEC Food-256** — 256 categorías de platos, usado para entrenar el detector de las 30 categorías más desperdiciadas en hogares europeos
- **Fruits-360** — 260 clases de frutas y verduras sobre fondo blanco

Los datos originales no se incluyen en este repositorio.

## Entrenamiento

Los experimentos de detección y clasificación (notebooks 01-04) se ejecutaron en **Kaggle Notebooks** con GPU NVIDIA Tesla P100/Tesla T4. Los experimentos de la fase de nutrición y validación (notebooks 05-07) se ejecutaron en **Google Colab**.

## Autor

Carmen — TFM, 2026
