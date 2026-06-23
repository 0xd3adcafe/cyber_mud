#!/usr/bin/env python3
"""One-shot helper: normalize mature_zh.yaml to Taiwan Traditional (繁體)."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from shared.zh_traditional_audit import normalize_tw_text

MATURE_ZH = ROOT / "data" / "mature" / "locale" / "mature_zh.yaml"

_MEASURED_NOIR = {
    "flirt": '*打量一眼* 「{persona} 很上鏡，{player}。」',
    "flirt_2": "「人潮散了再留下。」",
    "flirt_3": '*隱私場低鳴* 「階段三才開門。」',
    "spend": "時間摺疊——畫面淡出。",
    "spend_2": ">呼吸與暗影。畫面淡出。",
}

_QUIET_SCENE = {
    "body": "*{player}——私密熱度* 畫面暗示淡出。",
    "stage4": ">階段四——沒有目擊者。",
}

_FILTHY_SCENE = {
    "body": "*{player}——淫靡熱度* 畫面暗示淡出。",
    "stage4": ">階段四——沒有目擊者。",
}

_LEWD_ROMANCE = {
    "flirt": '*飢渴的一瞥* 「{persona} 讓我濕了，{player}。」',
    "flirt_2": "「靠近——階段二買你的手。」",
    "flirt_3": '*呼吸貼上你頸側* 「別停在第三階段。」',
    "spend": "身體撞在一起——畫面淡出。",
    "spend_2": ">脈搏很響。畫面淡出。",
}

_OVERRIDES: dict[str, str] = {}


def _add_measured_noir(prefix: str) -> None:
    for suffix, text in _MEASURED_NOIR.items():
        _OVERRIDES[f"mature.noir.romance.{prefix}_{suffix}"] = text


def _add_quiet_scene(prefix: str) -> None:
    _OVERRIDES[f"mature.noir.scene.{prefix}"] = _QUIET_SCENE["body"]
    _OVERRIDES[f"mature.noir.scene.{prefix}_4"] = _QUIET_SCENE["stage4"]


def _add_low_whisper(prefix: str) -> None:
    _OVERRIDES[f"mature.noir.whisper.{prefix}"] = '*低聲* 「{player} 私語：{message}」'


def _add_lewd_romance(prefix: str) -> None:
    for suffix, text in _LEWD_ROMANCE.items():
        _OVERRIDES[f"mature.lewd.romance.{prefix}_{suffix}"] = text


def _add_filthy_scene(prefix: str) -> None:
    _OVERRIDES[f"mature.lewd.scene.{prefix}"] = _FILTHY_SCENE["body"]
    _OVERRIDES[f"mature.lewd.scene.{prefix}_4"] = _FILTHY_SCENE["stage4"]


def _add_lewd_whisper(prefix: str) -> None:
    _OVERRIDES[f"mature.lewd.whisper.{prefix}"] = (
        '*一顫* 「{player} 低吼：{message}——我感受到了。」'
    )


for npc in (
    "amara",
    "selene",
    "haejin",
    "yoojin",
    "eunbi",
    "misato",
    "nari",
    "vera",
    "seojin",
):
    _add_measured_noir(npc)

for npc in (
    "kabuki_fixer_amara",
    "kabuki_artist_selene",
    "kabuki_idol_haejin",
    "watson_flatmate_yoojin",
    "watson_flatmate_eunbi",
    "little_china_host_misato",
    "shrine_net_shaman_nari",
    "tyrell_liaison_vera",
    "tyrell_gene_thief_seojin",
):
    _add_quiet_scene(npc)

for npc in (
    "kabuki_fixer_amara",
    "kabuki_artist_selene",
    "kabuki_idol_haejin",
    "watson_flatmate_yoojin",
    "watson_flatmate_eunbi",
    "little_china_host_misato",
    "shrine_net_shaman_nari",
    "tyrell_liaison_vera",
    "tyrell_gene_thief_seojin",
):
    _add_low_whisper(npc)

for npc in (
    "jenna",
    "neon",
    "airi",
    "rin",
    "meera",
    "sayaka",
    "wintr",
):
    _add_lewd_romance(npc)

for npc in (
    "kabuki_streamer_jenna",
    "kabuki_brat_neon",
    "kabuki_idol_airi",
    "tyrell_corp_attendant_meera",
    "little_china_sister_sayaka",
    "net_wintr_proxy",
):
    _add_filthy_scene(npc)

for npc in (
    "kabuki_streamer_jenna",
    "kabuki_brat_neon",
    "kabuki_idol_airi",
    "watson_flatmate_rin",
    "tyrell_corp_attendant_meera",
    "little_china_sister_sayaka",
    "net_wintr_proxy",
):
    _add_lewd_whisper(npc)

# NPC + talk lines (from mature_en, TW voice)
_OVERRIDES.update(
    {
        "mature.npc.kabuki_idol_haejin": "舞台妝藏著勒索時間戳。",
        "mature.npc.kabuki_idol_airi": "全息偶像餘輝貼在她皮膚上。",
        "mature.npc.kabuki_fixer_amara": "紫外墨在指甲上標出買片人。",
        "mature.npc.kabuki_streamer_jenna": "環形燈暈著汗與訂閱數。",
        "mature.npc.kabuki_artist_selene": "炭筆記錄每個包廂剪影。",
        "mature.npc.kabuki_brat_neon": "霓虹小惡魔——挑釁像前戲。",
        "mature.npc.tyrell_liaison_vera": "幽靈節點授權板在她平板上閃。",
        "mature.npc.tyrell_gene_thief_seojin": "樣本箱鎖在口袋裡咔噠響。",
        "mature.npc.tyrell_corp_attendant_meera": "微笑對齊武器登記嗶聲。",
        "mature.npc.watson_flatmate_yoojin": "夜班寒氣凝在咖啡杯上。",
        "mature.npc.watson_flatmate_eunbi": "舞步計數穿過薄牆低語。",
        "mature.npc.little_china_host_misato": "鑰匙圈掛著每間房的欠租。",
        "mature.npc.little_china_sister_sayaka": "書包藏著廟口傳聞列印件。",
        "mature.npc.shrine_net_shaman_nari": "全息餘燼與 mesh 幽靈繞著她扇子轉。",
        "mature.npc.net_wintr_proxy": "代理靜電——聲音走跳接，不走肉體。",
        "mature.talk.kabuki_idol_haejin": (
            "海珍壓低聲音：「VIP 在北——愛璃有她的版本。聽完我的再開 gigs。」"
        ),
        "mature.talk.kabuki_idol_airi": (
            "愛璃笑著不帶溫度：「海珍裝受害者。先去 VIP，再決定最後跟誰 talk。」"
        ),
        "mature.talk.kabuki_fixer_amara": (
            "阿玛拉敲紫外墨：「黃昏後片段往東流。珍娜知道串流密鑰。」"
        ),
        "mature.talk.kabuki_streamer_jenna": (
            "珍娜對環形燈眨眼：「聊天是公開的——flirt 在場下。聚光 gigs 阿玛拉付錢。」"
        ),
        "mature.talk.kabuki_artist_selene": (
            "瑟琳不抬頭：「別動。你的 chrome 比你的話更吃包廂的光。」"
        ),
        "mature.talk.kabuki_brat_neon": (
            "霓虹翻白眼：「信用點或膽子——在我卡座 flirt 前先選一個。」"
        ),
        "mature.talk.tyrell_liaison_vera": (
            "薇拉核對幽靈 ping：「大廳幽靈節點要入侵證明——tyrell_shadow 換街頭聲望。」"
        ),
        "mature.talk.tyrell_gene_thief_seojin": (
            "瑞珍低語：「黃昏樣本車道——廣場掃描儀只對泰瑞證件綠燈。」"
        ),
        "mature.talk.tyrell_corp_attendant_meera": (
            "米拉掃描你的證件：「大廳幽靈控制僅限授權 NETRUN——禁止錄影。」"
        ),
        "mature.talk.watson_flatmate_rin": (
            "凛指著摺疊床：「租約把 home 蓋在 watson_flat——scene 只在那扇門後。」"
        ),
        "mature.talk.watson_flatmate_yoojin": (
            "宥真啜冷咖啡：「又夜班——凛醒著就小聲點。」"
        ),
        "mature.talk.watson_flatmate_eunbi": (
            "恩妃輕聲數拍：「美里在牌樓收租——沙耶香在格點聽廟口消息。」"
        ),
        "mature.talk.little_china_host_misato": (
            "美里晃鑰匙：「房租日神聖——要聊家裡的事往南格點找沙耶香。」"
        ),
        "mature.talk.little_china_sister_sayaka": (
            "沙耶香整書包：「廟在東邊求運——娜莉抽牌前先讀 mesh 幽靈。」"
        ),
        "mature.talk.shrine_net_shaman_nari": (
            "娜莉扇全息餘燼：「每時段 interact shrine_arcana_spread 一次——敢就抽三張。」"
        ),
    }
)

# Fix typo 阿玛拉 -> 阿瑪拉 in talk lines
for key, value in list(_OVERRIDES.items()):
    _OVERRIDES[key] = value.replace("阿玛拉", "阿瑪拉")


def _set_by_path(root: dict, path: str, value: str) -> None:
    parts = path.split(".")
    node: Any = root
    for part in parts[:-1]:
        node = node[part]
    node[parts[-1]] = value


def _normalize_tree(node: Any) -> Any:
    if isinstance(node, dict):
        return {key: _normalize_tree(value) for key, value in node.items()}
    if isinstance(node, str):
        return normalize_tw_text(node)
    return node


def main() -> int:
    data = yaml.safe_load(MATURE_ZH.read_text(encoding="utf-8")) or {}
    data = _normalize_tree(data)
    for path, value in _OVERRIDES.items():
        _set_by_path(data, path, value)
    MATURE_ZH.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8",
    )
    print(f"OK: updated {MATURE_ZH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())