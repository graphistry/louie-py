"""Persona-journey tests for reasoning-aware Cursor and notebook streaming."""

from unittest.mock import Mock, patch

import pandas as pd

from louieai._client import Response
from louieai.notebook.cursor import Cursor, ResponseProxy, _render_response_html
from louieai.notebook.streaming import StreamingDisplay


def _reasoning_response() -> Response:
    elements = [
        {
            "id": "B_reason",
            "type": "TextElement",
            "text": "<script>reason</script>",
            "during_run_id": "R_root",
            "complete": True,
        },
        {
            "id": "B_final",
            "type": "TextElement",
            "text": "safe final",
            "during_run_id": "R_root",
            "complete": True,
        },
    ]
    messages = [
        {"type": "StreamingApiMessageStart", "dthread_id": "D_journey"},
        {
            "type": "StreamingApiMessageRunUpdate",
            "run_node": {
                "node_type": "MethodRun",
                "id": "R_phase",
                "parent_id": "R_root",
                "state": "Done",
                "run_type": "MethodRun",
                "action": {"expression": "QueryTool", "args": {}},
            },
        },
        {
            "type": "StreamingApiMessageRunUpdate",
            "run_node": {
                "node_type": "Run",
                "id": "R_root",
                "state": "Done",
                "run_type": "LouieAgent",
                "final_answer": "B_final",
            },
        },
        {"type": "StreamingApiMessageTrace", "payload": [20, 1, "done"]},
        {"type": "StreamingApiMessageTerminal", "success": True},
    ]
    return Response(
        "D_journey",
        elements,
        stream_messages=messages,
        include_reasoning=True,
    )


def test_response_cursor_and_history_have_reasoning_metadata_parity() -> None:
    response = _reasoning_response()
    cursor = Cursor(client=Mock())
    cursor._history.append(response)
    historical = cursor[-1]

    for result in (ResponseProxy(response), historical):
        assert result.text == "safe final"
        assert result.texts == ["safe final"]
        assert result.final_text == "safe final"
        assert result.reasoning_text == "<script>reason</script>"
        assert result.status == "succeeded"
        assert result.phases[0]["action"]["expression"] == "QueryTool"
        assert result.trace_events == [[20, 1, "done"]]

    assert cursor.response is response
    assert cursor.text == "safe final"
    assert cursor.texts == ["safe final"]
    assert cursor.reasoning_text == "<script>reason</script>"
    assert cursor.status == "succeeded"
    assert cursor.traces is False
    assert cursor.trace_events == [[20, 1, "done"]]
    # Server position order: B_reason precedes B_final on the wire. The previous
    # expectation ("text", "reasoning") encoded a defect — entries were grouped
    # by type, hoisting the final answer ahead of reasoning that arrived first.
    assert [element["type"] for element in cursor.elements] == [
        "reasoning",
        "text",
    ]
    assert [element["id"] for element in cursor.elements] == ["B_reason", "B_final"]


def test_cursor_texts_keep_tool_output_but_follow_explicit_final_pointer() -> None:
    response = _reasoning_response()
    response.elements.insert(
        1,
        {
            "id": "B_tool",
            "type": "TextElement",
            "text": "tool result",
            "during_run_id": "R_method",
        },
    )
    response.elements.append(response.elements.pop(0))
    cursor = Cursor(client=Mock())
    cursor._history.append(response)

    assert cursor.text == "safe final"
    assert cursor.texts == ["tool result", "safe final"]
    assert cursor[-1].text == "safe final"
    assert cursor[-1].texts == ["tool result", "safe final"]


def test_cursor_reports_terminal_and_lowercase_element_errors() -> None:
    failed = Response(
        "D_failed",
        [],
        stream_messages=[
            {
                "type": "StreamingApiMessageTerminal",
                "success": False,
                "error": "<script>retry after re-auth</script>",
            }
        ],
    )
    cursor = Cursor(client=Mock())
    cursor._history.append(failed)

    assert ResponseProxy(failed).has_errors is True
    assert cursor.has_errors is True
    assert cursor.terminal_error == "<script>retry after re-auth</script>"

    rendered_response = _render_response_html(failed)
    rendered_cursor = cursor._repr_html_()
    for rendered in (rendered_response, rendered_cursor):
        assert "<script>retry after re-auth</script>" not in rendered
        assert "&lt;script&gt;retry after re-auth&lt;/script&gt;" in rendered
    assert "lui.terminal_error" in rendered_cursor

    lowercase = Response("D_error", [{"type": "error", "message": "bad output"}])
    assert ResponseProxy(lowercase).errors == lowercase.errors
    assert ResponseProxy(lowercase).has_errors is True


def test_plain_cursor_forwards_per_call_and_session_reasoning_settings() -> None:
    client = Mock()
    client.add_cell.return_value = _reasoning_response()
    cursor = Cursor(client=client)

    with patch.object(cursor, "_in_jupyter", return_value=False):
        cursor("first", include_reasoning=True, traces=True)
        assert client.add_cell.call_args.kwargs["include_reasoning"] is True
        assert client.add_cell.call_args.kwargs["traces"] is True

        cursor.include_reasoning = True
        cursor("second")
        assert client.add_cell.call_args.kwargs["include_reasoning"] is True

        cursor("third", include_reasoning=False)
        assert client.add_cell.call_args.kwargs["include_reasoning"] is False

    assert cursor.include_reasoning is True
    assert cursor.new().include_reasoning is True


def test_jupyter_cursor_forwards_reasoning_and_retains_stream_messages() -> None:
    client = Mock()
    cursor = Cursor(client=client)
    result = {
        "dthread_id": "D_jupyter",
        "elements": _reasoning_response().elements,
        "stream_messages": _reasoning_response().stream_messages,
    }

    with (
        patch.object(cursor, "_in_jupyter", return_value=True),
        patch(
            "louieai.notebook.streaming.stream_response", return_value=result
        ) as stream,
    ):
        cursor("analyze", include_reasoning=True)

    assert stream.call_args.kwargs["include_reasoning"] is True
    assert cursor.text == "safe final"
    assert cursor.reasoning_text == "<script>reason</script>"
    assert cursor.stream_messages[-1]["type"] == "StreamingApiMessageTerminal"


def test_cursor_forwards_reasoning_to_all_upload_routes() -> None:
    client = Mock()
    client.upload_dataframe.return_value = _reasoning_response()
    client.upload_image.return_value = _reasoning_response()
    client.upload_binary.return_value = _reasoning_response()

    cases = [
        (pd.DataFrame({"x": [1]}), "upload_dataframe"),
        (b"\x89PNG\r\n\x1a\n", "upload_image"),
        (b"%PDF-1.4\n", "upload_binary"),
    ]
    for payload, method_name in cases:
        cursor = Cursor(client=client)
        with patch.object(cursor, "_in_jupyter", return_value=False):
            cursor("analyze", payload, include_reasoning=True)
        method = getattr(client, method_name)
        assert method.call_args.kwargs["include_reasoning"] is True
        method.reset_mock()


def test_streaming_display_labels_reasoning_phases_status_and_escapes_html() -> None:
    response = _reasoning_response()
    display = StreamingDisplay(include_reasoning=True)

    with patch("louieai.notebook.streaming.HAS_IPYTHON", False):
        for message in response.stream_messages[:1]:
            display.update(message)
        display.update(
            {
                "type": "StreamingApiMessageOutputUpdate",
                "position": 0,
                "payload": response.elements[0],
            }
        )
        display.update(
            {
                "type": "StreamingApiMessageOutputUpdate",
                "position": 1,
                "payload": response.elements[1],
            }
        )
        for message in response.stream_messages[1:]:
            display.update(message)

    rendered = display._render_html()

    assert "<b>Status:</b> succeeded" in rendered
    assert "Execution phases" in rendered
    assert "QueryTool: Done" in rendered
    assert "<summary><b>Reasoning</b></summary>" in rendered
    assert "&lt;script&gt;reason&lt;/script&gt;" in rendered
    assert "<script>reason</script>" not in rendered
