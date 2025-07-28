#!/bin/bash
# Test environment check script

echo "=== Environment Check ==="
echo

echo "1. Current shell Python:"
which python
python --version
echo

echo "2. UV run Python:"
uv run which python
uv run python --version
echo

echo "3. Current shell pytest:"
which pytest
pytest --version 2>/dev/null || echo "pytest not found in shell"
echo

echo "4. UV run pytest:"
uv run which pytest
uv run pytest --version
echo

echo "5. Python path in UV run:"
uv run python -c "import sys; print('sys.executable:', sys.executable)"
echo

echo "6. Test import graphistry:"
uv run python -c "import graphistry; print(f'graphistry version: {graphistry.__version__}')"
echo

echo "7. UV Python pin:"
cat .python-version 2>/dev/null || echo "No .python-version file"
echo

echo "8. UV lock Python requirement:"
grep -A2 "requires-python" uv.lock | head -3