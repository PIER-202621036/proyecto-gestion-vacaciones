"""Datos del proyecto: carga, limpieza y acceso a las hojas."""
import pandas as pd

URL_EXCEL = (
    "https://raw.githubusercontent.com/"
    "PIER-202621036/proyecto-gestion-vacaciones/"
    "main/data/empleados_vacaciones.xlsx"
)


def saludar():
  return "saludo desde datos"

#

# Diccionario único de configuración (alberga textos fijos y reglas)
PARAMETROS = {
    "estado_gozada": "Gozada",
    "estado_programada": "Programada",
    "decision_aprobada": "Aprobada",
    "decision_pendiente": "Pendiente",
    "tipo_venta": "Venta_50",
    "respuesta_acepto": "Aceptó",
    "fecha_corte": "2026-10-12",
}

# Hojas que usa Python (las demas del Excel son material de gestion)
HOJAS = [
    "Empleados", 
    "Puestos", 
    "Vacaciones", 
    "Programacion_Vacaciones",
    "Ofertas_Compensacion", 
    "Parametros_Vacaciones",
    "Parametros_Criticidad", 
    "Niveles_Criticidad"
]

# Unicas columnas que pueden estar vacias (segun el Diccionario)
NULOS_PERMITIDOS = ["motivo", "fecha_estado"]

def cargar_parametros(ruta=URL_EXCEL):
  """Lee la hoja Parametros_Vacaciones y devuelve {regla: valor}."""
  try:
      df = pd.read_excel(ruta, sheet_name="Parametros_Vacaciones")
  except (OSError, ValueError) as error:
      raise ConnectionError(
          f"No se pudo leer Parametros_Vacaciones: {error}"
      ) from error 

  for fila in df.to_dict("records"):
      PARAMETROS[fila["regla"]] = int(fila["valor"])
  return PARAMETROS

# Cargar todas las hojas del Excel
def cargar_datos(ruta=URL_EXCEL):
  """
    Lee el archivo Excel completo, valida que contenga las hojas obligatorias
    y devuelve un diccionario {nombre_hoja: dataframe}.
  """
  try:
    df = pd.read_excel(ruta, sheet_name=None)
  except OSError as error:
    raise ConnectionError(f"No se pudo leer el Excel: {error}") from error

  datos = {}
  for nombre_hoja in HOJAS:
    if nombre_hoja not in df:
        raise ValueError(f"El Excel no tiene la hoja {nombre_hoja}")

    # Guardar la hoja tal cual está
    datos[nombre_hoja] = df[nombre_hoja]
  return datos








