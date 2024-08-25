from crypt import methods
from flask import Flask, make_response, render_template, request, url_for, redirect
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy
from flask_login import (current_user, LoginManager, login_user, logout_user, login_required)
import hashlib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://prudente:1234@localhost:3306/mydb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

app.secret_key = 'testador01*'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'



class Usuario(db.Model):
    __tablename__ = "usuario"
    id = db.Column('usu_id', db.Integer, primary_key=True)
    nome = db.Column('usu_nome', db.String(256))
    cpf = db.Column('usu_cpf', db.String(256))
    end = db.Column('usu_end', db.String(256))
    fone = db.Column('usu_fone', db.String(256))
    email = db.Column('usu_email', db.String(256), unique=True)
    senha = db.Column('usu_senha', db.String(256)) 

    def __init__(self, nome, cpf, end, fone, email, senha):
        self.nome = nome
        self.cpf = cpf
        self.end = end
        self.fone = fone
        self.email = email
        self.senha = senha

    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return True
    
    def get_id(self):
        return str(self.id)
    

class Categoria(db.Model):
    __tablename__ = "categoria"
    id = db.Column('cat_id', db.Integer, primary_key=True)
    nome = db.Column('cat_nome', db.String(256))
    desc = db.Column('cat_desc', db.String(256))

    def __init__(self, nome, desc):
        self.nome = nome
        self.desc = desc

class Anuncio(db.Model):
    __tablename__ = "anuncio"
    id = db.Column('anu_id', db.Integer, primary_key=True)
    nome = db.Column('anu_nome', db.String(256))
    desc = db.Column('anu_desc', db.String(256))
    qtd = db.Column('anu_qtd', db.Integer)
    preco = db.Column('anu_preco', db.Float)
    cat_id = db.Column('cat_id', db.Integer, db.ForeignKey("categoria.cat_id"))
    usu_id = db.Column('usu_id', db.Integer, db.ForeignKey("usuario.usu_id"))

    categoria = db.relationship('Categoria', backref='anuncios')
    usuario = db.relationship('Usuario', backref='anuncios')

    def __init__(self, nome, desc, qtd, preco, cat_id, usu_id):
        self.nome = nome
        self.desc = desc
        self.qtd = qtd
        self.preco = preco
        self.cat_id = cat_id
        self.usu_id = usu_id

class Pergunta(db.Model):
    __tablename__ = "pergunta"
    id = db.Column('per_id', db.Integer, primary_key=True)
    texto = db.Column('per_texto', db.String(256))
    anuncio_id = db.Column('anu_id', db.Integer, db.ForeignKey("anuncio.anu_id"))

    anuncio = db.relationship('Anuncio', backref='perguntas')

    def __init__(self, texto, anuncio_id):
        self.texto = texto
        self.anuncio_id = anuncio_id

class Favorito(db.Model):
    __tablename__ = "favorito"
    id = db.Column('fav_id', db.Integer, primary_key=True)
    anuncio_id = db.Column('anu_id', db.Integer, db.ForeignKey("anuncio.anu_id"))
    usuario_id = db.Column('usu_id', db.Integer, db.ForeignKey("usuario.usu_id"))

    anuncio = db.relationship('Anuncio', backref='favoritos')
    usuario = db.relationship('Usuario', backref='favoritos')

    def __init__(self, anuncio_id, usuario_id):
        self.anuncio_id = anuncio_id
        self.usuario_id = usuario_id

@app.errorhandler(404)
def paginanaoencontrada(error):
    return render_template('paginanaoencontrada.html')

@login_manager.user_loader
def load_user(id):
    return Usuario.query.get(id)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = hashlib.sha512(str(request.form.get('senha')).encode("utf-8")).hexdigest()

        user = Usuario.query.filter_by(email=email, senha=password).first()

        if user:
            login_user(user)
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))
        
    return render_template('login.html', error="Login ou senha inválido")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/")
@login_required
def index():
    return render_template('index.html')

@app.route("/cad/usuario")
@login_required
def usuario():
    return render_template('usuario.html', usuarios=Usuario.query.all(), titulo="Usuário")

@app.route("/usuario/criar", methods=['POST'])
@login_required
def criarusuario():
    hash = hashlib.sha512(str(request.form.get('senha')).encode("utf-8")).hexdigest()
    usuario = Usuario(
        request.form.get('nome'),
        request.form.get('cpf'),
        request.form.get('end'),
        request.form.get('fone'),
        request.form.get('email'),
        hash
    )
    db.session.add(usuario)
    db.session.commit()
    return redirect(url_for('usuario'))

@app.route("/usuario/detalhar/<int:id>")
@login_required
def buscarusuario(id):
    usuario = Usuario.query.get(id)
    return usuario.nome

@app.route("/usuario/editar/<int:id>", methods=['GET', 'POST'])
@login_required
def editarusuario(id):
    usuario = Usuario.query.get(id)
    if request.method == 'POST':
        usuario.nome = request.form.get('nome')
        usuario.cpf = request.form.get('cpf')
        usuario.end = request.form.get('end')
        usuario.fone = request.form.get('fone')
        usuario.email = request.form.get('email')
        usuario.senha = hashlib.sha512(str(request.form.get('senha')).encode("utf-8")).hexdigest()
        db.session.commit()
        return redirect(url_for('usuario'))

    return render_template('edsuario.html', usuario=usuario, titulo="Usuário")

@app.route("/usuario/deletar/<int:id>")
@login_required
def deletarusuario(id):
    usuario = Usuario.query.get(id)
    db.session.delete(usuario)
    db.session.commit()
    return redirect(url_for('usuario'))

@app.route("/cad/anuncio")
@login_required
def anuncio():
    return render_template('anuncio.html', anuncios=Anuncio.query.all(), categorias=Categoria.query.all(), usuarios=Usuario.query.all(), titulo="Anúncio")

@app.route("/anuncio/criar", methods=['POST'])
@login_required
def criaranuncio():
    nome = request.form.get('nome')
    desc = request.form.get('desc')
    qtd = int(request.form.get('qtd'))
    preco = float(request.form.get('preco'))
    cat_id = int(request.form.get('cat'))
    usu_id = int(request.form.get('usu'))

    anuncio = Anuncio(nome, desc, qtd, preco, cat_id, usu_id)
    db.session.add(anuncio)
    db.session.commit()

    return redirect(url_for('anuncio'))

@app.route('/anuncio/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editaranuncio(id):
    anuncio = Anuncio.query.get(id) 

    if request.method == 'POST':
        anuncio.nome = request.form.get('nome')
        anuncio.desc = request.form.get('desc')
        anuncio.qtd = int(request.form.get('qtd'))
        anuncio.preco = float(request.form.get('preco'))
        anuncio.cat_id = int(request.form.get('cat'))
        db.session.commit()
        return redirect(url_for('anuncio'))

    categorias = Categoria.query.all()
    return render_template('edanuncio.html', anuncio=anuncio, categorias=categorias, titulo="Editar Anúncio")

@app.route("/anuncio/deletar/<int:id>")
@login_required
def deletaranuncio(id):
    anuncio = Anuncio.query.get(id)
    db.session.delete(anuncio)
    db.session.commit()
    return redirect(url_for('anuncio'))

@app.route("/anuncio/perguntas/<int:anuncio_id>", methods=['GET', 'POST'])
@login_required
def perguntas_anuncio(anuncio_id):
    anuncio = Anuncio.query.get_or_404(anuncio_id)
    perguntas = Pergunta.query.filter_by(anuncio_id=anuncio_id).all()

    if request.method == 'POST':
        texto = request.form.get('texto')
        print(f"Texto recebido: {texto}") 
        if texto:
            pergunta = Pergunta(texto=texto, anuncio_id=anuncio_id)
            db.session.add(pergunta)
            db.session.commit()
            print("Pergunta salva com sucesso")
        return redirect(url_for('perguntas_anuncio', anuncio_id=anuncio_id))

    return render_template('pergunta.html', anuncio=anuncio, perguntas=perguntas)

@app.route("/anuncio/favoritar/<int:anuncio_id>")
@login_required
def favoritar_anuncio(anuncio_id):
    favorito = Favorito.query.filter_by(anuncio_id=anuncio_id, usuario_id=current_user.id).first()
    if favorito:
        db.session.delete(favorito)
        db.session.commit()
        msg = "Favorito removido com sucesso!"
    else:
        favorito = Favorito(anuncio_id=anuncio_id, usuario_id=current_user.id)
        db.session.add(favorito)
        db.session.commit()
        msg = "Anúncio adicionado aos favoritos!"
    return redirect(url_for('anuncio', msg=msg))

@app.route("/favoritos")
@login_required
def favoritos_usuario():
    favoritos = Favorito.query.filter_by(usuario_id=current_user.id).all()
    anuncios_favoritos = [favorito.anuncio for favorito in favoritos]
    return render_template('favoritos.html', anuncios=anuncios_favoritos)

@app.route("/anuncios/compra")
@login_required
def compra():
    print("anuncio comprado")
    return ""

@app.route("/config/categoria")
@login_required
def categoria():
    return render_template('categoria.html', categorias=Categoria.query.all(), titulo='Categoria')

@app.route("/categoria/criar", methods=['POST'])
@login_required
def criarcategoria():
    categoria = Categoria(request.form.get('nome'), request.form.get('desc'))
    db.session.add(categoria)
    db.session.commit()
    return redirect(url_for('categoria'))

@app.route("/categoria/editar/<int:id>", methods=['GET', 'POST'])
@login_required
def editarcategoria(id):
    categoria = Categoria.query.get(id)
    if request.method == 'POST':
        categoria.nome = request.form.get('nome')
        categoria.desc = request.form.get('desc')
        db.session.commit()
        return redirect(url_for('categoria'))

    return render_template('edcategoria.html', categoria=categoria)

@app.route("/categoria/deletar/<int:id>", methods=['POST'])
@login_required
def deletarcategoria(id):
    categoria = Categoria.query.get(id)
    db.session.delete(categoria)
    db.session.commit()
    return redirect(url_for('categoria'))

@app.route("/relatorios/vendas")
@login_required
def relVendas():
    return render_template('relvendas.html')

@app.route("/relatorios/compras")
@login_required
def relCompras():
    return render_template('relcompras.html')

if __name__ == 'vaptvupt':
    with app.app_context():
        db.create_all()
    app.run(debug=True)