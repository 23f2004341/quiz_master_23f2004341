from flask import Flask
from config import Config
from extensions import db, login_manager, bcrypt, cache
from dotenv import load_dotenv
import os
from flask_cors import CORS

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS for frontend
    CORS(app, supports_credentials=True, origins=["http://localhost:8080"])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    # Initialize cache with error handling
    try:
        cache.init_app(app)
        print("Cache initialized successfully")
    except Exception as e:
        print(f"Cache initialization failed: {e}")
        print("Continuing without cache...")
    
    # Set up login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from api import api
    app.register_blueprint(api, url_prefix='/api')
    
    # Create database tables
    with app.app_context():
        db.create_all()
        # Ensure admin user exists with hashed password
        from models import User
        from werkzeug.security import generate_password_hash
        admin = User.query.filter_by(email="admin@123.com").first()
        if not admin:
            admin = User(
                email="admin@123.com",
                full_name="Admin",
                role="admin"
            )
            admin.password = generate_password_hash("admin123")
            db.session.add(admin)
            db.session.commit()
            print("Admin account created: email=admin@123.com password=admin123")
        else:
            # If admin exists but password is not hashed, re-hash it
            from werkzeug.security import check_password_hash
            try:
                # Try to check if password is already hashed
                check_password_hash(admin.password, "test")
            except Exception:
                admin.password = generate_password_hash("admin123")
                db.session.commit()
                print("Admin password was not hashed. Reset to default: admin123")
        
        # Try to warm up cache on startup for better performance
        try:
            from extensions import warm_cache, optimize_cache_performance
            print("Warming up cache...")
            warm_cache()
            
            print("Optimizing cache performance...")
            optimize_cache_performance()
        except Exception as e:
            print(f"Cache operations failed: {e}")
            print("Continuing without cache optimization...")
        
        print("Application initialized successfully!")
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)

