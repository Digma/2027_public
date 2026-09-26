"""Generate the add-to-calendar files in calendar/.

One file per combination of invited days, so each guest only gets the
events their invite covers. Re-run after changing a time or address:

    python3 scripts/make_ics.py
"""
from itertools import combinations
from pathlib import Path

SITE = "https://claraetgael.love"
OUT = Path(__file__).resolve().parent.parent / "calendar"

# Times in UTC (Montolieu is UTC+2 in May).
EVENTS = {
    "a": dict(
        uid="apero-2027@claraetgael.love",
        start="20270514T160000Z", end="20270514T190000Z",  # 18h-21h
        summary="Clara & Gaël · Apéro",
        location="La Coopérative-Musée Cérès Franco, 5 Rte d'Alzonne, 11170 Montolieu, France",
        description=(
            "Apéro au musée Cérès Franco / Drinks at the museum / Aperitivo en el museo\n"
            f"{SITE}"
        ),
    ),
    "w": dict(
        uid="mariage-2027@claraetgael.love",
        start="20270515T120000Z", end="20270516T020000Z",  # 14h-4h
        summary="Clara & Gaël · Mariage",
        location="Mairie de Montolieu, 8 Rue de la Mairie, 11170 Montolieu, France",
        description=(
            "14h rendez-vous à la mairie · 15h30 cérémonie à Saint-Roch · "
            "18h vin d'honneur & dîner\n"
            "2pm meet at the town hall · 3:30pm ceremony · 6pm drinks & dinner\n"
            "14h encuentro en el ayuntamiento · 15h30 ceremonia · 18h cóctel y cena\n"
            f"{SITE}"
        ),
    ),
    "p": dict(
        uid="paella-2027@claraetgael.love",
        start="20270516T110000Z", end="20270516T170000Z",  # 13h-19h
        summary="Clara & Gaël · Paella",
        location="La Manufacture Royale 1739, 16 Imp. de la Manufacture, 11170 Montolieu, France",
        description=f"Paella à la Manufacture Royale / Paella at the Manufacture Royale\n{SITE}",
    ),
}


def esc(text):
    return (text.replace("\\", "\\\\").replace(";", "\;")
                .replace(",", "\\,").replace("\n", "\\n"))


def fold(line):
    # RFC 5545: lines longer than 75 octets continue on the next line after a space.
    raw, out = line.encode("utf-8"), []
    while len(raw) > 75:
        cut = 75 if not out else 74
        while (raw[cut] & 0xC0) == 0x80:  # don't split a UTF-8 character
            cut -= 1
        out.append(raw[:cut].decode("utf-8"))
        raw = raw[cut:]
    out.append(raw.decode("utf-8"))
    return "\r\n ".join(out)


def calendar(keys):
    lines = [
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//claraetgael.love//FR",
        "CALSCALE:GREGORIAN", "METHOD:PUBLISH", "X-WR-CALNAME:Clara & Gaël",
    ]
    for k in keys:
        e = EVENTS[k]
        lines += [
            "BEGIN:VEVENT", f"UID:{e['uid']}", "DTSTAMP:20260926T000000Z",
            f"DTSTART:{e['start']}", f"DTEND:{e['end']}",
            f"SUMMARY:{esc(e['summary'])}", f"LOCATION:{esc(e['location'])}",
            f"DESCRIPTION:{esc(e['description'])}", f"URL:{SITE}", "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return "\r\n".join(fold(l) for l in lines) + "\r\n"


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for n in range(1, 4):
        for keys in combinations("awp", n):
            path = OUT / f"clara-gael-{''.join(keys)}.ics"
            path.write_bytes(calendar(keys).encode("utf-8"))
            print(path.name)
