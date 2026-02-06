from queue import Queue

db_queue = Queue()



'''

    Purpose: decouple trading engine from DB writes.
        Without queue:

        tick → trigger → insert DB → delay → next tick late
        With queue:

        tick → trigger → push event → continue trading
                            ↓
                        worker writes DB

        This prevents:
        DB lag from affecting strategy execution

'''