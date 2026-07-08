import os
import sys
import subprocess
import time
from pathlib import Path

def main():
    scripts_dir = Path(__file__).parent.resolve()
    project_root = scripts_dir.parent
    
    # Discover all test scripts in the scripts directory and its subdirectories
    test_scripts = []
    for root, _, files in os.walk(scripts_dir):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                test_scripts.append(Path(root) / file)
                
    if not test_scripts:
        print("No test scripts found.")
        return
        
    print(f"Found {len(test_scripts)} test scripts to run.\n")
    
    passed = []
    failed = []
    
    start_time = time.time()
    
    for script_path in sorted(test_scripts):
        rel_path = script_path.relative_to(project_root)
        print(f"=== Running: {rel_path} ===")
        
        # Run each script as a separate process
        result = subprocess.run([sys.executable, str(script_path)], cwd=str(project_root))
        
        if result.returncode == 0:
            print(f"--- SUCCESS: {rel_path} ---\n")
            passed.append(rel_path)
        else:
            print(f"--- FAILED: {rel_path} (Exit Code: {result.returncode}) ---\n")
            failed.append(rel_path)
            
    end_time = time.time()
    duration = end_time - start_time
    
    # Print summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests Run: {len(test_scripts)}")
    print(f"Passed:          {len(passed)}")
    print(f"Failed:          {len(failed)}")
    print(f"Duration:        {duration:.2f} seconds")
    print("=" * 60)
    
    if failed:
        print("\nFailed tests:")
        for f in failed:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("\nAll tests passed successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()
