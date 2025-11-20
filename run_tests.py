import pytest
import sys
import contextlib
import os

if __name__ == "__main__":
    # Use .txt to avoid gitignore
    log_file = "test_result.txt"
    
    # Remove if exists
    if os.path.exists(log_file):
        os.remove(log_file)

    with open(log_file, "w", encoding="utf-8") as f:
        with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
            # -v: verbose
            # --tb=long: full traceback
            # --color=no: no escape codes
            # Run all tests in the file
            result = pytest.main([
                "-v", 
                "--tb=long", 
                "--color=no", 
                "tests/test_guardrail_logic.py"
            ])
    
    # Read and print the result
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            print(f.read())
    except Exception as e:
        print(f"Failed to read log: {e}")
        
    sys.exit(result)
