import os
import json

def compile():
    # Read files
    with open("cleaner.py", "r", encoding="utf-8") as f:
        cleaner_code = f.read()
        
    with open("reporter.py", "r", encoding="utf-8") as f:
        reporter_code = f.read()
        
    with open("app.py", "r", encoding="utf-8") as f:
        app_code = f.read()
        
    with open("sample_data.csv", "r", encoding="utf-8") as f:
        csv_data = f.read()

    # HTML template using stlite (WebAssembly Streamlit)
    html_content = f"""<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
    <title>⚡ DataPulse Dashboard</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@stlite/mountable@0.58.0/build/style.css" />
    <style>
      /* Ensure clean background during WebAssembly loading screen */
      body {{
        background-color: #f9fafb;
      }}
    </style>
  </head>
  <body>
    <div id="root"></div>
    <script src="https://cdn.jsdelivr.net/npm/@stlite/mountable@0.58.0/build/stlite.js"></script>
    <script>
      stlite.mount(
        {{
          requirements: ["pandas", "plotly", "openpyxl"],
          entrypoint: "app.py",
          files: {{
            "cleaner.py": {json.dumps(cleaner_code)},
            "reporter.py": {json.dumps(reporter_code)},
            "app.py": {json.dumps(app_code)},
            "sample_data.csv": {json.dumps(csv_data)}
          }},
        }},
        document.getElementById("root")
      );
    </script>
  </body>
</html>
"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Successfully compiled index.html with stlite integration!")

if __name__ == "__main__":
    compile()
