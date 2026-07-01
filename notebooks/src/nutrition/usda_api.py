"""
usda_api.py
Consulta de información nutricional desde USDA FoodData Central.
Obtén tu API key gratuita en: https://fdc.nal.usda.gov/api-guide.html
"""

import requests


API_KEY = "TU_API_KEY_AQUI"  # Reemplaza con tu clave de USDA
BASE_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"


def buscar_alimento(nombre_en):
    """
    Busca un alimento en USDA FoodData Central.

    Args:
        nombre_en: nombre del alimento en inglés (ej: 'carrot raw')
    Returns:
        datos del primer resultado o None si no se encuentra
    """
    params = {
        "query":    nombre_en,
        "api_key":  API_KEY,
        "dataType": "Foundation,SR Legacy",
        "pageSize": 1
    }
    r = requests.get(BASE_URL, params=params)
    datos = r.json()

    if not datos.get("foods"):
        print(f"No encontrado: {nombre_en}")
        return None

    return datos["foods"][0]


def extraer_nutrientes(nombre_en):
    """
    Extrae los nutrientes principales de un alimento.

    Args:
        nombre_en: nombre del alimento en inglés (ej: 'carrot raw')
    Returns:
        diccionario con nutrientes o None si no se encuentra
    """
    alimento = buscar_alimento(nombre_en)
    if not alimento:
        return None

    # Extraer calorías en KCAL específicamente
    calorias = 0
    for n in alimento["foodNutrients"]:
        if n["nutrientName"] == "Energy" and n["unitName"] == "KCAL":
            calorias = n["value"]
            break

    nutrientes = {n["nutrientName"]: n["value"] for n in alimento["foodNutrients"]}

    return {
        "nombre_oficial_usda": alimento["description"],
        "calorias_kcal":       calorias,
        "proteinas_g":         nutrientes.get("Protein", 0),
        "carbohidratos_g":     nutrientes.get("Carbohydrate, by difference", 0),
        "grasas_g":            nutrientes.get("Total lipids (fat)", 0),
        "fibra_g":             nutrientes.get("Fiber, total dietary", 0),
        "azucares_g":          nutrientes.get("Sugars, total including NLEA", 0),
        "sodio_mg":            nutrientes.get("Sodium, Na", 0),
    }


def obtener_tabla_nutricional(lista_alimentos):
    """
    Obtiene la información nutricional de una lista de alimentos.

    Args:
        lista_alimentos: lista de nombres en inglés
    Returns:
        lista de diccionarios con nutrientes
    """
    tabla = []
    for nombre in lista_alimentos:
        print(f"Consultando: {nombre}...")
        datos = extraer_nutrientes(nombre)
        if datos:
            tabla.append(datos)
    return tabla


if __name__ == "__main__":
    # Ejemplo de uso
    zanahoria = extraer_nutrientes("carrot raw")
    if zanahoria:
        print(f"Nombre:        {zanahoria['nombre_oficial_usda']}")
        print(f"Calorías:      {zanahoria['calorias_kcal']} kcal")
        print(f"Proteínas:     {zanahoria['proteinas_g']} g")
        print(f"Carbohidratos: {zanahoria['carbohidratos_g']} g")
        print(f"Grasas:        {zanahoria['grasas_g']} g")
