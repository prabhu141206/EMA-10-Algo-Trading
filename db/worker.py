import time
from queue import Empty

from db.queue import db_queue
from db.pool import get_conn, release_conn


worker_running = True


def start_db_worker():
    print("[DB] Worker Started")

    while worker_running:

        # ---------------------------------------------
        # Wait for next database task
        # ---------------------------------------------
        try:
            task = db_queue.get(timeout=1)

        except Empty:
            continue

        # ---------------------------------------------
        # Process database task
        # ---------------------------------------------
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


# =====================================================
# STOP DB WORKER
# =====================================================

def stop_db_worker():

    global worker_running

    print("[DB] Stopping DB Worker...")

    worker_running = False