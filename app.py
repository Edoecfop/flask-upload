from flask import Flask, request, send_file, jsonify, render_template
import os
from werkzeug.utils import secure_filename
from reportlab.pdfgen import canvas

app = Flask(__name__)

# Cartella di upload
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Tipologie di documenti accettati
DOCUMENT_CATEGORIZATION = {
    "identita_codice_fiscale": [
        "carta_id_corsista_fronte", "carta_id_corsista_retro",
        "codice_fiscale_corsista_fronte", "codice_fiscale_corsista_retro",
        "carta_id_genitore_fronte", "carta_id_genitore_retro",
        "codice_fiscale_genitore_fronte", "codice_fiscale_genitore_retro"
    ],
    "titolo_studio": ["titolo_studio"],
    "documento_disabilita": ["documento_disabilita"]
}

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    """Verifica se il file ha un'estensione consentita."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

from flask import Flask, request, send_file, jsonify, render_template
import os
from werkzeug.utils import secure_filename
from reportlab.pdfgen import canvas

app = Flask(__name__, template_folder="templates")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload/<document_type>', methods=['POST'])
def upload_file(document_type):
    """Carica un file specificando il tipo di documento."""
    all_doc_types = sum(DOCUMENT_CATEGORIZATION.values(), [])  # Unisce tutte le categorie

    if document_type not in all_doc_types:
        return jsonify({"error": "Tipo di documento non valido"}), 400

    if 'file' not in request.files:
        return jsonify({"error": "Nessun file caricato"}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "Nessun file selezionato"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(f"{document_type}_{file.filename}")
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        return jsonify({"message": f"File per '{document_type}' caricato con successo!", "filepath": filepath})

    return jsonify({"error": "Formato file non supportato"}), 400

def create_pdf(pdf_name, document_types):
    """Genera un PDF con i documenti specificati."""
    pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], pdf_name)
    c = canvas.Canvas(pdf_path)
    
    y_position = 750  # Posizione iniziale per le immagini nel PDF

    for doc_type in document_types:
        for filename in os.listdir(UPLOAD_FOLDER):
            if filename.startswith(doc_type) and filename.endswith(('.png', '.jpg', '.jpeg')):
                img_path = os.path.join(UPLOAD_FOLDER, filename)
                c.drawString(50, y_position, doc_type.replace("_", " ").capitalize())  # Titolo
                y_position -= 20  

                c.drawImage(img_path, 50, y_position - 300, width=500, height=300)
                y_position -= 320  

                if y_position < 50:  # Nuova pagina se necessario
                    c.showPage()
                    y_position = 750

    c.save()
    return pdf_path if os.path.exists(pdf_path) else None

@app.route('/generate-pdf', methods=['GET'])
def generate_pdfs():
    """Genera i 3 PDF distinti per categoria."""
    results = {}

    # 📌 PDF 1: Identità & Codice Fiscale (Corsista & Genitore)
    pdf_id_cod = create_pdf("documenti_identita_codice_fiscale.pdf", DOCUMENT_CATEGORIZATION["identita_codice_fiscale"])
    if pdf_id_cod:
        results["documenti_identita_codice_fiscale"] = pdf_id_cod

    # 📌 PDF 2: Titolo di Studio
    pdf_titolo = create_pdf("titolo_studio.pdf", DOCUMENT_CATEGORIZATION["titolo_studio"])
    if pdf_titolo:
        results["titolo_studio"] = pdf_titolo

    # 📌 PDF 3: Documento di Disabilità (se presente)
    pdf_disabilita = create_pdf("documento_disabilita.pdf", DOCUMENT_CATEGORIZATION["documento_disabilita"])
    if pdf_disabilita:
        results["documento_disabilita"] = pdf_disabilita

    return jsonify(results)

@app.route('/download-pdf/<pdf_name>', methods=['GET'])
def download_pdf(pdf_name):
    """Permette di scaricare un PDF specifico se esiste."""
    pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], pdf_name)
    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True)
    return jsonify({"error": "Il file PDF non esiste"}), 404

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=5001)

