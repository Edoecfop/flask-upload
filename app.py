from flask import Flask, request, send_file, jsonify, render_template
import os
from werkzeug.utils import secure_filename
from PIL import Image
from reportlab.pdfgen import canvas

# Inizializza l'app Flask
app = Flask(__name__)

# Configura la cartella di upload
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Formati consentiti
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    """Verifica se il file ha un'estensione consentita."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 📌 Homepage per evitare l'errore "Not Found"
@app.route('/')
def index():
    return "<h1>Benvenuto! Il server Flask è attivo 🎉</h1><p>Prova a caricare un file usando /upload</p>"

# 📌 Route per il caricamento dei file
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Nessun file caricato"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "Nessun file selezionato"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        return jsonify({"message": "File caricato con successo!", "filepath": filepath})
    
    return jsonify({"error": "Formato file non supportato"}), 400

# 📌 Route per generare un PDF con le immagini caricate
@app.route('/generate-pdf', methods=['GET'])
def generate_pdf():
    pdf_filename = "documenti_scuola.pdf"
    pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], pdf_filename)
    c = canvas.Canvas(pdf_path)
    
    y_position = 750  # Posizione iniziale per le immagini nel PDF

    # Inserisci tutte le immagini nel PDF
    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            img_path = os.path.join(UPLOAD_FOLDER, filename)
            c.drawImage(img_path, 50, y_position, width=500, height=300)
            y_position -= 320  # Spazio tra le immagini

            if y_position < 50:  # Passa alla pagina successiva se non c'è più spazio
                c.showPage()
                y_position = 750

    c.save()
    return send_file(pdf_path, as_attachment=True)

# 📌 Avvia il server su Render con Gunicorn
if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=5001)
