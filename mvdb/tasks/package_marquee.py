from nornir.core.task import Task, Result
from typing import Any


def package_marquee(
    task: Task,
    **kwargs: Any
):
    """Creates compound str value named marquee for task.host.

    Compiles facts about task.host and creates a new compound str value
    for user presentation, stored in task.host.data["marquee"]. This is
    done in-place. The task itself returns None.

    Returns:
      None
    """
    exData = task.host.extended_data()
    title = task.host.data["title"]
    year = task.host.data["year"]
    runtime = task.host.data["runtime"]
    aspectRatio = f"{task.host.data['release']['aspect_ratio']}:1"
    media = exData["format"]
    if isinstance(task.host.data["director"], list):
        director = " & ".join(task.host.data["director"])
    else:
        director = task.host.data["director"]

    marquee = f"{title} ({year}/{runtime} min/{aspectRatio}) | dir. "
    marquee += f"{director} [{media}]"

    task.host.data["marquee"] = marquee
