from clients import model
from logger import log_header, log_info, log_success, log_warning, plural
from schemas import Finding, State, Verdict
from utils import (
    SUPPORTED,
    VERIFIABLE,
    check_citations,
    check_length,
    check_structure,
    own_prose,
    support_score,
    tone_level,
)


def critique(state: State) -> dict:
    log_header(f"Critiquing the Article (pass {state['revision_count'] + 1})")

    findings: list[Finding] = []

    findings += check_structure(state)
    findings += check_length(state)
    findings += check_citations(state)

    failures = len([f for f in findings if f.dimension in VERIFIABLE])
    log_info(f"Found {plural(failures, 'issue')} in structure, length, and citations")

    log_info("Asking the model to judge tone")
    levels = []
    for section in state["drafted"]:
        prose = own_prose(section.draft)
        verdict = model.with_structured_output(Verdict).invoke(
            f"Check one thing: whether this passage holds its target register."
            f"\n\nTarget register: {state['tone']}, for {state['audience']}.\n\n"
            f"A lapse is one specific passage that breaks that register. For "
            f"each, copy the offending span verbatim and say why it lapses. "
            f"Never count the same span twice. If the register is wrong "
            f"throughout rather than in places, set wrong_register and list "
            f"no lapses.\n\n"
            f"<passage>\n{prose}\n</passage>\n\n"
            f"List the lapses in the passage above, quoting each verbatim."
        )

        real = [
            l
            for l in verdict.lapses  # type: ignore
            if support_score(l.quote, prose) >= SUPPORTED
        ]
        level = tone_level(verdict.wrong_register, len(real))  # type: ignore
        levels.append(level)

        summary = (
            "wrong register throughout"
            if verdict.wrong_register  # type: ignore
            else plural(len(real), "lapse")
        )
        log_info(
            f"{section.index}. {section.heading} — tone level {level}/3 ({summary})"
        )
        for lapse in real:
            log_info(f'\t• "{lapse.quote}"')
            log_info(f"\t{lapse.why}")
        dropped = len(verdict.lapses) - len(real)  # type: ignore
        if dropped:
            log_info(
                f"       {plural(dropped, 'lapse')} ignored: quote not found in the section"
            )

        if level <= 1:
            findings.append(
                Finding(
                    section_index=section.index,  # located, so it can travel
                    dimension="tone",
                    severity="blocker",
                    detail=f"tone level {level}, {len(real)} lapses"
                    + (f': "{real[0].quote[:60]}"' if real else ""),
                )
            )

    blockers = len([f for f in findings if f.severity == "blocker"])
    if blockers:
        log_warning(f"{plural(blockers, 'blocker')} found")
    else:
        log_success("No blockers found")

    return {
        "findings": findings,
        "revision_count": state["revision_count"] + 1,
        "scores": [
            {  # append reducer: one entry per pass
                "pass": state["revision_count"],
                "failures": failures,  # the number the router watches
                "tone": min(levels, default=3),  # the worst section carries it
            }
        ],
    }
