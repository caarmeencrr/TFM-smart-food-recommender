"""
inference.py
Detección de alimentos en imágenes usando el modelo YOLOv8 entrenado.
"""

from ultralytics import YOLO


def cargar_modelo(ruta_pesos="models/best.pt"):
    """
    Carga el modelo YOLOv8 desde los pesos entrenados.

    Args:
        ruta_pesos: ruta al archivo .pt con los pesos del modelo
    Returns:
        modelo YOLO cargado
    """
    model = YOLO(ruta_pesos)
    print(f"Modelo cargado desde: {ruta_pesos}")
    return model


def detectar_alimentos(imagen, modelo, confianza_minima=0.30):
    """
    Detecta alimentos en una imagen.

    Args:
        imagen:           ruta a la imagen o array numpy
        modelo:           modelo YOLO cargado
        confianza_minima: umbral mínimo de confianza (0-1)
    Returns:
        lista de detecciones [{nombre, confianza, bbox}]
    """
    resultados = modelo(imagen, conf=confianza_minima, iou=0.5, verbose=False)

    detecciones = []
    for r in resultados:
        for box in r.boxes:
            detecciones.append({
                "nombre":     modelo.names[int(box.cls)],
                "confianza":  round(float(box.conf), 3),
                "bbox":       box.xyxy[0].tolist()  # [x1, y1, x2, y2]
            })

    # Ordenar por confianza descendente
    detecciones.sort(key=lambda x: x["confianza"], reverse=True)
    return detecciones


def detectar_desde_ruta(ruta_imagen, ruta_pesos="models/best.pt", confianza_minima=0.30):
    """
    Función de alto nivel: carga modelo y detecta en una imagen.

    Args:
        ruta_imagen:      ruta a la imagen
        ruta_pesos:       ruta al archivo .pt
        confianza_minima: umbral mínimo de confianza
    Returns:
        lista de detecciones
    """
    modelo = cargar_modelo(ruta_pesos)
    detecciones = detectar_alimentos(ruta_imagen, modelo, confianza_minima)

    print(f"\nDetectados {len(detecciones)} alimento(s):")
    for d in detecciones:
        print(f"  • {d['nombre']} — {d['confianza']:.0%} confianza")

    return detecciones


if __name__ == "__main__":
    # Ejemplo de uso
    detecciones = detectar_desde_ruta(
        ruta_imagen="ruta/a/tu/imagen.jpg",
        ruta_pesos="models/best.pt"
    )
