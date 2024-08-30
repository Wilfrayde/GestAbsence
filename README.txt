# GestAbsence - Application de Gestion des Absences

## Description
GestAbsence est une application web développée avec Flask pour gérer les absences du personnel. Elle permet d'ajouter, modifier et supprimer des personnels ainsi que leurs absences. L'application utilise une base de données PostgreSQL pour stocker les informations.

## Fonctionnalités
- **Ajouter un personnel** : Permet d'ajouter un nouveau membre du personnel avec son grade, nom et prénom.
- **Modifier un personnel** : Permet de modifier les informations d'un membre du personnel existant.
- **Supprimer un personnel** : Permet de supprimer un membre du personnel, à condition qu'il n'ait pas d'absences associées.
- **Ajouter une absence** : Permet d'ajouter une absence pour un membre du personnel avec les dates de début et de fin, ainsi que la raison de l'absence.
- **Modifier une absence** : Permet de modifier les informations d'une absence existante.
- **Supprimer une absence** : Permet de supprimer une absence.
- **Suppression automatique des absences expirées** : Un planificateur supprime automatiquement les absences dont la date de fin est passée.

## Structure des Fichiers
- **app.py** : Fichier principal de l'application Flask. Contient les routes et la logique de l'application.
- **models.py** : Définit les modèles de la base de données pour le personnel et les absences.
- **static/scripts.js** : Contient le script JavaScript pour initialiser les alertes Bootstrap.
- **static/styles.css** : Contient les styles CSS personnalisés pour l'application.
- **templates/** : Contient les templates HTML pour les différentes pages de l'application.

## Installation
1. **Cloner le dépôt** :
    ```bash
    git clone https://github.com/votre-utilisateur/gestabsence.git
    cd gestabsence
    ```

2. **Créer un environnement virtuel** :
    ```bash
    python -m venv venv
    source venv/bin/activate  # Sur Windows: venv\Scripts\activate
    ```

3. **Installer les dépendances** :
    ```bash
    pip install -r requirements.txt
    ```

4. **Configurer la base de données** :
    - Assurez-vous d'avoir PostgreSQL installé et en cours d'exécution.
    - Créez une base de données nommée `gestion_absences`.
    - Mettez à jour la chaîne de connexion dans `app.py` si nécessaire :
        ```python
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost:5432/gestion_absences'
        ```

5. **Initialiser la base de données** :
    ```bash
    flask db init
    flask db migrate
    flask db upgrade
    ```

6. **Lancer l'application** :
    ```bash
    flask run
    ```

## Utilisation
- **Page d'accueil** : Affiche la liste de tous les personnels avec des options pour ajouter, modifier ou supprimer un personnel, ainsi que pour ajouter une absence.
- **Ajouter un personnel** : Formulaire pour ajouter un nouveau membre du personnel.
- **Modifier un personnel** : Formulaire pour modifier les informations d'un membre du personnel existant.
- **Ajouter une absence** : Formulaire pour ajouter une absence pour un membre du personnel.
- **Modifier une absence** : Formulaire pour modifier les informations d'une absence existante.

## Planificateur de Tâches
L'application utilise `APScheduler` pour exécuter périodiquement une tâche qui supprime les absences expirées. Cette tâche est définie dans `app.py` :

scheduler = BackgroundScheduler()
scheduler.add_job(func=delete_expired_absences, trigger="interval", minutes=5)
scheduler.start()

## Filtres de Template
Un filtre de template est défini pour formater les dates dans un format plus lisible :

@app.template_filter('format_date')
def format_date(value):
date_obj = datetime.strptime(value, '%Y-%m-%d')
return date_obj.strftime('%d/%m/%Y')

## Auteurs
- **JOLIVET Wilfried** - Développeur principal