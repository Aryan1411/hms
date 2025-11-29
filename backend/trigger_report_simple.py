from application.tasks import send_monthly_reports

# Trigger the task
task = send_monthly_reports.delay()
print(f"Task triggered! ID: {task.id}")
print("Check celery_worker.log for output.")
print("Check doctor@test.com inbox for the monthly report email.")
