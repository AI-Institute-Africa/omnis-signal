import jinja2

loader = jinja2.FileSystemLoader("app/templates")
env = jinja2.Environment(loader=loader)

try:
    template = env.get_template("dashboard.html")
    print("Successfully loaded template")
    output = template.render(sources_count=10, records_count=20, snapshots_count=30)
    print("Successfully rendered template")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
