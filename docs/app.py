from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necessário para usar flash()

# Configuração do banco de dados (SQLite para testes; pode alterar para MySQL depois)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agendamentos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo do banco de dados para agendamentos
class Agendamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    data = db.Column(db.Date, nullable=False)
    horario = db.Column(db.String(5), nullable=False)
    mensagem = db.Column(db.Text, nullable=True)

# Rota para exibir o formulário
@app.route('/')
def index():
    return render_template('formulario.html')

# Rota para processar o agendamento
@app.route('/agendar', methods=['POST'])
def agendar():
    nome = request.form['nome']
    telefone = request.form['telefone']
    email = request.form['email']
    data = datetime.strptime(request.form['data'], '%Y-%m-%d').date()
    horario = request.form['horario']
    mensagem = request.form.get('mensagem')

    # Criação de um novo agendamento
    novo_agendamento = Agendamento(
        nome=nome, telefone=telefone, email=email, data=data, horario=horario, mensagem=mensagem
    )

    # Salvar no banco de dados
    db.session.add(novo_agendamento)
    db.session.commit()

    # Mensagem flash para informar o sucesso
    flash('Agendamento realizado com sucesso! Um SMS foi enviado para o seu número.', 'success')

    return redirect(url_for('index'))

# Rota para exibir a lista de agendamentos
@app.route('/agendamentos')
def lista_agendamentos():
    agendamentos = Agendamento.query.all()  # Recupera todos os agendamentos do banco de dados
    return render_template('lista_agendamentos.html', agendamentos=agendamentos)

# Rota para deletar um agendamento
@app.route('/deletar/<int:id>')
def deletar(id):
    agendamento = Agendamento.query.get_or_404(id)  # Recupera o agendamento pelo ID
    db.session.delete(agendamento)  # Exclui o agendamento
    db.session.commit()  # Salva a mudança no banco de dados
    return redirect(url_for('lista_agendamentos'))  # Redireciona para a página de agendamentos

@app.route('/horarios_indisponiveis', methods=['GET'])
def horarios_indisponiveis():
    data = request.args.get('data')  # Pega a data enviada na requisição
    if not data:
        return {"error": "Data não fornecida."}, 400

    try:
        data_obj = datetime.strptime(data, '%Y-%m-%d').date()
    except ValueError:
        return {"error": "Formato de data inválido."}, 400

    # Consulta os horários ocupados para a data específica
    agendamentos = Agendamento.query.filter_by(data=data_obj).all()
    horarios = [agendamento.horario for agendamento in agendamentos]

    return {"horarios_indisponiveis": horarios}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria o banco de dados e tabelas (se não existirem)
    app.run(debug=True)