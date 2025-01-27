from flask import Blueprint, render_template, abort, send_file, current_app, request, redirect, url_for, flash, jsonify
from app import db
import os
import logging
import asyncio
import edge_tts
import tempfile
import datetime
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
from app.models import Article

bp = Blueprint('article', __name__, url_prefix='/article')

@bp.route('/<int:id>')
def view(id):
    """View a specific article"""
    article = Article.query.get_or_404(id)
    return render_template('article/view.html', article=article)

@bp.route('/download/<int:id>')
def download_original(id):
    """Download the original document file"""
    try:
        logger.debug(f"Accessing download_original route for article ID: {id}")
        article = Article.query.get_or_404(id)
        
        if not article.html_path:
            logger.error("No HTML path available for article")
            abort(404, description="No file available for download")
            
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_path, 'uploads', article.html_path)
        logger.debug(f"Attempting to send file: {file_path}")
        
        if not os.path.exists(file_path):
            logger.error(f"File not found at path: {file_path}")
            abort(404, description="File not found")
            
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        logger.error(f"Error in download_original: {e}", exc_info=True)
        abort(500, description=f"Error downloading file: {str(e)}")

@bp.route('/<int:id>/update-level', methods=['POST'])
def update_level(id):
    """Update the level of an article"""
    try:
        article = Article.query.get_or_404(id)
        new_level = request.form.get('level')
        
        if new_level not in ['P1-P2', 'P3-P4', 'P5-P6', 'F1-F3', 'F4-F6']:
            flash('Invalid level selected', 'error')
            return redirect(url_for('article.view', id=id))
            
        article.level = new_level
        db.session.commit()
        flash('Article level updated successfully', 'success')
        
    except Exception as e:
        flash(f'Error updating article level: {str(e)}', 'error')
        
    return redirect(url_for('article.view', id=id))

@bp.route('/<int:id>/update-genre', methods=['POST'])
def update_genre(id):
    """Update the genre of an article"""
    try:
        article = Article.query.get_or_404(id)
        new_genre = request.form.get('genre')
        
        if not article.subject.is_chinese_subject:
            flash('Genre can only be updated for Chinese subjects', 'error')
            return redirect(url_for('article.view', id=id))
            
        valid_genres = ['記敘文', '描寫文', '說明文', '議論文', '抒情文', '書信', '日記', '讀後感', '詩詞', '應用文']
        if new_genre not in valid_genres:
            flash('Invalid genre selected', 'error')
            return redirect(url_for('article.view', id=id))
            
        article.genre = new_genre
        db.session.commit()
        flash('Article genre updated successfully', 'success')
        
    except Exception as e:
        flash(f'Error updating article genre: {str(e)}', 'error')
        
    return redirect(url_for('article.view', id=id))

@bp.route('/<int:id>/speak', methods=['POST'])
async def speak(id):
    """Generate TTS audio for the article content in Cantonese"""
    try:
        article = Article.query.get_or_404(id)
        
        # Extract text from HTML content
        if article.html_content:
            soup = BeautifulSoup(article.html_content, 'html.parser')
            text = f"{article.title}。{soup.get_text()}"
        else:
            text = article.title
            
        # Create unique filename using timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"article_{id}_{timestamp}.mp3"
        
        # Save in static/audio directory
        output_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'static', 'audio', filename)
            
        # Use Hong Kong Cantonese voice
        communicate = edge_tts.Communicate(text, 'zh-HK-HiuGaaiNeural')
        await communicate.save(output_file)
        
        # Return URL to the audio file
        audio_url = url_for('static', filename=f'audio/{filename}')
        return jsonify({'url': audio_url})
        
    except Exception as e:
        logger.error(f"Error in TTS generation: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500