from flask import Flask #pour creer l'appli
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import logging as lg
from datetime import datetime
from flask_login import UserMixin

app= Flask(__name__) # instance de l'appli
#  Montrer a flask le chemin du fichier de notre fichier de config
app.config.from_object('config')
app.config['SECRET_KEY'] = 'secret_key'
# Configuration pour stocker les images téléchargées
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}

# from main import app


# Creation d'une instance de la BD
# db=SQLAlchemy()
# db.init_app(app) # connecter l'appli avec la BD
# print(app.config)
db = SQLAlchemy(app) 

# Creation d'un model <=> Table dans la BD

class Annonce(db.Model):
    id= db.Column(db.Integer,primary_key=True)    
    choose_categorie=db.Column(db.String(100),nullable=False)
    img_url=db.Column(db.String(1000))
    titre= db.Column(db.String(200),nullable=False,unique=True)
    prix=db.Column(db.Integer,nullable=False)
    description=db.Column(db.Text,nullable=False)
    lieu=db.Column(db.String(255),nullable=False)
    livraison=db.Column(db.String(10))
    publier = db.Column(db.String(100))
    # publier = db.Column(db.DateTime,default=datetime.utcnow)


#  les fonctions executants des requetes au niveau de la BD
def getAnnonce():
    annonce=Annonce.query.all() # recuperer tous les annonces de la BD
    return annonce
def findAnnonceById(id_annonce):
    annonce = Annonce.query.get(id_annonce)# recuperer un seul annonce par son id
    return annonce 
def findAnnonceByCategories(categories):
    categories = Annonce.query.get(categories)# recuperer un seul annonce par son categories
    return categories 
def saveAnnonce(annonce: Annonce):# enregistrer une annonce dans la BD
    db.session.add(annonce)
    db.session.commit()
    
    
    
#------------QUELQUES REQUETE DE BASE
class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    nom_complet= db.Column(db.String(200),nullable=False)
    telephone= db.Column(db.Integer,unique=True)
    password= db.Column(db.String(50))
    email= db.Column(db.String(50))
    # afficher la classe user par defaut
    def __repr__(self) :
        return f"<User : {self.nom_complet} {self.telephone}>"

def tel_exist(telephone,password):
    # recuperer user dont le telephone et le password est deja dans la bd
    user = User.query.filter_by(telephone=telephone, password=password).first()
    return user
 
def insert_user(user:User):
    db.session.add(user)
    db.session.commit()
    lg.warning('insertion de User')

def recherche_annonces(recherche):
    Annonce.query.filter(or_(
            Annonce.titre.like(f'%{recherche}%'),
            Annonce.description.like(f'%{recherche}%')
        )).all()
# les commandes pour tester
# 01 init la bd  
@app.cli.command("init_db")# creer une commande
def init_db():
    # supprimer toutes les tables de la bD
    db.drop_all()
    # Creer à nouveau les tables
    db.create_all()
    lg.warning('La BDs a ete init')
# 02 insert into 
@app.cli.command('insert_user')
def insertInto():
    user1= User(nom_complet='seydou sow',password="free1",email="tiou@gmail.com")
    db.session.add(user1)
    user2= User(nom_complet='saly Diop',password="free2",email="saly@gmail.com")
    db.session.add(user2)
    db.session.commit()
    lg.warning('insertion de User')
# 03 SELECT ALL
@app.cli.command("select_all")
def select_all():
    # recuperer tous les users de la BD
    users= User.query.all()
    for u in users:
        print(u)
# 04 SELECT WHERE
@app.cli.command("select_where")
def select_where():
    # 1er methode :
    # recuperer user dont le username =az
    # az= User.query.filter_by(username="az").all()# recupere tous les users dont le username egal az
    #az= User.query.filter_by(username="az").first()# recupere le premier dont le username egal az
    # print(az)
    # 2 em methode:
    users= User.query.filter(User.username=="az").first()
    print(users)
    # Les users dont le nom est different de az
    # users= User.query.filter(User.username!="az").first()

# 05 SELECT LIKE
@app.cli.command("select_like")
def select_like():
    # selectionner tous les user dont le nom contient la ettre i:
    # user_i=User.query.filter(User.lastname.like("%i%")).all()
    # print(user_i)
    # -------------------------------------
    #  selectionner tous les Users quit ont un compte gmail$
    users_gmail=User.query.filter(User.email.like("%gmail.com")).all()
    print(users_gmail)
# 06  SELECT IN
@app.cli.command("select_in")
def select_in():
    # selectionner tous les users dont le prenom est aly ou lamine
    users_aly_lamine= User.query.filter(User.firstname.in_(['Aly','lamine'])).all()
    print(users_aly_lamine)
# 07  SELECT NOT IN
@app.cli.command("select_not_in")
def select_not_in():
    # selectionner tous les users dont le prenom n'est ni aly ni lamine
    users_not_in= User.query.filter(~User.firstname.in_(['Aly','lamine'])).all()
    print(users_not_in)
# 08  SELECT NULL - NOT NULL
@app.cli.command("select_null_notnull")
def select_nul_notnull():
    # selectionner tous les users qui n'ont pas d'email
    users_no_email= User.query.filter(User.email== None).all()
    print(users_no_email)
    # ----------------
    # selectionner les users qui ont un email
    users_email= User.query.filter(User.email != None).all()
    print(users_email)
    
# 09 SELECT AND
@app.cli.command("select_and")
def select_and():
    # selectionner le  1er User qui a comme login nat et mot de passe 123456
    # 1er methode
    # user= User.query.filter(User.username== 'nat',User.password=="123456").first()
    # print(user)
    # ----------------------------------
    # 2em methode
    # user=User.query.filter(User.username == "nat").filter(User.password== "123456").first()
    # print(user)
    # --------------------------------------
    # 3em methode
    user=User.query.filter(db.and_(  User.username == "nat",User.password== "123456")).first()
    print(user)
# 10 SELECT OR
@app.cli.command("select_or")
def select_or():
    #  selectionner les utilsateurs qui ont un compte gmail ou yahoo
    user=User.query.filter(db.or_(User.email.like("%@gmail.com"),User.email.like("%@yahoo.com"))).all()
    print(user)
# 11 SELECT ORDER BY
@app.cli.command("select_orderby")
def select_orderby():
    # recuperer tous les users de la BD par ordre alphabetique sur le nom
    users= User.query.order_by(User.lastname).all()
    print(users)
# 12 SELECT LIMIT
@app.cli.command("select_limit")
def select_limit():
    # recuperer  les 3 premiers users de la BD 
    # users= User.query.limit(3).all()
        # recuperer  les 2 premiers users de la BD par ordre alphabetique sur le nom
    users= User.query.order_by(User.lastname).limit(2).all()
    print(users)
    # NB: offset()saute les 2 premiers s'utilise de la meme facon que limit
# 13 SELECT COUNT
@app.cli.command("select_count")
def select_count():
    # recuperer  le nombre de users de la BD 
    nbr= User.query.count()
    print(nbr)
    # users = User.query.all()
    # print(len(users))


# creer la BD bd.sqlite
def test():
    
    with app.app_context():
        db.create_all() 
        #   inserer une annonce dans la BD
        annonce1=Annonce(
            choose_categorie="animaux",
            img_url="https://i.roamcdn.net/hz/ed/listing-thumb-360w/81b01d727eaa7726dbc0ca4c4ecd078f/-/horizon-files-prod/ed/picture/q788gmqq/8ccc6a0402034fc1238489a92c698ecfd7d71122.jpg",
            titre= "bantam",
            prix="50 000",
            description="couple pekin caillouté",
            lieu="grand dakar",
            livraison="non",
            publier ="28/mars 2023, 03:29",
        )
       
        db.session.add(annonce1) # Ajouter au niveau de la session 
        db.session.commit() # Ajouter dans BD 