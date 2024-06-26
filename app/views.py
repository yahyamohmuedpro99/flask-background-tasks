from app import app
from flask import Blueprint, render_template, request, jsonify
from app.tasks import background_task,queue_tasks
from rq.registry import FailedJobRegistry, FinishedJobRegistry, StartedJobRegistry, CanceledJobRegistry

bp = Blueprint('bp', __name__)

@bp.route('/addtask/')
def add_task():
    if request.args.get('n'):
        job = queue_tasks.enqueue(background_task, request.args.get('n'))
        return f"Task {job.id} added to queue at {job.enqueued_at}. There are currently {queue_tasks.count} tasks in the queue."
    return "Missing parameter 'n'."

@bp.route('/searchtask/')
def search_task():
    job_id = request.args.get('id')
    if job_id:
        job = queue_tasks.fetch_job(job_id)
        if job:
            job_info = {
                'id': job.id,
                'description': job.description,
                'start_date': job.started_at,
                'enqueued_at': job.enqueued_at,
                'end_date': job.ended_at,
                'status': job.get_status()
            }
            return jsonify(job_info)
        else:
            canceled_job = job_id in CanceledJobRegistry(queue=queue_tasks).get_job_ids()
            if canceled_job:
                job_info = {
                    'id': job_id,
                    'status': 'canceled'
                }
                return jsonify(job_info)
    return f"No task with id: {job_id}"

@bp.route('/canceltask/')
def cancel_task():
    job_id = request.args.get('id')
    if job_id:
        job = queue_tasks.fetch_job(job_id)
        if job:
            job.cancel()
            return f"Task {job_id} was cancelled"
        return f"No task with id: {job_id}"
    return "Missing parameter 'id'."

@bp.route('/deletetask/')
def delete_task():
    job_id = request.args.get('id')
    if job_id:
        job = queue_tasks.fetch_job(job_id)
        if job:
            job.delete()
            return f"Task {job_id} was deleted"
        return f"No task with id: {job_id}"
    return "Missing parameter 'id'."

@bp.route('/getall/')
def get_all():
    all_jobs = queue_tasks.get_jobs()
    finished_jobs = FinishedJobRegistry(queue=queue_tasks).get_job_ids()
    canceled_jobs = CanceledJobRegistry(queue=queue_tasks).get_job_ids()
    failed_jobs = FailedJobRegistry(queue=queue_tasks).get_job_ids()
    started=StartedJobRegistry(queue=queue_tasks).get_job_ids()

    response = {
        "all_jobs_count": len(all_jobs),
        "all_jobs": [job.get_status() for job in all_jobs],
        "finished_jobs": finished_jobs,
        "canceled_jobs": canceled_jobs,
        "failed_jobs": failed_jobs,
        "started_jobs": started,
    }
    return jsonify(response)

@bp.route('/task_management/')
def task_management():
    return render_template('task_management.html')
