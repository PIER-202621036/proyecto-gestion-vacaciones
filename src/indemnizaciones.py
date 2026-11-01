from . import datos  # pyright: ignore[reportMissingImports]
from . import vencidas  # pyright: ignore[reportMissingImports]

def saludar():
  return "saludo desde indemenizaciones"



def calcular_indemnizacion(salario, dias_sin_cubrir, parametros):
    """Devuelve los montos de UN periodo vencido.
    Retorna {'indemnizacion', 'remuneracion', 'descuento', 'bruto', 'neto'}:
    - Indemnizacion: salario x sueldos x factor, sin descuento.
    - Remuneracion vacacional: salario x sueldos x factor, con descuento.
    El factor es la parte del periodo sin cubrir (dias sin cubrir / 30).
    El sueldo del mes NO va aqui: se paga una sola vez por boleta
    (ver calcular_sueldo_mes).
    Ejemplos con salario 10800: 30 dias -> bruto 21600, neto 19440;
    15 dias -> bruto 10800, neto 9720.
    """
    if salario < 0 or dias_sin_cubrir < 0:
        raise ValueError("Salario y dias sin cubrir no pueden ser negativos")
    if dias_sin_cubrir == 0:
        return {"indemnizacion": 0.0, "remuneracion": 0.0,
                "descuento": 0.0, "bruto": 0.0, "neto": 0.0}
 
    factor = dias_sin_cubrir / parametros["dias_vacaciones_periodo"]
 
    # lambda + map(): la misma formula para los dos conceptos
    sueldos = [
        parametros["sueldos_indemnizacion"],
        parametros["sueldos_remuneracion_vacacional"],
    ]
    indemnizacion, remuneracion = map(
        lambda cantidad: round(salario * cantidad * factor, 2), sueldos
    )
 
    porcentaje = parametros["porcentaje_descuento"]
    descuento = round(remuneracion * porcentaje / 100, 2)
    bruto = round(indemnizacion + remuneracion, 2)
    return {
        "indemnizacion": indemnizacion,
        "remuneracion": remuneracion,
        "descuento": descuento,
        "bruto": bruto,
        "neto": round(bruto - descuento, 2),
    }
 
 
def calcular_sueldo_mes(salario, parametros):
    """Devuelve {'bruto', 'descuento', 'neto'} del sueldo del mes.
    Se paga el mes COMPLETO (sin factor) y UNA SOLA VEZ por boleta, con el
    descuento. Ejemplo con salario 10800: bruto 10800, neto 8640.
    """
    if salario < 0:
        raise ValueError("El salario no puede ser negativo")
    bruto = round(salario * parametros["sueldos_mes_goce"], 2)
    descuento = round(bruto * parametros["porcentaje_descuento"] / 100, 2)
    return {"bruto": bruto, "descuento": descuento,
            "neto": round(bruto - descuento, 2)}

def estado_gestion(ofertas):
    """Devuelve la gestion de la indemnizacion de un periodo.
    'Pagada' si hay una oferta Indemnizacion ya con estado Pagado, 
    'Avisada' si hay una con estado Avisado y 
    'Falta avisar' si no hay ninguna de las dos.
    """
    gestion = "Falta avisar"
    for oferta in ofertas:
        if oferta["tipo_oferta"] == datos.TIPO_INDEMNIZACION:
            if oferta["estado"] == datos.OFERTA_PAGADA:
                return "Pagada"
            if oferta["estado"] == datos.OFERTA_AVISADA:
                gestion = "Avisada"
    return gestion

def historial_indemnizacion(data_empleado, data_excel, fecha_corte=None):
    """Devuelve el HISTORIAL: todos los periodos indemnizables del empleado.
 
    Un periodo es indemnizable si esta vencido y tiene dias sin cubrir.
    Incluye los ya Pagados: es lo que el empleado tiene, no lo que se le debe
    pagar ahora (eso lo da resumen_indemnizacion).
    Es una lista de diccionarios; si no hay ninguno, devuelve [].
    """
    if fecha_corte is None:
        fecha_corte = datos.FECHA_CORTE
    if data_empleado is None:
        return []
 
    historial = []
    for periodo in datos.obtener_periodos(data_empleado, data_excel):
        id_periodo = periodo["vacacion_id"]
        ofertas = datos.obtener_ofertas(id_periodo, data_excel)
        programacion = datos.obtener_programacion(id_periodo, data_excel)
 
        # Funciones de Pier: dias sin cubrir y estado del periodo
        sin_cubrir = vencidas.calcular_dias_sin_cubrir(
            periodo, ofertas, programacion
        )
        estado = vencidas.estado_periodo(periodo, fecha_corte)
 
        # Indemnizable = vencido Y con dias sin cubrir. No lo es si todavia
        # esta vigente (aun puede gozarlo) o si ya no le quedan dias sin
        # cubrir (los tomo, los vendio o los programo con RR. HH.).
        if estado != "Vencido" or sin_cubrir == 0:
            continue
 
        historial.append({
            "periodo": periodo["periodo"],
            "vacacion_id": id_periodo,
            "dias_sin_cubrir": sin_cubrir,
            "gestion": estado_gestion(ofertas),
        })
    return historial
 
 
def resumen_indemnizacion(data_empleado, data_excel, parametros,
                          fecha_corte=None):
    """Calcula la BOLETA del proximo pago: lo que se le tiene que pagar.
    La boleta tiene, en este orden:
    1. El sueldo del mes completo, UNA sola vez, con descuento.
    2. La remuneracion vacacional de cada periodo pendiente, con descuento.
    3. La indemnizacion de cada periodo pendiente, sin descuento.
    Los periodos ya Pagados no entran (ya se pagaron). Sin periodos por
    pagar, la boleta solo trae el sueldo del mes.
    Ejemplo: id 91 -> bruto 43200, descuento 5400, neto 37800.
    Devuelve {'lineas', 'dias_a_pagar', 'bruto', 'descuento', 'neto'}.
    """
    resumen = { "lineas": [], 
                "dias_a_pagar": 0,
                "bruto": 0.0, 
                "descuento": 0.0, 
                "neto": 0.0
              }
    if data_empleado is None:
        return resumen
 
    salario = data_empleado["salario"]
    sueldo = calcular_sueldo_mes(salario, parametros)
    resumen["lineas"].append({
        "concepto": "Sueldo del mes", 
        "periodo": None, 
        "dias": None,
        "gestion": None, 
        "bruto": sueldo["bruto"],
        "descuento": sueldo["descuento"], 
        "neto": sueldo["neto"],
    })
 
    # Solo lo que falta pagar: se saltan los periodos Pagada
    pendientes = []
    for periodo in historial_indemnizacion(data_empleado, data_excel,
                                           fecha_corte):
        if periodo["gestion"] != "Pagada":
            pendientes.append(periodo)
 
    remuneraciones = []
    indemnizaciones = []
    for periodo in pendientes:
        montos = calcular_indemnizacion(
            salario, periodo["dias_sin_cubrir"], parametros
        )
        datos_periodo = {
            "periodo": periodo["periodo"],
            "dias": periodo["dias_sin_cubrir"],
            "gestion": periodo["gestion"],
        }
        remuneraciones.append({
            "concepto": "Remuneración vacacional", 
            **datos_periodo,
            "bruto": montos["remuneracion"], 
            "descuento": montos["descuento"],
            "neto": round(montos["remuneracion"] - montos["descuento"], 2),
        })
        indemnizaciones.append({
            "concepto": "Indemnización vacacional", 
            **datos_periodo,
            "bruto": montos["indemnizacion"], 
            "descuento": 0.0,
            "neto": montos["indemnizacion"],
        })
        resumen["dias_a_pagar"] += periodo["dias_sin_cubrir"]
 
    resumen["lineas"].extend(remuneraciones)
    resumen["lineas"].extend(indemnizaciones)
 
    for linea in resumen["lineas"]:
        resumen["bruto"] += linea["bruto"]
        resumen["descuento"] += linea["descuento"]
        resumen["neto"] += linea["neto"]
    for clave in ("bruto", "descuento", "neto"):
        resumen[clave] = round(resumen[clave], 2)
    return resumen
