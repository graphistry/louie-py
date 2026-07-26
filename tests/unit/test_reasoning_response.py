"""Reasoning-aware Response and stream accumulator contract tests."""

import json
from unittest.mock import Mock

from louieai._client import LouieClient, Response


def _current_contract_messages() -> list[dict]:
    return [
        {"type": "StreamingApiMessageStart", "dthread_id": "D_reasoning"},
        {
            "type": "StreamingApiMessageOutputUpdate",
            "position": 0,
            "payload": {
                "id": "B_reason",
                "type": "TextElement",
                "text": "checking",
                "during_run_id": "R_root",
                "complete": False,
            },
        },
        {
            "type": "StreamingApiMessageOutputUpdate",
            "position": 0,
            "payload": {
                "id": "B_reason",
                "type": "TextElement",
                "text": "checking the evidence",
                "during_run_id": "R_root",
                "complete": True,
            },
        },
        {
            "type": "StreamingApiMessageOutputUpdate",
            "position": 1,
            "payload": {
                "id": "B_tool",
                "type": "TextElement",
                "text": "tool result",
                "during_run_id": "R_method",
                "complete": True,
            },
        },
        {
            "type": "StreamingApiMessageRunUpdate",
            "run_node": {
                "node_type": "MethodRun",
                "id": "R_method",
                "parent_id": "R_root",
                "state": "Running",
                "run_type": "MethodRun",
                "action": {"expression": "SearchTool", "args": {}},
                "results": {},
                "children": [],
            },
        },
        {
            "type": "StreamingApiMessageRunUpdate",
            "run_node": {
                "node_type": "MethodRun",
                "id": "R_method",
                "parent_id": "R_root",
                "state": "Done",
                "run_type": "MethodRun",
                "action": {"expression": "SearchTool", "args": {}},
                "results": {"answer": "B_tool"},
                "children": [],
            },
        },
        {
            "type": "StreamingApiMessageOutputUpdate",
            "position": 2,
            "payload": {
                "id": "B_final",
                "type": "TextElement",
                "text": "final answer",
                "during_run_id": "R_root",
                "complete": True,
            },
        },
        {
            "type": "StreamingApiMessageRunUpdate",
            "run_node": {
                "node_type": "Run",
                "id": "R_root",
                "state": "Done",
                "run_type": "LouieAgent",
                "children": ["R_method"],
                "results": {},
                "final_answer": "B_final",
                "token_flow": {
                    "type": "TokenFlowStats",
                    "tokens_in": 20,
                    "tokens_out": 8,
                    "tokens_reasoning": 5,
                    "waiting": False,
                    "updated_at": 1,
                },
            },
        },
        {
            "type": "StreamingApiMessageTrace",
            "payload": [20, 1712345678000, "phase complete"],
        },
        {"type": "StreamingApiMessageTerminal", "success": True, "error": None},
    ]


def _parse_current_contract() -> Response:
    client = LouieClient(token="test-token")
    body = "\n".join(json.dumps(message) for message in _current_contract_messages())
    parsed = client._parse_jsonl_response(body)
    return Response(
        parsed["dthread_id"],
        parsed["elements"],
        stream_messages=parsed["stream_messages"],
        include_reasoning=True,
    )


def test_current_contract_separates_reasoning_final_and_tool_text() -> None:
    response = _parse_current_contract()

    assert response.thread_id == "D_reasoning"
    assert response.text == "final answer"
    assert response.final_text == "final answer"
    assert response.final_texts == ["tool result", "final answer"]
    assert response.reasoning_texts == ["checking the evidence"]
    assert response.reasoning_text == "checking the evidence"
    assert response.reasoning_elements[0]["complete"] is True
    assert response.final_answer_id == "B_final"


def test_current_contract_exposes_phases_status_tokens_traces_and_terminal() -> None:
    response = _parse_current_contract()

    assert [update["state"] for update in response.phase_updates] == [
        "Running",
        "Done",
    ]
    assert response.phases[0]["action"]["expression"] == "SearchTool"
    assert response.phases[0]["state"] == "Done"
    assert response.root_run["id"] == "R_root"
    assert response.status == "succeeded"
    assert response.token_flow["tokens_reasoning"] == 5
    assert response.trace_events == [[20, 1712345678000, "phase complete"]]
    assert response.terminal == {
        "type": "StreamingApiMessageTerminal",
        "success": True,
        "error": None,
    }
    assert response.succeeded is True
    assert response.terminal_error is None


def test_run_failure_is_authoritative_even_with_success_terminal() -> None:
    response = Response(
        "D_failed",
        [],
        stream_messages=[
            {
                "type": "StreamingApiMessageRunUpdate",
                "run_node": {
                    "node_type": "Run",
                    "id": "R_failed",
                    "state": "Failed",
                    "run_type": "LouieAgent",
                },
            },
            {"type": "StreamingApiMessageTerminal", "success": True},
        ],
    )

    assert response.succeeded is True
    assert response.status == "failed"


def test_last_of_multiple_upload_terminals_wins() -> None:
    response = Response(
        "D_upload",
        [],
        stream_messages=[
            {"type": "StreamingApiMessageTerminal", "success": True},
            {
                "type": "StreamingApiMessageTerminal",
                "success": False,
                "error": "follow-up scheduling failed",
            },
        ],
    )

    assert len(response.terminals) == 2
    assert response.succeeded is False
    assert response.status == "failed"
    assert response.terminal_error == "follow-up scheduling failed"
    assert response.has_errors


def test_no_final_pointer_keeps_root_text_conservatively_unclassified() -> None:
    response = Response(
        "D_legacy_failure",
        [
            {
                "id": "B_partial",
                "type": "TextElement",
                "text": "partial but useful",
                "during_run_id": "R_root",
                "complete": False,
            }
        ],
        stream_messages=[
            {
                "type": "StreamingApiMessageRunUpdate",
                "run_node": {
                    "node_type": "Run",
                    "id": "R_root",
                    "state": "Interrupted",
                    "run_type": "LouieAgent",
                    "final_answer": None,
                },
            }
        ],
    )

    assert response.reasoning_elements == []
    assert response.text == "partial but useful"
    assert response.status == "interrupted"


def test_legacy_draft_flag_remains_supported() -> None:
    response = Response(
        "D_old",
        [
            {"id": "B_draft", "type": "TextElement", "text": "draft", "draft": True},
            {"id": "B_final", "type": "TextElement", "text": "answer", "draft": False},
        ],
    )

    assert response.text == "answer"
    assert response.final_text == "answer"
    assert response.reasoning_text == "draft"


def test_explicit_final_answer_pointer_wins_even_when_reasoning_is_off() -> None:
    response = Response(
        "D_legacy",
        [
            {
                "id": "B_first",
                "type": "TextElement",
                "text": "first legitimate output",
                "during_run_id": "R_root",
            },
            {
                "id": "B_second",
                "type": "TextElement",
                "text": "second legitimate output",
                "during_run_id": "R_root",
            },
        ],
        stream_messages=[
            {
                "type": "StreamingApiMessageRunUpdate",
                "run_node": {
                    "node_type": "Run",
                    "id": "R_root",
                    "state": "Done",
                    "final_answer": "B_second",
                },
            }
        ],
        include_reasoning=False,
    )

    # BREAKING (unreleased): `.text` previously returned the first text element
    # here, ignoring the server's explicit final_answer pointer unless
    # include_reasoning was set. A pointer is the server stating which element
    # is the answer, so honouring it conditionally was indefensible.
    assert response.text == "second legitimate output"
    assert response.final_text == "second legitimate output"
    assert response.final_texts == [
        "first legitimate output",
        "second legitimate output",
    ]
    assert response.reasoning_elements == []


def test_three_concatenated_objects_are_all_decoded() -> None:
    client = LouieClient(token="test-token")
    body = (
        '{"type":"StreamingApiMessageStart","dthread_id":"D_three"}'
        '{"type":"StreamingApiMessageOutputUpdate","position":0,'
        '"payload":{"id":"B_1","type":"TextElement","text":"answer"}}'
        '{"type":"StreamingApiMessageTerminal","success":true}'
    )

    parsed = client._parse_jsonl_response(body)

    assert parsed["dthread_id"] == "D_three"
    assert parsed["elements"][0]["text"] == "answer"
    assert [message["type"] for message in parsed["stream_messages"]] == [
        "StreamingApiMessageStart",
        "StreamingApiMessageOutputUpdate",
        "StreamingApiMessageTerminal",
    ]


def test_position_replacement_removes_old_id_and_empty_update_clears_text() -> None:
    client = LouieClient(token="test-token")
    messages = [
        {
            "type": "StreamingApiMessageOutputUpdate",
            "position": 0,
            "payload": {"id": "B_old", "type": "TextElement", "text": "old"},
        },
        {
            "type": "StreamingApiMessageOutputUpdate",
            "position": 0,
            "payload": {"id": "B_new", "type": "TextElement", "text": "new"},
        },
        {
            "type": "StreamingApiMessageOutputUpdate",
            "position": 1,
            "payload": {"type": "TextElement", "text": "temporary"},
        },
        {
            "type": "StreamingApiMessageOutputUpdate",
            "position": 1,
            "payload": {"type": "TextElement", "text": ""},
        },
    ]

    parsed = client._parse_stream_objects(messages)

    assert [element.get("id") for element in parsed["elements"]] == ["B_new", None]
    assert parsed["elements"][1]["text"] == ""


def test_unknown_and_malformed_messages_degrade_safely() -> None:
    client = LouieClient(token="test-token")
    body = (
        "{malformed}\n"
        '{"type":"FutureMessage","payload":{"feature":true}}\n'
        '{"payload":{"id":"B_ok","type":"TextElement","text":"ok"}}'
    )

    parsed = client._parse_jsonl_response(body)

    assert parsed["elements"][0]["text"] == "ok"
    assert parsed["stream_messages"][0]["type"] == "FutureMessage"


def test_singleshot_uses_same_typed_accumulator() -> None:
    client = LouieClient(token="test-token")
    http_response = Mock()
    http_response.raise_for_status = Mock()
    http_response.json.return_value = _current_contract_messages()
    client._client = Mock()
    client._client.post.return_value = http_response

    response = client._chat_singleshot({"query": "test"}, include_reasoning=True)

    assert response.text == "final answer"
    assert response.status == "succeeded"
    assert response.reasoning_text == "checking the evidence"


def test_text_elements_matches_text_semantics() -> None:
    """`text_elements` is the plural of `text`, not the raw union.

    Previously `.text` excluded reasoning while `.text_elements` included it, so
    the singular and plural of the same word disagreed. The unfiltered view is
    `.elements`; reasoning specifically is `.reasoning_elements`.
    """
    response = Response(
        "D_split",
        [
            {
                "id": "B_draft",
                "type": "TextElement",
                "text": "thinking",
                "during_run_id": "R_root",
            },
            {
                "id": "B_final",
                "type": "TextElement",
                "text": "answer",
                "during_run_id": "R_root",
            },
        ],
        stream_messages=[
            {
                "type": "StreamingApiMessageRunUpdate",
                "run_node": {
                    "node_type": "Run",
                    "id": "R_root",
                    "state": "Done",
                    "final_answer": "B_final",
                },
            }
        ],
        include_reasoning=True,
    )

    assert [e["id"] for e in response.text_elements] == ["B_final"]
    assert response.text_elements == response.final_text_elements
    assert [e["id"] for e in response.reasoning_elements] == ["B_draft"]
    # The raw union remains reachable.
    assert len(response.elements) == 2
