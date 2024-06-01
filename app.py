import datetime
from flask import Flask, request
import redis
from rq import Queue
from tasks import background_task
from rq.registry import FailedJobRegistry ,FinishedJobRegistry,StartedJobRegistry,CanceledJobRegistry

app = Flask(__name__)

# Create client instance from Redis and create connection 
# to RQ, which is our queue for background tasks
redis_instance = redis.Redis()
queue_tasks = Queue(connection=redis_instance)
job_info={
    'id':str,
    'description':str,
    'start_date':datetime.datetime,
    'enquered_date':datetime.datetime,
    'end_date':datetime.datetime,
    'status':str

}

@app.route('/addtask/')
def add_task():
    if request.args.get('n'):
        job = queue_tasks.enqueue(background_task, request.args.get('n'))
        
        return f"Task {job.id} added to queue at {job.enqueued_at}. There are currently {queue_tasks.count} tasks in the queue."

@app.route('/searchtask/')
def task_search():
    
    if request.args.get('id'):
        id=request.args.get('id')
        job = queue_tasks.fetch_job(id)
        canceld_job=id in queue_tasks.canceled_job_registry.get
        if job is not None:
           print(f"if not found ----------------- {job} ------------")
           job_info = {
                'id': job.id,
                'description':job.description,
                'start_date':job.started_at,
                'enqueued_at':job.enqueued_at,
                'end_date':job.ended_at,
                'status':job.get_status()
            }
           return job_info
        elif canceld_job:
            job_info = {
                'id': id,
                # 'description':job.description,
                # 'start_date':job.started_at,
                # 'enqueued_at':job.enqueued_at,
                # 'end_date':job.ended_at,
                'status':'canceld'
            }
            return job_info

    return f"there is no task with this id {request.args.get('id')}"


@app.route('/canceltask/')
def cancel_task():
    if request.args.get('id'):
        id=request.args.get('id') 
        job = queue_tasks.fetch_job(id)
        job.cancel()
        return f"Task {id} was cancelled"
    return f"therer is no task with id : {job.id}"

@app.route('/deletetask/')
def delete_task():
    if request.args.get('id'):
        id=request.args.get('id') 
        job = queue_tasks.fetch_job(id)
        job.delete()
        return f"Task {id} was cancelled"
    return f"therer is no task with id : {job.id}"

@app.route('/getall/')
def get_all():
    all=queue_tasks.get_jobs()
    finished=queue_tasks.finished_job_registry.get_job_ids()
    canceled=queue_tasks.canceled_job_registry.get_job_ids() 
    faileld=queue_tasks.failed_job_registry.get_job_ids() 
    return f"all jobs({len(all)}) {[job.get_status() for job in all]} and finished {finished} and ----##--- failed : {faileld} ----##--- canceled: {canceled}"

if __name__ == '__main__':
    app.run()
