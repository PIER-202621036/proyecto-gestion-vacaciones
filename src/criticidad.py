from . import datos # pyright: ignore[reportMissingImports]

def saludar():
  return "saludo desde criticidad"

def calcular_score(puesto_id, data_excel):
  """Devuelve el score (0 a 100) de un puesto.
  Por cada variable: nota / nota maxima x peso x 100. Se suman los puntos.
  Ejemplos: P09 = 91 y P03 = 100.
  Lanza ValueError si el puesto no existe o si una nota esta fuera de
  rango (1 a 5).
  """
  puesto = datos.obtener_puesto(puesto_id, data_excel)

  # Los nombres de las variables se leen de la hoja Parametros_Criticidad
  variables_criticidad = data_excel["Parametros_Criticidad"]["variable"].tolist()

  score = 0
  for variable in variables_criticidad:
      regla = datos.obtener_regla(variable, data_excel)
      nota = puesto[variable]
      if nota < regla["nota_min"] or nota > regla["nota_max"]:
          raise ValueError(
              f"Puesto {puesto_id}: la nota de {variable} ({nota}) debe "
              f"estar entre {regla['nota_min']} y {regla['nota_max']}"
          )
      score += nota / regla["nota_max"] * regla["peso"] * 100
  return round(score, 2)

def obtener_nivel(score, data_excel):
    """Convierte un score en su nivel: Bajo, Medio, Alto o Critico.
 
    Limites: 39.99 es Bajo y 40 es Medio; 69.99 es Medio y 70 es Alto;
    84.99 es Alto y 85 es Critico.
    Lanza ValueError si el score no esta entre 0 y 100.
    """
    if score < 0 or score > 100:
        raise ValueError(f"El score {score} debe estar entre 0 y 100")
 
    niveles = datos.obtener_niveles(data_excel)
 
    # Se recorre del nivel mas alto al mas bajo: el primero cuyo minimo
    # alcanza el score es el nivel del puesto.
    for nivel in reversed(niveles):
        if score >= nivel["score_min"]:
            return nivel["nivel"]
 
 
def es_critico(nivel):
    """True si el nivel es Alto o Critico (candidato a oferta de venta)."""
    return nivel in [datos.NIVEL_ALTO, datos.NIVEL_CRITICO]
 
 
def nivel_empleado(data_empleado, data_excel):
    """Devuelve el nivel de criticidad de un empleado.
 
    Recibe el diccionario que devuelve obtener_empleado. El score es del
    puesto, no de la persona: el empleado hereda el nivel de su puesto.
    Ejemplo: id 91 (puesto P09) = Critico. Si el empleado no existe
    (None), devuelve None.
    """
    if data_empleado is None:
        return None
    score = calcular_score(data_empleado["puesto_id"], data_excel)
    return obtener_nivel(score, data_excel)
