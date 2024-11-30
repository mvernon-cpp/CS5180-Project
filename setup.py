import subprocess
import sys

def run_script(script_name):
    """Run another Python script."""
    try:
        print(f"Running {script_name}...")
        subprocess.run([sys.executable, script_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}: {e}")

if __name__ == "__main__":
    # Run the scripts in sequence
    print("CS5180 - Civil Engineering Search Engine")
    run_script("crawler.py")
    run_script("faculty_parser.py")    
    run_script("faculty_search.py")