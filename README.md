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
├── notebooks/                        # Experimentos en Kaggle
│   ├── 01_exploracion_uec256.ipynb
│   ├── 02_exploracion_fruits360.ipynb
│   ├── 03_experimento_fruits360_yolov8n.ipynb
│   └── 04_entrenamiento_yolov8_uec256.ipynb
├── src/
│   ├── detection/                    # Detección con YOLOv8
│   ├── nutrition/                    # Consulta USDA API
│   ├── recommendation/               # Scoring multiobjetivo
│   └── app/                          # Interfaz Streamlit
├── configs/                          # Configuración YOLO
├── data/                             # No incluido en el repositorio
├── models/                           # No incluido en el repositorio
└── results/                          # Métricas y figuras
```

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

Los experimentos se ejecutaron en **Kaggle Notebooks** con GPU NVIDIA Tesla P100 (16GB).

## Autor

Carmen — TFM, 2026
