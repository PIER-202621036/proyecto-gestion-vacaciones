# ==================================================================
# ZONA COMUN de datos.py: depuracion de datos
# ==================================================================

"""Datos del proyecto: carga, limpieza y acceso a las hojas."""
import pandas as pd

URL_EXCEL = (
    "https://raw.githubusercontent.com/"
    "PIER-202621036/proyecto-gestion-vacaciones/"
    "main/data/empleados_vacaciones.xlsx"
)


def saludar():
  return "saludo desde datos"

# Hojas que usa Python (las demas del Excel son material de gestion)
HOJAS = [
    "Empleados",                    #0
    "Puestos",                      #1        
    "Vacaciones",                   #2
    "Programacion_Vacaciones",      #3
    "Ofertas_Compensacion",         #4
    "Parametros_Vacaciones",        #5
    "Parametros_Criticidad",        #6
    "Niveles_Criticidad"            #7
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
  
  parametros = {}
  for fila in df.to_dict("records"):
      parametros[fila["regla"]] = int(fila["valor"])
  return parametros


# Reglas del negocio: se leen de la hoja Parametros_Vacaciones del Excel
PARAMETROS = cargar_parametros()
DIAS_VACACIONES_PERIODO = PARAMETROS["dias_vacaciones_periodo"]
PORCENTAJE_VENTA = PARAMETROS["porcentaje_venta"]
PERIODOS_CRITICOS = PARAMETROS["periodos_criticos"]
PORCENTAJE_DESCUENTO = PARAMETROS["porcentaje_descuento"]
DIAS_ALERTA_VENCIMIENTO = PARAMETROS["dias_alerta_vencimiento"]
 
# La fecha de corte no esta en la hoja: es la fecha de los datos
FECHA_CORTE = "2026-10-12"
 
# Textos que usan las hojas (se escriben una sola vez aqui)
ESTADO_GOZADA = "Gozada"
ESTADO_PROGRAMADA = "Programada"
DECISION_APROBADA = "Aprobada"
DECISION_PENDIENTE = "Pendiente"
TIPO_VENTA = "Venta_50"
RESPUESTA_ACEPTO = "Aceptó"



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


# ==================================================================
# ZONA PIER de datos.py: obtener empleado, periodos
# ==================================================================

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
  #return data_periodos_empleado 
  #return sorted(data_periodos_empleado, key=lambda p: p["periodo"], reverse=True)
  return sorted(data_periodos_empleado, key=lambda p: p["periodo"])

# ==================================================================
# ZONA DAVID de datos.py: programacion y ofertas de un periodo
# ==================================================================

def obtener_programacion(vacacion_id, data_excel):
  """Devuelve los bloques de programacion de un periodo.
  Es una lista de diccionarios. Si no tiene bloques, devuelve [].
  Ejemplo: obtener_programacion(67, data_excel) devuelve los 3 bloques
  del periodo 2025 de Carmen García (empleado id 17).
  """
  hoja = data_excel[HOJAS[3]] # Refiere a 'Programacion_Vacaciones'
  lista_programacion = hoja.to_dict(orient="records")

  # Filtrar los bloques del periodo con un bucle for tradicional
  data_programacion_vacaciones = []
  for programacion in lista_programacion:
      if programacion["vacacion_id"] == vacacion_id:
          data_programacion_vacaciones.append(programacion)
  return data_programacion_vacaciones

def obtener_programacion_empleado(empleado_id, data_excel):
  """Devuelve todos los bloques de programación de un empleado buscando por su ID.
  Si no tiene bloques o data_empleado es None, devuelve [].
  """
  if empleado_id is None:
      return []


  # Obtenemos la hoja desde HOJAS de forma dinámica
  hoja = data_excel[HOJAS[3]] # Refiere a 'Programacion_Vacaciones'
  lista_programacion = hoja.to_dict(orient="records")

  data_programacion_empleado = []

  for programacion in lista_programacion:
      if programacion.get("empleado_id") == empleado_id:
          data_programacion_empleado.append(programacion)

  return data_programacion_empleado



def obtener_ofertas(vacacion_id, data_excel):
    """Devuelve las ofertas de compensacion de un periodo.
    Incluye Venta_50 e Indemnizacion. Es una lista de diccionarios.
    Si no tiene ofertas, devuelve [].
    """
    hoja = data_excel[HOJAS[4]] # Refiere a 'Ofertas_Compensacion'
    lista_ofertas = hoja.to_dict(orient="records")

    # Filtrar las ofertas del periodo con un bucle for tradicional
    data_ofertas_periodo = []
    for oferta in lista_ofertas:
        if oferta["vacacion_id"] == vacacion_id:
            data_ofertas_periodo.append(oferta)
    return data_ofertas_periodo

def obtener_ofertas_empleado(empleado_id, data_excel):
    """Devuelve todas las ofertas de compensación de un empleado buscando por su ID.
    Si no tiene ofertas o data_empleado es None, devuelve [].
    """
    if empleado_id is None:
        return []

    hoja = data_excel[HOJAS[4]] # Refiere a 'Ofertas_Compensacion'
    lista_ofertas = hoja.to_dict(orient="records")

    data_ofertas_empleado = []

    for oferta in lista_ofertas:
        if oferta.get("empleado_id") == empleado_id:
            data_ofertas_empleado.append(oferta)

    return data_ofertas_empleado









