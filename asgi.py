#!/usr/bin/env python3.11
"""
ASGI configuration for Driver Drowsiness Detection on PythonAnywhere
"""

import sys
import os

# Add your project directory to Python path
project_home = '/home/yourusername/Driver_Drowsy_Master'  # Replace 'yourusername' with your actual username
server_path = os.path.join(project_home, 'server')

if project_home not in sys.path:
    sys.path.insert(0, project_home)
if server_path not in sys.path:
    sys.path.insert(0, server_path)

# Change working directory to server folder
os.chdir(server_path)

# Import the FastAPI app
from driver_drowsiness import app

# ASGI application for PythonAnywhere
application = app