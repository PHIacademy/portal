from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_chinese = db.Column(db.Boolean, default=False, nullable=False)  # Flag to identify Chinese subjects
    articles = db.relationship('Article', backref='subject', lazy=True)

    @property
    def is_chinese_subject(self):
        """Helper property to ensure boolean conversion"""
        return bool(self.is_chinese)

    def __repr__(self):
        return f'<Subject {self.name}>'

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    level = db.Column(db.String(20), nullable=False, default='F1-F3')  # Levels: P1-P2, P3-P4, P5-P6, F1-F3, F4-F6
    genre = db.Column(db.String(20))  # For Chinese articles: 記敘文, 描寫文, 說明文, 議論文, 抒情文, 書信, 日記, 看圖作文, 讀後感, 詩詞, 應用文
    html_content = db.Column(db.Text)
    html_path = db.Column(db.String(255))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Article {self.title}>'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_login = db.Column(db.DateTime)
    role = db.Column(db.String(20), default='student')  # student, teacher, admin
    auth_provider = db.Column(db.String(20), default='local')  # local, google, microsoft
    auth_provider_id = db.Column(db.String(255))
    reset_password_token = db.Column(db.String(100))
    reset_password_expires = db.Column(db.DateTime)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    profile_picture = db.Column(db.String(255))
    bio = db.Column(db.Text)

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """Set hashed password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if password matches."""
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        """Return user's full name or username if not set."""
        if self.first_name or self.last_name:
            return f"{self.first_name or ''} {self.last_name or ''}".strip()
        return self.username

    def update_last_login(self):
        """Update last login timestamp."""
        self.last_login = datetime.utcnow()
        db.session.commit()