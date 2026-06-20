from __future__ import annotations

from entities.player import Player


def migrate_vehicle_fields(player: Player) -> None:
    if player.vehicle_id and player.vehicle_id not in player.vehicles:
        player.vehicles.append(player.vehicle_id)
    if not player.active_vehicle and player.vehicle_id:
        player.active_vehicle = player.vehicle_id


def owned_vehicle_ids(player: Player) -> list[str]:
    migrate_vehicle_fields(player)
    return list(player.vehicles)


def active_vehicle_id(player: Player) -> str:
    migrate_vehicle_fields(player)
    if player.active_vehicle and player.active_vehicle in player.vehicles:
        return player.active_vehicle
    return player.vehicles[0] if player.vehicles else ""


def add_vehicle(player: Player, vehicle_id: str) -> None:
    migrate_vehicle_fields(player)
    if vehicle_id not in player.vehicles:
        player.vehicles.append(vehicle_id)
    if not player.active_vehicle:
        player.active_vehicle = vehicle_id
    player.vehicle_id = vehicle_id