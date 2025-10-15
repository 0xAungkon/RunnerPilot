#!/usr/bin/env python3
"""
Script to run tests with automatic logging and markdown generation.
"""
import subprocess
import sys
import os
from pathlib import Path

def run_tests_with_logging():
    """Run tests and generate markdown reports"""
    
    # Ensure we're in the right directory
    project_root = Path(__file__).parent.parent.parent
    os.chdir(project_root)
    
    print("🧪 Running tests with logging enabled...")
    
    # Create directory for reports
    (project_root / "logs").mkdir(exist_ok=True)
    (project_root / "logs" / "test_reports").mkdir(exist_ok=True)
    
    # Run pytest with verbose output
    cmd = ["python", "-m", "pytest", "-v", "--tb=short"]
    
    # Add any additional pytest args from command line
    if len(sys.argv) > 1:
        cmd.extend(sys.argv[1:])
    
    try:
        result = subprocess.run(cmd, check=False)
        exit_code = result.returncode
        
        print(f"\n✅ Tests completed with exit code: {exit_code}")
        
        # Check if markdown files were generated
        test_docs_dir = project_root / "logs" / "test_reports"
        md_files = list(test_docs_dir.glob("*.md"))
        
        if md_files:
            print(f"📝 Found {len(md_files)} markdown report files in {test_docs_dir}")
            for md_file in md_files:
                print(f"   - {md_file.name}")
        else:
            print("⚠️  No markdown report files found")
        
        return exit_code
        
    except KeyboardInterrupt:
        print("\n⏹️  Test execution interrupted by user")
        return 130
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1


if __name__ == "__main__":
    exit_code = run_tests_with_logging()
    sys.exit(exit_code)