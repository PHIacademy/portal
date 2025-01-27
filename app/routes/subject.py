from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, abort, session
from werkzeug.utils import secure_filename
from app.models import Subject, Article, db
import os
from datetime import datetime
from app.utils.converter import convert_doc_to_html
from app.utils.blob import upload_to_blob, delete_from_blob

bp = Blueprint('subject', __name__, url_prefix='/subject')

@bp.route('/<int:id>')
def view(id):
    """View a specific subject and its articles"""
    subject = Subject.query.get_or_404(id)
    articles = Article.query.filter_by(subject_id=id)\
        .order_by(Article.uploaded_at.desc(), Article.title)\
        .all()
    return render_template('subject/view.html', subject=subject, articles=articles)

@bp.route('/<int:id>/upload', methods=['GET', 'POST'])
def upload_article(id):
    """Handle article upload for a subject"""
    # Check if user has required role
    if session.get('user_role') not in ['admin', 'teacher']:
        flash('You do not have permission to upload articles.', 'error')
        return redirect(url_for('subject.view', id=id))
        
    subject = Subject.query.get_or_404(id)
    
    if request.method == 'POST':
        if 'article' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
            
        file = request.files['article']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
            
        if not file.filename.endswith('.doc') and not file.filename.endswith('.docx'):
            flash('Only .doc and .docx files are allowed', 'error')
            return redirect(request.url)
            
        try:
            # Process file and convert to HTML
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = secure_filename(file.filename)
            html_content = convert_doc_to_html(file)
            html_filename = f"{timestamp}_{os.path.splitext(filename)[0]}.html"
            
            # Upload HTML content to Vercel Blob
            blob_url = upload_to_blob(html_content, html_filename)
            
            # Create article record
            article_data = {
                'subject_id': subject.id,
                'title': request.form['title'],
                'level': request.form['level'],
                'html_content': html_content,
                'blob_url': blob_url
            }

            # Add genre if it's a Chinese subject
            if subject.is_chinese_subject:
                if 'genre' not in request.form:
                    flash('Genre is required for Chinese articles', 'error')
                    return redirect(request.url)
                article_data['genre'] = request.form['genre']

            article = Article(**article_data)
            
            db.session.add(article)
            db.session.commit()
            
            flash('Article uploaded successfully', 'success')
            return redirect(url_for('subject.view', id=subject.id))
            
        except Exception as e:
            flash(f'Error uploading article: {str(e)}', 'error')
            return redirect(request.url)
    
    return render_template('subject/upload.html', subject=subject)

@bp.route('/article/<int:id>/delete', methods=['POST'])
def delete_article(id):
    """Delete an article and its associated files"""
    # Check if user has required role
    if session.get('user_role') not in ['admin', 'teacher']:
        flash('You do not have permission to delete articles.', 'error')
        return redirect(url_for('subject.view', id=id))
        
    article = Article.query.get_or_404(id)
    subject_id = article.subject_id
    
    try:
        # Delete from Vercel Blob if blob_url exists
        if article.blob_url:
            delete_from_blob(article.blob_url)
        
        # Delete from database
        db.session.delete(article)
        db.session.commit()
        flash('Article deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting article: {str(e)}', 'error')
    
    return redirect(url_for('subject.view', id=subject_id))
