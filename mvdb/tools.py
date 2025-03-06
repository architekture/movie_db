from datetime import datetime


HEADER = ("-" * 79)


def start_timer():
    """datetime.now float value to mark the start of a task.
    
    Returns:
      start(float):
        Float value representing task start time.
    """
    start = datetime.now()

    return start


def stop_timer():
    """datetime.now float value to mark the end of a task.
    
    Returns:
      stop(float):
        Float value representing task end time.
      """
    stop = datetime.now()

    return stop


def lap_time(start: float, stop: float):
    """Calculates total execution time for a given task.
    
    Subtracts two float values with the resulting difference used to
    represent the total task execution time. This value is returned.

    Args:
      start(float):
        Time reference generated using tools.start_timer func.
      stop(float):
        Time reference generated using tools.stop_timer func.

    Returns:
      Float value representing the exec-time for a specified task as 
      "delta".
    """
    delta = stop - start

    return delta
    