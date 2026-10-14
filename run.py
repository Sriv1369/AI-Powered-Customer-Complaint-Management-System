import subprocess
import sys


def main():
    print("=====================================================================")
    print("  AI-Powered Customer Complaint Management System (Full Python)     ")
    print("=====================================================================")
    print("Starting Streamlit Web Interface...\n")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    main()
