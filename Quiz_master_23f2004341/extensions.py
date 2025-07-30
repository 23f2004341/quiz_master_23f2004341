from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_caching import Cache
import redis
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
cache = Cache()

# Direct Redis client for advanced operations
redis_client = redis.StrictRedis(
    host='localhost',
    port=6379,
    db=1,  # Use the same DB as your cache config
    decode_responses=True
)

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return db.session.get(User, int(user_id))

def send_email(to, subject, body, html=None):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = current_app.config['MAIL_DEFAULT_SENDER']
    msg['To'] = to
    part1 = MIMEText(body, 'plain')
    msg.attach(part1)
    if html:
        part2 = MIMEText(html, 'html')
        msg.attach(part2)
    try:
        with smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']) as server:
            if current_app.config.get('MAIL_USE_TLS'):
                server.starttls()
            server.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
            server.sendmail(msg['From'], [to], msg.as_string())
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

# Cache utility functions for performance optimization
def invalidate_cache_pattern(pattern):
    try:
        keys = redis_client.keys(f"quiz_master:{pattern}")
        if keys:
            redis_client.delete(*keys)
            print(f"Invalidated {len(keys)} cache keys matching pattern: {pattern}")
    except Exception as e:
        print(f"Cache invalidation error: {e}")

def invalidate_user_cache(user_id):
    invalidate_cache_pattern(f"user:{user_id}:*")

def invalidate_subject_cache():
    invalidate_cache_pattern("subjects*")

def invalidate_chapter_cache():
    invalidate_cache_pattern("chapters*")

def invalidate_quiz_cache():
    invalidate_cache_pattern("quizzes*")

def invalidate_question_cache():
    invalidate_cache_pattern("questions*")

def invalidate_charts_cache():
    invalidate_cache_pattern("charts*")
    invalidate_cache_pattern("analytics*")

def delete_cache_pattern(pattern):
    keys = redis_client.keys(pattern)
    if keys:
        redis_client.delete(*keys)

def cache_key_with_user(key, user_id):
    return f"user:{user_id}:{key}"

def cache_key_with_params(key, **params):
    param_str = ":".join([f"{k}={v}" for k, v in sorted(params.items())])
    return f"{key}:{param_str}"

def get_cache_stats():
    try:
        info = redis_client.info()
        return {
            'connected_clients': info.get('connected_clients', 0),
            'used_memory': info.get('used_memory_human', '0B'),
            'keyspace_hits': info.get('keyspace_hits', 0),
            'keyspace_misses': info.get('keyspace_misses', 0),
            'total_commands_processed': info.get('total_commands_processed', 0)
        }
    except Exception as e:
        print(f"Cache stats error: {e}")
        return {}

def warm_cache():
    print("Cache warming is a no-op in this configuration.")
    return True

def get_cache_hit_rate():
    try:
        info = redis_client.info()
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total = hits + misses
        if total > 0:
            hit_rate = (hits / total) * 100
            return round(hit_rate, 2)
        return 0
    except Exception as e:
        print(f"Cache hit rate calculation error: {e}")
        return 0

def optimize_cache_performance():
    try:
        # Set memory policy to allkeys-lru (Least Recently Used)
        redis_client.config_set('maxmemory-policy', 'allkeys-lru')
        # Set max memory to 100MB
        redis_client.config_set('maxmemory', '100mb')
        # Enable AOF persistence for better reliability
        redis_client.config_set('appendonly', 'yes')
        print("Cache performance optimization completed")
        return True
    except Exception as e:
        print(f"Cache optimization error: {e}")
        return False