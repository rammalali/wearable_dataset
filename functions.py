import logging
import pandas as pd
from flask import redirect, url_for
from score import score_ECG, score_Clinical, score_Metabolites, score_PAC, score_PSTAF, score_AF
import matplotlib.pyplot as plt
import numpy as np
import os
import plotly.graph_objects as go
import chardet



def read_csv_with_encoding(filepath):
    """
        Lit un fichier CSV en détectant automatiquement l'encodage et le délimiteur.
        Retourne un DataFrame pandas.
        """
    # Détection de l'encodage
    with open(filepath, 'rb') as f:
        raw_data = f.read(10000)
        result = chardet.detect(raw_data)
        encoding = result['encoding']

    # Essai de plusieurs délimiteurs
    delimiters = [',', ';', '\t', '|']
    for delimiter in delimiters:
        try:
            df = pd.read_csv(filepath, encoding=encoding, delimiter=delimiter)
            # Si plus d'une colonne, on considère que le délimiteur est bon
            if df.shape[1] > 1:
                return df
        except Exception:
            continue

def generate_score_plot(score, index, name, plot_folder, score_type):
    """
    Génère un graphique de score avec des éléments améliorés en utilisant Plotly.
    Enregistre le graphique au format PNG.
    """
    score_text_map = {
        1: "Score obtained with Metabolites data",
        2: "Score obtained with Clinical data",
        3: "Score obtained with Clinical and Metabolites data",
        4: "Score obtained with ECG data",
        5: "Score obtained with ECG and Metabolites data",
        6: "Score obtained with ECG and Clinical",
        7: "Score obtained with ECG, Clinical and Metabolites data",
        8: "Score for AF Progression",
        9 : "Score for the prediction of Atrial Cardiomyopathy",
        10 : "Score for the prediction of Sludge / Thrombus in AF"
    }

    texte_score = score_text_map.get(score_type, "")

    # Création du graphique
    fig = go.Figure()

    # Définir les bornes en fonction du score 
    ymin = min(-10, score - 2)
    ymax = max(10, score + 2)

    # Ligne horizontale au niveau du score
    fig.add_shape(type="line", x0=-0.1, x1=0.1, y0=score, y1=score,
                  line=dict(color="#3a8b8b", width=2))
    
    if score_type in [1, 2, 3, 4, 5, 6, 7] : 
        # (Optionnel) Zone grise neutre entre -1 et 1
        fig.add_shape(
            type="rect",
            x0=-0.2, x1=0.2, y0=-1, y1=1,
            fillcolor="grey",
            opacity=0.2,
            line_width=0
        )
        # Lignes de référence en pointillés
        for y in [-1, 1]:
            fig.add_shape(type="line", x0=-0.2, x1=0.2, y0=y, y1=y,
                        line=dict(color="#3a8b8b", dash="dash"))
            
        # Zone positive (au-dessus de 1)
        fig.add_shape(
            type="rect",
            x0=-0.2, x1=0.2, y0=1, y1= ymax,  # toute la partie haute
            fillcolor="#FFC170",
            opacity=0.3,
            line_width=0
        )

        # Zone négative (en-dessous de -1)
        fig.add_shape(
            type="rect",
            x0=-0.2, x1=0.2, y0= ymin, y1= -1,  # toute la partie basse
            fillcolor="#9ADE93",
            opacity=0.3,
            line_width=0
        )

            # Annotations positives/négatives
        fig.add_annotation(x=0.05, y=6, text="Positive", showarrow=False,
                        font=dict(color="#3a8b8b", size=12))
        fig.add_annotation(x=0.05, y=-7, text="Negative", showarrow=False,
                        font=dict(color="#3a8b8b", size=12))
        
    elif score_type == 8: 
        fig.add_shape(type ='line', x0 = -0.2, x1 = 0.2, y0 = -1.1310, y1 =-1.1310,
                    line=dict(color='#3a8b8b', dash='dash') )
        
            # Zone positive (au-dessus de 1)
        fig.add_shape(
            type="rect",
            x0=-0.2, x1=0.2, y0= -1.1310, y1= ymax,  # toute la partie haute
            fillcolor="#FFC170",
            opacity=0.3,
            line_width=0
        )

        # Zone négative (en-dessous de -1)
        fig.add_shape(
            type="rect",
            x0=-0.2, x1=0.2, y0= ymin, y1= -1.1310,  # toute la partie basse
            fillcolor="#9ADE93",
            opacity=0.3,
            line_width=0
        )
        
            # Annotations positives/négatives
        fig.add_annotation(x=0.05, y=6, text="AF Progression", showarrow=False,
                        font=dict(color="#3a8b8b", size=12))
        fig.add_annotation(x=0.05, y=-7, text="No progression", showarrow=False,
                        font=dict(color="#3a8b8b", size=12))
        
            
    elif score_type == 9 : 
        fig.add_shape(type ='line', x0 = -0.2, x1 = 0.2, y0 = -1.0, y1 =-1.0,
                      line=dict(color='#3a8b8b', dash='dash') )
        
            # Zone positive (au-dessus de 1)
        fig.add_shape(
            type="rect",
            x0=-0.2, x1=0.2, y0= -1, y1= ymax,  # toute la partie haute
            fillcolor="#FFC170",
            opacity=0.3,
            line_width=0
        )

        # Zone négative (en-dessous de -1)
        fig.add_shape(
            type="rect",
            x0=-0.2, x1=0.2, y0= ymin, y1= -1,  # toute la partie basse
            fillcolor="#9ADE93",
            opacity=0.3,
            line_width=0
        )
        
            # Annotations positives/négatives
        fig.add_annotation(x=0.05, y=6, text="Atrial Cardiomyopathy", showarrow=False,
                        font=dict(color="#3a8b8b", size=12))
        fig.add_annotation(x=0.05, y=-7, text="Healthy", showarrow=False,
                        font=dict(color="#3a8b8b", size=12))
    
    elif score_type == 10 : 
        fig.add_shape(type='line', x0 =-0.2, x1= 0.2, y0 = -1.55, y1 = -1.55,
                      line=dict(color = '#3a8b8b', dash='dash'))

        # Zone positive (au-dessus de 1)
        fig.add_shape(
            type="rect",
            x0=-0.2, x1=0.2, y0=-1.55, y1= ymax,  # toute la partie haute
            fillcolor="#FFC170",
            opacity=0.3,
            line_width=0
        )

        # Zone négative (en-dessous de -1)
        fig.add_shape(
            type="rect",
            x0=-0.2, x1=0.2, y0= ymin, y1= -1.55,  # toute la partie basse
            fillcolor="#9ADE93",
            opacity=0.3,
            line_width=0
        )

            # Annotations positives/négatives
        fig.add_annotation(x=0.05, y=6, text="Sludge/Thrombus in AF", showarrow=False,
                        font=dict(color="#3a8b8b", size=12))
        fig.add_annotation(x=0.05, y=-7, text="Healthy", showarrow=False,
                        font=dict(color="#3a8b8b", size=12))
        


    # Point représentant le score
    fig.add_trace(go.Scatter(
        x=[0], y=[score],
        mode='markers',
        marker=dict(size=15, color="#3a8b8b", symbol='square',
                    line=dict(width=2, color='black')),
        name=f'Score: {score}'
    ))

    # Légende score
    fig.add_annotation(
        x=0.95, y=0.95, xref="paper", yref="paper",
        text=f'<b>Score</b>: {score}',
        showarrow=False,
        bordercolor="#3a8b8b", borderwidth=2,
        bgcolor="#5b7173",
        font=dict(size=12, color="white"),
        align="left"
    )

    # Annotation texte_score en bas
    fig.add_annotation(
        x=0, y=-9.5, xref="x", yref="y",
        text=texte_score,
        showarrow=False,
        font=dict(size=14, color="#3a8b8b"),
        align="center"
    )

    # Configuration globale
    fig.update_layout(
        yaxis=dict(range=[ymin, ymax], showgrid=False, zeroline=False,
                   showline=False, showticklabels=False),
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, showline=False),
        showlegend=False,
        plot_bgcolor='#e7eee9',
        paper_bgcolor='#5b7173',
        margin=dict(l=10, r=10, t=10, b=10)
    )

    # Sauvegarde
    graph_path = os.path.join(plot_folder, f'graph_{index}.png')
    fig.write_image(graph_path, width=700, height=500, scale=3)

    # Retourne le chemin relatif depuis "static"
    relative_path = os.path.relpath(graph_path, 'static').replace('\\', '/')
    return relative_path # pour compatibilité Windows



def process_data_1(filepath, plot_folder, file_type="csv", orientation="rows"):
    if file_type == "csv":
        df = read_csv_with_encoding(filepath)
    else:
        df = pd.read_excel(filepath)

    d = False
    if df is None:
        d = True
        return [], d

    keywords = ['M0_LVESV_3D', 'M0_LVED_3D', 'M0_LA_tot_EmF', 'M0_LA_strain_conduit',
                'GLYC', 'Urea', 'Arginine', 'Met_MetSufoxide', 'Kynurenine']

    plot_paths = []

    if orientation == "columns":
        # Vérification de l'orientation (si première cellule numérique)
        if isinstance(df.iloc[0, 0], (int, float)):
            d = True
            return [], d

        # Ajouter les variables manquantes comme lignes
        missing_vars = {key: [0] * (len(df.columns) - 1) for key in keywords if key not in df.iloc[:, 0].values}
        for key, values in missing_vars.items():
            df.loc[len(df)] = [key] + values

        Index = df.columns[0]
        df2 = df[df[Index].isin(keywords)].sort_values(Index).reset_index(drop=True)
        patient_names = df2.columns[1:]

        for i, patient_name in enumerate(patient_names, start=1):
            data = df2.iloc[:, i]

            if np.isnan(data[0]):  # Skip colonnes vides
                logging.warning(f"Colonne {i} ({patient_name}) vide ou ne contenant pas de données valides.")
                continue

            data = data.fillna(0)
            plot_individual_paths = []
            scores = []
            type_of_score = [0, 0, 0]

            if all(val != 0 for val in data[:4]):
                score1 = score_ECG(data[0], data[1], data[2], data[3])
                scores.append(score1)
                type_of_score[0] = 1

            if all(val != 0 for val in data[4:6]):
                score2 = score_Clinical(data[4], data[5])
                scores.append(score2)
                type_of_score[1] = 1

            if all(val != 0 for val in data[6:9]):
                score3 = score_Metabolites(data[6], data[7], data[8])
                scores.append(score3)
                type_of_score[2] = 1

            if scores:
                total_score = sum(scores)
                plot_individual_paths.append(generate_score_plot(
                    total_score, f"{patient_name}_4", "Graph Combined Score", plot_folder, type_of_score
                ))

            plot_paths.append({
                'patient_name': i,
                'plots': plot_individual_paths
            })

    elif orientation == "rows":
        # Ajouter les colonnes manquantes
        for key in keywords:
            if key not in df.columns:
                df[key] = [0] * len(df)

        df = df[keywords]
        patient_names = range(len(df))

        for i, patient_name in enumerate(patient_names, start=1):
            data = df.iloc[i - 1]
            data = data.fillna(0)
            plot_individual_paths = []
            scores = []
            type_of_score = [0, 0, 0]

            if all(val != 0 for val in data[:4]):
                score1 = score_ECG(data[0], data[1], data[2], data[3])
                scores.append(score1)
                type_of_score[0] = 1

            if all(val != 0 for val in data[4:6]):
                score2 = score_Clinical(data[4], data[5])
                scores.append(score2)
                type_of_score[1] = 1

            if all(val != 0 for val in data[6:9]):
                score3 = score_Metabolites(data[6], data[7], data[8])
                scores.append(score3)
                type_of_score[2] = 1

            score_type = type_of_score[0]*4 + type_of_score[1]*2 + type_of_score[2]

            if scores:
                total_score = sum(scores)
                plot_individual_paths.append(generate_score_plot(
                    total_score, f"{patient_name}_4", "Graph Combined Score", plot_folder, score_type
                ))

            plot_paths.append({
                'patient_name': i,
                'plots': plot_individual_paths
            })

    if all(len(p['plots']) == 0 for p in plot_paths):
        d = True
        return [], d

    return plot_paths, d

def process_data_PAC(filepath, plot_folder, orientation="rows"):
    # 1. Lecture CSV
    df = pd.read_csv(filepath)

    # 2. Sélection des colonnes pertinentes pour ce modèle
    keywords = ['GEAT volume index', 'LA PLS', 'GEAT T1']  # remplacer par les vraies colonnes

    # 3. Traitement par patient / ligne ou colonne selon orientation
    plot_paths = []
    for i, row in df.iterrows():
        data = row[keywords].fillna(0)
        # calcul du score spécifique
        score = score_PAC(*data)
        # génération du plot
        plot_path = generate_score_plot(score, i, "Prediction of Atrial Cardiomyopathy", plot_folder, score_type=9)
        plot_paths.append({'patient_name': i+1, 'plots': [plot_path]})

    return plot_paths, False

def process_data_PSTAF(filepath, plot_folder, orientation="rows"):
    import pandas as pd
    import os

    # 1. Lecture CSV
    df = pd.read_csv(filepath)

    # 2. Colonnes attendues pour le modèle PSTAF
    keywords = ['LAA emptying flow velocity', 'ES LAA area', 'ES LAAV', 'LAA morphology']

    # 3. Ajouter les colonnes manquantes avec des zéros
    for key in keywords:
        if key not in df.columns:
            df[key] = 0

    plot_paths = []

    if orientation == "rows":
        for i, row in df.iterrows():
            data = row[keywords].fillna(0).values
            # Calcul du score spécifique
            score = score_PSTAF(*data)
            # Génération du plot
            plot_path = generate_score_plot(score, i+1, "Prediction of Atrial Cardiomyopathy", plot_folder, score_type=10)
            plot_paths.append({'patient_name': i+1, 'plots': [plot_path]})
    else:  # orientation == "columns"
        for j, col in enumerate(df.columns):
            if col not in keywords:
                continue
            data = df.loc[keywords, col].fillna(0).values
            score = score_PSTAF(*data)
            plot_path = generate_score_plot(score, j+1, "Prediction of Atrial Cardiomyopathy", plot_folder, score_type=10)
            plot_paths.append({'patient_name': j+1, 'plots': [plot_path]})

    # Si aucune ligne valide
    if len(plot_paths) == 0:
        return [], True

    return plot_paths, False




def process_data_afprogression(filepath, plot_folder, orientation="rows"):
    # 1. Lecture CSV
    df = pd.read_csv(filepath)

    # 2. Sélection des colonnes pertinentes pour ce modèle
    keywords = ['Age', 'LVEF', 'Sex', 'LAdiameter']  # remplacer par les vraies colonnes

    # 3. Traitement par patient / ligne ou colonne selon orientation
    plot_paths = []
    for i, row in df.iterrows():
        data = row[keywords].fillna(0)
        # calcul du score spécifique
        score = score_AF(*data)
        # génération du plot
        plot_path = generate_score_plot(score, i, "AF Progression", plot_folder, score_type=8)
        plot_paths.append({'patient_name': i+1, 'plots': [plot_path]})

    return plot_paths, False

# def process_data_afprogression(filepath, plot_folder, file_type="csv", orientation="rows"):
#     if file_type == "csv":
#         df = read_csv_with_encoding(filepath)
#     else:
#         df = pd.read_excel(filepath)

#     d = False
#     if df is None:
#         d = True
#         return [], d

#     # Colonnes nécessaires pour le modèle PSTAF
#     afprogression_keywords = ['Age', 'LVEF', 'Sex', 'LA diameter']  # À remplacer par les vraies variables

#     plot_paths = []

#     # Orientation "colonnes"
#     if orientation == "columns":
#         if isinstance(df.iloc[0, 0], (int, float)):
#             d = True
#             return [], d

#         # Ajouter les variables manquantes
#         missing_vars = {key: [0] * (len(df.columns) - 1) for key in afprogression_keywords if key not in df.iloc[:, 0].values}
#         for key, values in missing_vars.items():
#             df.loc[len(df)] = [key] + values

#         Index = df.columns[0]
#         df2 = df[df[Index].isin(afprogression_keywords)].sort_values(Index).reset_index(drop=True)
#         patient_names = df2.columns[1:]

#         for i, patient_name in enumerate(patient_names, start=1):
#             data = df2.iloc[:, i].fillna(0)

#             if all(val != 0 for val in data[:len(afprogression_keywords)]):
#                 score = score_AF(*data[:len(afprogression_keywords)])
#                 plot_individual_paths = [
#                     generate_score_plot(score, f"{patient_name}_AF_Progression", "af Progression Score", plot_folder, score_type=8)
#                 ]
#             else:
#                 plot_individual_paths = []

#             plot_paths.append({
#                 'patient_name': i,
#                 'plots': plot_individual_paths
#             })

#     # Orientation "rows"
#     elif orientation == "rows":
#         for key in afprogression_keywords:
#             if key not in df.columns:
#                 df[key] = [0] * len(df)

#         df = df[afprogression_keywords]
#         patient_names = range(len(df))

#         for i, patient_name in enumerate(patient_names, start=1):
#             data = df.iloc[i].fillna(0)

#             if all(val != 0 for val in data):
#                 score = score_AF(*data)
#                 plot_individual_paths = [
#                     generate_score_plot(score, f"{patient_name}_AF_progression", "Af progression Score", plot_folder, score_type=8)
#                 ]
#             else:
#                 plot_individual_paths = []

#             plot_paths.append({
#                 'patient_name': i,
#                 'plots': plot_individual_paths
#             })

#     if all(len(p['plots']) == 0 for p in plot_paths):
#         d = True
#         return [], d

#     return plot_paths, d