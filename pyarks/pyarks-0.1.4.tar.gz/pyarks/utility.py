#!/usr/bin/env python
# -*- coding: utf-8 -*- 

def universalNameToID(name):
    if name == "IOA" or name == "Islands of Adventure":
        return 10000
    elif name == "USF" or name == "Universal Studios Florida":
        return 10010
    elif name == "USH" or name == "Universal Studios Hollywood":
        return 13825
    elif name == "VB" or name == "Volcano Bay":
        return 13801
    else:
        return -1

def USJTranslate(name):
    if name == "ハローキティのカップケーキ・ドリーム":
        return "Hello Kitty's Cupcake Dream"
    elif name == "エルモのゴーゴー・スケートボード":
        return "Elmo's go-go skateboard"
    elif name == "モッピーのバルーン・トリップ":
        return "Mobi Balloon Trip"
    elif name == "フライング・スヌーピー":
        return "Flying Snoopy"
    elif name == "スヌーピーのグレートレース™":
        return "Snoopy's Great Race ™"
    elif name == "アメージング・アドベンチャー・オブ・スパイダーマン・ザ・ライド 4K3D":
        return "Amazing Adventure of Spider-Man The Ride 4K 3 D"
    elif name == "妖怪ウォッチ・ザ・リアル 4":
        return "Yokai Watch The Real 4"
    elif name == "ジュラシック・パーク・ザ・ライド®":
        return "Jurassic Park - The Ride ®"
    elif name == "ジョーズ®":
        return "Jaws ®"
    elif name == "セサミストリート 4-D ムービーマジック™":
        return "Sesame Street 4-D Movie Magic ™"
    elif name == "フライト・オブ・ザ・ヒッポグリフ™":
        return "Flight of the Hippogriff ™"
    elif name == "ハリウッド・ドリーム・ザ・ライド":
        return "Hollywood · Dream · The · Ride"
    elif name == "ハリウッド・ドリーム・ザ・ライド～バックドロップ～":
        return "Hollywood · Dream · The Ride ~ Backdrop ~"
    elif name == "ザ・フライング・ダイナソー":
        return "The Flying Dinosaur"
    elif name == "ハリー・ポッター・アンド・ザ・フォービドゥン・ジャーニー™":
        return "Harry Potter and the Forbidden Journey ™"
    elif name == "スペース・ファンタジー・ザ・ライド":
        return "Space Fantasy the Ride"
    elif name == "バックドラフト®":
        return "Backdraft ®"
    elif name == "シュレック 4-D アドベンチャー™":
        return "Shrek 4-D Adventure ™"
    elif name == "休止中":
        return "Inactive"
    else:
        return "No translation"

def seaworldNameToID(name):
    if name == "BGT":
        return "BG_TPA"
    elif name == "SWO":
        return "SW_MCO"
    elif name == "SWSD":
        return "SW_SAN"
    elif name == "SWSA":
        return "SW_SAT"
    elif name == "BGW":
        return "BG_PHF"
    else:
        return "BG_TPA"