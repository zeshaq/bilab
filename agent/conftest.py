import os
import sys

# make the repo root importable so `from agent.agent import ask` resolves
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
