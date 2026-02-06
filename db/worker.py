import time
from db.queue import db_queue
from db.pool import get_conn, release_conn


def start_db_worker():
    print("DB Worker Started")

    while True:
        try:
            task = db_queue.get()
            try:
                conn = get_conn()
                cursor = conn.cursor()

                cursor.execute(task["query"], task["values"])

                conn.commit()

                cursor.close()
                release_conn(conn)

            except Exception as e:

                print("DB Worker Error:", e)
                try:
                    release_conn(conn)
                except:
                    pass

                time.sleep(2)

            finally:
                db_queue.task_done()
        except:
            print("worker crashed. Restarting...")
            time.sleep(2)

'''

    Purpose: background thread.
    It:
        Runs forever
        Pulls events from queue
        Writes to DB
        So your trading engine stays fast.

'''