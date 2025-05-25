#!/bin/bash
# Demo script showing how to run PBT tests

echo "🧪 PBT Test Suite Demo"
echo "===================="
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest not found. Please install test dependencies:"
    echo "   pip install -r requirements-test.txt"
    exit 1
fi

echo "📋 Available test commands:"
echo ""
echo "1. Run all tests:"
echo "   pytest"
echo ""
echo "2. Run with coverage:"
echo "   pytest --cov=pbt --cov-report=html"
echo ""
echo "3. Run unit tests only:"
echo "   pytest tests/unit/"
echo ""
echo "4. Run integration tests only:"
echo "   pytest tests/integration/"
echo ""
echo "5. Run specific test file:"
echo "   pytest tests/unit/test_convert_command.py"
echo ""
echo "6. Run tests matching pattern:"
echo "   pytest -k 'convert'"
echo ""
echo "7. Run with verbose output:"
echo "   pytest -v"
echo ""
echo "8. Using the test runner script:"
echo "   python run_tests.py --help"
echo ""
echo "===================="
echo ""

# Run a simple test to verify setup
echo "🔍 Running example test to verify setup..."
echo ""
pytest tests/test_example.py -v --tb=short

echo ""
echo "✅ Test setup verified! You can now run the full test suite."