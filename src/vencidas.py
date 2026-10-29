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
