# PowerShell script to start Celery worker with correct PYTHONPATH
$env:PYTHONPATH = "C:\Users\LENOVO\OneDrive\Desktop\Quiz_master_23f2004341"
celery -A celery_worker worker --loglevel=info --pool=solo 