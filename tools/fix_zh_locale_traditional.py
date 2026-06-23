#!/usr/bin/env python3
"""Normalize data/locale/zh.yaml to Taiwan Traditional (繁體)."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from shared.zh_traditional_audit import normalize_tw_text

ZH_PATH = ROOT / "data" / "locale" / "zh.yaml"

_ARCANA_DRAW = {
    "fool": "霓虹一躍——開局沒有安全網。",
    "magician": "工具就位：意志、義體、一次專注的呼吸。",
    "priestess": "秘密在表層下匯聚——駭入前先聽。",
    "empress": "豐饒或貪欲——餵養就會生長。",
    "emperor": "秩序撐住街區——規矩換來時間。",
    "hierophant": "舊規仍束縛——傳統是鎖也是鑰。",
    "lovers": "帶熱度的抉擇——兩條路，同一脈搏。",
    "chariot": "動量取勝——格點追上你之前別停。",
    "strength": "溫柔手按住凶殘義體——耐心馴服野獸。",
    "hermit": "抽身才看得清——寂靜標出喧囂藏處。",
    "wheel": "循環轉動——運氣、債務、天氣一同旋轉。",
    "justice": "帳目會平——欠下的終會找來。",
    "hanged": "停頓改寫戰局——放手也是戰術。",
    "death": "終結騰出槽位——拆掉舊殼。",
    "temperance": "謹慎調和——義體過量稀釋靈魂。",
    "devil": "你自選的鎖鏈——慾望用信用點簽收。",
    "tower": "謊言崩塌——閃電貫穿假塔。",
    "star": "雨後希望——濕 chrome 上的遠光。",
    "moon": "幻象與本能——別信那條 feed。",
    "sun": "清明灼人——正午強光下赤裸真相。",
    "judgement": "裁決已到——回應召喚或付罰金。",
    "world": "圓滿低鳴——一電路闔上，另一路開啟。",
}

_TALK_OVERRIDES = {
    "kabuki_idol_haejin": "海珍壓低聲音：「VIP 在北——愛璃有她的版本。聽完我的再開 gigs。」",
    "kabuki_idol_airi": "愛璃笑著不帶溫度：「海珍裝受害者。先去 VIP，再決定最後跟誰 talk。」",
    "kabuki_fixer_amara": "阿瑪拉敲紫外墨：「黃昏後片段往東流。珍娜知道串流密鑰。」",
    "kabuki_streamer_jenna": "珍娜對環形燈眨眼：「聊天是公開的——flirt 在場下。聚光 gigs 阿瑪拉付錢。」",
    "kabuki_artist_selene": "瑟琳不抬頭：「別動。你的 chrome 比你的話更吃包廂的光。」",
    "kabuki_brat_neon": "霓虹翻白眼：「信用點或膽子——在我卡座 flirt 前先選一個。」",
    "tyrell_liaison_vera": "薇拉核對幽靈 ping：「大廳幽靈節點要入侵證明——tyrell_shadow 換街頭聲望。」",
    "tyrell_gene_thief_seojin": "瑞珍低語：「黃昏樣本車道——廣場掃描儀只對泰瑞證件綠燈。」",
    "tyrell_corp_attendant_meera": "米拉掃描你的證件：「大廳幽靈控制僅限授權 NETRUN——禁止錄影。」",
    "watson_flatmate_rin": "凜指著摺疊床：「租約把 home 蓋在 watson_flat——scene 只在那扇門後。」",
    "watson_flatmate_yoojin": "宥真啜冷咖啡：「又夜班——凜醒著就小聲點。」",
    "watson_flatmate_eunbi": "恩妃輕聲數拍：「美里在牌樓收租——沙耶香在格點聽廟口消息。」",
    "little_china_host_misato": "美里晃鑰匙：「房租日神聖——要聊家裡的事往南格點找沙耶香。」",
    "little_china_sister_sayaka": "沙耶香整書包：「廟在東邊求運——娜莉抽牌前先讀 mesh 幽靈。」",
    "shrine_net_shaman_nari": "娜莉扇全息餘燼：「每時段 interact shrine_arcana_spread 一次——敢就抽三張。」",
}


def _normalize_tree(node: Any) -> Any:
    if isinstance(node, dict):
        return {key: _normalize_tree(value) for key, value in node.items()}
    if isinstance(node, str):
        return normalize_tw_text(node)
    return node


def main() -> int:
    data = yaml.safe_load(ZH_PATH.read_text(encoding="utf-8")) or {}
    data = _normalize_tree(data)
    data.setdefault("weapon_class", {})["power"] = "動能"
    arcana_draw = data.setdefault("arcana", {}).setdefault("draw", {})
    for key, value in _ARCANA_DRAW.items():
        arcana_draw[key] = value
    talk = data.setdefault("talk", {})
    for key, value in _TALK_OVERRIDES.items():
        talk[key] = value
    ZH_PATH.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8",
    )
    print(f"OK: updated {ZH_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())