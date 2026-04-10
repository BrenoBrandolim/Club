from operator import index

from flask import Flask
from modules.usuarios.routes import usuario_bp
#from modules.comandas.routes import comandas_bp

app = Flask(__name__)
app.secret_key = 'qualquer_coisa'

#Blueprints
app.register_blueprint(usuario_bp)
#app.register_blueprint(comandas_bp)

@app.route('/')
def index():
    return {"msg": "API Club rodando"}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

