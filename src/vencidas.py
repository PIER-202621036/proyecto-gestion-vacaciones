import datos  # pyright: ignore[reportMissingImports]

from datetime import date

def saludar():
  return "saludo desde vencidas"

def convierto_texto_fecha(texto):
  """Convierte un texto AAAA-MM-DD en fecha. Lanza ValueError si es malo."""
  try:
      return date.fromisoformat(str(texto)[:10])
  except ValueError as error:
      raise ValueError(f"Fecha invalida: {texto!r}") from error


def estado_periodo(periodo, fecha_corte):
  """Devuelve 'Vencido' si el corte es posterior al fin, si no 'Vigente'."""
  if convierto_texto_fecha(periodo["fecha_fin_periodo"]) < convierto_texto_fecha(fecha_corte):
      return "Vencido"
  return "Vigente"

def periodos_vencidos(periodos, fecha_corte):
  """Devuelve solo los periodos que ya vencieron."""
  vencidos = []
  for periodo in periodos:
      if estado_periodo(periodo, fecha_corte) == "Vencido":
          vencidos.append(periodo)
  return vencidos
 
 
def periodos_vigentes(periodos, fecha_corte):
  """Devuelve solo los periodos que aun no vencen."""
  vigentes = []
  for periodo in periodos:
      if estado_periodo(periodo, fecha_corte) == "Vigente":
          vigentes.append(periodo)
  return vigentes


def calcular_dias_vendidos(periodo, ofertas):
  """Suma los dias de Venta_50 que el empleado acepto en el periodo."""
  
  total = 0
  for oferta in ofertas:
      if (oferta["vacacion_id"] == periodo["vacacion_id"]
              and oferta["tipo_oferta"] == datos.TIPO_VENTA
              and oferta["estado"] == datos.RESPUESTA_ACEPTO):
          total += oferta["dias"]
  return total
 
 
def calcular_dias_programados(periodo, programacion):
  """Suma los dias de bloques Programada con decision Aprobada."""
  
  total = 0
  for bloque in programacion:
      if (bloque["vacacion_id"] == periodo["vacacion_id"]
              and bloque["estado"] == datos.ESTADO_PROGRAMADA
              and bloque["decision_rrhh"] == datos.DECISION_APROBADA):
          total += bloque["dias"]
  return total
 
 
def calcular_dias_sin_cubrir(periodo, ofertas, programacion):
  """Devuelve dias pendientes - vendidos - programados aprobados.
  Nunca baja de 0.
  """
  vendidos = calcular_dias_vendidos(periodo, ofertas)
  programados = calcular_dias_programados(periodo, programacion)
  return max(0, periodo["dias_pendientes"] - vendidos - programados)    

  
