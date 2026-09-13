"""
scoring.py
Función de optimización multiobjetivo para la recomendación de alimentos.
Pondera valor nutricional, sostenibilidad ambiental y urgencia de consumo.

NOTA: esta es una implementación de referencia, más simple y didáctica,
de una fase temprana del proyecto. La aplicación final (src/app/app.py)
implementa su propia versión de la función de puntuación —con pesos
ajustables por el usuario desde la interfaz y componentes adicionales
(restricciones duras OBLIGATORIO/RESTRINGIDO)—, descrita en la memoria,
Capítulo 4, sección 4.2.4.
"""


# Pesos de la función multiobjetivo (deben sumar 1.0)
ALPHA = 0.40  # Peso del valor nutricional
BETA  = 0.35  # Peso de la sostenibilidad ambiental
GAMMA = 0.25  # Peso de la urgencia de consumo


def calcular_score(nutricion, sostenibilidad, urgencia):
    """
    Calcula el score final de un alimento según la función multiobjetivo.

    Args:
        nutricion:      puntuación nutricional normalizada (0-1)
        sostenibilidad: puntuación ambiental normalizada (0-1)
                        (mayor = más sostenible)
        urgencia:       urgencia de consumo normalizada (0-1)
                        (mayor = más urgente, ej. próximo a caducar)
    Returns:
        score final entre 0 y 1
    """
    return (ALPHA * nutricion) + (BETA * sostenibilidad) + (GAMMA * urgencia)


def normalizar(valor, minimo, maximo):
    """
    Normaliza un valor entre 0 y 1.

    Args:
        valor:   valor a normalizar
        minimo:  valor mínimo del rango
        maximo:  valor máximo del rango
    Returns:
        valor normalizado entre 0 y 1
    """
    if maximo == minimo:
        return 0.0
    return (valor - minimo) / (maximo - minimo)


def puntuar_alimentos(lista_alimentos):
    """
    Calcula el score de una lista de alimentos y los ordena.

    Args:
        lista_alimentos: lista de diccionarios con campos:
            - nombre
            - calorias_kcal
            - proteinas_g
            - co2_kg (huella de carbono por kg)
            - dias_para_caducar
    Returns:
        lista ordenada por score descendente
    """
    if not lista_alimentos:
        return []

    # Extraer rangos para normalización
    calorias     = [a["calorias_kcal"]     for a in lista_alimentos]
    proteinas    = [a["proteinas_g"]        for a in lista_alimentos]
    co2          = [a["co2_kg"]             for a in lista_alimentos]
    dias         = [a["dias_para_caducar"]  for a in lista_alimentos]

    resultados = []
    for alimento in lista_alimentos:

        # Nutrición: más proteína y menos calorías vacías = mejor
        score_nutricion = normalizar(alimento["proteinas_g"], min(proteinas), max(proteinas))

        # Sostenibilidad: menor CO2 = mejor (invertido)
        score_co2 = 1 - normalizar(alimento["co2_kg"], min(co2), max(co2))

        # Urgencia: menos días para caducar = más urgente
        score_urgencia = 1 - normalizar(alimento["dias_para_caducar"], min(dias), max(dias))

        score_final = calcular_score(score_nutricion, score_co2, score_urgencia)

        resultados.append({
            **alimento,
            "score_nutricion":    round(score_nutricion, 3),
            "score_co2":          round(score_co2, 3),
            "score_urgencia":     round(score_urgencia, 3),
            "score_final":        round(score_final, 3)
        })

    return sorted(resultados, key=lambda x: x["score_final"], reverse=True)


if __name__ == "__main__":
    # Ejemplo de uso
    alimentos = [
        {"nombre": "zanahoria", "calorias_kcal": 41,  "proteinas_g": 0.93, "co2_kg": 0.4, "dias_para_caducar": 3},
        {"nombre": "pollo",     "calorias_kcal": 165, "proteinas_g": 31.0, "co2_kg": 6.9, "dias_para_caducar": 1},
        {"nombre": "tomate",    "calorias_kcal": 18,  "proteinas_g": 0.88, "co2_kg": 1.4, "dias_para_caducar": 5},
    ]

    ranking = puntuar_alimentos(alimentos)
    print("\nRanking de alimentos:")
    for i, a in enumerate(ranking, 1):
        print(f"  {i}. {a['nombre']} — score: {a['score_final']}")
