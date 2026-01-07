"""
Integration tests for compute execution functions.

Tests run_python_file_on_databricks with a real cluster.
"""

import tempfile
import pytest
from pathlib import Path

from databricks_tools_core.compute import run_python_file_on_databricks

# Test cluster ID
CLUSTER_ID = "0709-132523-cnhxf2p6"


@pytest.mark.integration
class TestRunPythonFileOnDatabricks:
    """Tests for run_python_file_on_databricks function."""

    def test_simple_print(self):
        """Should execute a simple Python file and return output."""
        code = """
print("Hello from Databricks!")
print(1 + 1)
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            temp_path = f.name

        try:
            result = run_python_file_on_databricks(
                cluster_id=CLUSTER_ID,
                file_path=temp_path,
                timeout=120
            )

            print(f"\n=== Execution Result ===")
            print(f"Success: {result.success}")
            print(f"Output: {result.output}")
            print(f"Error: {result.error}")

            assert result.success, f"Execution failed: {result.error}"
            assert "Hello from Databricks!" in result.output

        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_spark_code(self):
        """Should execute Spark code and return results."""
        code = """
# Test Spark is available
from pyspark.sql import SparkSession
spark = SparkSession.builder.getOrCreate()

df = spark.range(5)
print(f"Row count: {df.count()}")
print("Spark execution successful!")
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            temp_path = f.name

        try:
            result = run_python_file_on_databricks(
                cluster_id=CLUSTER_ID,
                file_path=temp_path,
                timeout=120
            )

            print(f"\n=== Spark Execution Result ===")
            print(f"Success: {result.success}")
            print(f"Output: {result.output}")
            print(f"Error: {result.error}")

            assert result.success, f"Spark execution failed: {result.error}"
            assert "Row count: 5" in result.output

        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_error_handling(self):
        """Should capture Python errors with details."""
        code = """
# This will raise an error
x = 1 / 0
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            temp_path = f.name

        try:
            result = run_python_file_on_databricks(
                cluster_id=CLUSTER_ID,
                file_path=temp_path,
                timeout=120
            )

            print(f"\n=== Error Handling Result ===")
            print(f"Success: {result.success}")
            print(f"Output: {result.output}")
            print(f"Error: {result.error}")

            assert not result.success, "Should have failed with division by zero"
            assert result.error is not None
            assert "ZeroDivisionError" in result.error or "division" in result.error.lower()

        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_file_not_found(self):
        """Should handle missing file gracefully."""
        result = run_python_file_on_databricks(
            cluster_id=CLUSTER_ID,
            file_path="/nonexistent/path/to/file.py",
            timeout=120
        )

        print(f"\n=== File Not Found Result ===")
        print(f"Success: {result.success}")
        print(f"Error: {result.error}")

        assert not result.success
        assert "not found" in result.error.lower() or "nonexistent" in result.error.lower()


if __name__ == "__main__":
    # Run tests directly for quick debugging
    test = TestRunPythonFileOnDatabricks()

    print("\n" + "="*50)
    print("Running: test_simple_print")
    print("="*50)
    try:
        test.test_simple_print()
        print("✓ PASSED")
    except Exception as e:
        print(f"✗ FAILED: {e}")

    print("\n" + "="*50)
    print("Running: test_spark_code")
    print("="*50)
    try:
        test.test_spark_code()
        print("✓ PASSED")
    except Exception as e:
        print(f"✗ FAILED: {e}")

    print("\n" + "="*50)
    print("Running: test_error_handling")
    print("="*50)
    try:
        test.test_error_handling()
        print("✓ PASSED")
    except Exception as e:
        print(f"✗ FAILED: {e}")

    print("\n" + "="*50)
    print("Running: test_file_not_found")
    print("="*50)
    try:
        test.test_file_not_found()
        print("✓ PASSED")
    except Exception as e:
        print(f"✗ FAILED: {e}")
