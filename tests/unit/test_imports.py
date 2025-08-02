"""Test module imports and public API."""


class TestImports:
    """Test that the public API is correct."""

    def test_main_imports(self):
        """Test main module imports work correctly."""
        import louieai

        # These should be available
        assert hasattr(louieai, "louie")
        assert hasattr(louieai, "Cursor")
        assert hasattr(louieai, "Response")
        assert hasattr(louieai, "Thread")
        assert hasattr(louieai, "__version__")

        # These should NOT be available
        assert not hasattr(louieai, "LouieClient")
        assert not hasattr(louieai, "AuthManager")
        assert not hasattr(louieai, "lui")

    def test_louie_function(self):
        """Test louie() factory function."""
        from louieai import Cursor, louie

        # Should create cursor
        cursor = louie()
        assert isinstance(cursor, Cursor)
        assert callable(cursor)

    def test_cursor_class(self):
        """Test Cursor class is available."""
        from louieai import Cursor

        # Should be able to instantiate
        cursor = Cursor()
        assert callable(cursor)
        assert hasattr(cursor, "df")
        assert hasattr(cursor, "text")
        assert hasattr(cursor, "traces")

    def test_response_thread_classes(self):
        """Test Response and Thread classes are available."""
        from louieai import Response, Thread

        # Should be able to instantiate Thread
        thread = Thread(id="test_id", name="test_name")
        assert thread.id == "test_id"
        assert thread.name == "test_name"

        # Response requires proper initialization
        assert Response is not None

    def test_global_import(self):
        """Test global singleton import."""
        # Reset the global singleton before test
        import louieai.notebook

        louieai.notebook._global_cursor = None

        from louieai.globals import lui

        # Should be the singleton
        assert callable(lui)
        assert hasattr(lui, "df")
        assert hasattr(lui, "text")

    def test_no_internal_imports(self):
        """Test internal classes are not in public API."""
        import louieai

        # LouieClient should not be in the public API
        assert not hasattr(louieai, "LouieClient")
        assert "LouieClient" not in louieai.__all__

        # But can import directly if needed (for tests)
        from louieai._client import LouieClient

        assert LouieClient is not None

    def test_notebook_module(self):
        """Test notebook module exports."""
        from louieai import notebook
        from louieai.notebook import Cursor

        # Should export Cursor
        assert Cursor is not None
        assert "Cursor" in notebook.__all__

        # Should NOT export lui in __all__
        assert "lui" not in notebook.__all__

    def test_all_exports(self):
        """Test __all__ exports match reality."""
        import louieai

        # Check __all__ exists
        assert hasattr(louieai, "__all__")

        # Check all items in __all__ are actually available
        for name in louieai.__all__:
            assert hasattr(louieai, name), f"{name} in __all__ but not available"

        # Check expected items are in __all__
        expected = ["louie", "Cursor", "Response", "Thread", "__version__"]
        for name in expected:
            assert name in louieai.__all__, f"{name} should be in __all__"
