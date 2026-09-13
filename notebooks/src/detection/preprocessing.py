"""
preprocessing.py
Conversión de anotaciones UEC Food-256 al formato YOLOv8
y generación del split train/val/test.

NOTA: la lista CATEGORIAS_OBJETIVO de este módulo es un ejemplo de una fase
temprana del proyecto y no coincide con las categorías objetivo realmente
usadas en el experimento final sobre UEC Food-256 (basadas en estadísticas
de desperdicio de CE-Bioeconomy Brief 2021, WRAP 2022 y Frontiers Nutrition
2023). La selección y el preprocesamiento realmente ejecutados están
documentados en notebooks/04_entrenamiento_yolov8_uec256.ipynb.
"""

import os
import shutil
import random
from pathlib import Path


# Categorías objetivo (30 alimentos más desperdiciados en hogares europeos)
CATEGORIAS_OBJETIVO = [
    "rice", "eels on rice", "pilaf rice", "chicken and egg on rice",
    "pork cutlet on rice", "beef curry", "sushi", "chicken rice",
    "fried rice", "tempura bowl", "bibimbap", "toast",
    "croissant", "roll bread", "raisin bread", "chip butty",
    "hamburger", "pizza", "sandwiches", "udon noodle",
    "soba noodle", "ramen noodle", "beef noodle", "tensin noodle",
    "fried noodle", "spaghetti", "Japanese-style pancake",
    "takoyaki", "gratin", "sauteed vegetables"
]


def cargar_categorias(ruta_category_txt):
    """
    Lee el archivo category.txt de UEC Food-256.
    Devuelve un diccionario {id: nombre}.
    """
    categorias = {}
    with open(ruta_category_txt, "r") as f:
        for linea in f:
            partes = linea.strip().split("\t")
            if len(partes) == 2:
                categorias[int(partes[0])] = partes[1].lower()
    return categorias


def seleccionar_categorias(categorias, objetivos):
    """
    Filtra las categorías del dataset para quedarse solo
    con las que aparecen en la lista de objetivos.
    Devuelve un diccionario {id_original: nombre}.
    """
    seleccionadas = {}
    for id_cat, nombre in categorias.items():
        if nombre in [o.lower() for o in objetivos]:
            seleccionadas[id_cat] = nombre
    return seleccionadas


def convertir_bb_a_yolo(x1, y1, x2, y2, ancho_img, alto_img):
    """
    Convierte bounding box de formato UEC (x1, y1, x2, y2 en píxeles)
    al formato YOLOv8 (cx, cy, w, h normalizados entre 0 y 1).
    """
    cx = ((x1 + x2) / 2) / ancho_img
    cy = ((y1 + y2) / 2) / alto_img
    w  = (x2 - x1) / ancho_img
    h  = (y2 - y1) / alto_img
    return cx, cy, w, h


def preparar_dataset(ruta_uec, ruta_salida, categorias_sel, seed=42):
    """
    Prepara el dataset en formato YOLOv8:
    - Copia imágenes
    - Convierte anotaciones
    - Genera split 70/15/15

    Args:
        ruta_uec:       ruta raíz del dataset UEC Food-256
        ruta_salida:    ruta donde se generará el dataset YOLO
        categorias_sel: diccionario {id_original: nombre}
        seed:           semilla para reproducibilidad
    """
    random.seed(seed)

    # Crear estructura de carpetas
    for split in ["train", "val", "test"]:
        os.makedirs(f"{ruta_salida}/images/{split}", exist_ok=True)
        os.makedirs(f"{ruta_salida}/labels/{split}", exist_ok=True)

    # Mapeo de id original a id YOLO (0, 1, 2, ...)
    id_a_yolo = {id_orig: i for i, id_orig in enumerate(sorted(categorias_sel))}

    todas_las_imagenes = []

    for id_orig, nombre in categorias_sel.items():
        carpeta = Path(ruta_uec) / str(id_orig)
        bb_file = carpeta / "bb_info.txt"

        if not bb_file.exists():
            print(f"  Sin anotaciones: {nombre} (id {id_orig})")
            continue

        with open(bb_file) as f:
            lineas = f.readlines()[1:]  # Saltar cabecera

        for linea in lineas:
            partes = linea.strip().split()
            if len(partes) < 5:
                continue

            nombre_img = partes[0] + ".jpg"
            x1, y1, x2, y2 = int(partes[1]), int(partes[2]), int(partes[3]), int(partes[4])
            ruta_img = carpeta / nombre_img

            if not ruta_img.exists():
                continue

            todas_las_imagenes.append({
                "ruta_img":  ruta_img,
                "id_yolo":   id_a_yolo[id_orig],
                "nombre":    nombre,
                "x1": x1, "y1": y1, "x2": x2, "y2": y2
            })

    # Shuffle y split
    random.shuffle(todas_las_imagenes)
    n = len(todas_las_imagenes)
    n_train = int(n * 0.70)
    n_val   = int(n * 0.15)

    splits = (
        ("train", todas_las_imagenes[:n_train]),
        ("val",   todas_las_imagenes[n_train:n_train + n_val]),
        ("test",  todas_las_imagenes[n_train + n_val:])
    )

    for split_name, items in splits:
        for item in items:
            # Copiar imagen
            dest_img = f"{ruta_salida}/images/{split_name}/{item['ruta_img'].name}"
            shutil.copy(item["ruta_img"], dest_img)

            # Leer dimensiones
            import cv2
            img = cv2.imread(dest_img)
            alto_img, ancho_img = img.shape[:2]

            # Convertir y guardar anotación
            cx, cy, w, h = convertir_bb_a_yolo(
                item["x1"], item["y1"], item["x2"], item["y2"],
                ancho_img, alto_img
            )
            nombre_label = item["ruta_img"].stem + ".txt"
            dest_label = f"{ruta_salida}/labels/{split_name}/{nombre_label}"
            with open(dest_label, "w") as f:
                f.write(f"{item['id_yolo']} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}\n")

    print(f"Dataset preparado: {n_train} train / {n_val} val / {n - n_train - n_val} test")
    return id_a_yolo
