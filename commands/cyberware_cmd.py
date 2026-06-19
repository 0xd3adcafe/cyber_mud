from __future__ import annotations

from commands.registry import CommandContext, ok, player_meta, register
from shared.cyberware_slots import CYBERWARE_SLOTS, slot_label
from shared.i18n import t
from commands.install import implant_label


def handle(ctx: CommandContext):
    locale = ctx.player.locale
    lines = [t(locale, "cyberware.header"), ""]
    for slot in CYBERWARE_SLOTS:
        implant_id = ctx.player.cyberware.get(slot)
        if implant_id:
            implant = ctx.state.world.implant(implant_id)
            label = implant_label(implant, locale) if implant else implant_id
            desc = ""
            if implant:
                desc = implant.description_zh if locale == "zh" else (implant.description_en or implant.description_zh)
            lines.append(t(locale, "cyberware.installed", slot=slot_label(slot, locale), name=label, desc=desc or ""))
        else:
            lines.append(t(locale, "cyberware.empty", slot=slot_label(slot, locale)))
    lines.append("")
    lines.append(t(locale, "cyberware.hint"))
    return ok(lines, meta=player_meta(ctx))


register("cyberware", handle)
register("chrome", handle)