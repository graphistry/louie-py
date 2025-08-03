"""Performance benchmarks for notebook API trace overhead."""

import os
import time
from statistics import mean, stdev
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from louieai.notebook import Cursor


class MockResponse:
    """Mock response with realistic data."""

    def __init__(self, include_traces=False):
        self.thread_id = "test-thread-123"
        self.text_elements = [
            {"type": "TextElement", "content": "Analysis complete. " * 100}
        ]
        self.dataframe_elements = [
            {
                "type": "DfElement",
                "table": pd.DataFrame(
                    {
                        "col1": range(1000),
                        "col2": range(1000, 2000),
                        "col3": ["value"] * 1000,
                    }
                ),
            }
        ]
        self.graph_elements = []
        self.elements = []

        if include_traces:
            # Simulate trace data overhead
            self.trace_elements = [
                {
                    "type": "TraceElement",
                    "content": "Step " + str(i) + ": " + ("x" * 500),
                }
                for i in range(50)  # 50 trace steps
            ]


@pytest.mark.skipif(
    os.environ.get("CI") == "true",
    reason="Performance tests are unreliable in CI due to variable system load",
)
class TestTraceOverhead:
    """Benchmark trace overhead."""

    def setup_method(self):
        """Reset state before each test."""
        import louieai.notebook

        louieai.notebook._global_cursor = None

    @patch("louieai.notebook.cursor.LouieClient")
    def test_query_performance_without_traces(self, mock_client_class):
        """Benchmark query performance without traces."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Mock responses without traces
        mock_client.add_cell.return_value = MockResponse(include_traces=False)

        cursor = Cursor(client=mock_client)

        # Warm up
        cursor("warmup query")

        # Benchmark
        times = []
        for _ in range(100):
            start = time.perf_counter()
            cursor("test query")
            _ = cursor.df  # Access data
            _ = cursor.text
            end = time.perf_counter()
            times.append(end - start)

        avg_time = mean(times) * 1000  # Convert to ms
        std_dev = stdev(times) * 1000

        print(f"\nWithout traces: {avg_time:.2f}ms ± {std_dev:.2f}ms")

        # Store for comparison
        self.baseline_time = avg_time

        # Should be fast
        assert avg_time < 10  # Less than 10ms average

    @patch("louieai.notebook.cursor.LouieClient")
    def test_query_performance_with_traces(self, mock_client_class):
        """Benchmark query performance with traces."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Mock responses with traces
        mock_client.add_cell.return_value = MockResponse(include_traces=True)

        cursor = Cursor(client=mock_client)
        cursor.traces = True

        # Warm up
        cursor("warmup query")

        # Benchmark
        times = []
        for _ in range(100):
            start = time.perf_counter()
            cursor("test query")
            _ = cursor.df  # Access data
            _ = cursor.text
            end = time.perf_counter()
            times.append(end - start)

        avg_time = mean(times) * 1000  # Convert to ms
        std_dev = stdev(times) * 1000

        print(f"With traces: {avg_time:.2f}ms ± {std_dev:.2f}ms")

        # Should still be reasonable
        assert avg_time < 20  # Less than 20ms average

    @patch("louieai.notebook.cursor.LouieClient")
    def test_history_performance(self, mock_client_class):
        """Benchmark history access performance."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_client.add_cell.return_value = MockResponse(include_traces=False)

        cursor = Cursor(client=mock_client)

        # Fill history to max (100 items)
        for i in range(100):
            cursor(f"query {i}")

        # Benchmark history access
        times = []
        for _ in range(1000):
            start = time.perf_counter()
            # Access various history items
            _ = cursor[-1].df
            _ = cursor[-50].text
            _ = cursor[-99].elements
            end = time.perf_counter()
            times.append(end - start)

        avg_time = mean(times) * 1000  # Convert to ms
        std_dev = stdev(times) * 1000

        print(f"\nHistory access (100 items): {avg_time:.2f}ms ± {std_dev:.2f}ms")

        # History access should be very fast
        assert avg_time < 1  # Less than 1ms average

    @patch("louieai.notebook.cursor.LouieClient")
    def test_memory_usage_with_history(self, mock_client_class):
        """Test memory usage with full history."""
        import sys

        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Create large responses
        large_response = MockResponse(include_traces=True)
        large_response.dataframe_elements.append(
            {
                "type": "DfElement",
                "table": pd.DataFrame(
                    {
                        f"col{i}": range(10000)
                        for i in range(20)  # 20 columns, 10k rows
                    }
                ),
            }
        )

        mock_client.add_cell.return_value = large_response

        cursor = Cursor(client=mock_client)

        # Measure baseline
        sys.getsizeof(cursor._history)  # Baseline measurement

        # Fill history
        for i in range(100):
            cursor(f"query {i}")

        # Measure after
        final_size = sys.getsizeof(cursor._history)

        # History should be bounded
        print(f"\nHistory memory: {final_size / 1024:.1f}KB for 100 items")

        # Deque should maintain constant size
        assert len(cursor._history) == 100

        # Memory should be reasonable (less than 10MB for history)
        assert final_size < 10 * 1024 * 1024

    @patch("louieai.notebook.cursor.LouieClient")
    def test_dataframe_access_performance(self, mock_client_class):
        """Benchmark DataFrame access patterns."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Create response with multiple dataframes
        response = MockResponse(include_traces=False)
        for _ in range(10):
            response.dataframe_elements.append(
                {"type": "DfElement", "table": pd.DataFrame({"data": range(1000)})}
            )

        mock_client.add_cell.return_value = response

        cursor = Cursor(client=mock_client)
        cursor("test query")

        # Benchmark df access
        times = []
        for _ in range(1000):
            start = time.perf_counter()
            _ = cursor.df  # Should return first df quickly
            end = time.perf_counter()
            times.append(end - start)

        avg_time = mean(times) * 1000  # Convert to ms
        print(f"\nSingle df access: {avg_time:.4f}ms")

        # Benchmark dfs access
        times = []
        for _ in range(1000):
            start = time.perf_counter()
            _ = cursor.dfs  # Should extract all dfs
            end = time.perf_counter()
            times.append(end - start)

        avg_time = mean(times) * 1000  # Convert to ms
        print(f"All dfs access: {avg_time:.4f}ms")

        # Both should be fast
        assert avg_time < 1  # Less than 1ms


@pytest.mark.skipif(
    os.environ.get("CI") == "true",
    reason="Performance tests are unreliable in CI due to variable system load",
)
class TestOverheadComparison:
    """Compare notebook API overhead vs direct client."""

    @patch("louieai.notebook.cursor.LouieClient")
    def test_notebook_vs_client_overhead(self, mock_client_class):
        """Compare notebook API overhead to direct client usage."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        response = MockResponse(include_traces=False)
        mock_client.add_cell.return_value = response

        # Benchmark direct client
        direct_times = []
        for _ in range(100):
            start = time.perf_counter()
            resp = mock_client.add_cell("", "test query", traces=False)
            _ = resp.dataframe_elements[0]["table"]
            _ = resp.text_elements[0]["content"]
            end = time.perf_counter()
            direct_times.append(end - start)

        # Benchmark notebook API
        cursor = Cursor(client=mock_client)
        notebook_times = []
        for _ in range(100):
            start = time.perf_counter()
            cursor("test query")
            _ = cursor.df
            _ = cursor.text
            end = time.perf_counter()
            notebook_times.append(end - start)

        direct_avg = mean(direct_times) * 1000
        notebook_avg = mean(notebook_times) * 1000
        overhead = ((notebook_avg - direct_avg) / direct_avg) * 100

        print(f"\nDirect client: {direct_avg:.2f}ms")
        print(f"Notebook API: {notebook_avg:.2f}ms")
        print(f"Overhead: {overhead:.1f}%")

        # Overhead should be reasonable
        # Note: Notebook API adds trace management and display features
        # which can add overhead, especially for small operations
        assert overhead < 100  # Less than 100% overhead


if __name__ == "__main__":
    # Run benchmarks directly
    test = TestTraceOverhead()
    test.setup_method()

    print("Running performance benchmarks...")
    test.test_query_performance_without_traces()
    test.test_query_performance_with_traces()
    test.test_history_performance()
    test.test_memory_usage_with_history()
    test.test_dataframe_access_performance()

    comparison = TestOverheadComparison()
    comparison.test_notebook_vs_client_overhead()

    print("\nAll benchmarks completed!")
