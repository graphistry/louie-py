from louieai import LouieClient

# This should work with type checking
client: LouieClient = LouieClient()

# Test that type hints are available
def use_client(c: LouieClient) -> None:
    result = c.ask("test")
    # result should be typed as Any
    print(f"Result type: {type(result)}")

# This should fail type checking if types are exported correctly
wrong_type: LouieClient = "not a client"  # type error expected