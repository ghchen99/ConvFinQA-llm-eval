#!/usr/bin/env python3
"""
Test runner script for the Financial QA Predictor project.

This script provides convenient commands for running different types of tests
and generating coverage reports.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path


def run_command(cmd, description=""):
    """Run a shell command and handle errors."""
    if description:
        print(f"\n🔄 {description}")
        print("=" * 50)
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False, text=True)
    
    if result.returncode != 0:
        print(f"❌ Command failed with exit code {result.returncode}")
        sys.exit(1)
    else:
        print(f"✅ {description or 'Command'} completed successfully")
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Run tests for Financial QA Predictor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py --unit             # Run only unit tests
  python run_tests.py --integration      # Run only integration tests
  python run_tests.py --coverage         # Run tests with coverage report
  python run_tests.py --fast             # Run tests in parallel (faster)
  python run_tests.py --file test_settings.py  # Run specific test file
        """
    )
    
    parser.add_argument(
        '--unit', 
        action='store_true',
        help='Run only unit tests'
    )
    
    parser.add_argument(
        '--integration', 
        action='store_true',
        help='Run only integration tests'
    )
    
    parser.add_argument(
        '--slow', 
        action='store_true',
        help='Include slow tests'
    )
    
    parser.add_argument(
        '--coverage', 
        action='store_true',
        help='Generate detailed coverage report'
    )
    
    parser.add_argument(
        '--fast', 
        action='store_true',
        help='Run tests in parallel for faster execution'
    )
    
    parser.add_argument(
        '--file', 
        type=str,
        help='Run specific test file'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Quiet output'
    )
    
    parser.add_argument(
        '--failfast', '-x',
        action='store_true',
        help='Stop on first failure'
    )
    
    parser.add_argument(
        '--lf', '--last-failed',
        action='store_true',
        help='Run last failed tests only'
    )
    
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean coverage data and cache before running'
    )
    
    args = parser.parse_args()
    
    # Change to project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Clean up if requested
    if args.clean:
        cleanup_commands = [
            ['rm', '-rf', '.pytest_cache'],
            ['rm', '-rf', 'htmlcov'],
            ['rm', '-f', '.coverage'],
            ['rm', '-f', 'coverage.xml']
        ]
        
        for cmd in cleanup_commands:
            try:
                subprocess.run(cmd, capture_output=True)
            except:
                pass  # Ignore errors for cleanup
        
        print("🧹 Cleaned up previous test artifacts")
    
    # Build pytest command
    cmd = ['python', '-m', 'pytest']
    
    # Add test selection
    if args.unit:
        cmd.extend(['-m', 'unit'])
    elif args.integration:
        cmd.extend(['-m', 'integration'])
    elif args.slow:
        cmd.extend(['-m', 'slow'])
    elif not args.slow:
        cmd.extend(['-m', 'not slow'])
    
    # Add specific file if specified
    if args.file:
        test_file = f"tests/{args.file}" if not args.file.startswith('tests/') else args.file
        cmd.append(test_file)
    
    # Add output options
    if args.verbose:
        cmd.append('-v')
    elif args.quiet:
        cmd.append('-q')
    
    # Add execution options
    if args.failfast:
        cmd.append('-x')
    
    if args.lf:
        cmd.append('--lf')
    
    if args.fast:
        cmd.extend(['-n', 'auto'])  # Requires pytest-xdist
    
    # Add coverage options
    if args.coverage:
        cmd.extend([
            '--cov=src',
            '--cov-report=term-missing',
            '--cov-report=html:htmlcov',
            '--cov-report=xml'
        ])
    
    # Run the tests
    try:
        run_command(cmd, "Running tests")
        
        # Print coverage report location if coverage was generated
        if args.coverage:
            print(f"\n📊 Coverage reports generated:")
            print(f"  - HTML: file://{project_root}/htmlcov/index.html")
            print(f"  - XML: {project_root}/coverage.xml")
        
        print(f"\n🎉 All tests completed successfully!")
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Tests interrupted by user")
        sys.exit(1)


def install_dependencies():
    """Install test dependencies."""
    print("📦 Installing test dependencies...")
    
    cmd = [
        'pip', 'install', '-r', 'requirements-test.txt'
    ]
    
    run_command(cmd, "Installing test dependencies")


def check_environment():
    """Check if the test environment is properly set up."""
    print("🔍 Checking test environment...")
    
    # Check if pytest is installed
    try:
        import pytest
        print(f"✅ pytest {pytest.__version__} is installed")
    except ImportError:
        print("❌ pytest is not installed")
        print("Run: pip install -r requirements-test.txt")
        return False
    
    # Check if src directory exists
    if not Path('src').exists():
        print("❌ src directory not found")
        return False
    
    print("✅ Test environment looks good")
    return True


if __name__ == '__main__':
    # Check if we should install dependencies
    if len(sys.argv) > 1 and sys.argv[1] == 'install':
        install_dependencies()
        sys.exit(0)
    
    # Check if we should check environment
    if len(sys.argv) > 1 and sys.argv[1] == 'check':
        if check_environment():
            sys.exit(0)
        else:
            sys.exit(1)
    
    # Run main test function
    main()