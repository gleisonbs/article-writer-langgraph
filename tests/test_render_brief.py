from nodes.render_brief import render_brief


def test_first_pass_asks_for_a_plan():
    out = render_brief("LangGraph", "enineers", gaps=[], already_asked=[])
    assert "Propose the themes" in out


def test_second_pass_target_only_gaps():
    out = render_brief(
        "LangGraph", "engineers", gaps=["adoption"], already_asked=["overview"]
    )
    assert "- adoption" in out
    assert "Propose the themes" not in out
    assert "overview" in out
