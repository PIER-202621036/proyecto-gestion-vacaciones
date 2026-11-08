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
