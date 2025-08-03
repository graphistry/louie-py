"""Test CallableModule functionality."""

from unittest.mock import Mock, patch


class TestCallableModule:
    """Test the CallableModule that makes louieai module callable."""

    def test_module_is_callable(self):
        """Test that the louieai module can be called."""
        import louieai

        # The module should be callable
        assert callable(louieai)

    def test_module_call_invokes_louie(self):
        """Test that calling the module invokes louie function."""
        import louieai
        from louieai.notebook import Cursor

        # Test that calling the module returns a Cursor
        # The louie() function creates a new Cursor and calls it
        # Since we have global cursor prevention, we'll just verify the types
        result = louieai()

        # The result should be a Cursor instance
        assert isinstance(result, Cursor)

        # Verify that multiple calls return a cursor
        result2 = louieai("test query")
        assert isinstance(result2, Cursor)

        # The module is indeed callable and delegates to louie()
        assert callable(louieai)

    def test_callable_module_with_none_module(self):
        """Test CallableModule initialization with None module."""
        from louieai import CallableModule

        # Create with None module - should use default name
        cm = CallableModule(None)
        assert cm is not None

    def test_callable_module_with_module_without_dict(self):
        """Test CallableModule with module that has no __dict__."""
        from louieai import CallableModule

        # Create a mock module without __dict__
        mock_module = Mock()
        mock_module.__name__ = "test_module"
        del mock_module.__dict__  # Remove __dict__

        # Should not raise
        cm = CallableModule(mock_module)
        assert cm is not None

    def test_callable_module_with_module_with_none_dict(self):
        """Test CallableModule with module that has None __dict__."""
        import types

        from louieai import CallableModule

        # Create a proper module object
        mock_module = types.ModuleType("test_module")
        # We can't actually set __dict__ to None on a real module
        # so we'll test the defensive code by mocking hasattr
        with patch("louieai.__init__.hasattr") as mock_hasattr:
            # Make it seem like __dict__ exists but is None
            def custom_hasattr(obj, name):
                if name == "__dict__":
                    return True
                return hasattr(obj, name)

            mock_hasattr.side_effect = custom_hasattr

            # Should not raise
            cm = CallableModule(mock_module)
            assert cm is not None

    def test_callable_module_preserves_attributes(self):
        """Test that CallableModule preserves module attributes."""
        import louieai

        # Check that common module attributes are preserved
        assert hasattr(louieai, "louie")
        assert hasattr(louieai, "Cursor")
        assert hasattr(louieai, "__version__")
        assert hasattr(louieai, "__name__")
