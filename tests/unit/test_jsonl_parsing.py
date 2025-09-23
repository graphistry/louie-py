"""Unit tests for JSONL response parsing, especially concatenated JSON fix."""

from louieai._client import LouieClient, Response


class TestJSONLParsing:
    """Test JSONL parsing handles various server response formats."""

    def test_parse_standard_jsonl(self):
        """Test parsing standard JSONL with one object per line."""
        client = LouieClient()

        response_text = """{"dthread_id":"D_test123"}
{"payload":{"id":"B_1","type":"TextElement","text":"Hello world"}}
{"payload":{"id":"B_2","type":"DfElement","df_id":"DF_abc","metadata":{"shape":[3,2]}}}"""

        result = client._parse_jsonl_response(response_text)

        assert result["dthread_id"] == "D_test123"
        assert len(result["elements"]) == 2
        assert result["elements"][0]["type"] == "TextElement"
        assert result["elements"][0]["text"] == "Hello world"
        assert result["elements"][1]["type"] == "DfElement"
        assert result["elements"][1]["df_id"] == "DF_abc"

    def test_parse_concatenated_json(self):
        """Test parsing when server concatenates JSON objects on same line."""
        client = LouieClient()

        # This is what the server actually sends sometimes
        response_text = (
            '{"dthread_id":"D_test123"}'
            '{"position":0,"payload":{"id":"B_1","type":"TextElement",'
            '"text":"Calculate total"}}'
        )

        result = client._parse_jsonl_response(response_text)

        assert result["dthread_id"] == "D_test123"
        assert len(result["elements"]) == 1
        assert result["elements"][0]["type"] == "TextElement"
        assert result["elements"][0]["text"] == "Calculate total"

    def test_parse_mixed_format(self):
        """Test parsing mix of concatenated and normal lines."""
        client = LouieClient()

        response_text = (
            '{"dthread_id":"D_test123"}'
            '{"payload":{"id":"B_1","type":"TextElement","text":"First"}}\n'
            '{"payload":{"id":"B_2","type":"TextElement","text":"Second"}}\n'
            '{"payload":{"id":"B_1","type":"TextElement","text":"First updated"}}'
        )

        result = client._parse_jsonl_response(response_text)

        assert result["dthread_id"] == "D_test123"
        assert len(result["elements"]) == 2
        # Check text update was applied
        assert result["elements"][0]["text"] == "First updated"
        assert result["elements"][1]["text"] == "Second"

    def test_response_text_property(self):
        """Test Response.text property extracts text correctly."""
        elements = [
            {"id": "B_1", "type": "TextElement", "text": "This is the answer"},
            {"id": "B_2", "type": "DfElement", "df_id": "DF_123"},
        ]

        response = Response("D_test", elements)

        assert response.text == "This is the answer"
        assert response.thread_id == "D_test"
        assert len(response.text_elements) == 1
        assert len(response.dataframe_elements) == 1

    def test_response_text_with_value_field(self):
        """Test Response.text handles 'value' field as fallback."""
        elements = [{"id": "B_1", "type": "TextElement", "value": "Using value field"}]

        response = Response("D_test", elements)
        assert response.text == "Using value field"

    def test_response_text_none_when_no_text(self):
        """Test Response.text returns None when no text elements."""
        elements = [{"id": "B_1", "type": "DfElement", "df_id": "DF_123"}]

        response = Response("D_test", elements)
        assert response.text is None

    def test_parse_upload_response_real_example(self):
        """Test parsing real upload response from server."""
        client = LouieClient()

        # Real response captured from server
        response_text = (
            '{"dthread_id":"D_i2uvefHK3HjAyL1s_bOq"}'
            '{"position":0,"payload":{"id":"B_7AGP6ZG4","type":"TextElement",'
            '"parent":"B_laza0Wy4","text":"Calculate the total inventory value '
            '(sum of price * quantity for each product)"}}'
        )

        result = client._parse_jsonl_response(response_text)

        assert result["dthread_id"] == "D_i2uvefHK3HjAyL1s_bOq"
        assert len(result["elements"]) == 1
        assert "Calculate the total inventory value" in result["elements"][0]["text"]

        # Test Response object
        response = Response(result["dthread_id"], result["elements"])
        assert response.thread_id == "D_i2uvefHK3HjAyL1s_bOq"
        assert "Calculate the total inventory value" in response.text

    def test_parse_empty_response(self):
        """Test parsing empty response."""
        client = LouieClient()

        result = client._parse_jsonl_response("")
        assert result["dthread_id"] is None
        assert len(result["elements"]) == 0

    def test_parse_malformed_json_skipped(self):
        """Test malformed JSON lines are skipped."""
        client = LouieClient()

        response_text = """{"dthread_id":"D_test123"}
{malformed json here}
{"payload":{"id":"B_1","type":"TextElement","text":"Valid element"}}"""

        result = client._parse_jsonl_response(response_text)

        assert result["dthread_id"] == "D_test123"
        assert len(result["elements"]) == 1
        assert result["elements"][0]["text"] == "Valid element"
