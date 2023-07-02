from flask import Flask ,jsonify ,request
from flask_cors import CORS      
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_login import LoginManager, login_required, current_user
from bcrypt import bcrypt

app = Flask(__name__)
CORS(app, origins='http://127.0.0.1:5500')

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/Crudpython'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)
ma = Marshmallow(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class Producto(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	nombre = db.Column(db.String(100))
	precio = db.Column(db.Float())
	stock = db.Column(db.Integer)
	imagen = db.Column(db.String(400))
	
	
	def __init__(self,nombre,precio,stock,imagen):
		self.nombre = nombre
		self.precio = precio
		self.stock = stock
		self.imagen = imagen


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(255))

    def set_password(self, password):
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt)
        self.password_hash = hashed_password.decode('utf-8')

    def check_password(self, password):
        password_bytes = password.encode('utf-8')
        hashed_password_bytes = self.password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_password_bytes)

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))



with app.app_context():
	db.create_all()

class ProductoSchema(ma.Schema):
	class Meta:
		fields=('id','nombre','precio','stock','imagen')
	

producto_schema=ProductoSchema()            # El objeto producto_schema es para traer un producto
productos_schema=ProductoSchema(many=True)  # El objeto productos_schema es para traer multiples registros de producto


@app.route('/productos', methods=['GET']) #get,delete,post, put}
def get_productos():
	productos = Producto.query.all()
	resultado = productos_schema.dump(productos)
	return jsonify(resultado)

@app.route('/productos/<id>',methods=['GET'])
def get_producto(id):
	producto=Producto.query.get(id)
	return producto_schema.jsonify(producto)   # retorna el JSON de un producto recibido como parametro

@app.route('/productos/<id>',methods=['DELETE'])
@login_required
def delete_producto(id):
	producto=Producto.query.get(id)
	db.session.delete(producto)
	db.session.commit()
	return producto_schema.jsonify(producto)

@app.route('/productos',methods=['POST'])
@login_required
def create_producto():
	nombre = request.json['nombre']
	precio = request.json['precio']
	stock = request.json['stock']
	imagen = request.json['imagen']
	nuevo_producto = Producto(nombre,precio,stock,imagen)
	db.session.add(nuevo_producto)
	db.session.commit()
	return jsonify(message='Producto creado exitosamente')

@app.route('/productos/<id>',methods=['PUT'])
def update_producto(id):
	producto = Producto.query.get(id)
	nombre = request.json['nombre']
	precio = request.json['precio']
	stock = request.json['stock']
	imagen = request.json['imagen']

	producto.nombre = nombre
	producto.precio = precio
	producto.stock = stock
	producto.imagen = imagen
	
	db.session.commit()
	return producto_schema.jsonify(producto)


@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']

    admin = Admin.query.filter_by(username=username).first()

    if admin and admin.check_password(password):
        # Generar y devolver el token de autenticación
        # Manejar la lógica de inicio de sesión exitoso
        return jsonify(message='Inicio de sesión exitoso')

    # Manejar la lógica de inicio de sesión fallido
    return jsonify(message='Credenciales inválidas')

if __name__ == '__main__':
    app.run(debug=True, port=5000)