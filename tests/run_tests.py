"""
Test runner for Forever Siam Fashion Boutique chatbot.
Executes all test cases and generates a report.
"""

import unittest
import sys
import os
from datetime import datetime
from test_config import setup_test_environment

def run_tests():
    """Run all tests and generate report"""
    # Set up test environment
    setup_test_environment()
    
    # Create test suite
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern="test_*.py")
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate report
    generate_report(result)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1

def generate_report(result):
    """Generate test report"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("\n" + "="*50)
    print(f"Test Report - {timestamp}")
    print("="*50)
    
    # Summary
    print(f"\nTotal Tests: {result.testsRun}")
    print(f"Successful: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    # Failures
    if result.failures:
        print("\nFailures:")
        for failure in result.failures:
            print(f"\n{failure[0]}")
            print(failure[1])
    
    # Errors
    if result.errors:
        print("\nErrors:")
        for error in result.errors:
            print(f"\n{error[0]}")
            print(error[1])
    
    print("\n" + "="*50)

if __name__ == "__main__":
    sys.exit(run_tests()) 