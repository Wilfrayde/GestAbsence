from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Personnel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.String(5), nullable=False)
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50), nullable=False)
    absences = db.relationship('Absence', backref='personnel', lazy=True)

class Absence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    debut = db.Column(db.String(50), nullable=False)
    fin = db.Column(db.String(50), nullable=False)
    raison = db.Column(db.String(200), nullable=False)
    personnel_id = db.Column(db.Integer, db.ForeignKey('personnel.id'), nullable=False)