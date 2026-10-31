from . import datos  # pyright: ignore[reportMissingImports]
from . import vencidas  # pyright: ignore[reportMissingImports]

def saludar():
  return "saludo desde indemenizaciones"



def calcular_indemnizacion(salario, dias_sin_cubrir, parametros):
    """Devuelve {'bruto': 0.00, 'neto': 0.00} de un periodo vencido.
    Se suman tres conceptos, cada uno = salario x sueldos x factor:
    indemnizacion (sin descuento), remuneracion vacacional y sueldo del
    mes (estos dos llevan descuento en el neto).
    Ejemplo: salario 10800 y 30 dias sin cubrir -> bruto 32400, neto 28080.
    """
    if salario < 0 or dias_sin_cubrir < 0:
        raise ValueError("Salario y dias sin cubrir no pueden ser negativos")
 
    # El factor es la proporción del período que quedó sin cubrir.
    # Responde a “¿qué fracción de un período completo le debo al empleado?”.
    # ejemplo: 30 / 30	1.0 se paga completo
    # ejemplo: 15 / 30	0.5	se paga la mitad
    factor = dias_sin_cubrir / parametros["dias_vacaciones_periodo"]
    sueldos_indemnizacion = parametros["sueldos_indemnizacion"]
    sueldos_remuneracion_vacacional = parametros["sueldos_remuneracion_vacacional"]
    sueldos_mes = parametros["sueldos_mes_goce"]
 
    indemnizacion = salario * sueldos_indemnizacion * factor
    remuneracion = salario * sueldos_remuneracion_vacacional * factor
    sueldo_mes = salario * sueldos_mes * factor
 
    # lambda + map(): aplica el descuento a los montos que lo llevan
    descuento = parametros["porcentaje_descuento"]
    con_descuento = list(map(
        lambda monto: monto * (1 - descuento / 100),
        [remuneracion, sueldo_mes],
    ))
 
    bruto = indemnizacion + remuneracion + sueldo_mes
    neto = indemnizacion + sum(con_descuento)
    return {"bruto": round(bruto, 2), "neto": round(neto, 2)}



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


def resumen_indemnizacion(data_empleado, data_excel, parametros,
                          fecha_corte=None):
    
    """Calcula lo que falta pagar de los periodos indemnizables de un empleado.
    Un periodo es indemnizable si esta vencido y tiene dias sin cubrir.
    Los periodos ya Pagados se muestran, pero no suman.
    Recibe el diccionario que devuelve obtener_empleado.
    Si no se da fecha_corte, se usa datos.FECHA_CORTE.
    Ejemplo: id 91 -> bruto 48600, neto 42120.
    """

    if fecha_corte is None:
        fecha_corte = datos.FECHA_CORTE
 
    resumen = {"periodos": [], "dias_a_pagar": 0, "bruto": 0, "neto": 0}
    if data_empleado is None: # si no hay empleado se devuelve resumen vacio
        return resumen
 
    for periodo in datos.obtener_periodos(data_empleado, data_excel): # Función de Pier 
        vacacion_id = periodo["vacacion_id"]
        ofertas = datos.obtener_ofertas(vacacion_id, data_excel)
        programacion = datos.obtener_programacion(vacacion_id, data_excel)
 
        # Funciones de Pier: dias sin cubrir y estado del periodo
        sin_cubrir = vencidas.calcular_dias_sin_cubrir(
            periodo, ofertas, programacion
        )

        # Para que sea indemnizable, el empleado tiene que tener
        # vacaciones vencidas Y con dias sin cubrir.
        # No es indemnizable porque esta vigente el periodo (aun puede gozarlo) 
        # o si ya no le quedan dias sin cubrir lo cual significa: 
        # que los tomo, los vendio o los programo con RR. HH.
        estado = vencidas.estado_periodo(periodo, fecha_corte)
        if estado != "Vencido" or sin_cubrir == 0:
            continue  # no es indemnizable
 
        gestion = estado_gestion(ofertas)
        if gestion == "Pagada":
            montos = {"bruto": 0, "neto": 0}  # ya se pago: no se paga otra vez
        else:
            montos = calcular_indemnizacion(
                data_empleado["salario"], sin_cubrir, parametros
            )
            resumen["dias_a_pagar"] += sin_cubrir
            resumen["bruto"] += montos["bruto"]
            resumen["neto"] += montos["neto"]
 
        resumen["periodos"].append({
            "periodo": periodo["periodo"],
            "vacacion_id": vacacion_id,
            "dias_sin_cubrir": sin_cubrir,
            "gestion": gestion,
            "bruto": montos["bruto"],
            "neto": montos["neto"],
        })
 
    resumen["bruto"] = round(resumen["bruto"], 2)
    resumen["neto"] = round(resumen["neto"], 2)
    return resumen
