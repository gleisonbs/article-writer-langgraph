def render_brief(topic, audience, gaps, already_asked) -> str:
    lines = [f"Topic: {topic}", f"Audience: {audience}", ""]

    if not gaps:
        lines.append("Propose the themes this article must cover, one query each.")
    else:
        lines.append("Still under-covered - write queries for ONLY these:")
        lines += [f"- {g}" for g in gaps]
        lines += ["", "Already tried:"]
        lines += [f"- {q}" for q in already_asked]

    return "\n".join(lines)
