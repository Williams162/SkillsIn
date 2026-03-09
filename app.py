from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'skillsin_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///skillsin.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


# =========================
# DATABASE MODEL
# =========================
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    qualification = db.Column(db.String(150), nullable=False)
    headline = db.Column(db.String(200))
    bio = db.Column(db.Text)
    role = db.Column(db.String(20), default="user")   # Admin/User


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# =========================
# ROUTES
# =========================

@app.route('/')
def home():
    return redirect(url_for('login'))


# REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        existing_user = User.query.filter_by(email=request.form['email']).first()
        if existing_user:
            flash("Email already registered!", "danger")
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        new_user = User(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            email=request.form['email'],
            password=hashed_password,
            address=request.form['address'],
            qualification=request.form['qualification']
        )

        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and bcrypt.check_password_hash(user.password, request.form['password']):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password.", "danger")
    return render_template('login.html')


# DASHBOARD
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


# EDIT PROFILE
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.headline = request.form['headline']
        current_user.bio = request.form['bio']
        current_user.address = request.form['address']
        current_user.qualification = request.form['qualification']
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('dashboard'))
    return render_template('edit_profile.html')


# LOGOUT
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))


# =========================
# ADMIN DASHBOARD ROUTE
# =========================
@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != "admin":  # Only admin can access
        flash("Access denied!", "danger")
        return redirect(url_for('dashboard'))
    users = User.query.all()
    return render_template("admin_dashboard.html", users=users)


# =========================
# RUN APPLICATION
# =========================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Create default admin if not exists
        if not User.query.filter_by(email="admin@skillsin.com").first():
            admin_password = bcrypt.generate_password_hash("admin123").decode('utf-8')
            admin = User(
                first_name="Admin",
                last_name="User",
                email="admin@skillsin.com",
                password=admin_password,
                address="Admin Office",
                qualification="System Administrator",
                role="admin"
            )
            db.session.add(admin)
            db.session.commit()

    app.run(debug=True)