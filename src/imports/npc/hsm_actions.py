# ...existing code...
"""
Acciones concretas para estados de la HSM.
Cada función recibe (context, params) o (context, dt, params) según corresponda.
Las acciones usan la API pública del NPC: set_algorithm, follow_path_from_nodes,
current_animation, update_with_algorithm, etc.
"""

from typing import Dict, Any, Optional
from imports.pathfinding.a_star import a_star_search
import math
import time

def _set_algorithm_from_params(npc, params: Optional[Dict[str, Any]]):
    """Helper: configurar algoritmo en el NPC si params lo indican."""
    if not params:
        return
    alg_name = params.get('algorithm_name')
    # Si se proporciona algorithm_name, asignarlo y pasar parámetros a set_algorithm
    if alg_name:
        npc.algorithm_name = alg_name
        # Pasar parámetros extra (ej. target, path, max_speed) a set_algorithm
        alg_params = params.get('algorithm_params', {})
        npc.set_algorithm(**alg_params)

# --- Acciones específicas para la Tejedora (TEJER / LANZAR_RED / ALERTAR) ---

def action_enter_search_jars(context, params: Dict[str, Any]):
    """
    Al entrar en BuscarTarrosSinRed:
    - Seleccionar animación de búsqueda.
    - Intentar localizar el tarro más cercano no protegido usando world.jar_positions.
    - Si se encuentra un objetivo, configurar el algoritmo para moverse hacia él.
    """
    npc = context.npc
    world = context.world
    npc.current_animation = 'walk'

    # Buscar tarro más cercano no protegido (si el mundo provee jar_positions y protected_jars)
    if not world:
        return
    jar_positions = getattr(world, 'honey_pots', None)
    protected_jars = getattr(world, 'protected_jars', set())
    if not jar_positions:
        return
    protected_jars = {j for j in jar_positions if j.on_web}
    # Encontrar tarro más cercano que no esté protegido
    min_dist = float('inf')
    target_pos = None
    for j in jar_positions:
        if j in protected_jars:
            continue
        # j puede ser tuple (x,y) o Vector2; calcular distancia aproximada al NPC
        dx = (j.initial_pos[0] - npc.kinematic.position.x) if hasattr(npc, 'kinematic') else (j[0])
        dy = (j.initial_pos[1] - npc.kinematic.position.y) if hasattr(npc, 'kinematic') else (j[1])
        d = math.hypot(dx, dy)
        if d < min_dist:
            min_dist = d
            target_pos = j.initial_pos

    # Si se encontró un tarro, pedir al NPC que lo persiga mediante FollowPath o algoritmo indicado
    if target_pos is not None:
        npc.hsm_goal = target_pos
        # Priorizar follow_path_from_nodes si el world provee nav_mesh/nav_nodes
        nav_mesh = getattr(world, 'nav_mesh', None)
        if nav_mesh:
            # obtener nodo objetivo y construir ruta simplificada
            try:
                target_node = nav_mesh.find_node_at_position(target_pos)
            except Exception as e:
                target_node = None
            # Si hay nodos, usar follow_path_from_nodes (requiere path_nodes y nav_mesh_nodes)
            if target_node is not None:
                path_nodes = a_star_search(npc.current_node_id, target_node, world.nav_mesh.nodes, world.nav_mesh.edges)
                target = params['explicit_target']
                target.kinematic.position = target_pos
                npc.follow_path_from_nodes(path_nodes, world.nav_mesh.nodes, explicit_target=target)
                return
        # Fallback: usar set_algorithm con target explícito (FollowPath si está disponible en SWITCHER)
        npc.algorithm_name = 'FollowPath'
        npc.set_algorithm(explicit_target=target_pos)


def action_update_search_jars(context, dt: float, params: Dict[str, Any]):
    """
    Update de BuscarTarrosSinRed: delega el movimiento al algoritmo configurado.
    - Ejecuta update_with_algorithm del NPC.
    """
    npc = context.npc
    world = context.world
    bounds = (world.map.width_pixels, world.map.height_pixels) if world and hasattr(world, 'map') else None
    nav_mesh = getattr(world, 'nav_mesh', None) if world else None
    obstacles = getattr(world.map, 'obstacles', None) if world and hasattr(world, 'map') else None
    margin = (npc.sprite_size[0] // 2, npc.sprite_size[1] // 2) if hasattr(npc, 'sprite_size') else (0, 0)
    npc.update_with_algorithm(dt, uses_rotation=False, bounds=bounds, margin=margin, obstacles=obstacles, nav_mesh=nav_mesh)


def action_exit_search_jars(context, params: Dict[str, Any]):
    """
    Al salir de BuscarTarrosSinRed: limpiar configuraciones temporales si es necesario.
    - Por defecto no hace mucho, pero dejamos la posibilidad de detener algoritmos.
    """
    npc = context.npc
    # Detener algoritmo de búsqueda al salir
    npc.algorithm_name = ''
    npc.set_algorithm()


def action_enter_protect(context, params: Dict[str, Any]):
    """
    Al entrar en Proteger:
    - Poner animación de guardia y configurar comportamiento de vigilancia alrededor del tarro.
    - params puede contener 'guard_radius' para definir distancia de vigilancia.
    """
    npc = context.npc
    npc.current_animation = 'walk'
    if hasattr(npc, 'hsm_goal') and npc.hsm_goal:
        # hsm_goal puede ser tuple (x,y) o referencia a objeto; guardamos la forma original
        npc.protected_jar = getattr(npc, 'hsm_goal')
    else:
        # fallback: permitir especificar protected_jar en params
        if params and params.get('protected_jar') is not None:
            npc.protected_jar = params.get('protected_jar')
    # Intentar usar un algoritmo de patrulla/seek alrededor del tarro si se provee en params
    params['algorithm_params']['target'].kinematic.position = npc.hsm_goal
    _set_algorithm_from_params(npc, params)
    # Si no hay algoritmo explícito, mantener al NPC en posición (detener movimiento)
    if not getattr(npc, 'algorithm_class', None):
        npc.algorithm_name = ''
        npc.set_algorithm()


def action_update_protect(context, dt: float, params: Dict[str, Any]):
    """
    Update de Proteger: delega la actualización al algoritmo (si existe).
    """
    npc = context.npc
    world = context.world
    bounds = (world.map.width_pixels, world.map.height_pixels) if world and hasattr(world, 'map') else None
    nav_mesh = getattr(world, 'nav_mesh', None) if world else None
    obstacles = getattr(world.map, 'obstacles', None) if world and hasattr(world, 'map') else None
    margin = (npc.sprite_size[0] // 2, npc.sprite_size[1] // 2) if hasattr(npc, 'sprite_size') else (0, 0)
    npc.update_with_algorithm(dt, uses_rotation=False, bounds=bounds, margin=margin, obstacles=obstacles, nav_mesh=nav_mesh)


def action_exit_protect(context, params: Dict[str, Any]):
    """
    Al salir de Proteger: limpiar estado de guardia.
    """
    npc = context.npc
    npc.algorithm_name = ''
    npc.set_algorithm()
    npc.current_animation = 'idle'


def action_start_throw_net(context, params: Dict[str, Any]):
    """
    Al entrar en LANZAR_RED:
    - Preparar animación de lanzamiento, detener movimiento y marcar NPC como atacando.
    - No dispara eventos de HSM aquí; el sistema externo debe emitir 'realizo_ataque' o 'jugador_cae_en_red'.
    """
    npc = context.npc
    world = context.world
    # Marcar estado de ataque y animación
    setattr(npc, 'is_attacking', True)
    npc.current_animation = params.get('attack_animation', 'walk') if params else 'idle'
    # Detener movimiento para preparar ataque
    npc.algorithm_name = 'Face'
    npc.set_algorithm(face_target=world.player, explicit_target=params['explicit_target'])
    # Guardar referencia al objetivo de ataque (si existe)
    target_pos = getattr(world, 'player_position', None) if world else None
    setattr(npc, 'attack_target', target_pos)
    # Registrar tiempo de inicio de ataque (puede usarse para temporizar 'realizo_ataque')
    npc._attack_started_at = time.time()


def action_update_throw_net(context, dt: float, params: Dict[str, Any]):
    """
    Update en LANZAR_RED:
    - Opcionalmente comprobar duración del ataque y marcar 'realizo_ataque' en el HSM externo.
    - Aquí sólo mantenemos al NPC en animación de ataque.
    """
    npc = context.npc
    world = context.world
    bounds = (world.map.width_pixels, world.map.height_pixels) if world and hasattr(world, 'map') else None
    nav_mesh = getattr(world, 'nav_mesh', None) if world else None
    obstacles = getattr(world.map, 'obstacles', None) if world and hasattr(world, 'map') else None
    margin = (npc.sprite_size[0] // 2, npc.sprite_size[1] // 2) if hasattr(npc, 'sprite_size') else (0, 0)
    npc.update_with_algorithm(dt, uses_rotation=True, bounds=bounds, margin=margin, obstacles=obstacles, nav_mesh=nav_mesh)
    if hasattr(npc, 'perform_throw_net'):
        attack_performed = npc.perform_throw_net(world)


def action_stop_throw_net(context, params: Dict[str, Any]):
    """
    Al salir de LANZAR_RED: limpiar flags de ataque y volver a animación por defecto.
    """
    npc = context.npc
    npc.algorithm_name = ''
    npc.set_algorithm()
    setattr(npc, 'is_attacking', False)
    npc.current_animation = params.get('after_animation', 'walk') if params else 'walk'
    if hasattr(npc, 'attack_target'):
        delattr(npc, 'attack_target')
    if hasattr(npc, '_attack_started_at'):
        delattr(npc, '_attack_started_at')


def action_enter_alert(context, params: Dict[str, Any]):
    """
    Al entrar en ALERTAR:
    - Emitir alerta al mundo (si la función existe).
    - Poner animación y registrar tiempo de inicio para controlar duración de la alerta.
    """
    npc = context.npc
    world = context.world
    npc.current_animation = 'idle'
    # Notificar al mundo (si implementado)
    if world and hasattr(world, 'notify_alert'):
        try:
            world.notify_alert(npc.kinematic.position, source=npc)
        except Exception:
            pass
    # Registrar inicio de alerta para poder medir duración
    setattr(npc, '_alert_started_at', time.time())


def action_update_alert(context, dt: float, params: Dict[str, Any]):
    """
    Update de ALERTAR:
    - Si la duración de la alerta se agota, el sistema externo puede emitir 'tiempo_agotado' para volver a TEJER.
    - Esta función también puede comprobar la proximidad del jugador y permitir emitir 'jugador_sigue_cerca'.
    """
    npc = context.npc
    world = context.world
    # Comprobar distancia a jugador y anotar para sistema externo
    if world and hasattr(world, 'player_position'):
        px, py = world.player_position
        nx = npc.kinematic.position.x if hasattr(npc, 'kinematic') else 0
        ny = npc.kinematic.position.y if hasattr(npc, 'kinematic') else 0
        dist = math.hypot(px - nx, py - ny)
        # Guardar distancia en npc para que el controlador externo pueda decidir emitir eventos
        setattr(npc, '_player_distance', dist)


def action_exit_alert(context, params: Dict[str, Any]):
    """
    Al salir de ALERTAR: limpiar datos temporales relacionados con la alerta.
    """
    npc = context.npc
    if hasattr(npc, '_alert_started_at'):
        delattr(npc, '_alert_started_at')
    if hasattr(npc, '_player_distance'):
        delattr(npc, '_player_distance')

# --- Acciones específicas para la Cazadora (CAZAR / EMBOSCAR / HUIR) ---
def action_enter_cazar(context, params):
    """Entrar en CAZAR: configurar algoritmo de búsqueda/persecución."""
    npc = context.npc
    npc.current_animation = 'walk'
    _set_algorithm_from_params(npc, params)

def action_update_cazar(context, dt, params):
    """Update CAZAR: delegar movimiento al algoritmo y dejar chequeos de condiciones."""
    npc = context.npc
    world = context.world
    bounds = (world.map.width_pixels, world.map.height_pixels) if world and hasattr(world, 'map') else None
    obstacles = getattr(world.map, 'obstacles', None) if world and hasattr(world, 'map') else None
    nav_mesh = getattr(world, 'nav_mesh', None) if world else None
    margin = (npc.sprite_size[0] // 2, npc.sprite_size[1] // 2) if hasattr(npc, 'sprite_size') else (0,0)
    npc.update_with_algorithm(dt, uses_rotation=False, bounds=bounds, margin=margin, obstacles=obstacles, nav_mesh=nav_mesh)

def action_exit_cazar(context, params):
    """Salir de CAZAR: limpiar algoritmo si es necesario."""
    npc = context.npc
    npc.algorithm_name = ''
    npc.set_algorithm()

# -- EMBOSCAR: Robar / HuirConTarro --
def action_enter_rob(context, params):
    """Entrar en Robar: perseguir al jugador para robarle los tarros."""
    npc = context.npc
    world = context.world
    npc.current_animation = 'walk'
    # configurar algoritmo para perseguir al jugador (FollowPath o DynamicArrive)
    alg_params = {
        'face_target': world.player,
        'explicit_target': params['explicit_target']
    }
    # target será el jugador
    npc.algorithm_name = 'Face'
    npc.set_algorithm(**alg_params)
    npc._steal_in_progress = False
    npc._steal_started_at = None
    npc._has_stolen = False

def action_update_rob(context, dt, params):
    """Update Robar: mover hacia el jugador; la detección de éxito (capturo_tarro) debe emitir evento."""
    npc = context.npc
    world = context.world
    steal_radius = float(params.get('steal_radius', 48.0)) if params else 48.0
    steal_duration = float(params.get('steal_duration', 0.6)) if params else 0.6
    player = getattr(world, 'player', None)
    if player is None:
        return
    
    try:
        # calcular distancia entre npc y player
        if hasattr(player, 'kinematic') and hasattr(player.kinematic, 'position'):
            px, py = player.kinematic.position.x, player.kinematic.position.y
        elif hasattr(player, 'rect'):
            px, py = player.rect.centerx, player.rect.centery
        elif hasattr(world, 'player_position'):
            px, py = world.player_position
        else:
            return

        if hasattr(npc, 'kinematic') and hasattr(npc.kinematic, 'position'):
            nx, ny = npc.kinematic.position.x, npc.kinematic.position.y
        elif hasattr(npc, 'rect'):
            nx, ny = npc.rect.centerx, npc.rect.centery
        else:
            return

        dist = math.hypot(px - nx, py - ny)
    except Exception:
        return
    
    # Si ya robó, no repetir
    if getattr(npc, '_has_stolen', False):
        return

    # Si estamos suficientemente cerca, iniciar la animación de robo
    if dist <= steal_radius:
        if not getattr(npc, '_steal_in_progress', False):
            # iniciar animación y temporizador
            npc._steal_in_progress = True
            npc._steal_started_at = time.time()
            npc.current_animation = params.get('steal_animation', 'idle') if params else 'idle'
            # opcional: detener movimiento para la animación
            npc.algorithm_name = ''
            npc.set_algorithm()
        else:
            # comprobar si la animación / duración finalizó
            if (time.time() - (npc._steal_started_at or 0.0)) >= steal_duration:
                # ejecutar lógica de captura (intentar API del mundo primero)
                captured = False
                try:
                    # Preferir API explícita del mundo si existe
                    transfer_fn = getattr(world, 'transfer_jar_from_player_to_npc', None)
                    if callable(transfer_fn):
                        captured = transfer_fn(player, npc)
                    else:
                        # Fallback: manipular flags comunes del player
                        carrying = bool(
                            getattr(player, 'carrying_jar', False) or
                            getattr(player, 'has_jar', False) or
                            getattr(player, 'honey_collected', 0) > 0 if hasattr(player, 'honey_collected') else False
                        )
                        if carrying:
                            # intentar decrementar conteo o limpiar flag
                            if hasattr(player, 'honey_collected') and getattr(player, 'honey_collected', 0) > 0:
                                player.honey_collected = max(0, player.honey_collected - 1)
                            if hasattr(player, 'carrying_jar'):
                                player.carrying_jar = False
                            if hasattr(player, 'has_jar'):
                                player.has_jar = False
                            # registrar en npc el tarro protegido como posición actual del npc
                            try:
                                npc.protected_jar = (nx, ny)
                            except Exception:
                                npc.protected_jar = getattr(npc, 'hsm_goal', None)
                            captured = True
                except Exception:
                    captured = False

                # Si se capturó el tarro, marcar y emitir evento para la HSM
                if captured:
                    npc._has_stolen = True
                    # añadir al world.protected_jars si existe
                    try:
                        if not hasattr(world, 'protected_jars'):
                            world.protected_jars = set()
                        world.protected_jars.add(npc.protected_jar)
                    except Exception:
                        pass
                    # emitir evento HSM para cambiar a HuirConTarro
                    try:
                        npc.emit_hsm_event('capturo_tarro')
                    except Exception:
                        pass
                else:
                    # si no se pudo capturar, resetear flags para intentar otra vez o abandonar
                    npc._steal_in_progress = False
                    npc._steal_started_at = None
                    npc.current_animation = params.get('enter_animation', 'walk') if params else 'walk'

def action_exit_rob(context, params):
    """Salir de Robar: limpiar flags si corresponde."""
    npc = context.npc
    npc.algorithm_name = ''
    npc.set_algorithm()

def action_enter_flee_with_jar(context, params):
    """Entrar en HuirConTarro: configurar algoritmo de huida con el tarro."""
    npc = context.npc
    world = context.world
    npc.current_animation = 'walk'
    webs = getattr(world, 'spider_webs', None)
    if webs is None:
        webs = getattr(world, 'honey_pots', None)
    target_pos = None
    if webs:
        print("webs:", webs)
        min_d = float('inf')
        for w in webs:
            has_pot = getattr(w, 'has_pot', None)
            if has_pot is None:
                print("has_pot es None")
                has_pot = getattr(w, 'on_web', None)
            if has_pot:
                continue
            
            wpos = getattr(w, 'initial_pos', (0,0))
            nx, ny = npc.kinematic.position

            d =  math.hypot(wpos[0] - nx, wpos[1] - ny)
            if d < min_d:
                min_d = d
                target_pos = wpos
    
    if target_pos is None:
        npc.algorithm_name = 'DynamicFlee'
        npc.set_algorithm(target=getattr(world, 'player', None), max_acceleration=80)
        npc.hsm_goal = None

        npc._flee_started_at = time.time()
        npc._flee_duration = float(params.get('flee_duration', 5.0)) if params else 5.0

        return
    
    if target_pos is not None:
        nav_mesh = getattr(world, 'nav_mesh', None)
        try:
            if nav_mesh and hasattr(nav_mesh, 'find_node_at_position') and hasattr(nav_mesh, 'nodes') and hasattr(nav_mesh, 'edges'):
                # obtener nodo de inicio y nodo objetivo
                start_node = None
                try:
                    if hasattr(npc, 'current_node_id') and npc.current_node_id is not None:
                        start_node = npc.current_node_id
                    else:
                        start_node = nav_mesh.find_node_at_position((npc.kinematic.position.x, npc.kinematic.position.y))
                except Exception:
                    start_node = None
                target_node = nav_mesh.find_node_at_position(target_pos)
                if start_node is not None and target_node is not None:
                    # calcular ruta A* (devuelve lista de node ids)
                    path_nodes = a_star_search(start_node, target_node, nav_mesh.nodes, nav_mesh.edges)
                    if path_nodes:
                        # llamar follow_path_from_nodes con nodos calculados
                        npc.follow_path_from_nodes(path_nodes, nav_mesh.nodes, explicit_target=params['explicit_target'])
                        # guardar meta HSM para condiciones posteriores
                        npc.hsm_goal = target_pos
                        return
            # Fallback: usar FollowPath simple con explicit_target tuple/pos
            npc.algorithm_name = 'FollowPath'
            npc.set_algorithm(explicit_target=params['explicit_target'])
            npc.hsm_goal = target_pos
        except Exception:
            # en caso de fallo, dejar algoritmo vacío y confiar en update para reintentar
            npc.algorithm_name = ''
            npc.set_algorithm()
            npc.hsm_goal = target_pos

def action_update_flee_with_jar(context, dt, params):
    """Update HuirConTarro: actualizar huida."""
    npc = context.npc
    world = context.world
    bounds = (world.map.width_pixels, world.map.height_pixels) if world and hasattr(world, 'map') else None
    obstacles = getattr(world.map, 'obstacles', None) if world and hasattr(world, 'map') else None
    nav_mesh = getattr(world, 'nav_mesh', None) if world else None
    margin = (npc.sprite_size[0] // 2, npc.sprite_size[1] // 2) if hasattr(npc, 'sprite_size') else (0,0)
    npc.update_with_algorithm(dt, uses_rotation=False, bounds=bounds, margin=margin, obstacles=obstacles, nav_mesh=nav_mesh)

    try:
        start = getattr(npc, '_flee_started_at', None)
        duration = getattr(npc, '_flee_duration', None)
        if start is not None and duration is not None:
            if (time.time() - start) >= float(duration):
                npc.emit_hsm_event('flee_timeout')
                npc._flee_started_at = None
                npc._flee_duration = 0.0
    except Exception:
        pass

def action_exit_flee_with_jar(context, params):
    """Salir de HuirConTarro: limpiar estado."""
    npc = context.npc
    npc.algorithm_name = ''
    npc.set_algorithm()
    npc._flee_started_at = None
    npc._flee_duration = 0.0

# -- HUIR --
def action_enter_flee(context, params):
    """Entrar en HUIR: establecer algoritmo DynamicFlee con parámetros."""
    npc = context.npc
    npc.current_animation = 'walk'
    npc._flee_started_at = time.time()
    npc._flee_duration = float(params.get('flee_duration', 5.0)) if params else 5.0
    _set_algorithm_from_params(npc, params)

def action_update_flee(context, dt, params):
    """Update HUIR: delegar movimiento al algoritmo de flee."""
    npc = context.npc
    world = context.world
    bounds = (world.map.width_pixels, world.map.height_pixels) if world and hasattr(world, 'map') else None
    obstacles = getattr(world.map, 'obstacles', None) if world and hasattr(world, 'map') else None
    nav_mesh = getattr(world, 'nav_mesh', None) if world else None
    margin = (npc.sprite_size[0] // 2, npc.sprite_size[1] // 2) if hasattr(npc, 'sprite_size') else (0,0)
    npc.update_with_algorithm(dt, uses_rotation=False, bounds=bounds, margin=margin, obstacles=obstacles, nav_mesh=nav_mesh)

def action_exit_flee(context, params):
    npc = context.npc
    npc.algorithm_name = ''
    npc.set_algorithm()

# --- Acciones específicas para la Criadora (CRIAR / BUSCAR_ZONA_SEGURA) ---
def action_enter_lay_egg(context, params):
    """Entrar en PonerHuevo: configurar animación y preparar huevo."""
    npc = context.npc
    npc.current_animation = 'idle'
    npc._egg_laid = False
    npc._egg_lay_started_at = time.time()
    npc._egg_lay_duration = float(params.get('egg_lay_duration', 2.0)) if params else 2.0

def action_update_lay_egg(context, dt, params):
    """Update PonerHuevo: comprobar si se ha completado la puesta del huevo."""
    npc = context.npc
    world = context.world
    try:
        start = getattr(npc, '_egg_lay_started_at', None)
        duration = getattr(npc, '_egg_lay_duration', None)
        if start is not None and duration is not None:
            if (time.time() - start) >= float(duration):
                if not getattr(npc, '_egg_laid', False):
                    # Lógica para crear el huevo en el mundo
                    egg_position = (npc.kinematic.position.x, npc.kinematic.position.y) if hasattr(npc, 'kinematic') else (0,0)
                    if world and hasattr(world, 'spawn_egg'):
                        world.spawn_egg(egg_position)
                    npc._egg_laid = True
                    # Emitir evento para indicar que el huevo ha sido puesto
                    npc.emit_hsm_event('huevo_puesto')
    except Exception:
        pass

def action_exit_lay_egg(context, params):
    """Salir de PonerHuevo: limpiar estado relacionado con la puesta del huevo."""
    npc = context.npc

def action_enter_protect_egg(context, params):
    """Entrar en ProtegerHuevo: configurar animación y comportamiento de protección."""
    npc = context.npc
    npc.current_animation = 'walk'
    # Intentar usar un algoritmo de patrulla/seek alrededor del tarro si se provee en params
    params['algorithm_params']['target'].kinematic.position = context.world.nav_mesh.nodes[npc.hsm_goal]
    _set_algorithm_from_params(npc, params)

def action_update_protect_egg(context, dt, params):
    """Update ProtegerHuevo: delegar movimiento al algoritmo de protección."""
    npc = context.npc
    world = context.world
    bounds = (world.map.width_pixels, world.map.height_pixels) if world and hasattr(world, 'map') else None
    obstacles = getattr(world.map, 'obstacles', None) if world and hasattr(world, 'map') else None
    nav_mesh = getattr(world, 'nav_mesh', None) if world else None
    margin = (npc.sprite_size[0] // 2, npc.sprite_size[1] // 2) if hasattr(npc, 'sprite_size') else (0,0)
    npc.update_with_algorithm(dt, uses_rotation=False, bounds=bounds, margin=margin, obstacles=obstacles, nav_mesh=nav_mesh)

def action_exit_protect_egg(context, params):
    """Salir de ProtegerHuevo: limpiar algoritmo si es necesario."""
    npc = context.npc
    npc.algorithm_name = ''
    npc._egg_laid = False
    npc._egg_lay_started_at = None
    npc._egg_lay_duration = 0.0
    npc.set_algorithm()

def action_enter_search_safe_zone(context, params):
    """Entrar en BuscarZonaSegura: configurar algoritmo para moverse a zona segura."""
    npc = context.npc
    world = context.world
    npc.current_animation = 'walk'
    min_distance = float(params.get('min_safe_distance', 200.0)) if params else 200.0
    top_candidates = int(params.get('top_candidates', 8)) if params else 8
    
    # 2) Intentar elegir nodo de nav_mesh más lejano del jugador y alcanzable por A*
    nav_mesh = getattr(world, 'nav_mesh', None)
    player = getattr(world, 'player', None)
    if nav_mesh and nav_mesh.nodes and player:
        try:
            # obtener posición del jugador
            if hasattr(player, 'kinematic') and hasattr(player.kinematic, 'position'):
                ppos = (player.kinematic.position.x, player.kinematic.position.y)
            elif hasattr(world, 'player_position'):
                ppos = tuple(world.player_position)
            else:
                ppos = None

            if ppos is not None:
                # construir lista de (node_id, node_pos, dist_to_player)
                nodes = [(nid, tuple(pos), (pos[0]-ppos[0])**2 + (pos[1]-ppos[1])**2)
                         for nid, pos in nav_mesh.nodes.items()]

                # ordenar por distancia al jugador descendente (más lejos primero)
                nodes.sort(key=lambda t: t[2], reverse=True)

                # encontrar nodo inicial del NPC (o calcular uno cercano)
                try:
                    start_node = getattr(npc, 'current_node_id', None)
                    if start_node is None:
                        start_node = nav_mesh.find_node_at_position((npc.kinematic.position.x, npc.kinematic.position.y))
                except Exception:
                    start_node = None

                # probar los primeros candidatos y verificar A* alcance
                attempts = 0
                for nid, npos, _ in nodes:
                    if attempts >= top_candidates:
                        break
                    attempts += 1
                    # opcional: evitar nodos demasiado cercanos al jugador
                    if math.hypot(npos[0] - ppos[0], npos[1] - ppos[1]) < min_distance:
                        continue
                    # si no tenemos start_node, intentar usar A* desde el nodo mas cercano al NPC
                    try:
                        if start_node is None:
                            # encontrar nodo cercano al NPC y asignarlo
                            start_node = nav_mesh.find_node_at_position((npc.kinematic.position.x, npc.kinematic.position.y))
                            if start_node is None:
                                continue
                        # intentar A*
                        path_nodes = a_star_search(start_node, nid, nav_mesh.nodes, nav_mesh.edges)
                        if path_nodes:
                            npc.follow_path_from_nodes(path_nodes, nav_mesh.nodes, explicit_target=params['explicit_target'])
                            npc.hsm_goal = nid
                            return
                    except Exception:
                        # ignorar candidatos con fallo en A*
                        continue
        except Exception:
            pass

def action_update_search_safe_zone(context, dt, params):
    """Update BuscarZonaSegura: delegar movimiento al algoritmo configurado."""
    npc = context.npc
    world = context.world
    bounds = (world.map.width_pixels, world.map.height_pixels) if world and hasattr(world, 'map') else None
    obstacles = getattr(world.map, 'obstacles', None) if world and hasattr(world, 'map') else None
    nav_mesh = getattr(world, 'nav_mesh', None) if world else None
    margin = (npc.sprite_size[0] // 2, npc.sprite_size[1] // 2) if hasattr(npc, 'sprite_size') else (0,0)
    npc.update_with_algorithm(dt, uses_rotation=False, bounds=bounds, margin=margin, obstacles=obstacles, nav_mesh=nav_mesh)

def action_exit_search_safe_zone(context, params):
    print("ENTRO A SALIR DE BUSCAR ZONA SEGURA")
    """Salir de BuscarZonaSegura: limpiar algoritmo si es necesario."""
    npc = context.npc
    npc.algorithm_name = ''
    npc.set_algorithm()