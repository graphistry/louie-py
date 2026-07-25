"""Credential-gated smoke test for reasoning-aware response semantics."""

import pytest


@pytest.mark.integration
def test_reasoning_aware_live_contract(real_client):
    """Keep final text stable while retaining opt-in stream metadata."""
    response = real_client.add_cell(
        "",
        "Think briefly, then answer only the result of 2 + 2.",
        traces=True,
        include_reasoning=True,
    )

    assert response.final_text
    assert response.text == response.final_text
    assert response.stream_messages
    assert response.terminal is not None
    assert response.succeeded is True
    assert response.terminal_error is None
    assert response.status == "succeeded"

    final_ids = {element.get("id") for element in response.final_text_elements}
    reasoning_ids = {element.get("id") for element in response.reasoning_elements}
    assert final_ids.isdisjoint(reasoning_ids)
