from flask import Flask, render_template, request, url_for, send_from_directory, redirect, session
import os
import uuid
from werkzeug.utils import secure_filename
import logging
import psutil  # Pour suivre l'utilisation du CPU
from score import score_ECG, score_Clinical, score_Metabolites, score_AF, score_PAC, score_PSTAF
from functions import  generate_score_plot, process_data_1, process_data_PAC, process_data_PSTAF, process_data_afprogression
from prometheus_flask_exporter import PrometheusMetrics
import threading


# Initialize the Flask application

app = Flask(__name__)

app.secret_key = 'maestria_dsfjsdf48ZAE*$ds'  # à personnaliser


 # Le serveur de métriques s'exécutera sur le port 8000
metrics = PrometheusMetrics(app)

# Configuration de l'application
UPLOAD_FOLDER = 'uploads'  # Dossier pour stocker les fichiers téléchargés
PLOT1_FOLDER = 'static/plots1'  # Dossier pour stocker le premier ensemble de graphiques
PLOT2_FOLDER = 'static/plots2'  # Dossier pour stocker le second ensemble de graphiques
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}  # Extensions de fichiers autorisées
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PLOT1_FOLDER'] = PLOT1_FOLDER
app.config['PLOT2_FOLDER'] = PLOT2_FOLDER

# Configure le logging
logging.basicConfig(level=logging.INFO)

# Créer les dossiers d'upload et de plots s'ils n'existent pas
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PLOT1_FOLDER, exist_ok=True)
os.makedirs(PLOT2_FOLDER, exist_ok=True)


# Fonction pour vérifier si un fichier est autorisé
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_session_id():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']

def cleanup_session(session_id):
    for folder_base in [UPLOAD_FOLDER, PLOT1_FOLDER, PLOT2_FOLDER]:
        folder = os.path.join(folder_base, session_id)
        if os.path.exists(folder):
            for f in os.listdir(folder):
                try:
                    os.remove(os.path.join(folder, f))
                except Exception as e:
                    logging.warning(f"Could not delete {f}: {e}")
            try:
                os.rmdir(folder)
            except Exception as e:
                logging.warning(f"Could not remove directory {folder}: {e}")





@app.route('/')
def maestria():
    return render_template('maestria.html')


@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/index')
def index():
    return render_template('E_strain.html')

@app.route('/afprogression')
def af_progression():
    return render_template('afprogression.html')


@app.route('/predictionofatrialcardiomyopathy')
def predictionofatrialcardiomyopathy():
    return render_template('predictionofatrialcardiomyopathy.html')

@app.route('/predictionofsludgethrombusinaf')
def predictionofsludgethrombusinaf ():
    return render_template('predictionofsludgethrombusinaf.html')


@app.route('/data_formats')
def data_formats():
    return render_template('data_formats.html')


@app.route('/tutorials')
def tutorials():
    return render_template('tutorials.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')




@app.route('/upload', methods=['POST'])
def upload_file():
    # Dossier où sauvegarder les plots
    plot_path = app.config['PLOT1_FOLDER']
    os.makedirs(plot_path, exist_ok=True)

    # Récupération des données du formulaire
    use_default_csv = request.form.get('use_default_csv')
    orientation = request.form.get('orientation', 'rows')  # 'rows' par défaut

    # Cas 1 : utiliser le CSV par défaut
    if use_default_csv:
        default_csv_path = os.path.join('static', 'default.csv')
        if not os.path.exists(default_csv_path):
            return "Default CSV file not found.", 400

        plot_paths, d = process_data_1(default_csv_path, plot_path, orientation=orientation)
        if d:
            return "No plots could be generated from the default CSV.", 400

        return render_template('plot.html', plot_paths=plot_paths)

    # Cas 2 : traitement des fichiers uploadés
    if 'file' not in request.files:
        return "No file uploaded.", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file.", 400

    if not file.filename.lower().endswith('.csv'):
        return "Only CSV files are allowed.", 400

    # Sauvegarde du fichier uploadé
    filename = secure_filename(file.filename)
    upload_path = os.path.join('uploads', filename)
    os.makedirs('uploads', exist_ok=True)
    file.save(upload_path)

    # Traitement du CSV
    plot_paths, d = process_data_1(upload_path, plot_path, orientation=orientation)
    if d:
        return "No plots could be generated from the uploaded CSV.", 400

    return render_template('plot.html', plot_paths=plot_paths)



@app.route('/submit-answers', methods=['POST'])
def submit_answers():
    # Récupération et conversion des données du formulaire
    field_names = [
        'question1', 'question2', 'question3', 'question4',
        'question5', 'question6',
        'question7', 'question8', 'question9'
    ]
    data = [float(request.form[name]) for name in field_names]

    # Définition des groupes : (indices, fonction_score, label_plot, poids)
    score_groups = [
        ((0, 1, 2, 3), score_ECG, "Graph Score ECG", 4),
        ((4, 5), score_Clinical, "Graph Score Clinical", 2),
        ((6, 7, 8), score_Metabolites, "Graph Score Metabolites", 1),
    ]

    plot_paths = []
    scores = []
    total_weight = 0

    for i, (indices, scoring_function, plot_label, weight) in enumerate(score_groups, start=1):
        values = [data[idx] for idx in indices]
        if all(val != 0 for val in values):
            score = scoring_function(*values)
            plot_path = generate_score_plot(score, i, plot_label, app.config['PLOT2_FOLDER'], weight)
            plot_paths.append(plot_path)
            scores.append(score)
            total_weight += weight

    # Score global combiné
    if scores:
        total_score = sum(scores)
        combined_plot = generate_score_plot(total_score, len(score_groups)+1, "Graph Combined Score", app.config['PLOT2_FOLDER'], total_weight)
        plot_paths.append({'patient_name': len(score_groups)+1, 'plots':[combined_plot]})

    return render_template('plot.html', plot_paths=plot_paths)





@app.route('/submit-answers-af', methods=['POST'])
def submit_answers_af():
    # Récupère les données du formulaire
    rythme_ECG = float(request.form['question1'])
    age = float(request.form['question2'])
    antico = int(request.form['question3'])
    LA_d = float(request.form['question4'])

    # Calcul du score AF
    score_af = score_AF(rythme_ECG, age, antico, LA_d)

    # Génération du graphique associé (si besoin)
    plot_path = generate_score_plot(score_af, 5, "AF Progression Score", "static/plots2",8)

    # Redirection vers une page affichant le résultat
    return render_template('display_graph.html', plot_paths=[plot_path])


@app.route('/submit-answers-pac', methods=['POST'])
def submit_answers_pac():
    # Récupérer les valeurs du formulaire et les convertir en float
    geat_volume_index = float(request.form['question1'])
    la_pls = float(request.form['question2'])
    geat_t1 = float(request.form['question3'])

    # Calculer le CMR score
    cmr_score = score_PAC(geat_volume_index, la_pls, geat_t1) 

    # Si tu veux, tu peux générer un graphique du score (optionnel)
    plot_path = generate_score_plot(cmr_score, 1, "CMR Score", "static/plots2", 9)

    # Afficher le résultat dans une page HTML
    return render_template('display_graph.html', plot_paths = [plot_path])


@app.route('/submit-answers-pstaf', methods=['POST'])
def submit_answers_pstaf():
    # Récupérer les valeurs du formulaire et les convertir en float
    laa_emptying_flow_velocity = float(request.form['question1'])
    es_la_area = float(request.form['question2'])
    es_laav = float(request.form['question3'])
    laa_morphology = float(request.form['question4'])

    # Calculer le score
    pstaf_score = score_PSTAF (laa_emptying_flow_velocity, es_la_area, es_laav, laa_morphology) 

    # Si tu veux, tu peux générer un graphique du score (optionnel)
    plot_path = generate_score_plot(pstaf_score, 1, "PSTAF Score", "static/plots2", 10)

    # Afficher le résultat dans une page HTML
    return render_template('display_graph.html', plot_paths = [plot_path])


@app.route('/display-graph')
def display_graph():
    plot_paths = request.args.getlist('plot_paths')
    session_id = session.get('session_id')

    response = render_template('display_graph.html', plot_paths=plot_paths)

    if session_id:
        cleanup_session(session_id)
        session.pop('session_id', None)

    return response



@app.route('/error')
def error():
    return render_template('ERROR.html')


@app.route('/static/<path:filename>')
def download_file(filename):
    return send_from_directory('static', filename, as_attachment=True)


@app.route('/uploads/<path:filename>')
def download_file2(filename):
    return send_from_directory('uploads', filename, as_attachment=True, mimetype='text/csv')

@app.route('/upload_PAC', methods=['POST'])
def upload_file_PAC():
    plot_path = app.config['PLOT1_FOLDER']
    os.makedirs(plot_path, exist_ok=True)

    use_default_csv = request.form.get('use_default_csv')
    orientation = request.form.get('orientation', 'rows')

    if use_default_csv:
        default_csv_path = os.path.join('static', 'default_PAC.csv')
        if not os.path.exists(default_csv_path):
            return "Default CSV file not found.", 400
        plot_paths, d = process_data_PAC(default_csv_path, plot_path, orientation)
        if d:
            return "No plots could be generated from default CSV.", 400
        return render_template('plot.html', plot_paths=plot_paths)

    if 'file' not in request.files:
        return "No file uploaded.", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file.", 400

    filename = secure_filename(file.filename)
    upload_path = os.path.join('uploads', filename)
    os.makedirs('uploads', exist_ok=True)
    file.save(upload_path)

    plot_paths, d = process_data_PAC(upload_path, plot_path, orientation)
    if d:
        return "No plots could be generated from uploaded CSV.", 400

    return render_template('plot.html', plot_paths=plot_paths)



@app.route('/upload_pstaf', methods=['POST'])
def upload_file_pstaf():
    # Dossier où sauvegarder les plots
    plot_path = app.config['PLOT1_FOLDER']
    os.makedirs(plot_path, exist_ok=True)

    # Récupération des données du formulaire
    use_default_csv = request.form.get('use_default_csv')
    orientation = request.form.get('orientation', 'rows')  # 'rows' par défaut

    # Cas 1 : utiliser le CSV par défaut
    if use_default_csv:
        default_csv_path = os.path.join('static', 'default_pstaf.csv')
        if not os.path.exists(default_csv_path):
            return "Default CSV file not found.", 400

        plot_paths, d = process_data_PSTAF(default_csv_path, plot_path, orientation=orientation)
        if d:
            return "No plots could be generated from the default CSV.", 400

        return render_template('plot.html', plot_paths=plot_paths)

    # Cas 2 : traitement des fichiers uploadés
    if 'file' not in request.files:
        return "No file uploaded.", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file.", 400

    if not file.filename.lower().endswith('.csv'):
        return "Only CSV files are allowed.", 400

    # Sauvegarde du fichier uploadé
    filename = secure_filename(file.filename)
    upload_path = os.path.join('uploads', filename)
    os.makedirs('uploads', exist_ok=True)
    file.save(upload_path)

    # Traitement du CSV
    plot_paths, d = process_data_PSTAF(upload_path, plot_path, orientation=orientation)
    if d:
        return "No plots could be generated from the uploaded CSV.", 400

    return render_template('plot.html', plot_paths=plot_paths)


@app.route('/upload_afprogression', methods=['POST'])
def upload_file_afprogression():
    # Dossier où sauvegarder les plots
    plot_path = app.config['PLOT1_FOLDER']
    os.makedirs(plot_path, exist_ok=True)

    # Récupération des données du formulaire
    use_default_csv = request.form.get('use_default_csv')
    orientation = request.form.get('orientation', 'rows')  # 'rows' par défaut

    # Cas 1 : utiliser le CSV par défaut
    if use_default_csv:
        default_csv_path = os.path.join('static', 'default_afprogression.csv')
        if not os.path.exists(default_csv_path):
            return "Default CSV file not found.", 400

        plot_paths, d = process_data_afprogression(default_csv_path, plot_path, orientation=orientation)
        if d:
            return "No plots could be generated from the default CSV.", 400

        return render_template('plot.html', plot_paths=plot_paths)

    # Cas 2 : traitement des fichiers uploadés
    if 'file' not in request.files:
        return "No file uploaded.", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file.", 400

    if not file.filename.lower().endswith('.csv'):
        return "Only CSV files are allowed.", 400

    # Sauvegarde du fichier uploadé
    filename = secure_filename(file.filename)
    upload_path = os.path.join('uploads', filename)
    os.makedirs('uploads', exist_ok=True)
    file.save(upload_path)

    # Traitement du CSV
    plot_paths, d = process_data_afprogression(upload_path, plot_path, orientation=orientation)
    if d:
        return "No plots could be generated from the uploaded CSV.", 400

    return render_template('plot.html', plot_paths=plot_paths)


@app.route('/test', methods=['GET'])
def test():
    return "Route test OK"



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)







