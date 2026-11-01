import json
import re

# Reflect adds a "Guna Balance" section to its answer: how strongly the journal entry
# reflects each of Sankhya's three gunas, as JSON. The API saves it, and only streams it
# to app versions that ask for it, so older apps never see the JSON.

HEADER = "### Guna Balance"

INSTRUCTIONS = """

After those two sections, add exactly one more section with the header: ### Guna Balance
Under it, using Sankhya philosophy, estimate how strongly the journal entry reflects each of the three gunas:
- Sattva: clarity, calm, contentment, insight, kindness, balance
- Rajas: activity, desire, restlessness, ambition, worry, anger, attachment
- Tamas: inertia, fatigue, dullness, confusion, avoidance, heaviness
Output only a JSON object in a ```json code block with these keys:
"sattva", "rajas", "tamas": whole numbers that add up to 100;
"dominant": "sattva", "rajas" or "tamas";
"insight": one sentence in everyday language (at most 25 words) explaining the balance;
"practice": one small, concrete thing to do today that moves toward sattva (at most 20 words).
"""

GUNAS = ("sattva", "rajas", "tamas")


def parse(text):
    """The guna balance from a Reflect answer's Guna Balance section, or None."""
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
        values = {g: max(0, int(round(float(data[g])))) for g in GUNAS}
    except (ValueError, KeyError, TypeError):
        return None
    total = sum(values.values())
    if total == 0:
        return None
    if total != 100:
        # Rescale so the three always add up to 100, putting any rounding difference on the largest.
        values = {g: round(v * 100 / total) for g, v in values.items()}
        largest = max(values, key=values.get)
        values[largest] += 100 - sum(values.values())
    dominant = data.get("dominant")
    return {
        **values,
        "dominant": dominant if dominant in GUNAS else max(values, key=values.get),
        "insight": str(data.get("insight", ""))[:300],
        "practice": str(data.get("practice", ""))[:300],
    }


class StreamSplitter:
    """Splits a streamed Reflect answer into the visible text and the Guna Balance section.

    feed() returns the text that's safe to show now; anything that might be the start of
    the Guna Balance header is held back until it's clear either way.
    """

    def __init__(self):
        self.visible = ""
        self.guna_text = ""
        self._pending = ""
        self._in_guna = False

    def feed(self, chunk):
        if self._in_guna:
            self.guna_text += chunk
            return ""
        self._pending += chunk
        index = self._pending.find(HEADER)
        if index >= 0:
            out, self.guna_text = self._pending[:index], self._pending[index + len(HEADER):]
            self._pending, self._in_guna = "", True
        else:
            keep = self._partial_header_length(self._pending)
            out = self._pending[: len(self._pending) - keep]
            self._pending = self._pending[len(self._pending) - keep:]
        self.visible += out
        return out

    def finish(self):
        out, self._pending = self._pending, ""
        self.visible += out
        return out

    @staticmethod
    def _partial_header_length(text):
        for length in range(min(len(HEADER) - 1, len(text)), 0, -1):
            if HEADER.startswith(text[-length:]):
                return length
        return 0
