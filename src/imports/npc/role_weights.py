# Pesos tácticos para cada rol
ROLE_WEIGHTS = {
    "Tejedora": {
        "honey_amount": -50,  # Medio negativo para priorizar influencia de miel
        "is_cover": -100,     # Gran negativo para priorizar cobertura
        "is_corner": 0,       # Pequeño positivo para neutralidad en esquinas
        "is_crossroad": 0,    # Pequeño positivo para neutralidad en conectividad
    },
    "Cazadora": {
        "honey_amount": 0,    # Pequeño positivo para neutralidad en influencia de miel
        "is_crossroad": -100, # Gran negativo para priorizar conectividad
        "is_cover": 500,      # Gran positivo para evitar cobertura
        "is_corner": 100,     # Medio positivo para evitar esquinas
    },
    "Criadora": {
        "honey_amount": 0,    # Pequeño positivo para neutralidad en influencia de miel
        "is_cover": -100,     # Gran negativo para priorizar cobertura
        "is_corner": -50,     # Medio negativo para priorizar esquinas
        "is_crossroad": 500,  # Medio positivo para evitar conectividad
    }
}