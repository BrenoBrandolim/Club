from dotenv import load_dotenv
load_dotenv(override=True)

from operator import index

from flask import Flask, render_template, request, jsonify
from modules.usuarios.routes import usuario_bp
from modules.comandas.routes import comandas_bp
from modules.pontos.routes import pontos_bp
from modules.resgates.routes import resgates_bp
from modules.produtos.routes import produtos_bp
app = Flask(__name__)
app.secret_key = 'qualquer_coisa'

#Blueprints
app.register_blueprint(usuario_bp)
app.register_blueprint(comandas_bp)
app.register_blueprint(pontos_bp)
app.register_blueprint(resgates_bp)
app.register_blueprint(produtos_bp)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

