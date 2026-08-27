---
name: Flask preview routing
description: Replit preview forwarding behavior for a Flask app in an artifact workspace
---

When a Flask app runs as a standalone workflow in an artifact workspace, a healthy
listener on `0.0.0.0:$PORT` is not always enough for the root preview to reach
it. The application router can send the root request to a registered artifact
service instead of the standalone workflow.

**Why:** The Flask workflow was healthy on port 5000 while the preview returned
404 until the registered root artifact route forwarded non-API requests to Flask.

**How to apply:** Verify the actual proxied root request, not only the workflow
port. Keep Flask bound to `0.0.0.0` and `$PORT`; if the workspace has a
registered artifact router, make sure its root preview path reaches the Flask
service while preserving any API paths.