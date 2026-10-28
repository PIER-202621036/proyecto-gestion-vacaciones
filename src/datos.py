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

# Limpiar datos
def limpiar_datos(data_excel):
  # Se calcula una sola vez, no en cada columna
  permitidos = [n.lower() for n in NULOS_PERMITIDOS]

  data_limpia = {} # diccionario NUEVO

  for nombre_hoja, df in data_excel.items():

    # 1. Duplicados
    cantidad_duplicados = df.duplicated().sum()
    if cantidad_duplicados > 0:
        print(f"Hoja {nombre_hoja}: {cantidad_duplicados} duplicados.")
        df = df.drop_duplicates()

    # 2. Nulos (excluyendo NULOS_PERMITIDOS), Comprensión de Listas
    columnas_obligatorias = [
        col 
        for col in df.columns if col.lower() not in permitidos
    ]

    # Cuenta las CELDAS vacias en las columnas obligatorias:
    # isna() marca True/False y el primer sum() suma por columna;
    # el segundo sum() suma todas las columnas en un solo numero.
    cantidad_nulos = df[columnas_obligatorias].isna().sum().sum()
    
    if cantidad_nulos > 0:
        print(f"Hoja {nombre_hoja}: {cantidad_nulos} nulos no permitidos.")
        df = df.dropna(subset=columnas_obligatorias)

    # Guardamos la hoja limpia en el diccionario nuevo
    data_limpia[nombre_hoja] = df.reset_index(drop=True)

  return data_limpia

def obtener_empleado(empleado_id, data_excel):

  # 1. Convertir los DataFrames a listas de diccionarios sencillos
  empleados = data_excel["Empleados"].to_dict(orient="records")
  puestos = data_excel["Puestos"].to_dict(orient="records")

  # 2. Bucle tradicional
  data_empleado = None

  for emp in empleados:
      if emp["id"] == empleado_id:
          data_empleado = emp.copy()
          for p in puestos:
              if (p["puesto_id"] == emp["puesto_id"]):
                  data_empleado["puesto"] = p["puesto"]
                  break
          break
  return data_empleado

def obtener_periodos(data_empleado, data_excel):
  """Devuelve los periodos del empleado, del mas antiguo al mas nuevo.
     Es una lista de diccionarios. Si aun no tiene periodos, devuelve [].
  """

  # Inicializamos la lista
  data_periodos_empleado = []

  # 1. Si resultado_obtener_empleado is None, no existe el empleado
  if data_empleado is not None:

    vacaciones = data_excel["Vacaciones"].to_dict(orient="records")

    # 2. Filtrar las vacaciones del empleado usando un bucle for tradicional
    data_periodos_empleado = []

    for v in vacaciones:
        if v["empleado_id"] == data_empleado["id"]:
            data_periodos_empleado.append(v)
  return data_periodos_empleado

