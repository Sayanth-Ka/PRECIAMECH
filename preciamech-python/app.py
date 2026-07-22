import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-in-production-use-a-random-string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///preciamech.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'
login_manager.login_message = 'Please log in to access the admin panel.'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    client_name = db.Column(db.String(200))
    location = db.Column(db.String(200), nullable=False)
    nature_of_work = db.Column(db.String(300), nullable=False)
    sector = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='completed')
    description = db.Column(db.Text)
    featured = db.Column(db.Boolean, default=False)
    image_filename = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    SECTOR_LABELS = {
        'pharma_api': 'Pharma API',
        'pharma_formulation': 'Pharma Formulation',
        'chemical': 'Chemical',
        'food_beverage': 'Food & Beverage',
        'fmcg': 'FMCG',
        'polymer': 'Polymer',
        'other': 'Other',
    }

    @property
    def sector_label(self):
        return self.SECTOR_LABELS.get(self.sector, self.sector)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Admin, int(user_id))


@app.route('/')
def index():
    featured = Project.query.filter_by(featured=True).order_by(Project.created_at.desc()).limit(6).all()
    total = Project.query.count()
    sectors = db.session.query(Project.sector, db.func.count(Project.id)).group_by(Project.sector).all()
    return render_template('index.html', featured=featured, total=total, sectors=sectors)


@app.route('/services')
def services():
    return render_template('services.html')


@app.route('/projects')
def projects():
    sector = request.args.get('sector', '')
    status = request.args.get('status', '')
    query = Project.query
    if sector:
        query = query.filter_by(sector=sector)
    if status:
        query = query.filter_by(status=status)
    all_projects = query.order_by(Project.created_at.desc()).all()
    return render_template('projects.html', projects=all_projects,
                           sectors=Project.SECTOR_LABELS,
                           selected_sector=sector, selected_status=status)


@app.route('/projects/<int:project_id>')
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('project_detail.html', project=project)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        flash('Thank you for your inquiry. We will get back to you shortly.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user = Admin.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('admin/login.html')


@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/admin')
@login_required
def admin_dashboard():
    all_projects = Project.query.order_by(Project.created_at.desc()).all()
    employees = Employee.query.all()
    employee_count = len(employees)
    total = len(all_projects)
    completed = sum(1 for p in all_projects if p.status == 'completed')
    featured_count = sum(1 for p in all_projects if p.featured)
    return render_template(
        'admin/dashboard.html',
        projects=all_projects,
        total=total,
        completed=completed,
        featured_count=featured_count
    )
    return render_template(
        'admin/dashboard.html',
        projects=all_projects,
        total=total,
        completed=completed,
        featured_count=featured_count,
        employee_count=employee_count
    )


@app.route('/admin/projects/new', methods=['GET', 'POST'])
@login_required
def admin_project_new():
    if request.method == 'POST':
        image_filename = None
        if 'image' in request.files:
            f = request.files['image']
            if f and f.filename and allowed_file(f.filename):
                filename = secure_filename(f.filename)
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename
        project = Project(
            title=request.form['title'],
            client_name=request.form.get('client_name') or None,
            location=request.form['location'],
            nature_of_work=request.form['nature_of_work'],
            sector=request.form['sector'],
            status=request.form['status'],
            description=request.form.get('description') or None,
            featured='featured' in request.form,
            image_filename=image_filename,
        )
        db.session.add(project)
        db.session.commit()
        flash('Project created successfully.', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/project_form.html', project=None,
                           sectors=Project.SECTOR_LABELS, action='new')


@app.route('/admin/projects/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_project_edit(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        if 'image' in request.files:
            f = request.files['image']
            if f and f.filename and allowed_file(f.filename):
                filename = secure_filename(f.filename)
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                project.image_filename = filename
        project.title = request.form['title']
        project.client_name = request.form.get('client_name') or None
        project.location = request.form['location']
        project.nature_of_work = request.form['nature_of_work']
        project.sector = request.form['sector']
        project.status = request.form['status']
        project.description = request.form.get('description') or None
        project.featured = 'featured' in request.form
        db.session.commit()
        flash('Project updated successfully.', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/project_form.html', project=project,
                           sectors=Project.SECTOR_LABELS, action='edit')


@app.route('/admin/projects/<int:project_id>/delete', methods=['POST'])
@login_required
def admin_project_delete(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/projects/<int:project_id>/toggle-featured', methods=['POST'])
@login_required
def admin_toggle_featured(project_id):
    project = Project.query.get_or_404(project_id)
    project.featured = not project.featured
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


def init_db():
    with app.app_context():
        db.create_all()
        if not Admin.query.first():
            admin = Admin(email='admin@preciamech.com')
            admin.set_password('Admin@1234')
            db.session.add(admin)
            db.session.commit()
            print('Default admin created: admin@preciamech.com / Admin@1234')


@app.route('/employees')
@app.route('/employees')
def employees():

    senior_manager = Employee.query.filter_by(category='senior_manager').all()
    manager = Employee.query.filter_by(category='manager').all()
    engineer = Employee.query.filter_by(category='engineer').all()
    designer = Employee.query.filter_by(category='designer').all()

    return render_template(
        'employees.html',
        senior_manager=senior_manager,
        manager=manager,
        engineer=engineer,
        designer=designer
    )

@app.route('/employees/<int:employee_id>')
def employee_detail(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    return render_template(
        'employee_detail.html',
        employee=employee
    )
@app.route('/admin/employees')
@login_required
def admin_employees():
    employees = Employee.query.order_by(Employee.created_at.desc()).all()
    return render_template(
        'admin/employee_dashboard.html',
        employees=employees
    )

@app.route('/admin/employees/new', methods=['GET', 'POST'])
@login_required
def admin_employee_new():

    if request.method == 'POST':

        image_filename = None

        if 'image' in request.files:
            file = request.files['image']

            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename

        employee = Employee(
            name=request.form['name'],
            category=request.form['category'],
            qualification=request.form.get('qualification'),
            experience=request.form.get('experience'),
            description=request.form.get('description'),
            phone=request.form.get('phone'),
            email=request.form.get('email'),
            image_filename=image_filename
        )

        db.session.add(employee)
        db.session.commit()

        flash("Employee added successfully.", "success")

        return redirect(url_for('admin_employees'))

    return render_template(
        'admin/employee_form.html',
        employee=None,
        action='new'
    )

@app.route('/admin/employees/<int:employee_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_employee_edit(employee_id):

    employee = Employee.query.get_or_404(employee_id)

    if request.method == 'POST':

        if 'image' in request.files:
            file = request.files['image']

            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                employee.image_filename = filename

        employee.name = request.form['name']
        employee.category = request.form['category']
        employee.qualification = request.form.get('qualification')
        employee.experience = request.form.get('experience')
        employee.description = request.form.get('description')
        employee.phone = request.form.get('phone')
        employee.email = request.form.get('email')

        db.session.commit()

        flash("Employee updated successfully.", "success")

        return redirect(url_for('admin_employees'))

    return render_template(
        'admin/employee_form.html',
        employee=employee,
        action='edit'
    )

@app.route('/admin/employees/<int:employee_id>/delete', methods=['POST'])
@login_required
def admin_employee_delete(employee_id):

    employee = Employee.query.get_or_404(employee_id)

    db.session.delete(employee)
    db.session.commit()

    flash("Employee deleted successfully.", "success")

    return redirect(url_for('admin_employees'))


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(20), nullable=False)
    qualification = db.Column(db.String(200))
    experience = db.Column(db.String(100))
    description = db.Column(db.Text)
    image_filename = db.Column(db.String(250))
    phone = db.Column(db.String(30))
    email = db.Column(db.String(150))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)



