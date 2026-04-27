from datetime import date, timedelta
from typing import Tuple


def calculate_sm2(
    quality: int, repetitions: int, ease_factor: float, interval: int
) -> Tuple[int, float, int, date]:
    """
    Implementación del algoritmo SM-2 (SuperMemo 2).

    Parámetros:
    - quality: 0-2 (0=Difícil, 1=Bien, 2=Fácil)
    - repetitions: repeticiones consecutivas correctas
    - ease_factor: factor de facilidad (mínimo 1.3)
    - interval: intervalo actual en días

    Retorna:
    - new_interval: nuevo intervalo en días
    - new_ease_factor: nuevo factor de facilidad
    - new_repetitions: nuevo conteo de repeticiones
    - next_review: fecha del próximo repaso
    """
    # Mapeo: calidad interna del 0-5 del SM-2
    # 0 = falló (quality 0), 1-2 = corretas (quality 1-2)

    if quality == 0:
        # Falló - reiniciarRepetitions = 0
        # interval = 1
        new_interval = 1
        new_repetitions = 0
    else:
        # Correcta - incrementa interval
        if repetitions == 0:
            new_interval = 1
        elif repetitions == 1:
            new_interval = 6
        else:
            new_interval = int(interval * ease_factor)

        new_repetitions = repetitions + 1

    # Calcula nuevo ease factor
    # EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    # Adaptado para quality 0-2
    if quality == 0:
        # Penalización mayor si falló
        new_ease_factor = max(1.3, ease_factor - 0.2)
    elif quality == 1:
        new_ease_factor = max(1.3, ease_factor - 0.05)
    else:
        # quality == 2 (Fácil) - bonificación
        new_ease_factor = ease_factor + 0.1

    # Calcula fecha próxima
    next_review = date.today() + timedelta(days=new_interval)

    return new_interval, new_ease_factor, new_repetitions, next_review


def get_quality_from_button(button: str) -> int:
    """
    Convierte botón de UI a calidad SM-2.
    """
    quality_map = {
        "difficult": 0,  # Difícil
        "good": 1,  # Bien
        "easy": 2,  # Fácil
    }
    return quality_map.get(button, 1)
