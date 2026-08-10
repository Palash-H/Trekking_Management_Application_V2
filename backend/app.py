from flask import Flask, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from flask_cors import CORS
from config import Config
from extensions import cache


from routes.api import auth_b
from routes.admin_api import auth_bp
from routes.booking_api import booking_bp
from routes.catalog_api import catalog_bp
from routes.celery_api import reports_bp
from routes.staff_bp import staff_bp
from routes.trekker_api import user_bp
# from routes.ops_api import ops_b
from model import db, User, TokenBlocklist

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)



cache.init_app(app)
db.init_app(app)


app.register_blueprint(auth_b, url_prefix='/')
app.register_blueprint(auth_bp, url_prefix='/')
app.register_blueprint(booking_bp, url_prefix='/')
app.register_blueprint(catalog_bp, url_prefix='/')
app.register_blueprint(reports_bp, url_prefix='/')
app.register_blueprint(staff_bp, url_prefix="/"),
app.register_blueprint(user_bp, url_prefix="/")
# app.register_blueprint(ops_b, url_prefix='/api/ops')

jwt = JWTManager(app)

@app.route("/", methods=['GET'])
@jwt_required()
def home():
    print(get_jwt_identity())
    data = {
        "numbers": [1, 2, 4, 5, 6],
        "message": "Hello, World"
    }
    
    return jsonify(data), 200


@jwt.token_in_blocklist_loader
def check_revoke(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload['jti']
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()
    return token is not None


def admin_reg():
    # Querying the unified User table for the admin email
    if not User.query.filter_by(email=Config.admin_email).first():
        admin = User(
            email=Config.admin_email,
            name="Admin",
            passhash=generate_password_hash(Config.admin_password),
            role='admin'  # Explicitly defining the role as 'admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("Default Admin created successfully.")
    else:
        pass


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        admin_reg()

    app.run(debug=True, port=5050)