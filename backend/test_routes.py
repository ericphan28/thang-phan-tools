"""Test if settings routes are properly registered"""
from app.main_simple import app

print(f"Total routes: {len(app.routes)}\n")

settings_routes = [r for r in app.routes if 'settings' in str(r.path).lower()]
print(f"Settings routes found: {len(settings_routes)}")

for route in settings_routes:
    methods = getattr(route, 'methods', 'N/A')
    print(f"  {route.path} [{methods}] -> {route.name}")

print("\n\nFirst 30 routes:")
for i, route in enumerate(app.routes[:30]):
    methods = getattr(route, 'methods', set())
    print(f"{i+1}. {route.path} [{methods}]")
