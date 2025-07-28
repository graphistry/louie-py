#!/bin/bash
# test-install-common.sh - Common functions for installation tests

# Test Python imports and basic functionality
test_python_imports() {
    local test_dir="$1"
    
    print_step "Testing Python imports"
    cd "$test_dir"
    
    python -c "
import sys
print(f'Python: {sys.version}')

try:
    import louieai
    print(f'✅ Successfully imported louieai version {louieai.__version__}')
    
    from louieai import LouieClient
    print('✅ Successfully imported LouieClient')
    
    # Test instantiation (won't work without auth, but should not import error)
    try:
        client = LouieClient()
        print('✅ LouieClient instantiation works (will fail on API calls without auth)')
    except Exception as e:
        if 'import' in str(e).lower():
            raise
        print(f'✅ LouieClient instantiation failed as expected without auth: {type(e).__name__}')
    
except ImportError as e:
    print(f'❌ Import failed: {e}')
    sys.exit(1)
except Exception as e:
    print(f'❌ Unexpected error: {e}')
    sys.exit(1)
"
}

# Build package and return wheel path
build_package() {
    local build_dir="$1"
    
    print_step "Building package"
    cd "$build_dir"
    
    # Clean any previous builds
    rm -rf dist/
    
    # Build the package
    python -m build --wheel . || print_error "Build failed"
    
    # Find the wheel file
    WHEEL_FILE=$(find dist -name "*.whl" | head -n 1)
    if [ -z "$WHEEL_FILE" ]; then
        print_error "No wheel file found after build"
    fi
    
    print_success "Built wheel: $(basename "$WHEEL_FILE")"
    echo "$WHEEL_FILE"
}