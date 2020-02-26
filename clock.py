from apscheduler.schedulers.blocking import BlockingScheduler
from helpers.dbms import post_to_slack, clear_denied
import os

host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/slack-confessions')
client = MongoClient(host=f'{host}?retryWrites=false')
db = client.get_default_database()

users = db.users
confessions = db.confessions

# scheduler instantiation
sched = BlockingScheduler()

@sched.scheduled_job('cron', hour='*', minute=10)
def scheduled_daily():
    post_to_slack(confessions)

@sched.scheduled_job('cron',day='*/3',hour=0, minute=50)
def scheduled_bi_weekly():
    clear_denied(confessions)


sched.start()
