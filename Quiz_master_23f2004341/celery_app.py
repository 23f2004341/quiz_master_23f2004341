from celery import Celery
import os
import csv
from datetime import datetime, timedelta
from extensions import db, send_email
from models import User, Quiz, Score, Subject, Chapter
import requests

# Configure Celery to use Redis as the broker and result backend
celery = Celery('tasks', 
                broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
                backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'))

celery.conf.update(
    worker_concurrency=1,  # Use single worker process
    worker_pool='solo',    # Use solo pool instead of prefork
    task_always_eager=False,
    task_eager_propagates=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=True
)

def get_flask_app():
    from app import create_app
    app = create_app()
    return app

@celery.task
def test_task(x, y):
    print(f"Running test_task with {x} + {y}")
    return x + y

@celery.task(name='celery_worker.export_quiz_history_task')
def export_quiz_history_task(user_id):
    app = get_flask_app()
    with app.app_context():
        user = User.query.get(user_id)
        scores = Score.query.filter_by(user_id=user_id).all()
        filename = f"quiz_history_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        export_dir = os.path.join(os.getcwd(), 'exports')
        os.makedirs(export_dir, exist_ok=True)
        filepath = os.path.join(export_dir, filename)
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Quiz ID', 'Chapter ID', 'Chapter Name', 'Subject Name', 'Date of Quiz', 'Quiz Duration', 'Quiz Remarks', 'Score', 'Attempt Date', 'User Name'])
            for score in scores:
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
        send_email(
            to=user.email,
            subject="Quiz Master: Quiz History Export Complete",
            body=f"Hi {user.full_name},\n\nYour quiz history export has been completed successfully!\n\nExport Details:\n- File: {filename}\n- Records: {len(scores)} quiz attempts\n- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nYou can download the file from your dashboard.\n\nBest regards,\nQuiz Master Team"
        )
        print(f"Quiz history export completed for user {user_id}: {filename}")
        return filepath

@celery.task(name='celery_worker.export_all_users_stats_task')
def export_all_users_stats_task():
    app = get_flask_app()
    with app.app_context():
        users = User.query.filter(User.role == 'user').all()
        filename = f"all_users_stats_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        export_dir = os.path.join(os.getcwd(), 'exports')
        os.makedirs(export_dir, exist_ok=True)
        filepath = os.path.join(export_dir, filename)
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['User ID', 'Email', 'Quizzes Taken', 'Average Score'])
            for user in users:
                scores = Score.query.filter_by(user_id=user.id).all()
                quizzes_taken = len(scores)
                avg_score = sum(s.total_score for s in scores) / quizzes_taken if quizzes_taken else 0
                writer.writerow([user.id, user.email, quizzes_taken, round(avg_score, 2)])
        return filepath

def get_inactive_users(since_days=1):
    app = get_flask_app()
    with app.app_context():
        cutoff = datetime.now() - timedelta(days=since_days)
        users = User.query.filter(User.role == 'user').all()
        inactive = []
        for user in users:
            last_score = Score.query.filter_by(user_id=user.id).order_by(Score.timestamp.desc()).first()
            if not last_score or last_score.timestamp < cutoff:
                inactive.append(user)
        return inactive

def get_new_quiz_users():
    app = get_flask_app()
    with app.app_context():
        yesterday = datetime.now() - timedelta(days=1)
        recent_quizzes = Quiz.query.filter(Quiz.date_of_quiz >= yesterday.date()).all()
        if not recent_quizzes:
            return []
        users = User.query.filter(User.role == 'user').all()
        unattempted = []
        for user in users:
            for quiz in recent_quizzes:
                attempted = Score.query.filter_by(user_id=user.id, quiz_id=quiz.id).first()
                if not attempted:
                    unattempted.append((user, quiz))
        return unattempted

def send_google_chat_message(webhook_url, message):
    try:
        payload = {"text": message}
        response = requests.post(webhook_url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Google Chat error: {e}")
        return False

def send_sms_message(phone_number, message):
    try:
        print(f"SMS would be sent to {phone_number}: {message}")
        return True
    except Exception as e:
        print(f"SMS error: {e}")
        return False

@celery.task(name='celery_worker.daily_reminder_task')
def daily_reminder_task():
    app = get_flask_app()
    with app.app_context():
        reminder_time = os.getenv('DAILY_REMINDER_TIME', '18:00')
        use_email = os.getenv('REMINDER_USE_EMAIL', 'true').lower() == 'true'
        use_google_chat = os.getenv('REMINDER_USE_GOOGLE_CHAT', 'false').lower() == 'true'
        use_sms = os.getenv('REMINDER_USE_SMS', 'false').lower() == 'true'
        google_chat_webhook = os.getenv('GOOGLE_CHAT_WEBHOOK_URL', '')
        inactive_users = get_inactive_users()
        new_quiz_users = get_new_quiz_users()
        notified = set()
        total_notifications = 0
        for user in inactive_users:
            if user.email in notified:
                continue
            message = f"Hi {user.full_name},\n\nYou haven't visited Quiz Master in the last day. Don't forget to attempt the latest quizzes!\n\nBest,\nQuiz Master Team"
            if use_email:
                send_email(
                    to=user.email,
                    subject="Quiz Master: Daily Reminder",
                    body=message
                )
                total_notifications += 1
            if use_google_chat and google_chat_webhook:
                send_google_chat_message(google_chat_webhook, message)
                total_notifications += 1
            if use_sms:
                pass
            notified.add(user.email)
        for user, quiz in new_quiz_users:
            if user.email in notified:
                continue
            message = f"Hi {user.full_name},\n\nA new quiz has been created: Quiz {quiz.id} (Date: {quiz.date_of_quiz}). Don't miss out - attempt it now!\n\nBest,\nQuiz Master Team"
            if use_email:
                send_email(
                    to=user.email,
                    subject="Quiz Master: New Quiz Available",
                    body=message
                )
                total_notifications += 1
            if use_google_chat and google_chat_webhook:
                send_google_chat_message(google_chat_webhook, message)
                total_notifications += 1
            if use_sms:
                pass
            notified.add(user.email)
        print(f"Daily reminders sent to {len(notified)} users via {total_notifications} notifications.")
        return f"Reminders sent: {len(notified)} users, {total_notifications} notifications"

@celery.task(name='celery_worker.monthly_report_task')
def monthly_report_task():
    app = get_flask_app()
    with app.app_context():
        users = User.query.filter(User.role == 'user').all()
        now = datetime.now()
        start = datetime(now.year, now.month, 1)
        all_monthly_scores = Score.query.filter(Score.timestamp >= start).all()
        for user in users:
            scores = Score.query.filter(Score.user_id == user.id, Score.timestamp >= start).all()
            total = len(scores)
            avg = sum(s.total_score for s in scores) / total if total else 0
            quiz_rankings = []
            for score in scores:
                quiz_scores = [s for s in all_monthly_scores if s.quiz_id == score.quiz_id]
                quiz_scores.sort(key=lambda x: x.total_score, reverse=True)
                rank = next((i + 1 for i, s in enumerate(quiz_scores) if s.user_id == user.id), 0)
                total_participants = len(quiz_scores)
                quiz = Quiz.query.get(score.quiz_id)
                subject = Subject.query.get(quiz.subject_id) if quiz else None
                chapter = Chapter.query.get(quiz.chapter_id) if quiz else None
                quiz_rankings.append({
                    'quiz_id': score.quiz_id,
                    'score': score.total_score,
                    'rank': rank,
                    'total_participants': total_participants,
                    'quiz_name': quiz.title if quiz else f"Quiz {score.quiz_id}",
                    'subject': subject.name if subject else "Unknown",
                    'chapter': chapter.name if chapter else "Unknown",
                    'date': score.timestamp.strftime('%Y-%m-%d %H:%M')
                })
            user_total_score = sum(s.total_score for s in scores)
            all_user_totals = []
            for u in users:
                u_scores = Score.query.filter(Score.user_id == u.id, Score.timestamp >= start).all()
                u_total = sum(s.total_score for s in u_scores)
                all_user_totals.append((u.id, u_total))
            all_user_totals.sort(key=lambda x: x[1], reverse=True)
            overall_rank = next((i + 1 for i, (uid, _) in enumerate(all_user_totals) if uid == user.id), 0)
            total_users = len(all_user_totals)
            report_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset=\"UTF-8\">
                <title>Quiz Master - Monthly Activity Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                    .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    .header {{ text-align: center; color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 20px; margin-bottom: 30px; }}
                    .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
                    .stat-card {{ background: #ecf0f1; padding: 20px; border-radius: 8px; text-align: center; }}
                    .stat-number {{ font-size: 2em; font-weight: bold; color: #3498db; }}
                    .stat-label {{ color: #7f8c8d; margin-top: 5px; }}
                    .quiz-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                    .quiz-table th, .quiz-table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                    .quiz-table th {{ background-color: #3498db; color: white; }}
                    .quiz-table tr:nth-child(even) {{ background-color: #f9f9f9; }}
                    .rank-badge {{ background: #e74c3c; color: white; padding: 4px 8px; border-radius: 12px; font-size: 0.8em; }}
                    .footer {{ margin-top: 30px; text-align: center; color: #7f8c8d; font-size: 0.9em; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>📊 Monthly Activity Report</h1>
                        <p>Report Period: {start.strftime('%B %Y')}</p>
                    </div>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-number">{total}</div>
                            <div class="stat-label">Quizzes Taken</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{avg:.1f}</div>
                            <div class="stat-label">Average Score</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{overall_rank}/{total_users}</div>
                            <div class="stat-label">Overall Rank</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{user_total_score}</div>
                            <div class="stat-label">Total Points</div>
                        </div>
                    </div>
                    <h2>📝 Quiz Performance Details</h2>
                    <table class="quiz-table">
                        <thead>
                            <tr>
                                <th>Quiz</th>
                                <th>Subject</th>
                                <th>Chapter</th>
                                <th>Score</th>
                                <th>Rank</th>
                                <th>Date</th>
                            </tr>
                        </thead>
                        <tbody>
            """
            for quiz_data in quiz_rankings:
                rank_class = "rank-badge" if quiz_data['rank'] <= 3 else ""
                rank_text = f"#{quiz_data['rank']}" if quiz_data['rank'] > 0 else "N/A"
                report_html += f"""
                            <tr>
                                <td><strong>{quiz_data['quiz_name']}</strong></td>
                                <td>{quiz_data['subject']}</td>
                                <td>{quiz_data['chapter']}</td>
                                <td><strong>{quiz_data['score']}</strong></td>
                                <td><span class=\"{rank_class}\">{rank_text}</span></td>
                                <td>{quiz_data['date']}</td>
                            </tr>
                """
            report_html += f"""
                        </tbody>
                    </table>
                    <div class="footer">
                        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                        <p>Keep up the great work! 🚀</p>
                    </div>
                </div>
            </body>
            </html>
            """
            send_email(
                to=user.email,
                subject=f"Quiz Master: Monthly Activity Report - {start.strftime('%B %Y')}",
                body=f"Hi {user.full_name},\n\nYour monthly activity report for {start.strftime('%B %Y')} is attached.\n\nBest regards,\nQuiz Master Team",
                html=report_html
            )
        print(f"Monthly reports sent to {len(users)} users.")
        return f"Monthly reports sent to {len(users)} users"

@celery.task(name='celery_worker.test_email_task')
def test_email_task():
    app = get_flask_app()
    with app.app_context():
        try:
            result = send_email(
                to=app.config['MAIL_DEFAULT_SENDER'],
                subject="Quiz Master: Email Test",
                body="This is a test email from Quiz Master backend jobs system."
            )
            if result:
                print("Test email sent successfully!")
                return "Email sent successfully"
            else:
                print("Failed to send test email")
                return "Email failed"
        except Exception as e:
            print(f"Email test error: {e}")
            return f"Email error: {e}"

celery.conf.beat_schedule = {
    'send-daily-reminders': {
        'task': 'celery_worker.daily_reminder_task',
        'schedule': 120,  # every 24 hours must change once demonstrated
    },
    'send-monthly-reports': {
        'task': 'celery_worker.monthly_report_task',
        'schedule': 120,  # every 30 days must change once demonstrated
    },
} 