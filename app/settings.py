from os import environ as env


HOST = env.get("HOST", "localhost")
PORT = env.get("PORT", "8000")
BASEURL = env.get("BASEURL", f"http://{HOST}:{PORT}")
