import subprocess
import os
import sys

def run_tests():
    """Run tests with coverage."""
    print("=== Running Tests with Coverage ===")
    
    # Create a directory for coverage reports
    if not os.path.exists('coverage_reports'):
        os.makedirs('coverage_reports')
    
    # Run tests with coverage
    try:
        result = subprocess.run([
            'pytest', 
            '--cov=app', 
            '--cov-report=term', 
            '--cov-report=html:coverage_reports/html',
            '--cov-report=xml:coverage_reports/coverage.xml',
            'tests/'
        ], check=True)
        
        print("\n=== Tests completed successfully! ===")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"\n=== Tests failed with exit code {e.returncode} ===")
        return e.returncode

if __name__ == "__main__":
    sys.exit(run_tests())