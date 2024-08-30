from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Personnel, Absence
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost:5432/gestion_absences'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'
db.init_app(app)

def delete_expired_absences():
    """
    Supprime les absences expirées de la base de données.

    Cette fonction est exécutée périodiquement par le planificateur.
    Elle effectue les actions suivantes :
    1. Obtient la date du jour au format 'YYYY-MM-DD'.
    2. Recherche toutes les absences dont la date de fin est aujourd'hui.
    3. Supprime ces absences de la base de données.
    4. Valide les changements dans la base de données.

    Note: Cette fonction nécessite un contexte d'application Flask pour fonctionner correctement.
    """
    with app.app_context():
        today = datetime.today().strftime('%Y-%m-%d')
        expired_absences = Absence.query.filter(Absence.fin == today).all()
        for absence in expired_absences:
            db.session.delete(absence)
        db.session.commit()

scheduler = BackgroundScheduler()
scheduler.add_job(func=delete_expired_absences, trigger="interval", minutes=5)
scheduler.start()

@app.template_filter('format_date')
def format_date(value):
    """
    Filtre de template pour formater une date.

    Args:
        value (str): La date au format 'YYYY-MM-DD'.

    Returns:
        str: La date formatée au format 'DD/MM/YYYY'.

    Cette fonction est utilisée dans les templates Jinja2 pour afficher les dates dans un format plus lisible.
    """
    date_obj = datetime.strptime(value, '%Y-%m-%d')
    return date_obj.strftime('%d/%m/%Y')

@app.route('/')
def index():
    """
    Affiche la page d'accueil de l'application.

    Returns:
        render_template: Rendu du template 'index.html' avec la liste de tous les personnels.

    Cette fonction récupère tous les personnels de la base de données et les passe au template pour affichage.
    """
    personnels = Personnel.query.all()
    return render_template('index.html', personnels=personnels)

@app.route('/add_personnel', methods=['GET', 'POST'])
def add_personnel():
    """
    Gère l'ajout d'un nouveau personnel.

    Returns:
        - Si la méthode est GET : render_template pour afficher le formulaire d'ajout.
        - Si la méthode est POST : 
            - redirect vers la page d'accueil si l'ajout est réussi.
            - redirect vers le formulaire d'ajout si une erreur survient.

    Cette fonction traite à la fois l'affichage du formulaire d'ajout (GET) 
    et le traitement des données soumises (POST).
    Elle vérifie que tous les champs sont remplis, formate les données, 
    et ajoute le nouveau personnel à la base de données.
    """
    if request.method == 'POST':
        grade = request.form['grade'].upper()
        nom = request.form['nom'].upper()
        prenom = request.form['prenom'].capitalize()
        if not grade or not nom or not prenom:
            flash('Tous les champs sont obligatoires.', 'danger')
            return redirect(url_for('add_personnel'))
        new_personnel = Personnel(grade=grade, nom=nom, prenom=prenom)
        db.session.add(new_personnel)
        db.session.commit()
        flash('Personnel ajouté avec succès !', 'success')
        return redirect(url_for('index'))
    return render_template('add_personnel.html')

@app.route('/edit_personnel/<int:id>', methods=['GET', 'POST'])
def edit_personnel(id):
    """
    Gère la modification d'un personnel existant.

    Args:
        id (int): L'identifiant du personnel à modifier.

    Returns:
        - Si la méthode est GET : render_template pour afficher le formulaire de modification.
        - Si la méthode est POST : redirect vers la page d'accueil après la modification.

    Cette fonction récupère les informations du personnel, 
    affiche le formulaire pré-rempli (GET) et traite les modifications soumises (POST).
    """
    personnel = Personnel.query.get_or_404(id)
    if request.method == 'POST':
        personnel.grade = request.form['grade'].upper()
        personnel.nom = request.form['nom'].upper()
        personnel.prenom = request.form['prenom'].capitalize()
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_personnel.html', personnel=personnel)

@app.route('/delete_personnel/<int:id>', methods=['POST'])
def delete_personnel(id):
    """
    Supprime un personnel de la base de données.

    Args:
        id (int): L'identifiant du personnel à supprimer.

    Returns:
        redirect: Redirige vers la page d'accueil après la suppression ou en cas d'erreur.

    Cette fonction vérifie d'abord si le personnel a des absences associées.
    Si oui, elle affiche un message d'erreur. Sinon, elle procède à la suppression.
    """
    personnel = Personnel.query.get_or_404(id)
    if personnel.absences:
        flash('Toutes les absences doivent être supprimées avant de supprimer cette personne.', 'danger')
        return redirect(url_for('index'))
    db.session.delete(personnel)
    db.session.commit()
    flash('Personnel supprimé avec succès !', 'success')
    return redirect(url_for('index'))

@app.route('/add_absence/<int:personnel_id>', methods=['GET', 'POST'])
def add_absence(personnel_id):
    """
    Gère l'ajout d'une nouvelle absence pour un personnel.

    Args:
        personnel_id (int): L'identifiant du personnel pour lequel ajouter l'absence.

    Returns:
        - Si la méthode est GET : render_template pour afficher le formulaire d'ajout d'absence.
        - Si la méthode est POST : 
            - redirect vers la page d'accueil si l'ajout est réussi.
            - redirect vers le formulaire d'ajout si une erreur survient.

    Cette fonction vérifie la validité des dates d'absence et ajoute l'absence à la base de données.
    """
    if request.method == 'POST':
        debut = request.form['debut']
        fin = request.form['fin']
        raison = request.form['raison']
        if not debut or not fin or not raison:
            flash('Tous les champs sont obligatoires.', 'danger')
            return redirect(url_for('add_absence', personnel_id=personnel_id))
        if datetime.strptime(fin, '%Y-%m-%d') < datetime.strptime(debut, '%Y-%m-%d'):
            flash('La date de fin ne peut pas être antérieure à la date de début.', 'danger')
            return redirect(url_for('add_absence', personnel_id=personnel_id))
        new_absence = Absence(debut=debut, fin=fin, raison=raison, personnel_id=personnel_id)
        db.session.add(new_absence)
        db.session.commit()
        flash('Absence ajoutée avec succès !', 'success')
        return redirect(url_for('index'))
    return render_template('add_absence.html', personnel_id=personnel_id)

@app.route('/edit_absence/<int:id>', methods=['GET', 'POST'])
def edit_absence(id):
    """
    Gère la modification d'une absence existante.

    Args:
        id (int): L'identifiant de l'absence à modifier.

    Returns:
        - Si la méthode est GET : render_template pour afficher le formulaire de modification.
        - Si la méthode est POST : 
            - redirect vers la page d'accueil si la modification est réussie.
            - redirect vers le formulaire de modification si une erreur survient.

    Cette fonction vérifie la validité des nouvelles dates d'absence et met à jour l'absence dans la base de données.
    """
    absence = Absence.query.get_or_404(id)
    if request.method == 'POST':
        debut = request.form['debut']
        fin = request.form['fin']
        raison = request.form['raison']
        if not debut or not fin or not raison:
            flash('Tous les champs sont obligatoires.')
            return redirect(url_for('edit_absence', id=id))
        if datetime.strptime(fin, '%Y-%m-%d') < datetime.strptime(debut, '%Y-%m-%d'):
            flash('La date de fin ne peut pas être antérieure à la date de début.')
            return redirect(url_for('edit_absence', id=id))
        absence.debut = debut
        absence.fin = fin
        absence.raison = raison
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_absence.html', absence=absence)

@app.route('/delete_absence/<int:id>', methods=['POST'])
def delete_absence(id):
    """
    Supprime une absence de la base de données.

    Args:
        id (int): L'identifiant de l'absence à supprimer.

    Returns:
        redirect: Redirige vers la page d'accueil après la suppression.

    Cette fonction supprime l'absence spécifiée de la base de données et affiche un message de confirmation.
    """
    absence = Absence.query.get_or_404(id)
    db.session.delete(absence)
    db.session.commit()
    flash('Absence supprimée avec succès !', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)


