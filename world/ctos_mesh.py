from __future__ import annotations

from entities.player import Player
from shared.i18n import t
from shared.locale_content import net_node_label_with_id
from shared.locks import evaluate_lock
from world.state import WorldState


def mesh_link_key(node_a: str, node_b: str) -> str:
    a, b = sorted((node_a, node_b))
    return f"{a}<->{b}"


def discover_mesh_in_room(player: Player, state: WorldState, room_id: str) -> list[str]:
    new_lines: list[str] = []
    locale = player.locale
    for node in state.world.net_nodes_in_room(room_id):
        for link_id in node.links:
            key = mesh_link_key(node.id, link_id)
            if key in player.discovered_net_links:
                continue
            lock_expr = node.link_locks.get(link_id, "")
            if lock_expr and not evaluate_lock(lock_expr, player, state):
                continue
            player.discovered_net_links.append(key)
            target = state.world.net_node(link_id)
            if target:
                label = net_node_label_with_id(target, locale)
                new_lines.append(t(locale, "ctos.mesh.discovered", link=label))
    return new_lines


def format_mesh_map_lines(player: Player, state: WorldState, locale: str) -> list[str]:
    if not player.discovered_net_links:
        return []
    lines = ["", t(locale, "ctos.mesh.header")]
    for key in sorted(player.discovered_net_links):
        a_id, b_id = key.split("<->", 1)
        node_a = state.world.net_node(a_id)
        node_b = state.world.net_node(b_id)
        if node_a and node_b:
            lines.append(
                t(
                    locale,
                    "ctos.mesh.line",
                    a=net_node_label_with_id(node_a, locale),
                    b=net_node_label_with_id(node_b, locale),
                )
            )
    return lines


def hop_lock_denial(
    player: Player,
    state: WorldState,
    from_node_id: str,
    to_node_id: str,
    locale: str,
    *,
    action: str = "probe",
) -> list[str] | None:
    node = state.world.net_node(from_node_id)
    if node is None or to_node_id not in node.links:
        return None
    expr = node.link_locks.get(to_node_id, "")
    if not expr or evaluate_lock(expr, player, state):
        return None
    key = f"ctos.mesh.lock_{action}"
    msg = t(locale, key)
    return [msg if msg != key else t(locale, "lock.denied")]