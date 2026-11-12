#!/usr/bin/env python3
"""Turkish-Q layout for 19th-century Armeno-Turkish (Western Armenian letter values). Writes ArmenoTurkce.keylayout."""
import re
from pathlib import Path

# keycode: (armenian lower, armenian upper, latin key for Cmd/Ctrl shortcuts)
LETTERS = {
    12: ("ե", "Ե", "q"), 13: ("ւ", "Ւ", "w"), 14: ("է", "Է", "e"), 15: ("ր", "Ր", "r"),  # q: ե for եա/եէ spellings
    17: ("թ", "Թ", "t"), 16: ("յ", "Յ", "y"), 32: ("ու", "Ու", "u"), 34: ("ը", "Ը", "i"),  # ı key
    31: ("օ", "Օ", "o"), 35: ("փ", "Փ", "p"), 33: ("ղ", "Ղ", "ğ"), 30: ("իւ", "Իւ", "ü"),
    0: ("ա", "Ա", "a"), 1: ("ս", "Ս", "s"), 2: ("տ", "Տ", "d"), 3: ("ֆ", "Ֆ", "f"),
    5: ("կ", "Կ", "g"), 4: ("հ", "Հ", "h"), 38: ("ժ", "Ժ", "j"), 40: ("ք", "Ք", "k"),
    37: ("լ", "Լ", "l"), 41: ("շ", "Շ", "ş"), 39: ("ի", "Ի", "i"),  # i key
    6: ("զ", "Զ", "z"), 7: ("խ", "Խ", "x"), 8: ("ճ", "Ճ", "c"), 9: ("վ", "Վ", "v"),
    11: ("պ", "Պ", "b"), 45: ("ն", "Ն", "n"), 46: ("մ", "Մ", "m"),
    43: ("էօ", "Էօ", "ö"), 47: ("ջ", "Ջ", "ç"),
}
# Turkish Q symbols: keycode: (normal, shift, option)
SYMBOLS = {
    50: ('"', "é", "<"), 10: ("<", ">", "|"),
    18: ("1", "՜", "!", ">"),  # Armenian exclamation; Option gives Latin "!", Shift+Option ">"
    19: ("2", "'", "£"), 20: ("3", "^", "#"), 21: ("4", "+", "$"),
    23: ("5", "%", "½"), 22: ("6", "&", "6"), 26: ("7", "/", "{"), 28: ("8", "(", "["),
    25: ("9", ")", "]"), 29: ("0", "=", "}"), 24: ("-", "_", "|"),
    27: ("*", "՞", "\\", "?"),  # Armenian question mark; Shift+Option gives Latin "?"
    42: (",", ";", "`"),
    44: ("։", "․", ".", ":"),  # Armenian full stop / mijaket (U+2024); Option(+Shift) gives Latin "." ":"
}
OPTION_LETTERS = {12: "@", 14: "€", 30: "~", 41: "՝", 43: "«", 47: "»"}  # Option+q=@ etc.; ş/ö/ç: Armenian marks
CONTROL = {
    36: "\r", 48: "\t", 49: " ", 51: "\b", 53: "\x1b", 76: "\x03", 117: "\x7f",
    123: "\x1c", 124: "\x1d", 125: "\x1f", 126: "\x1e", 115: "\x01", 119: "\x04",
    116: "\x0b", 121: "\x0c", 114: "\x05", 71: "\x1b",
    65: ".", 67: "*", 69: "+", 75: "/", 78: "-", 81: "=",
    82: "0", 83: "1", 84: "2", 85: "3", 86: "4", 87: "5", 88: "6", 89: "7", 91: "8", 92: "9",
    **{k: "\x10" for k in (122, 120, 99, 118, 96, 97, 98, 100, 101, 109, 103, 111)},
}


def esc(s):
    return "".join(f"&#x{ord(c):04X};" for c in s)


def layer(i):
    """0 normal, 1 shift, 2 caps, 3 option, 4 shift+option, 5 command/control (Latin)."""
    keys = dict(CONTROL)
    for k, (lo, up, lat) in LETTERS.items():
        if i == 5:
            keys[k] = lat
        elif i == 3 and k in OPTION_LETTERS:
            keys[k] = OPTION_LETTERS[k]
        else:
            keys[k] = up if i in (1, 2, 4) else lo
    for k, (n, s, o, *so) in SYMBOLS.items():
        keys[k] = {1: s, 4: so[0] if so else s, 3: o}.get(i, n)
    rows = "\n".join(f'      <key code="{k}" output="{esc(v)}"/>' for k, v in sorted(keys.items()))
    return f'    <keyMap index="{i}">\n{rows}\n    </keyMap>'


def build():
    maps = "\n".join(layer(i) for i in range(6))
    return f"""<?xml version="1.1" encoding="UTF-8"?>
<!DOCTYPE keyboard SYSTEM "file://localhost/System/Library/DTDs/KeyboardLayout.dtd">
<keyboard group="126" id="-28461" name="Armeno-Türkçe Q" maxout="3">
  <layouts>
    <layout first="0" last="17" modifiers="m" mapSet="k"/>
  </layouts>
  <modifierMap id="m" defaultIndex="0">
    <keyMapSelect mapIndex="0"><modifier keys=""/></keyMapSelect>
    <keyMapSelect mapIndex="1"><modifier keys="anyShift caps?"/></keyMapSelect>
    <keyMapSelect mapIndex="2"><modifier keys="caps"/></keyMapSelect>
    <keyMapSelect mapIndex="3"><modifier keys="anyOption caps?"/></keyMapSelect>
    <keyMapSelect mapIndex="4"><modifier keys="anyShift anyOption caps?"/></keyMapSelect>
    <keyMapSelect mapIndex="5">
      <modifier keys="command anyShift? anyOption? caps? anyControl?"/>
      <modifier keys="anyControl anyShift? anyOption? caps?"/>
    </keyMapSelect>
  </modifierMap>
  <keyMapSet id="k">
{maps}
  </keyMapSet>
</keyboard>
"""


if __name__ == "__main__":
    xml = build()
    # self-check: ş -> շ, u -> ու, d -> տ, ö -> էօ, Cmd+c stays latin
    assert esc("շ") in re.search(r'code="41" output="([^"]+)"', xml).group(1)
    assert f'code="32" output="{esc("ու")}"' in xml
    assert f'code="2" output="{esc("տ")}"' in xml and f'code="43" output="{esc("էօ")}"' in xml
    shift, shift_opt = xml.split('<keyMap index="1">')[1], xml.split('<keyMap index="4">')[1]
    assert f'code="27" output="{esc("՞")}"' in shift and f'code="27" output="{esc("?")}"' in shift_opt
    assert f'code="44" output="{esc("․")}"' in shift and f'code="44" output="{esc(":")}"' in shift_opt
    assert all(f'code="{k}" output="{esc(d)}"' in xml for k, d in ((19, "2"), (20, "3"), (21, "4")))
    assert xml.split('<keyMap index="5">')[1].count('code="8" output="&#x0063;"') == 1
    out = Path(__file__).with_name("ArmenoTurkce.keylayout")
    out.write_text(xml, encoding="utf-8")
    print("wrote", out)
