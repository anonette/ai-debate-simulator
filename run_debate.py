import streamlit as st
import subprocess
import sys

def install_requirements():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit", "asyncio", "python-dotenv"])

try:
    import streamlit as st
except ImportError:
    install_requirements()
    import streamlit as st

# Now run the debate app
if __name__ == "__main__":
    print("Starting debate app...")
    subprocess.run(["streamlit", "run", "debate_app.py"]) 