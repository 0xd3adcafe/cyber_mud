from __future__ import annotations

from entities.player import Player
from shared.i18n import t
from shared.locale_content import net_node_label_with_id
from world.ctos_events import district_event_active
from world.footprint import HIGH_FOOTPRINT_THRESHOLD, add_footprint
from world.state import WorldState
from world.wanted import add_wanted

TRACE_MAX = 100


def clear_net_session(player: Player) -> None:
    player.net_trace = 0
    player.net_connected_node = ""
    player.net_route_node = ""
    player.net_breached_nodes.clear()


def is_breached(player: Player, node_id: str) -> bool:
    return node_id in player.net_breached_nodes


def force_disconnect_netrun(
    player: Player,
    state: WorldState,
    locale: str,
    reason: str,
) -> list[str]:
    if not player.net_shell:
        return []
    key = f"net.disconnect.{reason}"
    line = t(locale, key)
    lines = [line if line != key else t(locale, "net.disconnect.generic")]
    if reason == "trace":
        lines.extend(_trace_breach_penalty(player, state, locale))
    player.net_shell = False
    clear_net_session(player)
    return lines


def _trace_breach_penalty(player: Player, state: WorldState, locale: str) -> list[str]:
    lines: list[str] = []
    if player.ram > 0:
        player.ram = max(0, player.ram - 1)
        lines.append(t(locale, "net.trace.penalty_ram"))
    lines.extend(add_footprint(player, 15, state, locale, reason="trace"))
    lines.extend(add_wanted(player, 1, locale))
    return lines


def trace_rate_per_tick(player: Player, state: WorldState) -> int:
    if not player.net_shell:
        return 0
    rate = 1
    if player.net_connected_node:
        rate += 2
    room = state.world.room(player.room_id)
    if room and room.district == "corpo":
        rate += 1
    if player.footprint >= HIGH_FOOTPRINT_THRESHOLD:
        rate += 2
    elif player.footprint >= 40:
        rate += 1
    if player.wanted_level >= 2:
        rate += 1
    if room and room.district and district_event_active(state, room.district, "blackout"):
        rate += 2
    if player.faction == "dedsec":
        rate = max(1, rate - 1)
    if player.intelligence >= 6:
        rate = max(1, rate - 1)
    if player.net_route_node:
        rate = max(1, rate - 2)
        if player.ram > 0:
            player.ram -= 1
    node = state.world.net_node(player.net_connected_node) if player.net_connected_node else None
    if node and getattr(node, "security", "") == "high":
        rate += 1
    return max(1, rate)


def tick_net_trace(player: Player, state: WorldState) -> list[str]:
    if not player.net_shell:
        return []
    gain = trace_rate_per_tick(player, state)
    before = player.net_trace
    player.net_trace = min(TRACE_MAX, player.net_trace + gain)
    if player.net_trace >= TRACE_MAX:
        return force_disconnect_netrun(player, state, player.locale, "trace")
    if player.net_trace > before and player.net_trace >= 80:
        return [t(player.locale, "net.trace.critical", value=str(player.net_trace))]
    return []


def probe_trace_bump(player: Player, amount: int = 2) -> None:
    if player.net_shell:
        player.net_trace = min(TRACE_MAX, player.net_trace + amount)


def breach_trace_bump(player: Player, amount: int = 8) -> None:
    if player.net_shell:
        player.net_trace = min(TRACE_MAX, player.net_trace + amount)


def connect_node(
    player: Player,
    state: WorldState,
    node_id: str,
    locale: str,
) -> list[str]:
    node = state.world.net_node(node_id)
    if node is None:
        return [t(locale, "net.no_node")]
    in_room = any(n.id == node_id for n in state.world.net_nodes_in_room(player.room_id))
    routed = player.net_route_node == node_id
    if not in_room and not routed:
        return [t(locale, "net.connect.out_of_range", target=net_node_label_with_id(node, locale))]
    player.net_connected_node = node_id
    probe_trace_bump(player, 3)
    return [t(locale, "net.connect.ok", target=net_node_label_with_id(node, locale))]


def breach_node(
    ctx,
    node_id: str,
) -> list[str]:
    from commands.lock_helpers import check_entity_lock

    player = ctx.player
    state = ctx.state
    locale = player.locale
    node = state.world.net_node(node_id)
    if node is None:
        return [t(locale, "net.no_node")]
    if player.net_connected_node != node_id:
        return [t(locale, "net.breach.not_connected", target=net_node_label_with_id(node, locale))]
    if is_breached(player, node_id):
        return [t(locale, "net.breach.already", target=net_node_label_with_id(node, locale))]

    lock_denial = check_entity_lock(ctx, node, "hack")
    if lock_denial is not None:
        return lock_denial

    ram_cost = 2 if getattr(node, "security", "") == "high" else 1
    if player.ram < ram_cost:
        return [t(locale, "net.no_ram")]
    player.ram -= ram_cost
    player.net_breached_nodes.append(node_id)
    breach_trace_bump(player, 10 if getattr(node, "security", "") == "high" else 6)
    from world.life import gain_fatigue

    gain_fatigue(player, "netrun")
    return [t(locale, "net.breach.ok", target=net_node_label_with_id(node, locale))]


def exploit_node_rewards(
    player: Player,
    state: WorldState,
    node_id: str,
    locale: str,
) -> list[str]:
    node = state.world.net_node(node_id)
    if node is None:
        return [t(locale, "net.no_node")]
    if not is_breached(player, node_id):
        return [t(locale, "net.exploit.not_breached", target=net_node_label_with_id(node, locale))]
    label = net_node_label_with_id(node, locale)
    lines = [t(locale, "net.exploit.ok", target=label)]
    from world.progression import award_xp

    lines.extend(award_xp(player, 15, locale))
    from world.proficiencies import award_proficiency_xp

    lines.extend(
        award_proficiency_xp(
            player,
            "breach_protocol",
            18,
            locale,
            proficiencies=state.world.proficiencies,
        )
    )
    from world.street_cred import STREET_CRED_PER_HACK, award_street_cred

    lines.extend(award_street_cred(player, STREET_CRED_PER_HACK, locale))
    from world.reactions import reputation_from_net_hack, shift_reputation

    lines.extend(shift_reputation(player, reputation_from_net_hack(), locale))
    from world.quests import advance_quest_on_hack

    lines.extend(advance_quest_on_hack(player, state, node_id, locale))
    from world.footprint import CORPO_HACK_FOOTPRINT, add_footprint, corpo_footprint_bonus

    lines.extend(
        add_footprint(
            player,
            corpo_footprint_bonus(state, player.room_id, CORPO_HACK_FOOTPRINT),
            state,
            locale,
            reason="hack",
        )
    )
    probe_trace_bump(player, 4)
    return lines


def auto_hack_pipeline(ctx, node_id: str) -> list[str]:
    player = ctx.player
    state = ctx.state
    locale = player.locale
    lines: list[str] = []
    if player.net_connected_node != node_id:
        lines.extend(connect_node(player, state, node_id, locale))
        if player.net_connected_node != node_id:
            return lines
    if not is_breached(player, node_id):
        lines.extend(breach_node(ctx, node_id))
        if not is_breached(player, node_id):
            return lines
    lines.extend(exploit_node_rewards(player, state, node_id, locale))
    return lines


def route_via_mesh(
    player: Player,
    state: WorldState,
    target_id: str,
    locale: str,
) -> list[str]:
    target = state.world.net_node(target_id)
    if target is None:
        return [t(locale, "net.no_node")]
    origin_id = player.net_connected_node
    if not origin_id:
        room_nodes = [n.id for n in state.world.net_nodes_in_room(player.room_id)]
        if not room_nodes:
            return [t(locale, "net.route.no_local")]
        origin_id = room_nodes[0]
    origin = state.world.net_node(origin_id)
    if origin is None or target_id not in origin.links:
        return [t(locale, "net.route.no_link", target=net_node_label_with_id(target, locale))]
    from world.ctos_mesh import hop_lock_denial

    denial = hop_lock_denial(player, state, origin_id, target_id, locale, action="probe")
    if denial:
        return denial
    if player.ram < 1:
        return [t(locale, "net.no_ram")]
    player.ram -= 1
    player.net_route_node = target_id
    player.net_connected_node = target_id
    return [
        t(
            locale,
            "net.route.ok",
            target=net_node_label_with_id(target, locale),
        )
    ]


def cat_file(player: Player, state: WorldState, file_key: str, locale: str) -> list[str]:
    node_id = player.net_connected_node
    if not node_id or not is_breached(player, node_id):
        return [t(locale, "net.cat.not_breached")]
    node = state.world.net_node(node_id)
    if node is None:
        return [t(locale, "net.no_node")]
    content = node.file_content(file_key, locale)
    if not content:
        return [t(locale, "net.cat.missing", file=file_key)]
    return [t(locale, "net.cat.header", file=file_key), "", content]


def cover_traces(player: Player, state: WorldState, locale: str) -> list[str]:
    if not player.net_connected_node or not is_breached(player, player.net_connected_node):
        return [t(locale, "net.cover.not_breached")]
    if player.ram < 1:
        return [t(locale, "net.no_ram")]
    player.ram -= 1
    before = player.net_trace
    player.net_trace = max(0, player.net_trace - 20)
    lines = [t(locale, "net.cover.ok", reduced=str(before - player.net_trace))]
    if player.footprint > 0:
        player.footprint = max(0, player.footprint - 5)
        lines.append(t(locale, "net.cover.footprint"))
    return lines