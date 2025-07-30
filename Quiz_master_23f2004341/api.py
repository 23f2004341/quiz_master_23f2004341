from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required, current_user
from extensions import db, cache, invalidate_cache_pattern, invalidate_user_cache, invalidate_subject_cache, invalidate_chapter_cache, invalidate_quiz_cache, invalidate_question_cache, invalidate_charts_cache, cache_key_with_user, cache_key_with_params, get_cache_stats, delete_cache_pattern
from models import User, Subject, Chapter, Quiz, Question, Score
from datetime import datetime
import os
import csv
import glob
from celery_app import export_all_users_stats_task, export_quiz_history_task, test_email_task, monthly_report_task

api = Blueprint('api', __name__)

# User Management APIs
@api.route('/register', methods=['POST'])
def api_register():
    data = request.get_json()
    # Check if user already exists
    existing_user = User.query.filter_by(email=data.get('email')).first()
    if existing_user:
        return jsonify({'error': 'User already exists'}), 400
    
    # Create new user
    user = User(
        email=data.get('email'),
        full_name=data.get('full_name'),
        role='user'
    )
    user.set_password(data.get('password'))
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully!'}), 201

@api.route('/login', methods=['POST'])
def api_login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()
    if user and user.check_password(data.get('password')):
        from flask_login import login_user
        login_user(user)
        return jsonify({'message': 'Login successful!', 'user': {'id': user.id, 'email': user.email, 'role': user.role}}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@api.route('/logout', methods=['POST'])
@login_required
def api_logout():
    from flask_login import logout_user
    logout_user()
    return jsonify({'message': 'Logout successful!'}), 200

@api.route('/users', methods=['GET'])
@login_required
@cache.cached(timeout=1, key_prefix=lambda: f"users_list_{current_user.role}")
def get_users():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    users = User.query.filter_by(role='user').all()
    user_list = [
        {
            'id': u.id,
            'email': u.email,
            'full_name': u.full_name,
            'role': u.role
        } for u in users
    ]
    return jsonify({'users': user_list}), 200

@api.route('/users/<int:user_id>', methods=['GET'])
@login_required
@cache.cached(timeout=1, key_prefix=lambda: f"user_{request.view_args['user_id']}")
def get_user(user_id):
    if current_user.role != 'admin' and current_user.id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    user = User.query.get_or_404(user_id)
    user_data = {
        'id': user.id,
        'email': user.email,
        'full_name': user.full_name,
        'role': user.role
    }
    return jsonify({'user': user_data}), 200

@api.route('/users/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    if current_user.role != 'admin' and current_user.id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    user.full_name = data.get('full_name', user.full_name)
    user.email = data.get('email', user.email)
    if data.get('password'):
        user.set_password(data.get('password'))
    db.session.commit()
    
    # Invalidate user cache
    invalidate_user_cache(user_id)
    cache.delete(f"user_{user_id}")
    # Invalidate users list cache for all roles
    cache.delete(f"users_list_admin")
    cache.delete(f"users_list_user")
    
    return jsonify({'message': 'User updated successfully!'}), 200

@api.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    # Invalidate user cache
    invalidate_user_cache(user_id)
    cache.delete(f"user_{user_id}")
    # Invalidate users list cache for all roles
    cache.delete(f"users_list_admin")
    cache.delete(f"users_list_user")
    
    return jsonify({'message': 'User deleted successfully!'}), 200

# Subject Management APIs
@api.route('/subjects', methods=['GET'])
@login_required
@cache.cached(timeout=1)  
def get_subjects():
    subjects = Subject.query.all()
    subject_list = [
        {
            'id': s.id,
            'name': s.name,
            'description': s.description
        } for s in subjects
    ]
    return jsonify({'subjects': subject_list}), 200

@api.route('/subjects/<int:subject_id>', methods=['GET'])
@login_required
@cache.cached(timeout=1, key_prefix=lambda: f"subject_{request.view_args['subject_id']}")
def get_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    subject_data = {
        'id': subject.id,
        'name': subject.name,
        'description': subject.description
    }
    return jsonify({'subject': subject_data}), 200

@api.route('/subjects', methods=['POST'])
@login_required
def create_subject():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    subject = Subject(
        name=data.get('name'),
        description=data.get('description')
    )
    db.session.add(subject)
    db.session.commit()
    
    # Invalidate subject cache
    invalidate_subject_cache()
    
    return jsonify({'message': 'Subject created successfully!', 'id': subject.id}), 201

@api.route('/subjects/<int:subject_id>', methods=['PUT'])
@login_required
def update_subject(subject_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    subject = Subject.query.get_or_404(subject_id)
    data = request.get_json()
    subject.name = data.get('name', subject.name)
    subject.description = data.get('description', subject.description)
    db.session.commit()
    
    # Invalidate subject cache
    invalidate_subject_cache()
    cache.delete(f"subject_{subject_id}")
    # Invalidate subjects list cache
    cache.delete("quiz_masterview//api/subjects")
    
    return jsonify({'message': 'Subject updated successfully!'}), 200

@api.route('/subjects/<int:subject_id>', methods=['DELETE'])
@login_required
def delete_subject(subject_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    
    # Invalidate subject cache
    invalidate_subject_cache()
    cache.delete(f"subject_{subject_id}")
    # Invalidate subjects list cache
    cache.delete("quiz_masterview//api/subjects")
    
    return jsonify({'message': 'Subject deleted successfully!'}), 200

# Chapter Management APIs
@api.route('/chapters', methods=['GET'])
@login_required
@cache.cached(timeout=1)  
def get_chapters():
    chapters = Chapter.query.all()
    chapter_list = [
        {
            'id': c.id,
            'name': c.name,
            'description': c.description,
            'subject_id': c.subject_id
        } for c in chapters
    ]
    return jsonify({'chapters': chapter_list}), 200

@api.route('/chapters/<int:chapter_id>', methods=['GET'])
@login_required
@cache.cached(timeout=1, key_prefix=lambda: f"chapter_{request.view_args['chapter_id']}")
def get_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    chapter_data = {
        'id': chapter.id,
        'name': chapter.name,
        'description': chapter.description,
        'subject_id': chapter.subject_id
    }
    return jsonify({'chapter': chapter_data}), 200

@api.route('/chapters', methods=['POST'])
@login_required
def create_chapter():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    chapter = Chapter(
        name=data.get('name'),
        description=data.get('description'),
        subject_id=data.get('subject_id')
    )
    db.session.add(chapter)
    db.session.commit()
    
    # Invalidate chapter cache
    invalidate_chapter_cache()
    
    return jsonify({'message': 'Chapter created successfully!', 'id': chapter.id}), 201

@api.route('/chapters/<int:chapter_id>', methods=['PUT'])
@login_required
def update_chapter(chapter_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    chapter = Chapter.query.get_or_404(chapter_id)
    data = request.get_json()
    chapter.name = data.get('name', chapter.name)
    chapter.description = data.get('description', chapter.description)
    chapter.subject_id = data.get('subject_id', chapter.subject_id)
    db.session.commit()
    
    # Invalidate chapter cache
    invalidate_chapter_cache()
    cache.delete(f"chapter_{chapter_id}")
    
    return jsonify({'message': 'Chapter updated successfully!'}), 200

@api.route('/chapters/<int:chapter_id>', methods=['DELETE'])
@login_required
def delete_chapter(chapter_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    
    # Invalidate chapter cache
    invalidate_chapter_cache()
    cache.delete(f"chapter_{chapter_id}")
    
    return jsonify({'message': 'Chapter deleted successfully!'}), 200

# Quiz Management APIs
@api.route('/quizzes', methods=['GET'])
@login_required
@cache.cached(timeout=1)  
def get_quizzes():
    quizzes = Quiz.query.all()
    quiz_list = [
        {
            'id': q.id,
            'chapter_id': q.chapter_id,
            'date_of_quiz': q.date_of_quiz.strftime('%Y-%m-%d'),
            'duration': q.duration,
            'remarks': q.remarks
        } for q in quizzes
    ]
    return jsonify({'quizzes': quiz_list}), 200

@api.route('/quizzes/<int:quiz_id>', methods=['GET'])
@login_required
@cache.cached(timeout=1, key_prefix=lambda: f"quiz_{request.view_args['quiz_id']}")
def get_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    quiz_data = {
        'id': quiz.id,
        'chapter_id': quiz.chapter_id,
        'date_of_quiz': quiz.date_of_quiz.strftime('%Y-%m-%d'),
        'duration': quiz.duration,
        'remarks': quiz.remarks
    }
    return jsonify({'quiz': quiz_data}), 200

@api.route('/quizzes', methods=['POST'])
@login_required
def create_quiz():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    # Validate required fields
    if not data.get('chapter_id') or not data.get('date_of_quiz') or not data.get('duration'):
        return jsonify({'error': 'Missing required fields: chapter_id, date_of_quiz, duration'}), 400
    
    quiz = Quiz(
        chapter_id=data.get('chapter_id'),
        date_of_quiz=datetime.strptime(data.get('date_of_quiz'), '%Y-%m-%d').date(),
        duration=data.get('duration'),
        remarks=data.get('remarks', '')
    )
    db.session.add(quiz)
    db.session.commit()
    
    # Invalidate quiz cache
    invalidate_quiz_cache()
    
    return jsonify({'message': 'Quiz created successfully!', 'id': quiz.id}), 201

@api.route('/quizzes/<int:quiz_id>', methods=['PUT'])
@login_required
def update_quiz(quiz_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    quiz = Quiz.query.get_or_404(quiz_id)
    data = request.get_json()
    quiz.chapter_id = data.get('chapter_id', quiz.chapter_id)
    if data.get('date_of_quiz'):
        quiz.date_of_quiz = datetime.strptime(data.get('date_of_quiz'), '%Y-%m-%d').date()
    quiz.duration = data.get('duration', quiz.duration)
    quiz.remarks = data.get('remarks', quiz.remarks)
    db.session.commit()
    
    # Invalidate quiz cache
    invalidate_quiz_cache()
    cache.delete(f"quiz_{quiz_id}")
    
    return jsonify({'message': 'Quiz updated successfully!'}), 200

@api.route('/quizzes/<int:quiz_id>', methods=['DELETE'])
@login_required
def delete_quiz(quiz_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    
    # Invalidate quiz cache
    invalidate_quiz_cache()
    cache.delete(f"quiz_{quiz_id}")
    
    return jsonify({'message': 'Quiz deleted successfully!'}), 200

# Question Management APIs
@api.route('/questions', methods=['GET'])
@login_required
@cache.cached(timeout=1)  
def get_questions():
    questions = Question.query.all()
    question_list = [
        {
            'id': q.id,
            'quiz_id': q.quiz_id,
            'question_statement': q.question_statement,
            'option1': q.option1,
            'option2': q.option2,
            'option3': q.option3,
            'option4': q.option4,
            'correct_option': q.correct_option
        } for q in questions
    ]
    return jsonify({'questions': question_list}), 200

@api.route('/questions/<int:question_id>', methods=['GET'])
@login_required
@cache.cached(timeout=1, key_prefix=lambda: f"question_{request.view_args['question_id']}")
def get_question(question_id):
    question = Question.query.get_or_404(question_id)
    question_data = {
        'id': question.id,
        'quiz_id': question.quiz_id,
        'question_statement': question.question_statement,
        'option1': question.option1,
        'option2': question.option2,
        'option3': question.option3,
        'option4': question.option4,
        'correct_option': question.correct_option
    }
    return jsonify({'question': question_data}), 200

@api.route('/questions', methods=['POST'])
@login_required
def create_question():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    required_fields = ['quiz_id', 'question_statement', 'option1', 'option2', 'option3', 'option4', 'correct_option']
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400
    
    question = Question(
        quiz_id=data.get('quiz_id'),
        question_statement=data.get('question_statement'),
        option1=data.get('option1'),
        option2=data.get('option2'),
        option3=data.get('option3'),
        option4=data.get('option4'),
        correct_option=data.get('correct_option')
    )
    db.session.add(question)
    db.session.commit()
    
    # Invalidate question cache
    invalidate_question_cache()
    
    return jsonify({'message': 'Question created successfully!', 'id': question.id}), 201

@api.route('/questions/<int:question_id>', methods=['PUT'])
@login_required
def update_question(question_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    question = Question.query.get_or_404(question_id)
    data = request.get_json()
    question.quiz_id = data.get('quiz_id', question.quiz_id)
    question.question_statement = data.get('question_statement', question.question_statement)
    question.option1 = data.get('option1', question.option1)
    question.option2 = data.get('option2', question.option2)
    question.option3 = data.get('option3', question.option3)
    question.option4 = data.get('option4', question.option4)
    question.correct_option = data.get('correct_option', question.correct_option)
    db.session.commit()
    
    # Invalidate question cache
    invalidate_question_cache()
    cache.delete(f"question_{question_id}")
    
    return jsonify({'message': 'Question updated successfully!'}), 200

@api.route('/questions/<int:question_id>', methods=['DELETE'])
@login_required
def delete_question(question_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    
    # Invalidate question cache
    invalidate_question_cache()
    cache.delete(f"question_{question_id}")
    
    return jsonify({'message': 'Question deleted successfully!'}), 200

# Score Management APIs
@api.route('/scores', methods=['GET'])
@login_required
@cache.cached(timeout=1, key_prefix=lambda: f"scores_list_{current_user.role}")
def get_scores():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    scores = Score.query.all()
    score_list = [
        {
            'id': s.id,
            'user_id': s.user_id,
            'quiz_id': s.quiz_id,
            'total_score': s.total_score,
            'timestamp': s.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        } for s in scores
    ]
    return jsonify({'scores': score_list}), 200

@api.route('/scores/<int:score_id>', methods=['GET'])
@login_required
@cache.cached(timeout=1, key_prefix=lambda: f"score_{request.view_args['score_id']}")
def get_score(score_id):
    score = Score.query.get_or_404(score_id)
    if current_user.role != 'admin' and current_user.id != score.user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    score_data = {
        'id': score.id,
        'user_id': score.user_id,
        'quiz_id': score.quiz_id,
        'total_score': score.total_score,
        'timestamp': score.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    }
    return jsonify({'score': score_data}), 200

# Quiz Attempt API
@api.route('/quizzes/<int:quiz_id>/attempt', methods=['POST'])
@login_required
def attempt_quiz(quiz_id):
    data = request.get_json()
    answers = data.get('answers', {})
    
    # Get quiz questions
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    total_score = 0
    
    for question in questions:
        user_answer = answers.get(str(question.id))
        if user_answer is not None and int(user_answer) == question.correct_option:
            total_score += 1
    
    # Save score with timestamp
    score = Score(
        user_id=current_user.id,
        quiz_id=quiz_id,
        total_score=total_score,
        timestamp=datetime.now()
    )
    db.session.add(score)
    db.session.commit()
    
    # Invalidate user-specific cache
    invalidate_user_cache(current_user.id)
    invalidate_charts_cache()
    
    return jsonify({
        'message': 'Quiz completed successfully!',
        'total_score': total_score,
        'total_questions': len(questions)
    }), 200

# User-specific APIs
@api.route('/user/quiz_history', methods=['GET'])
@login_required
@cache.cached(timeout=1, key_prefix=lambda: f"quiz_history_{current_user.id}")
def quiz_history():
    scores = Score.query.filter_by(user_id=current_user.id).all()
    history = [
        {
            'id': s.id,
            'quiz_id': s.quiz_id,
            'total_score': s.total_score,
            'timestamp': s.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        } for s in scores
    ]
    return jsonify({'history': history}), 200

# CSV Export APIs
@api.route('/user/export_quiz_history', methods=['POST'])
@login_required
def export_quiz_history():
    user_id = current_user.id
    # Only allow user or admin to export their own history
    if current_user.role != 'admin' and int(request.json.get('user_id', user_id)) != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    # Enqueue Celery task
    task = export_quiz_history_task.delay(user_id)
    return jsonify({'message': 'Export started', 'task_id': str(task.id)}), 202

@api.route('/user/download_quiz_history/<task_id>', methods=['GET'])
@login_required
def download_quiz_history(task_id):
    # Get Celery task result
    from celery_worker import celery
    result = celery.AsyncResult(task_id)
    if not result.ready():
        return jsonify({'status': 'pending'}), 202
    filepath = result.result
    # Only proceed if filepath is a string and exists
    if not isinstance(filepath, str) or not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    return send_file(filepath, as_attachment=True)

@api.route('/user/analytics', methods=['GET'])
@login_required
@cache.cached(timeout=1, key_prefix=lambda: f"user_analytics_{current_user.id}")
def user_analytics():
    """Get user-specific analytics and summary data"""
    user_id = current_user.id
    
    # Get user's quiz history
    scores = Score.query.filter_by(user_id=user_id).all()
    
    if not scores:
        return jsonify({
            'total_quizzes': 0,
            'average_score': 0,
            'best_score': 0,
            'total_score': 0,
            'recent_activity': [],
            'performance_by_subject': {},
            'performance_by_chapter': {},
            'score_trend': []
        }), 200
    
    # Calculate basic statistics
    total_quizzes = len(scores)
    total_score = sum(s.total_score for s in scores)
    average_score = total_score / total_quizzes
    best_score = max(s.total_score for s in scores)
    
    # Recent activity (last 5 attempts)
    recent_scores = sorted(scores, key=lambda x: x.timestamp, reverse=True)[:5]
    recent_activity = []
    for score in recent_scores:
        quiz = Quiz.query.get(score.quiz_id)
        chapter = Chapter.query.get(quiz.chapter_id) if quiz else None
        subject = Subject.query.get(chapter.subject_id) if chapter else None
        recent_activity.append({
            'quiz_id': score.quiz_id,
            'score': score.total_score,
            'date': score.timestamp.strftime('%Y-%m-%d'),
            'chapter': chapter.name if chapter else 'Unknown',
            'subject': subject.name if subject else 'Unknown'
        })
    
    # Performance by subject
    performance_by_subject = {}
    for score in scores:
        quiz = Quiz.query.get(score.quiz_id)
        if quiz:
            chapter = Chapter.query.get(quiz.chapter_id)
            if chapter:
                subject = Subject.query.get(chapter.subject_id)
                if subject:
                    subject_name = subject.name
                    if subject_name not in performance_by_subject:
                        performance_by_subject[subject_name] = []
                    performance_by_subject[subject_name].append(score.total_score)
    
    # Calculate average by subject
    for subject in performance_by_subject:
        performance_by_subject[subject] = sum(performance_by_subject[subject]) / len(performance_by_subject[subject])
    
    # Performance by chapter
    performance_by_chapter = {}
    for score in scores:
        quiz = Quiz.query.get(score.quiz_id)
        if quiz:
            chapter = Chapter.query.get(quiz.chapter_id)
            if chapter:
                chapter_name = chapter.name
                if chapter_name not in performance_by_chapter:
                    performance_by_chapter[chapter_name] = []
                performance_by_chapter[chapter_name].append(score.total_score)
    
    # Calculate average by chapter
    for chapter in performance_by_chapter:
        performance_by_chapter[chapter] = sum(performance_by_chapter[chapter]) / len(performance_by_chapter[chapter])
    
    # Score trend (last 10 attempts)
    trend_scores = sorted(scores, key=lambda x: x.timestamp)[-10:]
    score_trend = []
    for i, score in enumerate(trend_scores):
        score_trend.append({
            'attempt': i + 1,
            'score': score.total_score,
            'date': score.timestamp.strftime('%Y-%m-%d')
        })
    
    return jsonify({
        'total_quizzes': total_quizzes,
        'average_score': round(average_score, 2),
        'best_score': best_score,
        'total_score': total_score,
        'recent_activity': recent_activity,
        'performance_by_subject': performance_by_subject,
        'performance_by_chapter': performance_by_chapter,
        'score_trend': score_trend
    }), 200

@api.route('/user/export_quiz_history_direct', methods=['GET'])
@login_required
def export_quiz_history_direct():
    user_id = current_user.id
    # Only allow user or admin to export their own history
    if current_user.role != 'admin' and int(request.args.get('user_id', user_id)) != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Direct CSV generation without Celery
    user = User.query.get(user_id)
    scores = Score.query.filter_by(user_id=user_id).all()
    
    filename = f"quiz_history_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    export_dir = os.path.join(os.getcwd(), 'exports')
    os.makedirs(export_dir, exist_ok=True)
    filepath = os.path.join(export_dir, filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Enhanced CSV headers with all required fields
        writer.writerow(['Quiz ID', 'Chapter ID', 'Chapter Name', 'Subject Name', 'Date of Quiz', 'Quiz Duration', 'Quiz Remarks', 'Score', 'Attempt Date', 'User Name'])
        
        for score in scores:
            # Get quiz details
            quiz = Quiz.query.get(score.quiz_id)
            chapter = Chapter.query.get(quiz.chapter_id) if quiz else None
            subject = Subject.query.get(chapter.subject_id) if chapter else None
            
            writer.writerow([
                score.quiz_id,
                quiz.chapter_id if quiz else 'N/A',
                chapter.name if chapter else 'N/A',
                subject.name if subject else 'N/A',
                quiz.date_of_quiz.strftime('%Y-%m-%d') if quiz else 'N/A',
                quiz.duration if quiz else 'N/A',
                quiz.remarks if quiz else 'N/A',
                score.total_score,
                score.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                user.full_name
            ])
    
    return send_file(filepath, as_attachment=True, download_name=filename)

# Admin APIs
@api.route('/admin/charts', methods=['GET'])
@login_required
@cache.cached(timeout=1) 
def admin_charts():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    from models import Quiz, Score
    quizzes = Quiz.query.all()
    labels = []
    avg_scores = []
    for quiz in quizzes:
        scores = Score.query.filter_by(quiz_id=quiz.id).all()
        if scores:
            avg = sum(s.total_score for s in scores) / len(scores)
            labels.append(f"Quiz {quiz.id}")
            avg_scores.append(round(avg, 2))
    chart_data = {
        'labels': labels,
        'scores': avg_scores
    }
    return jsonify({'chart_data': chart_data}), 200

@api.route('/admin/search', methods=['POST'])
@login_required
@cache.cached(timeout=1, key_prefix=lambda: f"search_{hash(str(request.get_json()))}")
def admin_search():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    from models import User, Subject, Chapter, Quiz, Question
    data = request.get_json()
    term = data.get('term', '')
    results = {
        "users": [],
        "subjects": [],
        "chapters": [],
        "quizzes": [],
        "questions": []
    }
    results['users'] = [
        {
            'id': u.id,
            'email': u.email,
            'full_name': u.full_name
        } for u in User.query.filter(
            User.full_name.ilike(f"%{term}%") | User.email.ilike(f"%{term}%")
        ).all()
    ]
    results['subjects'] = [
        {
            'id': s.id,
            'name': s.name,
            'description': s.description
        } for s in Subject.query.filter(Subject.name.ilike(f"%{term}%")).all()
    ]
    results['chapters'] = [
        {
            'id': c.id,
            'name': c.name,
            'description': c.description
        } for c in Chapter.query.filter(Chapter.name.ilike(f"%{term}%")).all()
    ]
    results['quizzes'] = [
        {
            'id': q.id,
            'chapter_id': q.chapter_id,
            'date_of_quiz': q.date_of_quiz.strftime('%Y-%m-%d'),
            'duration': q.duration
        } for q in Quiz.query.filter(Quiz.remarks.ilike(f"%{term}%")).all()
    ]
    results['questions'] = [
        {
            'id': q.id,
            'quiz_id': q.quiz_id,
            'question_text': q.question_statement
        } for q in Question.query.filter(Question.question_statement.ilike(f"%{term}%")).all()
    ]
    # Invalidate search cache
    delete_cache_pattern("quiz_mastersearch_*")
    return jsonify({'results': results}), 200

@api.route('/admin/analytics', methods=['GET'])
@login_required
@cache.cached(timeout=1)  
def admin_analytics():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    from models import User, Quiz, Score, Subject, Chapter
    total_users = User.query.filter_by(role='user').count()
    total_quizzes = Quiz.query.count()
    total_scores = Score.query.count()
    total_subjects = Subject.query.count()
    total_chapters = Chapter.query.count()
    
    # Calculate average score
    avg_score = 0
    if total_scores > 0:
        avg_score = db.session.query(db.func.avg(Score.total_score)).scalar()
    
    analytics = {
        'total_users': total_users,
        'total_quizzes': total_quizzes,
        'total_scores': total_scores,
        'total_subjects': total_subjects,
        'total_chapters': total_chapters,
        'average_score': round(avg_score, 2) if avg_score else 0
    }
    # Attempts over time (last 7 days)
    from datetime import datetime, timedelta
    today = datetime.now().date()
    attempts_over_time = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = Score.query.filter(db.func.date(Score.timestamp) == day).count()
        attempts_over_time.append({'date': day.strftime('%Y-%m-%d'), 'count': count})

    # Top scoring users (by total score)
    user_scores = db.session.query(User.full_name, db.func.sum(Score.total_score).label('score')) \
        .join(Score, User.id == Score.user_id) \
        .group_by(User.id) \
        .order_by(db.func.sum(Score.total_score).desc()) \
        .limit(5).all()
    top_users = [{'name': name, 'score': score} for name, score in user_scores]

    return jsonify({
        'analytics': analytics,
        'attempts_over_time': attempts_over_time,
        'top_users': top_users
    }), 200

# Admin Export APIs
@api.route('/admin/export_all_users_stats', methods=['POST'])
@login_required
def admin_export_all_users_stats():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    task = export_all_users_stats_task.delay()
    return jsonify({'message': 'Export started', 'task_id': str(task.id)}), 202

@api.route('/admin/download_all_users_stats/latest', methods=['GET'])
@login_required
def download_latest_all_users_stats():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    export_dir = os.path.join(os.getcwd(), 'exports')
    if not os.path.exists(export_dir):
        return jsonify({'error': 'No exports found'}), 404
    files = glob.glob(os.path.join(export_dir, 'all_users_stats_*.csv'))
    if not files:
        return jsonify({'error': 'No export files found'}), 404
    latest_file = max(files, key=os.path.getctime)
    return send_file(latest_file, as_attachment=True)

@api.route('/admin/download_all_users_stats/<filename>', methods=['GET'])
@login_required
def download_all_users_stats(filename):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    filepath = os.path.join(os.getcwd(), 'exports', filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    return send_file(filepath, as_attachment=True)

# Admin Test APIs
@api.route('/admin/test_email', methods=['POST'])
@login_required
def test_email():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    task = test_email_task.delay()
    return jsonify({'message': 'Test email sent', 'task_id': str(task.id)}), 202

@api.route('/admin/test_monthly_report', methods=['POST'])
@login_required
def test_monthly_report():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    task = monthly_report_task.delay()
    return jsonify({'message': 'Monthly report generation started', 'task_id': str(task.id)}), 202

# Cache Management API
@api.route('/admin/cache/stats', methods=['GET'])
@login_required
def cache_stats():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    from extensions import get_cache_stats, get_cache_hit_rate
    stats = get_cache_stats()
    hit_rate = get_cache_hit_rate()
    stats['hit_rate'] = hit_rate
    return jsonify({'cache_stats': stats}), 200

@api.route('/admin/cache/clear', methods=['POST'])
@login_required
def clear_cache():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    try:
        cache.clear()
        return jsonify({'message': 'Cache cleared successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to clear cache: {str(e)}'}), 500

@api.route('/admin/cache/warm', methods=['POST'])
@login_required
def warm_cache_endpoint():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    try:
        from extensions import warm_cache
        success = warm_cache()
        if success:
            return jsonify({'message': 'Cache warmed successfully'}), 200
        else:
            return jsonify({'error': 'Failed to warm cache'}), 500
    except Exception as e:
        return jsonify({'error': f'Cache warming error: {str(e)}'}), 500

@api.route('/admin/cache/optimize', methods=['POST'])
@login_required
def optimize_cache():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    try:
        from extensions import optimize_cache_performance
        success = optimize_cache_performance()
        if success:
            return jsonify({'message': 'Cache optimized successfully'}), 200
        else:
            return jsonify({'error': 'Failed to optimize cache'}), 500
    except Exception as e:
        return jsonify({'error': f'Cache optimization error: {str(e)}'}), 500

