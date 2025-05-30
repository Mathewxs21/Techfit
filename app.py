from flask import Flask, redirect, render_template, url_for, request, flash
from models import User
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import os, secure_filename
import sqlite3

from flask_login import LoginManager, login_user, current_user, login_required, logout_user
login_manager = LoginManager()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ULTRAMEGADIFICIL'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/')
def index():    
    return render_template('index.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form.get('senha') 
        confirmasenha = request.form['confirmasenha']
        email = request.form['email']
        telefone = request.form['telefone']
        data_nascimento = request.form['data']
        tipo_usuario = request.form['tipoUsuario']
        genero = request.form['genero']
        dias_treino = request.form.get('dias_treino')
        horario_treino = request.form['horario_treino']
        dias_trabalho = request.form.get('dias_trabalho')
        horario_trabalho = request.form['horario_trabalho']

        if User.exists(email) == False:
            if senha == confirmasenha:
                id = User.inserir_users(nome, senha, email, telefone, data_nascimento, genero, tipo_usuario, dias_treino, horario_treino, dias_trabalho, horario_trabalho)

                user = User(id=id, nome=nome, email=email, senha=senha, telefone=telefone, data_nascimento=data_nascimento, genero=genero, tipo_usuario=tipo_usuario, dias_treino=dias_treino, horario_treino=horario_treino, dias_trabalho=dias_trabalho, horario_trabalho=horario_trabalho)
                login_user(user)
               
                flash("Cadastro realizado com sucesso. Faça login agora!")
                return redirect(url_for('index'))  # Redirect to index to show the modal
            else:
                flash("As senhas não coincidem.")
        else:
            flash("Usuário já existente.")
    return render_template('index.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.get_by_email(email)
        
        if user and check_password_hash(user.senha, password):
            login_user(user)
            
            if user.tipo_usuario == 'Aluno' or user.tipo_usuario == 'aluno' :
                return redirect(url_for('profile'))
            else:
                return 'Personalllllllllllllll'
            
        else:
            flash('Credenciais inválidas')
            return redirect(url_for('index'))
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    user_id = current_user.get_id() 
    user = User.get(user_id)  
    if 'foto_perfil' in request.files:
        foto_perfil = request.files['foto_perfil']
        if foto_perfil:
            filename = secure_filename(foto_perfil.filename)
            file_path = os.path.join('uploads/profile_pictures', filename)
            foto_perfil.save(file_path)
            
            # Atualize o caminho da imagem no banco de dados
            User.atualizar_foto_perfil(user_id, file_path)
            flash("Foto de perfil atualizada com sucesso!")
        else:
            flash("Nenhuma imagem foi selecionada.")

    if user:
        return render_template('profile.html', user_info=user)
    else:
        flash("Usuário não encontrado.")
        return redirect(url_for('index'))
    

@app.route('/incrementar', methods=['POST'])
@login_required
def incrementar_contador():
    user_id = current_user.get_id()
    User.atualizar_contador(user_id)
    novo_valor = User.get(user_id).contador
    return str(novo_valor)

@app.route('/tela_exercicios')
def tela_exercicios():
    return render_template('tela_exercicios.html')

@app.route('/exercise_page')
def exercise_page():
    return render_template('exercise_page.html')

@app.route('/medidas')
def medidas():
    user_id = current_user.get_id() 
    user = User.get(user_id)  

    if user:
        return render_template('medidas.html', user_info=user)
    else:
        flash("Usuário não encontrado.")
        return redirect(url_for('index'))

@app.route('/configuracoes', methods=['GET', 'POST'])
def configuracoes():
    userid = current_user.get_id()
    user = User.get(userid) 
    if request.method == 'POST':
        nome = request.form['nome_edit']
        senha = request.form.get('senha_edit') 
        confirmasenha = request.form['confirmasenha_edit']
        email = request.form['email_edit']
        telefone = request.form['telefone_edit']
        data_nascimento = request.form['data_nascimento_edit']
        dias_treino = request.form.get('dias_treino_edit')
        horario_treino = request.form['horario_treino_edit']

        if senha == confirmasenha and check_password_hash(user.senha, senha):
            User.atualizar_dados(nome, email, telefone, data_nascimento, dias_treino, horario_treino, userid)
        else:
            flash("As senhas não coincidem.")
    um_user = User.one(userid)
    return render_template('configuracoes.html', user=um_user, user_info=user)

# 8 - logout
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
