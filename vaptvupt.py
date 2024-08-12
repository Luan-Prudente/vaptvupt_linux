from crypt import methods
from flask import Flask, make_response, render_template, request, url_for, redirect
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://prudente:1234@localhost:3306/mydb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Usuario(db.Model):
    __tablename__ = "usuario"
    id = db.Column('usu_id', db.Integer, primary_key=True)
    nome = db.Column('usu_nome', db.String(256))
    cpf = db.Column('usu_cpf', db.String(256))
    end = db.Column('usu_end', db.String(256))
    fone = db.Column('usu_fone', db.String(256))
    email = db.Column('usu_email', db.String(256))
    senha = db.Column('usu_senha', db.String(256)) 

    def __init__(self, nome, cpf, end, fone, email, senha):
        self.nome = nome
        self.cpf = cpf
        self.end = end
        self.fone = fone
        self.email = email
        self.senha = senha

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

@app.errorhandler(404)
def paginanaoencontrada(error):
    return render_template('paginanaoencontrada.html')

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/cad/usuario")
def usuario():
    return render_template('usuario.html', usuarios=Usuario.query.all(), titulo="Usuário")

@app.route("/usuario/criar", methods=['POST'])
def criarusuario():
    usuario = Usuario(
        request.form.get('user'),
        request.form.get('cpf'),
        request.form.get('end'),
        request.form.get('fone'),
        request.form.get('email'),
        request.form.get('password')
    )
    db.session.add(usuario)
    db.session.commit()
    return redirect(url_for('usuario'))

@app.route("/usuario/detalhar/<int:id>")
def buscarusuario(id):
    usuario = Usuario.query.get(id)
    return usuario.nome

@app.route("/usuario/editar/<int:id>", methods=['GET', 'POST'])
def editarusuario(id):
    usuario = Usuario.query.get(id)
    if request.method == 'POST':
        usuario.nome = request.form.get('user')
        usuario.cpf = request.form.get('cpf')
        usuario.end = request.form.get('end')
        usuario.fone = request.form.get('fone')
        usuario.email = request.form.get('email')
        usuario.senha = request.form.get('password')
        db.session.commit()
        return redirect(url_for('usuario'))

    return render_template('edsuario.html', usuario=usuario, titulo="Usuário")

@app.route("/usuario/deletar/<int:id>")
def deletarusuario(id):
    usuario = Usuario.query.get(id)
    db.session.delete(usuario)
    db.session.commit()
    return redirect(url_for('usuario'))

@app.route("/cad/anuncio")
def anuncio():
    return render_template('anuncio.html', anuncios=Anuncio.query.all(), categorias=Categoria.query.all(), usuarios=Usuario.query.all(), titulo="Anúncio")


@app.route("/anuncio/criar", methods=['POST'])
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
def editaranuncio(id):
    anuncio = Anuncio.query.get(id) 

    if request.method == 'POST':
        anuncio.nome = request.form.get('nome')
        anuncio.desc = request.form.get('desc')
        anuncio.qtd = int(request.form.get('qtd'))
        anuncio.preco = float(request.form.get('preco'))
        anuncio.cat_id = int(request.form.get('cat'))
        anuncio.usu_id = int(request.form.get('usu'))
        db.session.commit()
        return redirect(url_for('anuncio'))

    categorias = Categoria.query.all()
    usuarios = Usuario.query.all()
    return render_template('edanuncio.html', anuncio=anuncio, categorias=categorias, usuarios=usuarios, titulo="Editar Anúncio")

@app.route("/anuncio/deletar/<int:id>")
def deletaranuncio(id):
    anuncio = Anuncio.query.get(id)
    db.session.delete(anuncio)
    db.session.commit()
    return redirect(url_for('anuncio'))

@app.route("/anuncios/pergunta")
def pergunta():
    return render_template('pergunta.html')

@app.route("/anuncios/compra")
def compra():
    print("anuncio comprado")
    return ""

@app.route("/anuncio/favoritos")
def favoritos():
    print("favorito inserido")
    return f"<h4>Favorito inserido</h4>"

@app.route("/config/categoria")
def categoria():
    return render_template('categoria.html', categorias=Categoria.query.all(), titulo='Categoria')

@app.route("/categoria/criar", methods=['POST'])
def criarcategoria():
    categoria = Categoria(request.form.get('nome'), request.form.get('desc'))
    db.session.add(categoria)
    db.session.commit()
    return redirect(url_for('categoria'))

@app.route("/categoria/editar/<int:id>", methods=['GET', 'POST'])
def editarcategoria(id):
    categoria = Categoria.query.get(id)
    if request.method == 'POST':
        categoria.nome = request.form.get('nome')
        categoria.desc = request.form.get('desc')
        db.session.commit()
        return redirect(url_for('categoria'))

    return render_template('edcategoria.html', categoria=categoria)


@app.route("/categoria/deletar/<int:id>", methods=['POST'])
def deletarcategoria(id):
    categoria = Categoria.query.get(id)
    db.session.delete(categoria)
    db.session.commit()
    return redirect(url_for('categoria'))


@app.route("/relatorios/vendas")
def relVendas():
    return render_template('relvendas.html')

@app.route("/relatorios/compras")
def relCompras():
    return render_template('relcompras.html')

if __name__ == 'vaptvupt':
    with app.app_context():
        db.drop_all()
        db.create_all()
    app.run(debug=True)