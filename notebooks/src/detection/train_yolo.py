"""
train_yolo.py
Entrenamiento de YOLOv8 sobre el dataset UEC Food-256
preparado con preprocessing.py.
"""

import yaml
from pathlib import Path
from ultralytics import YOLO


def generar_data_yaml(ruta_dataset, nombres_clases, ruta_salida="configs/yolo_config.yaml"):
    """
    Genera el archivo data.yaml necesario para entrenar YOLOv8.

    Args:
        ruta_dataset:   ruta raíz del dataset en formato YOLO
        nombres_clases: lista de nombres de clases en orden
        ruta_salida:    dónde guardar el yaml
    """
    config = {
        "path":  str(ruta_dataset),
        "train": "images/train",
        "val":   "images/val",
        "test":  "images/test",
        "nc":    len(nombres_clases),
        "names": nombres_clases
    }

    Path(ruta_salida).parent.mkdir(parents=True, exist_ok=True)
    with open(ruta_salida, "w") as f:
        yaml.dump(config, f, allow_unicode=True)

    print(f"data.yaml generado en: {ruta_salida}")
    return ruta_salida


def entrenar(
    data_yaml,
    modelo_base="yolov8s.pt",
    epochs=50,
    imgsz=640,
    batch=16,
    proyecto="results",
    nombre_experimento="yolov8_uec256"
):
    """
    Lanza el entrenamiento de YOLOv8.

    Args:
        data_yaml:            ruta al archivo data.yaml
        modelo_base:          modelo preentrenado de partida
        epochs:               número de épocas
        imgsz:                tamaño de imagen de entrada
        batch:                tamaño de batch
        proyecto:             carpeta donde se guardan los resultados
        nombre_experimento:   nombre del experimento
    """
    model = YOLO(modelo_base)

    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        project=proyecto,
        name=nombre_experimento,
        exist_ok=True
    )

    print(f"\nEntrenamiento completado.")
    print(f"Mejor modelo guardado en: {proyecto}/{nombre_experimento}/weights/best.pt")
    return results


if __name__ == "__main__":
    # Ejemplo de uso
    DATA_YAML = "configs/yolo_config.yaml"

    entrenar(
        data_yaml=DATA_YAML,
        modelo_base="yolov8s.pt",
        epochs=50,
        imgsz=640,
        batch=16
    )
