from flask import  render_template,redirect,url_for,request,flash,session
from sqlalchemy import func
import secrets
import string
from werkzeug.utils import secure_filename
import os

from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from models import (
    app,
    getAnnonce,
    findAnnonceById,
    findAnnonceByCategories,
    User,
    insert_user,
    db,
    recherche_annonces,
    saveAnnonce,
    Annonce,
                    )
# initialisation de l'extension Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# fonction de chargement de l'utilisateur
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#  accueil
@app.route('/')
def home():
     annonces = Annonce.query.order_by(func.random()).limit(6).all()
     boutiques = Annonce.query.order_by(func.random()).limit(6).all()
     return render_template("front/index.html",annonces=annonces,boutiques=boutiques) # ici on met le nom de la route
#  route partie annonces
@app.route('/annonces')
def annonces():
    annonces= getAnnonce()
    return render_template("front/annonces.html",annonces=annonces)
@app.route("/annonces/<categories>/<id_annonce>")
def d_annonce(id_annonce,categories):
    annonce= findAnnonceById(id_annonce)
    categories=findAnnonceByCategories(categories)
    if not d_annonce:
        return redirect(url_for('home'))
    return render_template("front/d_annonce.html",annonce=annonce,categories=categories)
 # routes partie categories
@app.route('/vehicules')
def vehicules():
    annonces = Annonce.query.filter_by(choose_categorie='vehicules').all()
    return render_template("front/categories/vehicules.html",annonces=annonces)
@app.route('/emploi')
def emploi():
    annonces = Annonce.query.filter_by(choose_categorie='emploi').all()
    return render_template("front/categories/emploi.html",annonces=annonces)
@app.route('/immobilier')
def immobilier():
    annonces = Annonce.query.filter_by(choose_categorie='immobilier').all()
    return render_template("front/categories/immobilier.html", annonces=annonces)
@app.route('/multimedia')
def multimedia():
    annonces = Annonce.query.filter_by(choose_categorie='multimedia').all()
    return render_template("front/categories/multimedia.html",annonces=annonces)
@app.route('/maison')
def maison():
    annonces = Annonce.query.filter_by(choose_categorie='maison').all()
    return render_template("front/categories/maison.html",annonces=annonces)
# --------------------------------------
# ------------------- USER ------------------------  
# --------------------LOGIN---------------------
@app.route('/compte/login', methods=["POST", "GET"])
def login():
      if request.method == 'POST':
        telephone = request.form['telephone']
        user = User.query.filter_by(telephone=telephone).first()
        if user:
            return redirect(url_for('confirm_login', telephone=telephone))
        else:
            return redirect(url_for('register', telephone=telephone))
      return render_template('backend/user/login.html')

#  ----------------CONFIRM_LOGIN-------------------------------------------
@app.route('/compte/login/confirm/<telephone>', methods=['GET', 'POST'])
def confirm_login(telephone):
    user = User.query.filter_by(telephone=telephone).first()
    if request.method == 'POST':
        password = request.form['password']
        if password == user.password:
            # création d'une session pour l'utilisateur connecté
            login_user(user)
            flash('Vous êtes connecté avec succès.')
            return redirect(url_for('home_user'))
    return render_template('backend/user/confirm.html', telephone=telephone)
#  ---------------REGISTER------------------------
@app.route('/compte/register/<telephone>', methods=['GET', 'POST'])
def register(telephone):
        # necessary imports
# define the alphabet
    letters = string.ascii_letters # a à z
    digits = string.digits # 0 à 9
    special_chars = string.punctuation # caractere special
    alphabet = letters + digits + special_chars # tous l'alphabet
    # fix password length
    username_length = 12
    # generate password meeting constraints
    while True:
        username = ''
        for i in range(username_length):
            username += ''.join(secrets.choice(alphabet))
        # doit avoir au moins un caractère special
        # et au moins 2 chiffres
        if (any(char in special_chars for char in username) and 
            sum(char in digits for char in username)>=2):
                break
    if request.method == 'POST':
        nom_complet = username # username generé 
        password = request.form['password']
        user = User(telephone=telephone, password=password,nom_complet=nom_complet)
        insert_user(user)
        # création d'une session pour l'utilisateur connecté
        login_user(user)
        flash('Bravo Vous Vous êtes inscris avec succès.')
        return redirect(url_for('home_user'))
    return render_template('backend/user/register.html', telephone=telephone)
#  ------------------------------------------
# route d'accueil (accessible aux utilisateurs connectés)
#  ----------------accueil user ---------------------
@app.route('/home_user')
@login_required
def home_user():
     return render_template("backend/index_user.html",user=current_user) # ici on met le nom de la route
# ------------ route partie annonces user --------------------------
@app.route('/annonces_user', methods=['GET', 'POST'])
@login_required
def annonces_user():
    annonces= getAnnonce()
    # recherche = request.args.get('recherche')
    # if recherche:
    #     annonces = Annonce.query.filter(Annonce.titre.like(f'%{recherche}%')).all()
    # else:
    #  return redirect(url_for('home_user'))
    return render_template("backend/annonces_user.html",annonces=annonces,user=current_user)
# -----------details annonce user --------------------
@app.route("/annonces/<categories>/<id_annonce>")
@login_required
def d_annonce_user(id_annonce,categories):
    annonce= findAnnonceById(id_annonce)
    categories=findAnnonceByCategories(categories)
    if not d_annonce:
        return redirect(url_for('home_user'))
    return render_template("backend/d_annonce_user.html",annonce=annonce,categories=categories,user=current_user)
 # routes partie categories
@app.route('/vehicules_user')
@login_required
def vehicules_user():
    annonces = Annonce.query.filter_by(choose_categorie='vehicules').all()
    return render_template("backend/categories/vehicules_user.html",annonces=annonces,user=current_user)
@app.route('/emploi_user')
@login_required
def emploi_user():
    annonces = Annonce.query.filter_by(choose_categorie='emploi').all()
    return render_template("backend/categories/emploi_user.html",annonces=annonces,user=current_user)
@app.route('/immobilier_user')
@login_required
def immobilier_user():
    annonces = Annonce.query.filter_by(choose_categorie='immobilier').all()
    return render_template("backend/categories/immobilier_user.html",annonces=annonces,user=current_user)
@app.route('/multimedia_user')
@login_required
def multimedia_user():
    annonces = Annonce.query.filter_by(choose_categorie='multimedia').all()
    return render_template("backend/categories/multimedia_user.html",annonces=annonces,user=current_user)
@app.route('/maison_user')
@login_required
def maison_user():
     annonces = Annonce.query.filter_by(choose_categorie='maison').all()
     return render_template("backend/categories/maison_user.html",annonces=annonces,user=current_user)
# ---------route de déconnexion ------------------
@app.route('/deconnexion')
@login_required
def logout():
    logout_user()
    flash('Vous êtes déconnecté avec succès.')
    return redirect(url_for('home'))
#  --------------------creer un annonce----------------------------
# ---------------------01 create---------------------------

# Route pour la première page du formulaire
@app.route('/compte/listing/create/annonces', methods=['GET', 'POST'])
@login_required
def create_annonce1():
      if request.method == 'POST':
        # Traiter le formulaire ici
        categorie = request.form['categories']
        # Rediriger vers la page suivante tout en gardant la catégorie sélectionnée
        return redirect(url_for('create_annonce2', categorie=categorie))
      else:
        # Afficher le formulaire de sélection de catégorie
        return render_template("backend/create/create_annonce1.html",user=current_user)
# ---------------------02 file---------------------------
# Route pour la deuxième page du formulaire (description)
@app.route('/compte/listing/file', methods=['GET', 'POST'])
@login_required
def create_annonce2():
        if request.method == 'POST':
            categories = request.form['categories']
            images = request.files.getlist('files[]')
            # Faire quelque chose avec les images (par exemple, les sauvegarder sur le disque dur)
            session['categories'] = categories
            session['files[]'] = images
            return redirect(url_for('create_annonce3',images=images,categories=categories))
        return render_template("backend/create/create_annonce2.html",user=current_user)
# ---------------------03 edit---------------------------
# Route pour la troisième page du formulaire (adresse)
@app.route('/compte/listing/edit', methods=['GET', 'POST'])
@login_required
def create_annonce3():
    if request.method == 'POST':
        # Récupère les données du formulaire et les stocke dans une session
        titre = request.form['titre']
        prix = request.form['prix']
        description = request.form['description']
        choose_categorie= session['categories']
        imag_url = session['files[]'] 
        titre = session['titre'] 
        prix= session['prix'] 
        description = session['description'] 
        titre=titre
        prix=prix
        description=description
        annonce= Annonce(choose_categorie,imag_url,description,titre,prix,description)
        saveAnnonce(annonce)
        return redirect(url_for('create_annonce4'))
    return render_template("backend/create/create_annonce3.html",itre=titre,user=current_user)
# ---------------------04 review---------------------------
# Route pour la quatrième page du formulaire (contact)
@app.route('/compte/review', methods=['GET', 'POST'])
@login_required
def create_annonce4():
   
    return render_template("backend/create/create_annonce4.html",user=current_user)


 
 
 
 
 
 
 
 
 
#  ------------ 404 -----------------
@app.errorhandler(404)
def page404(error):
    return render_template("errors/404.html"), 404
@app.errorhandler(404)
@login_required
def page404_user(error):
    return render_template("errors/404_user.html"), 404

if __name__ == '__main__':
    app.run(debug=True)

