"""
Implementación compacta y declarativa de una Máquina de Estados Jerárquica (HSM).
- Definición de estados con on_enter/on_exit/on_update y transiciones por evento.
- Maneja estado inicial y opción de historia (shallow).
- Resolución de rutas de destino por nombre (relativo o absoluto desde root).
- Integración mediante Context(npc, world).
"""
from typing import Callable, Dict, Optional, Any, List
from imports.npc import hsm_actions 
from imports.npc import hsm_conditions
from imports.player.player import Player

class Context:
	"""Contexto que se pasa a las acciones: referencia al NPC y al mundo."""
	def __init__(self, npc, world=None):
		self.npc = npc
		self.world = world


class StateDef:
	"""Definición de un estado en la HSM."""
	def __init__(
		self,
		name: str,
		on_enter = None,
		on_exit = None,
		on_update = None,
		transitions = None,
		substates = None,
		initial = None,
		history= False,
		params = None
	):
		# Nombre del estado (único por subtree preferible)
		self.name = name
		# Acciones al entrar/salir/actualizar (reciben Context y params)
		self.on_enter = on_enter
		self.on_exit = on_exit
		self.on_update = on_update
		# Mapa evento -> destino (nombre o ruta)
		self.transitions = transitions or {}
		# Subestados anidados
		self.substates = substates or {}
		# Subestado inicial de este compuesto (si existe)
		self.initial = initial
		# Si debe recordar el subestado previo (shallow history)
		self.history = history
		# Parámetros asociados al estado (se pasan a acciones)
		self.params = params or {}
		# Referencia al padre (se completa al enlazar)
		self.parent: Optional[StateDef] = None
		# Registro de última subruta activa si history=True
		self._last_active: Optional[str] = None


class HSM:
	"""Motor minimal de HSM que soporta entrada/salida, transiciones y actualización por frame."""
	def __init__(self, root: StateDef, context: Context):
		# Nodo raíz de la HSM
		self.root = root
		# Contexto con npc/world
		self.context = context
		# Camino activo desde la raíz hasta el estado hoja activo
		self.active_path: List[StateDef] = []
		# Enlazar padres y establecer estado inicial
		self._link_parents(self.root, None)
		print("HSM inicializada. Entrando en estado inicial...")
		self._enter_initial(self.root)
	
	def _active_path_str(self) -> str:
		return "/" .join([s.name for s in self.active_path]) if self.active_path else "(empty)"
	# ---------- Evaluación de condiciones ----------
	def _evaluate_conditions(self) -> bool:
		"""
		Recorre desde el estado hoja activo hacia arriba y evalúa 'condition_checks'
		definidos en state.params. 
		Si alguna condición se cumple emite el evento asociado y devuelve True.
		"""
		if not self.active_path:
			return False
		# Empezar desde la hoja más específica hacia la raíz
		for node in reversed(self.active_path):
			cond_map = node.params.get('condition_checks') if node.params else None
			if not cond_map:
				continue
			for cond_name, ev in cond_map.items():
				# permitir dos formas: ev = 'evento' o ev = ('evento', params_for_condition)
				if isinstance(ev, (list, tuple)) and len(ev) >= 1:
					event_name = ev[0]
					cond_params = ev[1] if len(ev) > 1 else {}
				else:
					event_name = ev
					cond_params = node.params.get('condition_params', {})
				# Evaluar la condición usando hsm_conditions
				if hsm_conditions.evaluate_condition(cond_name, self.context, cond_params):
					# Emitir evento y detener evaluación (prioridad a la condición más específica)
					self.handle_event(event_name) #type:ignore
					return True
		return False

	# ---------- Construcción / enlace ----------
	def _link_parents(self, node: StateDef, parent: Optional[StateDef]):
		"""Enlaza referencias parent para cada subestado recursivamente."""
		node.parent = parent
		for child in node.substates.values():
			self._link_parents(child, node)

	# ---------- Entradas y salidas ----------
	def _push_state(self, state: StateDef):
		"""Entra en un estado: ejecutar on_enter y añadir a active_path."""
		if state.on_enter:
			state.on_enter(self.context, state.params)
		self.active_path.append(state)
		print(f"[HSM] enter -> {self._active_path_str()}")

	def _pop_state(self) -> Optional[StateDef]:
		"""Sale del estado más profundo: ejecutar on_exit y devolverlo."""
		if not self.active_path:
			return None
		s = self.active_path.pop()
		if s.on_exit:
			s.on_exit(self.context, s.params)
		# Si el padre quiere historia, registrar el subestado salido
		if s.parent and s.parent.history:
			s.parent._last_active = s.name
		print(f"[HSM] exit -> {self._active_path_str()}")
		return s

	def _pop_to(self, ancestor: Optional[StateDef]):
		"""Salir desde el estado más profundo hasta (pero sin incluir) el ancestro dado."""
		while self.active_path and self.active_path[-1] is not ancestor:
			self._pop_state()

	# ---------- Inicialización de estado compuesto ----------
	def _enter_initial(self, node: StateDef):
		"""
		Entra recursivamente por el subestado inicial o por la historia (si está configurada).
		Llama a on_enter en cada nivel visitado hasta alcanzar una hoja.
		"""
		# Entrar en el nodo actual
		self._push_state(node)
		# Determinar el siguiente hijo a entrar
		target_name = None
		if node.history and node._last_active:
			target_name = node._last_active
		elif node.initial:
			target_name = node.initial
		# Si hay un hijo objetivo, entrar recursivamente
		if target_name:
			child = node.substates.get(target_name)
			if child:
				self._enter_initial(child)
		# Si no hay subestado, queda como hoja activa

	# ---------- Resolución y utilidades ----------
	def _find_in_tree(self, node: StateDef, name: str) -> Optional[StateDef]:
		"""Buscar un estado por nombre en el subárbol del nodo dado (búsqueda DFS)."""
		if node.name == name:
			return node
		for c in node.substates.values():
			r = self._find_in_tree(c, name)
			if r:
				return r
		return None

	def _resolve_path(self, path: str, relative_to: StateDef) -> Optional[StateDef]:
		"""
		Resolver destino de transición.
		- Si path contiene '/', se interpreta como ruta absoluta desde root: 'Root/A/B'.
		- Si path es nombre simple, se busca primero en el subárbol de relative_to hacia arriba.
		- Si no se encuentra, se busca en todo el árbol desde root (fallback).
		"""
		# Ruta absoluta desde root
		if '/' in path:
			parts = path.strip('/').split('/')
			node = self.root
			for part in parts:
				node = node.substates.get(part)
				if node is None:
					return None
			return node
		# Buscar hacia arriba (primer intento: relativos en ancestros)
		node = relative_to
		while node:
			candidate = self._find_in_tree(node, path)
			if candidate:
				return candidate
			node = node.parent
		# Fallback: buscar en todo el árbol
		return self._find_in_tree(self.root, path)

	def _find_lca(self, a: StateDef, b: StateDef) -> Optional[StateDef]:
		"""Encontrar ancestro común mínimo entre dos nodos usando active_path como referencia."""
		# Construir conjunto de ancestros de a
		ancestors = set()
		node = a
		while node:
			ancestors.add(node)
			node = node.parent
		# Subir desde b hasta encontrar primer ancestro en el conjunto
		node = b
		while node:
			if node in ancestors:
				return node
			node = node.parent
		return self.root

	# ---------- Manejo de eventos y transiciones ----------
	def handle_event(self, event: str) -> bool:
		"""
		Manejar un evento: buscar transición desde el estado hoja hacia arriba.
		Devuelve True si se ejecutó alguna transición.
		"""
		if not self.active_path:
			return False
		node = self.active_path[-1]
		while node:
			dest_path = node.transitions.get(event)
			if dest_path:
				self._transition(node, dest_path)
				return True
			node = node.parent
		return False

	def _transition(self, source: StateDef, dest_path: str):
		"""
		Ejecutar una transición:
		- Resolver destino.
		- Calcular LCA.
		- Salir hasta el LCA (ejecutando on_exit).
		- Ejecutar la acción de transición implícita (aquí se delega a on_enter del destino).
		- Entrar por la rama destino hasta su hoja inicial/historia.
		"""
		dest = self._resolve_path(dest_path, source)
		if not dest:
			return
		lca = self._find_lca(source, dest)
		# Salir hasta LCA (sin incluir)
		self._pop_to(lca)
		# Construir lista de nodos a entrar desde LCA hacia dest
		stack_to_enter: List[StateDef] = []
		node = dest
		while node is not lca:
			if node:
				stack_to_enter.append(node)
				node = node.parent
		# Entrar en orden desde el primer hijo hasta el destino
		for s in reversed(stack_to_enter):
			self._push_state(s)
		# Si el destino es un compuesto, entrar en su initial/historia
		# (usar _enter_initial solo para el destino si tiene hijos)
		if dest.substates:
			# Si ya estamos dentro del destino (push lo hizo), proceder a inicialización de hijos
			# Si el destino tiene initial o history, recorrerlos
			target_name = None
			if dest.history and dest._last_active:
				target_name = dest._last_active
			elif dest.initial:
				target_name = dest.initial
			if target_name:
				child = dest.substates.get(target_name)
				if child:
					self._enter_initial(child)

	# ---------- Actualización por frame ----------
	def update(self, dt: float):
		"""
		Llamar on_update del estado más interno activo (si existe).
		- dt: delta time en segundos.
		"""
		if not self.active_path:
			return
		self._evaluate_conditions()
		leaf = self.active_path[-1]
		if leaf.on_update:
			leaf.on_update(self.context, dt, leaf.params)

def build_tejedora_hsm(context: Context) -> HSM:
    """
    Construye la HSM para el rol 'TEJEDORA' según el diagrama en context/HSM/HSM-tejedora.md.
    Estructura:
      Root
        - TEJER (compuesto)
            - BuscarTarrosSinRed (inicial)
            - Proteger
        - LANZAR_RED
        - ALERTAR
    """
    # Subestado: Proteger (vigilar tarro protegido)
    proteger = StateDef(
        name='Proteger',
        on_enter=hsm_actions.action_enter_protect,
        on_exit=hsm_actions.action_exit_protect,
        on_update=hsm_actions.action_update_protect,
        transitions={
			'encuentra_jugador': 'LANZAR_RED', 
			'recibe_dano': 'LANZAR_RED',
			'tarro_perdido': 'BuscarTarrosSinRed'
		},
        params={
			'algorithm_name': 'DynamicSeek', 
			'algorithm_params': {
				'target': Player("Target", 0,0,0),
				'max_acceleration': 150
			},
			'condition_checks': {
				'player_near': "encuentra_jugador",
				'received_damage': "recibe_dano",
				'protected_jar_lost': "tarro_perdido",
			}
		}
    )

    # Subestado inicial: Buscar Tarros Sin Red
    buscar_tarros = StateDef(
        name='BuscarTarrosSinRed',
        on_enter=hsm_actions.action_enter_search_jars,
        on_exit=hsm_actions.action_exit_search_jars,
        on_update=hsm_actions.action_update_search_jars,
        transitions={'encuentra_tarro': 'Proteger', 'encuentra_jugador': 'LANZAR_RED', 'recibe_dano': 'LANZAR_RED'},
        params={
			'explicit_target': Player("Target", 0, 0, 0),
			'condition_checks': {
				'reached_goal': "encuentra_tarro",
				'player_near': "encuentra_jugador",
				'received_damage': "recibe_dano",
			}
		}
    )

    # Estado compuesto TEJER con subestados BuscarTarrosSinRed (inicial) y Proteger
    tejer = StateDef(
        name='TEJER',
        substates={'BuscarTarrosSinRed': buscar_tarros, 'Proteger': proteger},
        initial='BuscarTarrosSinRed',
        history=True  # recordar subestado previo al volver a TEJER
    )

    # Estado LANZAR_RED (ataque): preparar y lanzar la red
    lanzar_red = StateDef(
        name='LANZAR_RED',
        on_enter=hsm_actions.action_start_throw_net,
        on_exit=hsm_actions.action_stop_throw_net,
        on_update=hsm_actions.action_update_throw_net,
        transitions={'jugador_cae_en_red': 'ALERTAR', 'realizo_ataque': 'TEJER'},
        params={
			'net_range': 200,
			'explicit_target': Player("Target", 0, 0, 0),
			'condition_checks':{
				'applied_attack': "realizo_ataque",
			}
		}
    )

    alertar = StateDef(
        name='ALERTAR',
        on_enter=hsm_actions.action_enter_alert,
        on_exit=hsm_actions.action_exit_alert,
        on_update=hsm_actions.action_update_alert,
        transitions={'jugador_sigue_cerca': 'LANZAR_RED', 'tiempo_agotado': 'TEJER'},
        params={
			'alert_duration': 5.0,
			'condition_checks':{
				'alert_time_expired': "tiempo_agotado",
			}
		}
    )

    # Nodo raíz con la HSM completa
    root = StateDef(
        name='Root',
        substates={'TEJER': tejer, 'LANZAR_RED': lanzar_red, 'ALERTAR': alertar},
        initial='TEJER'
    )

    return HSM(root, context)

def build_cazadora_hsm(context: Context) -> HSM:
	"""
	Construye la HSM para el rol 'CAZADORA' según context/HSM/HSM-cazadora.md.
    Estructura:
      Root
        - CAZAR
        - EMBOSCAR (compuesto)
			- Robar (inicial)
			- HuirConTarro
        - LANZAR_RED (reutiliza acciones de tejedora)
        - HUIR
	"""
	robar = StateDef(
		name='Robar',
		on_enter=hsm_actions.action_enter_rob,
		on_exit=hsm_actions.action_exit_rob,
		on_update=hsm_actions.action_update_rob,
		transitions={'capturo_tarro': 'HuirConTarro'},
		params={
			'explicit_target': Player("Target", 0, 0, 0),
		}
	)

	huir_con_tarro = StateDef(
		name='HuirConTarro',
		on_enter=hsm_actions.action_enter_flee_with_jar,
		on_exit=hsm_actions.action_exit_flee_with_jar,
		on_update=hsm_actions.action_update_flee_with_jar,
		transitions={
			'guardo_tarro': 'CAZAR',
			'flee_timeout': 'CAZAR'
		},
		params={
			'explicit_target': Player("Target", 0, 0, 0),
			'algorithm_name': 'FollowPath',
            'algorithm_params': {},
			'condition_checks': {
				'reached_goal': "guardo_tarro",
			}
		}
	)

	emboscar = StateDef(
		name='EMBOSCAR',
		substates={'Robar': robar, 'HuirConTarro': huir_con_tarro},
		initial='Robar',
		history=False
	)

	cazar = StateDef(
		name='CAZAR',
		on_enter=hsm_actions.action_enter_cazar,
		on_exit=hsm_actions.action_exit_cazar,
		on_update=hsm_actions.action_update_cazar,
		transitions={
			'encontro_jugador_con_tarro': 'EMBOSCAR',
			'encontro_jugador_sin_tarro': 'LANZAR_RED',
			'recibe_dano': 'LANZAR_RED',
			'recibe_dano_critico': 'HUIR'
		},
		params={
			'algorithm_name': 'DynamicArrive',
			'algorithm_params': {
				'target': getattr(context.world, 'player', Player("Target", 0,0,0)),
				'max_acceleration': 150,
				'max_speed': 100,
				'target_radius': 5,
				'slow_radius': 100,
				'time_to_target': 0.1
			},
			'condition_checks': {
				'player_near_with_honey': "encontro_jugador_con_tarro",
				'player_near_no_honey': "encontro_jugador_sin_tarro",
				'received_damage': "recibe_dano",
			},
			'condition_params':{
				'radius': 150,
				'critical_threshold': 25,
			}
		}
	)

	lanzar_red = StateDef(
		name='LANZAR_RED',
		on_enter=hsm_actions.action_start_throw_net,
		on_exit=hsm_actions.action_stop_throw_net,
		on_update=hsm_actions.action_update_throw_net,
		transitions={
			'jugador_huye': 'CAZAR',
            'recibe_dano_critico': 'HUIR'
		},
		params={
            'net_range': 200,
            'explicit_target': Player("Target", 0, 0, 0),
            'condition_checks': { 
				'critical_damage': 'recibe_dano_critico',
				'player_far': 'jugador_huye'
			}
        }
	)

	huir = StateDef(
		name='HUIR',
		on_enter=hsm_actions.action_enter_flee,
		on_exit=hsm_actions.action_exit_flee,
		on_update=hsm_actions.action_update_flee,
		transitions={'pasa_peligro': 'CAZAR'},
		params={
			'algorithm_name': 'DynamicFlee', 
			'algorithm_params': {
				'target': getattr(context.world, 'player', Player("Target", 0,0,0)),
				'max_acceleration': 50
			},
            'condition_checks': {
                'flee_time_expired': 'pasa_peligro'
            },
            'condition_params': {
                'duration': 6.0
            }
		}
	)

	root = StateDef(
		name='Root',
		substates={'CAZAR': cazar, 'EMBOSCAR': emboscar, 'LANZAR_RED': lanzar_red, 'HUIR': huir},
		initial='CAZAR'
	)

	return HSM(root, context)

def build_criadora_hsm(context: Context) -> HSM:
	"""
	Construye la HSM para el rol 'CRIADORA' según context/HSM/HSM-criadora.md.
	Estructura:
	  Root
		- BUSCAR_ZONA_SEGURA
		- CRIAR (compuesto):
			- PonerHuevo (inicial)
			- ProtegerHuevo
		- HUIR
	"""
	poner_huevo = StateDef(
		name='PonerHuevo',
		on_enter=hsm_actions.action_enter_lay_egg,
		on_exit=hsm_actions.action_exit_lay_egg,
		on_update=hsm_actions.action_update_lay_egg,
		transitions={
			'huevo_puesto': 'ProtegerHuevo',
			'enemigo_en_zona': 'HUIR',
		},
		params={
			'condition_checks': {
				'player_near': 'enemigo_en_zona',
			}
		}
	)

	proteger_huevo = StateDef(
		name='ProtegerHuevo',
		on_enter=hsm_actions.action_enter_protect_egg,
		on_exit=hsm_actions.action_exit_protect_egg,
		on_update=hsm_actions.action_update_protect_egg,
		transitions={
			'enemigo_en_zona': 'HUIR',
			'nacio_cria': 'BUSCAR_ZONA_SEGURA'
		},
		params={
			'algorithm_name': 'DynamicSeek', 
			'algorithm_params': {
				'target': Player("Target", 0,0,0),
				'max_acceleration': 150
			},
			'condition_checks': {
				'player_near': 'enemigo_en_zona',
				'offspring_born': 'nacio_cria'
			}
		}
	)

	criar = StateDef(
		name='CRIAR',
		substates={'PonerHuevo': poner_huevo, 'ProtegerHuevo': proteger_huevo},
		initial='PonerHuevo',
		history=False
	)

	buscar_zona_segura = StateDef(
		name='BUSCAR_ZONA_SEGURA',
		on_enter=hsm_actions.action_enter_search_safe_zone,
		on_exit=hsm_actions.action_exit_search_safe_zone,
		on_update=hsm_actions.action_update_search_safe_zone,
		transitions={'encuentra_zona': 'CRIAR'},
		params={
			'explicit_target': Player("Target", 0,0,0),
			'condition_checks': {
				'found_safe_zone': 'encuentra_zona'
			}
		}
	)

	huir = StateDef(
		name='HUIR',
		on_enter=hsm_actions.action_enter_flee,
		on_exit=hsm_actions.action_exit_flee,
		on_update=hsm_actions.action_update_flee,
		transitions={'flee_time_expired': 'BUSCAR_ZONA_SEGURA'},
		params={
			'algorithm_name': 'DynamicFlee',
			'algorithm_params': {
				'target': getattr(context.world, 'player', Player("Target", 0,0,0)),
				'max_acceleration': 50
			},
			'condition_checks': {
				'flee_time_expired': 'flee_time_expired'
			},
			'condition_params': {
				'duration': 6.0
			}
		}
	)

	root = StateDef(
		name='Root',
		substates={'BUSCAR_ZONA_SEGURA': buscar_zona_segura, 'CRIAR': criar, 'HUIR': huir},
		initial='BUSCAR_ZONA_SEGURA'
	)

	return HSM(root, context)