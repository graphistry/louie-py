"""Regression tests for the normalized `ResponseProxy.elements` view.

Two defects, both in this one function:

1. Error text always read a `message` key. Current servers send
   `ExceptionElement.text` (`graphistrygpt/models/elements.py`), so every
   error surfaced the literal "Unknown error" while the real message sat
   unread in the element.
2. Entries dropped the element `id` and were regrouped by type, so nothing
   could be correlated with `Response.final_answer_id` and an error raised
   midway was hoisted to the front.

Neither affected `text`, `final_text`, or the raw `errors` list.
"""

from __future__ import annotations

import pytest

from louieai._client import Response
from louieai.notebook.cursor import ResponseProxy

pytestmark = pytest.mark.unit


def _run_msgs(final_answer: str, run_id: str = "R_root") -> list[dict]:
    return [
        {
            "type": "StreamingApiMessageRunUpdate",
            "run_node": {
                "node_type": "Run",
                "id": run_id,
                "state": "Done",
                "final_answer": final_answer,
            },
        }
    ]


def test_exception_element_text_is_surfaced() -> None:
    """Current wire format: ExceptionElement carries `text`, not `message`."""
    response = Response(
        "D", [{"id": "B_e", "type": "ExceptionElement", "text": "division by zero"}]
    )

    entry = ResponseProxy(response).elements[0]

    assert entry["type"] == "error"
    assert entry["value"] == "division by zero"


def test_legacy_message_key_still_surfaced() -> None:
    """Older elements used `message`; it remains a fallback."""
    response = Response(
        "D", [{"id": "B_e", "type": "ExceptionElement", "message": "legacy boom"}]
    )

    assert ResponseProxy(response).elements[0]["value"] == "legacy boom"


def test_text_wins_over_legacy_message_when_both_present() -> None:
    """Precedence, not just presence.

    Tests that supply only one key pass regardless of ordering, so they do not
    pin which field wins. `text` is the current wire format and must take
    precedence over the legacy `message`.
    """
    response = Response(
        "D",
        [
            {
                "id": "B_e",
                "type": "ExceptionElement",
                "text": "current wire format",
                "message": "legacy field",
            }
        ],
    )

    assert ResponseProxy(response).elements[0]["value"] == "current wire format"


def test_unknown_error_only_when_nothing_available() -> None:
    response = Response("D", [{"id": "B_e", "type": "ExceptionElement"}])

    assert ResponseProxy(response).elements[0]["value"] == "Unknown error"


def test_entries_expose_id_and_match_final_answer_id() -> None:
    """Entries must be correlatable with the root run's final-answer pointer."""
    response = Response(
        "D",
        [
            {
                "id": "B_1",
                "type": "TextElement",
                "text": "thinking",
                "during_run_id": "R_root",
            },
            {
                "id": "B_2",
                "type": "TextElement",
                "text": "the answer",
                "during_run_id": "R_root",
            },
        ],
        stream_messages=_run_msgs("B_2"),
        include_reasoning=True,
    )

    entries = ResponseProxy(response).elements

    assert all("id" in entry for entry in entries)
    matched = [e for e in entries if e["id"] == response.final_answer_id]
    assert [e["type"] for e in matched] == ["text"]
    assert matched[0]["value"] == "the answer"


def test_entries_keep_server_position_order() -> None:
    """An error raised midway must not be hoisted to the front."""
    response = Response(
        "D",
        [
            {
                "id": "B_1",
                "type": "TextElement",
                "text": "step one done",
                "during_run_id": "R_root",
            },
            {"id": "B_2", "type": "ExceptionElement", "text": "boom"},
            {
                "id": "B_3",
                "type": "TextElement",
                "text": "final answer",
                "during_run_id": "R_root",
            },
        ],
        stream_messages=_run_msgs("B_3"),
        include_reasoning=True,
    )

    entries = ResponseProxy(response).elements

    assert [e["id"] for e in entries] == ["B_1", "B_2", "B_3"]
    assert [e["type"] for e in entries] == ["reasoning", "error", "text"]


def test_empty_response_returns_empty_list() -> None:
    assert ResponseProxy(None).elements == []
    assert ResponseProxy(Response("D", [])).elements == []
