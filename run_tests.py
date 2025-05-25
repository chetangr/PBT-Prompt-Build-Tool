#!/usr/bin/env python3
"""Test runner script for PBT with various test configurations"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle output"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    print(f"Running: {' '.join(cmd)}")
    print()
    
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Run PBT tests")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--failfast", "-x", action="store_true", help="Stop on first failure")
    parser.add_argument("--specific", "-k", help="Run specific test pattern")
    parser.add_argument("--no-cov", action="store_true", help="Disable coverage")
    
    args = parser.parse_args()
    
    # Base pytest command
    cmd = ["pytest"]
    
    # Add verbosity
    if args.verbose:
        cmd.append("-vv")
    else:
        cmd.append("-v")
    
    # Add failfast
    if args.failfast:
        cmd.append("-x")
    
    # Add specific test pattern
    if args.specific:
        cmd.extend(["-k", args.specific])
    
    # Test selection
    if args.unit:
        cmd.extend(["-m", "unit", "tests/unit"])
    elif args.integration:
        cmd.extend(["-m", "integration", "tests/integration"])
    else:
        # Run all tests
        cmd.append("tests/")
    
    # Coverage options
    if not args.no_cov:
        cmd.extend([
            "--cov=pbt",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov"
        ])
        
        if args.coverage:
            cmd.append("--cov-report=xml")
    
    # Run the tests
    success = run_command(cmd, "Running PBT Tests")
    
    # Generate coverage report
    if not args.no_cov and success:
        print("\n📊 Coverage Report Generated:")
        print("   - Terminal: See output above")
        print("   - HTML: htmlcov/index.html")
        if args.coverage:
            print("   - XML: coverage.xml")
    
    # Run specific test suites if requested
    if not args.unit and not args.integration and not args.specific:
        print("\n" + "="*60)
        print("📋 Test Summary")
        print("="*60)
        
        # Quick test counts
        unit_count = len(list(Path("tests/unit").glob("test_*.py")))
        integration_count = len(list(Path("tests/integration").glob("test_*.py")))
        
        print(f"Unit tests: {unit_count} files")
        print(f"Integration tests: {integration_count} files")
        
        if success:
            print("\n✅ All tests passed!")
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()