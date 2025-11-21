from typing import Callable, Dict, Any, Optional
import time
from pygame.math import Vector2

# Registro global de condiciones
_CONDITIONS: Dict[str, Callable[[Any, Optional[Dict[str, Any]]], bool]] = {}

def register_condition(name: str):
    """Decorador para registrar una condición reutilizable."""
    def deco(fn: Callable[[Any, Optional[Dict[str, Any]]], bool]):
        _CONDITIONS[name] = fn
        return fn
    return deco

def evaluate_condition(name: str, context, state_params: Optional[Dict[str, Any]] = None) -> bool:
    """Evalúa la condición registrada por nombre; devuelve False si no existe."""
    fn = _CONDITIONS.get(name)
    if not fn:
        return False
    try:
        return bool(fn(context, state_params or {}))
    except Exception:
        return False

# ---------- Condiciones predefinidas útiles ----------

@register_condition('reached_goal')
def cond_reached_goal(context, params: Optional[Dict[str, Any]]) -> bool:  # params puede ser None
    """
    True si el NPC alcanzó su meta HSM (npc.hsm_goal) por distancia o si el algoritmo reporta terminado.
    Parámetros opcionales:
      - threshold: distancia en píxeles para considerar llegada (default 8).
    """
    npc = context.npc
    goal = getattr(npc, 'hsm_goal', None)
    if goal is None:
        return False

    # 1) Por implementar: proveer finish/is_finished en los algoritmos
    alg = getattr(npc, 'algorithm_instance', None)
    if alg:
        if getattr(alg, 'finished', False) or getattr(alg, 'is_done', False):
            return True
        if hasattr(alg, 'is_finished') and callable(getattr(alg, 'is_finished')):
            try:
                if alg.is_finished():
                    return True
            except Exception:
                pass

    # 2) Fallback: distancia entre npc.kinematic.position y goal
    try:
        pos = getattr(npc, 'kinematic').position
        pv = Vector2(pos.x, pos.y) if hasattr(pos, 'x') else Vector2(pos)
        gv = Vector2(goal)
        threshold = float(params.get('threshold', 8.0)) if params else 8.0
        return (pv - gv).length() <= threshold
    except Exception:
        return False


@register_condition('player_near')
def cond_player_near(context, params: Optional[Dict[str, Any]]) -> bool:  # params puede ser None
    """
    True si el jugador está dentro de un radio.
    Parámetros:
      - radius: distancia umbral (default 150)
    """
    world = context.world
    npc = context.npc
    if not world:
        return False
    try:
        px, py = world.player.kinematic.position
        pos = getattr(npc, 'kinematic').position
        dx = px - pos.x
        dy = py - pos.y
        r = float(params.get('radius', 80.0)) if params else 80.0
        return dx*dx + dy*dy <= r*r
    except Exception:
        return False

@register_condition('player_far')
def cond_player_far(context, params: Optional[Dict[str, Any]]) -> bool:  # params puede ser None
    """
    True si el jugador está fuera de un radio.
    Parámetros:
      - radius: distancia umbral (default 200)
    """
    world = context.world
    npc = context.npc
    if not world:
        return False
    try:
        px, py = world.player.kinematic.position
        pos = getattr(npc, 'kinematic').position
        dx = px - pos.x
        dy = py - pos.y
        r = float(params.get('radius', 200.0)) if params else 200.0
        return dx*dx + dy*dy > r*r
    except Exception:
        return False

@register_condition('received_damage')
def cond_received_damage(context, params: Optional[Dict[str, Any]]) -> bool:  # params puede ser None
    """
    True si el NPC recientemente recibió daño.
    - Usa npc.is_hit o npc.last_damage_time si existe.
    """
    npc = context.npc
    # Si is_hit, la usamos y luego el sistema puede limpiarla externamente
    if getattr(npc, 'is_hit', False):
        return True
    # Alternativa: tiempo desde last_damage_time comparado con window
    last = getattr(npc, 'last_damage_time', None)
    if last and params:
        window = float(params.get('window', 1.0))
        return (time.time() - last) <= window
    return False

@register_condition('alert_time_expired')
def cond_alert_time_expired(context, params: Optional[Dict[str, Any]]) -> bool:  # params puede ser None
    """
    True si el tiempo de alerta en npc._alert_started_at excede params['alert_duration'].
    """
    npc = context.npc
    started = getattr(npc, '_alert_started_at', None)
    if started is None:
        return False
    dur = float(params.get('alert_duration', 5.0)) if params else 5.0
    import time
    return (time.time() - started) >= dur

@register_condition('applied_attack')
def cond_already_attack(context, params: Optional[Dict[str, Any]]) -> bool:
    npc = context.npc
    last = getattr(npc, '_last_attack_time', None)
    if last is None:
        return False
    window = float(params.get('window', 0.5)) if params else 0.5
    return (time.time() - last) <= window

@register_condition('protected_jar_lost')
def cond_protected_jar_lost(context, params: Optional[Dict[str, Any]]) -> bool:
    npc = context.npc
    world = context.world

    protected = getattr(npc, 'protected_jar', None)
    if not protected:
        return False
    
    protected_set = getattr(world, 'protected_jars', None)
    if protected_set is not None:
        return protected not in protected_set

    honey_list = getattr(world, 'honey_pots', None)
    if honey_list:
        if hasattr(protected, 'initial_pos'):
            ppos = tuple(getattr(protected, 'initial_pos'))
            for h in honey_list:
                if hasattr(h, 'initial_pos') and tuple(h.initial_pos) == ppos:
                    return False
            return True
        else:
            return protected not in honey_list
    return False

@register_condition('player_near_with_honey')
def cond_player_near_with_honey(context, params: Optional[Dict[str, Any]]) -> bool:
    """True si el jugador está cerca y tiene tarros (honey_collected > 0)."""
    world = context.world
    npc = context.npc
    if not world or not hasattr(world, 'player'):
        return False
    try:
        px, py = world.player.kinematic.position
        nx, ny = npc.kinematic.position.x, npc.kinematic.position.y
        radius = float(params.get('radius', 80.0)) if params else 80.0
        if (px - nx)**2 + (py - ny)**2 > radius * radius:
            return False
        return getattr(world.player, 'honey_collected', 0) > 0
    except Exception:
        return False

@register_condition('player_near_no_honey')
def cond_player_near_no_honey(context, params: Optional[Dict[str, Any]]) -> bool:
    """True si el jugador está cerca y NO tiene tarros."""
    world = context.world
    npc = context.npc
    if not world or not hasattr(world, 'player'):
        return False
    try:
        px, py = world.player.kinematic.position
        nx, ny = npc.kinematic.position.x, npc.kinematic.position.y
        radius = float(params.get('radius', 80.0)) if params else 80.0
        if (px - nx)**2 + (py - ny)**2 > radius * radius:
            return False
        count = getattr(world.player, 'honey_collected', 0)
        return count == 0
    except Exception:
        return False

@register_condition('critical_damage')
def cond_critical_damage(context, params: Optional[Dict[str, Any]]) -> bool:
    """True si la salud del NPC está por debajo del umbral crítico (params['threshold'])."""
    npc = context.npc
    try:
        threshold = float(params.get('critical_threshold', 25.0)) if params else 25.0
        return getattr(npc, 'health', 9999) <= threshold
    except Exception:
        return False
    
@register_condition('flee_time_expired')
def cond_flee_time_expired(context, params: Optional[Dict[str, Any]]) -> bool:
    """
    True si el NPC lleva en modo 'flee' más tiempo del permitido.
    - Usa npc._flee_started_at y npc._flee_duration si existen.
    - Parámetros opcionales en params:
        - duration: duración en segundos para considerar expirado (si se pasa, tiene prioridad).
    """
    npc = context.npc
    # Obtener inicio y duración
    start = getattr(npc, '_flee_started_at', None)
    duration = None
    try:
        if params and 'duration' in params:
            duration = float(params['duration'])
        else:
            duration = float(getattr(npc, '_flee_duration', 0.0)) if getattr(npc, '_flee_duration', None) is not None else None
    except Exception:
        duration = None

    if start is None or duration is None or duration <= 0:
        # Sin temporizador válido no consideramos expirado
        return False

    try:
        return (time.time() - float(start)) >= float(duration)
    except Exception:
        return False

@register_condition('found_safe_zone')
def cond_fount_safe_zone(context, params: Optional[Dict[str, Any]]) -> bool:
    npc = context.npc

    return npc.current_node_id == npc.hsm_goal

@register_condition('offspring_born')
def cond_offspring_born(context, params: Optional[Dict[str, Any]]) -> bool:
    npc = context.npc
    egg_laid = getattr(npc, '_egg_laid', False)
    egg_laid_at = getattr(npc, '_egg_lay_started_at', None)
    try:
        incubation = float(params.get('incubation', 5.0)) if params else 5.0
    except Exception:
        incubation = 5.0
    if egg_laid and egg_laid_at is not None:
        try:
            import time
            if (time.time() - float(egg_laid_at)) >= incubation:
                return True
        except Exception:
            pass
    return False