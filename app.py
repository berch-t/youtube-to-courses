#!/usr/bin/env python3
"""
YouTube Course Builder - Flask Web Application
Unified interface for YouTube transcription and SOTA course generation.
"""
from __future__ import annotations

import json
import os
import uuid
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import urlparse

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename

from pipelines.audio_pipeline import create_audio_pipeline
from pipelines.course_pipeline import create_course_pipeline

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-change-this')

# Configuration
CACHE_DIR = Path('cache')
OUTPUT_DIR = Path('outputs')
UPLOAD_DIR = Path('uploads')

# Create directories
CACHE_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

# Global task storage (in production, use Redis or database)
tasks = {}

class TaskStatus:
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'

def is_valid_youtube_url(url: str) -> bool:
    """Validate if the URL is a valid YouTube URL"""
    try:
        parsed = urlparse(url)
        return (parsed.hostname in ['www.youtube.com', 'youtube.com', 'youtu.be'] and 
                (parsed.path.startswith('/watch') or parsed.hostname == 'youtu.be'))
    except Exception:
        return False

def create_task(task_type: str, **kwargs) -> str:
    """Create a new task and return task ID"""
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        'id': task_id,
        'type': task_type,
        'status': TaskStatus.PENDING,
        'progress': 0,
        'message': 'Task created',
        'created_at': datetime.now().isoformat(),
        'result': None,
        'error': None,
        **kwargs
    }
    return task_id

def update_task(task_id: str, **updates):
    """Update task status and information"""
    if task_id in tasks:
        tasks[task_id].update(updates)
        tasks[task_id]['updated_at'] = datetime.now().isoformat()

def process_youtube_pipeline(task_id: str, url: str, chunk_minutes: int = 10):
    """Process YouTube URL through complete pipeline"""
    try:
        update_task(task_id, status=TaskStatus.PROCESSING, progress=10, 
                   message="Initializing YouTube download...")
        
        # Step 1: Audio pipeline
        audio_pipeline = create_audio_pipeline(
            url=url,
            chunk_min=chunk_minutes,
            outdir=str(CACHE_DIR),
            use_cli=False,
            do_ollama=False
        )
        
        update_task(task_id, progress=20, message="Downloading YouTube audio...")
        
        transcript_md, transcript_txt = audio_pipeline.process()
        
        update_task(task_id, progress=60, message="Transcript completed. Generating SOTA course...")
        
        # Step 2: Course pipeline
        course_output_path = OUTPUT_DIR / f"course_{task_id}.md"
        course_pipeline = create_course_pipeline(
            input_path=str(transcript_md),
            output_path=str(course_output_path)
        )
        
        final_course = course_pipeline.process()
        
        update_task(task_id, 
                   status=TaskStatus.COMPLETED, 
                   progress=100, 
                   message="SOTA Course generated successfully!",
                   result={
                       'transcript_file': str(transcript_md),
                       'course_file': str(final_course),
                       'download_url': f'/download/{final_course.name}'
                   })
        
    except Exception as e:
        update_task(task_id, 
                   status=TaskStatus.FAILED, 
                   progress=0, 
                   message=f"Error: {str(e)}",
                   error=str(e))

def process_local_transcript(task_id: str, transcript_path: str, output_path: str):
    """Process local transcript file to SOTA course"""
    try:
        update_task(task_id, status=TaskStatus.PROCESSING, progress=20,
                   message="Processing local transcript...")
        
        # Validate input file
        transcript_file = Path(transcript_path)
        if not transcript_file.exists():
            raise FileNotFoundError(f"Transcript file not found: {transcript_path}")
        
        # Course pipeline
        course_pipeline = create_course_pipeline(
            input_path=transcript_path,
            output_path=output_path
        )
        
        update_task(task_id, progress=50, message="Generating SOTA course...")
        
        final_course = course_pipeline.process()
        
        update_task(task_id, 
                   status=TaskStatus.COMPLETED, 
                   progress=100, 
                   message="SOTA Course generated successfully!",
                   result={
                       'course_file': str(final_course),
                       'download_url': f'/download/{Path(final_course).name}'
                   })
        
    except Exception as e:
        update_task(task_id, 
                   status=TaskStatus.FAILED, 
                   progress=0, 
                   message=f"Error: {str(e)}",
                   error=str(e))

@app.route('/')
def index():
    """Main page with both YouTube and local file options"""
    return render_template('index.html')

@app.route('/process-youtube', methods=['POST'])
def process_youtube():
    """Handle YouTube URL processing"""
    data = request.get_json()
    
    url = data.get('url', '').strip()
    chunk_minutes = int(data.get('chunk_minutes', 10))
    
    # Validate URL
    if not url:
        return jsonify({'error': 'YouTube URL is required'}), 400
    
    if not is_valid_youtube_url(url):
        return jsonify({'error': 'Invalid YouTube URL'}), 400
    
    # Create task
    task_id = create_task('youtube_pipeline', url=url, chunk_minutes=chunk_minutes)
    
    # Start processing in background
    thread = threading.Thread(
        target=process_youtube_pipeline, 
        args=(task_id, url, chunk_minutes)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'task_id': task_id,
        'message': 'Processing started',
        'status_url': f'/status/{task_id}'
    })

@app.route('/process-local', methods=['POST'])
def process_local():
    """Handle local transcript file processing"""
    # Check if files were uploaded
    if 'transcript_file' not in request.files:
        return jsonify({'error': 'No transcript file uploaded'}), 400
    
    transcript_file = request.files['transcript_file']
    output_filename = request.form.get('output_filename', 'course.md')
    
    if transcript_file.filename == '':
        return jsonify({'error': 'No transcript file selected'}), 400
    
    # Validate file extension
    if not transcript_file.filename.lower().endswith('.md'):
        return jsonify({'error': 'Transcript file must be a Markdown (.md) file'}), 400
    
    # Save uploaded file
    filename = secure_filename(transcript_file.filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved_filename = f"{timestamp}_{filename}"
    transcript_path = UPLOAD_DIR / saved_filename
    transcript_file.save(transcript_path)
    
    # Determine output path
    if not output_filename.endswith('.md'):
        output_filename += '.md'
    output_path = OUTPUT_DIR / f"{timestamp}_{secure_filename(output_filename)}"
    
    # Create task
    task_id = create_task('local_transcript', 
                         transcript_path=str(transcript_path),
                         output_path=str(output_path))
    
    # Start processing in background
    thread = threading.Thread(
        target=process_local_transcript, 
        args=(task_id, str(transcript_path), str(output_path))
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'task_id': task_id,
        'message': 'Processing started',
        'status_url': f'/status/{task_id}'
    })

@app.route('/status/<task_id>')
def task_status(task_id: str):
    """Get task status"""
    if task_id not in tasks:
        return jsonify({'error': 'Task not found'}), 404
    
    task = tasks[task_id]
    return jsonify(task)

@app.route('/download/<filename>')
def download_file(filename: str):
    """Download generated course file"""
    file_path = OUTPUT_DIR / filename
    
    if not file_path.exists():
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=filename,
        mimetype='text/markdown'
    )

@app.route('/tasks')
def list_tasks():
    """List all tasks (for debugging)"""
    return jsonify(list(tasks.values()))

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_tasks': len([t for t in tasks.values() if t['status'] == TaskStatus.PROCESSING])
    })

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Check environment variables
    required_env_vars = ['OPENAI_API_KEY']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables before running the application.")
        exit(1)
    
    print("🚀 Starting YouTube Course Builder...")
    print("📁 Cache directory:", CACHE_DIR.absolute())
    print("📁 Output directory:", OUTPUT_DIR.absolute())
    print("🌐 Access the application at: http://localhost:5000")
    
    # Run Flask app
    app.run(
        debug=False,  # Désactiver debug pour éviter les reloads intempestifs
        host='0.0.0.0', 
        port=5000,
        threaded=True
    )