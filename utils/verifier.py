from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher
from typing import TYPE_CHECKING

from schemas import Finding

if TYPE_CHECKING:
    from schemas import State

CITE = re.compile(r'\[(\d+):\s*"([^"]{10,300})"\]')
_WS = re.compile(r"\s+")
_FOLD = str.maketrans(
    {
        "\u2018": "'",  # curly singles
        "\u2019": "'",  # curly singles
        "\u201c": '"',  # curly doubles
        "\u201d": '"',  # curly doubles
        "\u2013": "-",  # en / em dash
        "\u2014": "-",  # en / em dash
        "\u00a0": " ",  # non-breaking space
        "\u00ad": "",
    }
)  # soft hyphen)
SUPPORTED, REVIEW = 0.9, 0.7
VERIFIABLE = {"citation", "structure", "length"}


def canon(text: str) -> str:
    t = unicodedata.normalize("NFKC", text).translate(_FOLD)
    return _WS.sub(" ", t).strip().casefold()


def support_score(quote: str, document: str) -> float:
    q, d = canon(quote), canon(document)
    if not q:
        return 0.0
    if q in d:
        return 1.0

    n, best, step = len(q), 0.0, max(1, len(q) // 4)
    for start in range(0, max(1, len(d) - n), step):
        window = d[start : start + n + n // 4]
        best = max(best, SequenceMatcher(None, q, window).ratio())
    return best


def verdict(score: float) -> str:
    if score >= SUPPORTED:
        return "supported"
    if score >= REVIEW:
        return "needs_judge"
    return "unsupported"


def check_citations(state: State) -> list[Finding]:
    by_id = {s["id"]: s for s in state["sources"]}
    out: list[Finding] = []
    for section in state["drafted"]:
        cites = CITE.findall(section.draft)
        if not cites:
            out.append(
                Finding(
                    section_index=section.index,
                    dimension="citation",
                    severity="major",
                    detail="section cites nothing",
                )
            )

        for sid, quote in cites:
            source = by_id.get(int(sid))
            if source is None:
                out.append(
                    Finding(
                        section_index=section.index,
                        dimension="citation",
                        severity="blocker",
                        detail=f"cites source {sid}, which does not exist",
                    )
                )
                continue
            score = support_score(quote, source["content"])
            if score < REVIEW:
                out.append(
                    Finding(
                        section_index=section.index,
                        dimension="citation",
                        severity="blocker",
                        detail=f"quote not in source {sid}: {quote[:60]}",
                    )
                )
            elif score < SUPPORTED:
                out.append(
                    Finding(
                        section_index=section.index,
                        dimension="citation",
                        severity="major",
                        detail=f"quote loosely matches source {sid}: ({score:.2f})",
                    )
                )
    return out


def check_structure(state: State) -> list[Finding]:
    want = [s.heading for s in state["outline"]]
    got = [s.heading for s in state["drafted"]]
    if got != want:
        return [
            Finding(
                dimension="structure",
                severity="major",
                detail=f"sections {got} do not match outline {want}",
            )
        ]
    return []


def check_length(state: State) -> list[Finding]:
    target_word_count_per_section = state["target_words"] // len(state["outline"])
    n, target = len(state["article"].split()), target_word_count_per_section
    difference_target_to_real_word_count = abs(n - target) / target
    if difference_target_to_real_word_count > 0.99:
        return [
            Finding(
                dimension="length",
                severity="blocker",
                detail=f"{n} words against a target of {target}",
            )
        ]
    elif difference_target_to_real_word_count > 0.50:
        return [
            Finding(
                dimension="length",
                severity="major",
                detail=f"{n} words against a target of {target}",
            )
        ]
    elif difference_target_to_real_word_count > 0.15:
        return [
            Finding(
                dimension="length",
                severity="minor",
                detail=f"{n} words against a target of {target}",
            )
        ]

    return []


def tone_level(wrong_register: bool, n_lapses: int) -> int:
    if wrong_register:
        return 0
    if n_lapses == 0:
        return 3
    if n_lapses <= 2:
        return 2
    return 1


def own_prose(text: str) -> str:
    return CITE.sub("", text)
