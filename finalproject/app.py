# final project
#
# to build: docker build -t edge-app .      
# to run:   docker run -p 5000:5000 edge-app

from flask import Flask, request, send_file, render_template_string, send_from_directory
import os
import cv2

app = Flask(__name__)

UPLOAD_FOLDER = "static"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML = """
<h2>Image Processor</h2>

<form method="POST" action="/edges" enctype="multipart/form-data">
    <label>Image:</label>
    <input type="file" name="file">

    <label>Threshold:</label>
    <input type="number" name="T" value="100">

    <input type="submit" value="Run">
</form>

<hr>

{% if original and processed %}

<h3>Result (Threshold: {{ threshold }})</h3>

<div style="display:flex; gap:20px; align-items:flex-start;">

    <div>
        <p><b>Original</b></p>
        <img src="{{ original }}" style="max-width:350px;">
    </div>

    <div>
        <p><b>Processed</b></p>
        <img src="{{ processed }}" style="max-width:350px;">
    </div>

</div>

{% endif %}
"""

def detect_edges(input_path, output_path, T=100):
    T1 = int(T * 0.5)
    T2 = int(T)
    img = cv2.imread(input_path)
    edges = cv2.Canny(img, T1, T2)
    cv2.imwrite(output_path, edges)
    return output_path


@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/output.jpg")
def output_image():
    return send_file("output.jpg", mimetype="image/jpeg")


@app.route("/edges", methods=["POST"])
def edges_route():
    T = request.form.get("T", default=100, type=int)

    file = request.files.get("file", None)

    original_path = os.path.join(UPLOAD_FOLDER, "original.jpg")
    output_path = os.path.join(UPLOAD_FOLDER, "output.jpg")

    # ✅ If new file uploaded, overwrite stored image
    if file and file.filename != "":
        file.save(original_path)

    # ❗ If no file AND no existing image → error case
    if not os.path.exists(original_path):
        return "No image uploaded yet."

    detect_edges(original_path, output_path, T)

    return render_template_string(
        HTML,
        original="/static/original.jpg",
        processed="/static/output.jpg",
        threshold=T
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
