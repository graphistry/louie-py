"""Credential-gated integration coverage for upload response parsing."""

import pandas as pd

from louieai.notebook.cursor import Cursor


def test_upload_parsing_integration(real_client):
    """Upload parsing retains elements, final text, and thread continuity."""
    lui = Cursor(client=real_client)
    df = pd.DataFrame(
        {
            "product": ["Widget A", "Widget B", "Widget C"],
            "price": [10.99, 15.49, 8.99],
            "quantity": [100, 75, 150],
        }
    )

    lui("Calculate the total inventory value", df)

    first_response = lui.response
    assert first_response is not None
    assert first_response.thread_id.startswith("D_")
    assert first_response.elements
    assert first_response.text is not None

    lui("What is the average price?", df)

    second_response = lui.response
    assert second_response is not None
    assert second_response.thread_id == first_response.thread_id
    assert second_response.elements
