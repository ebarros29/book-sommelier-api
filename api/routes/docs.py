import yaml
from flask import Blueprint, Response, jsonify

docs_bp = Blueprint("docs", __name__)


@docs_bp.route("/swagger.json", methods=["GET"])
def swagger_json():
    spec_path = "/app/docs/swagger.yaml"
    with open(spec_path, "r", encoding="utf-8") as fh:
        spec = yaml.safe_load(fh)
    return jsonify(spec)


@docs_bp.route("/docs", methods=["GET"])
def swagger_ui():
    # Minimal Swagger UI page using CDN
    html = """
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>API Docs</title>
        <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@4/swagger-ui.css" />
      </head>
      <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@4/swagger-ui-bundle.js"></script>
        <script>
          window.onload = () => {
            const ui = SwaggerUIBundle({
              url: '/swagger.json',
              dom_id: '#swagger-ui',
            });
          };
        </script>
      </body>
    </html>
    """
    return Response(html, mimetype="text/html")
