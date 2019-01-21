"""CRUD operations on todo.txt files"""
from hashlib import sha256

from blockbuster.core.factory import create_task
from blockbuster.core.model import TasksAdded, TasksDeleted, TasksUpdated


def read_tasks(file):
    """Create Tasks instances from a todo.txt file

    Parameters
    ----------
    file
        A Path instance

    Returns
    -------
    list
        of Task instances
    """
    with file.open("r") as f:
        tasks_raw = f.readlines()

    return [create_task(todotxt) for todotxt in tasks_raw]


def add_tasks(additions, file):
    """Add tasks to a todo.txt file

    Parameters
    ----------
    additions
        A list or tuple of strings in todo.txt format
    file
        A Path instance

    Returns
    -------
    TasksAdded
        An instance of blockbuster.core.model.Event
    """
    with file.open("r+") as f:
        prior_hash = sha256(f.read().encode(encoding="UTF-8")).hexdigest()
        for task in additions:
            f.write(f"{task}\n")
        f.seek(0)
        new_hash = sha256(f.read().encode(encoding="UTF-8")).hexdigest()

    return TasksAdded(
        tasks=additions, file=file, prior_hash=prior_hash, new_hash=new_hash
    )


def delete_tasks(deletions, file):
    """Delete lines from a todo.txt file

    Parameters
    ----------
    deletions
        A list or tuple of index numbers indicating which tasks to delete by
        their position in the file
    file
        A Path instance

    Returns
    -------
    TasksDeleted
        An instance of blockbuster.core.model.Event
    """
    with file.open("r+") as f:
        prior_hash = sha256(f.read().encode(encoding="UTF-8")).hexdigest()
        f.seek(0)
        tasks = f.readlines()
        keep_ids = [i for i in range(len(tasks)) if i not in deletions]
        f.seek(0)
        for task in [tasks[i] for i in keep_ids]:
            f.write(task)
        f.truncate()
        f.seek(0)
        new_hash = sha256(f.read().encode(encoding="UTF-8")).hexdigest()
    deleted_tasks = [tasks[i] for i in deletions]
    return TasksDeleted(
        tasks=deleted_tasks, file=file, prior_hash=prior_hash, new_hash=new_hash
    )


def update_tasks(updates, file):
    """Update lines in a todo.txt file

    Parameters
    ----------
    updates
        A dictionary mapping the index number of the task within the file to
        a string of its updated content
    file
        A Path instance

    Returns
    -------
    TasksUpdated
        An instance of blockbuster.core.model.Event
    """
    with file.open("r+") as f:
        prior_hash = sha256(f.read().encode(encoding="UTF-8")).hexdigest()
        f.seek(0)
        tasks = f.readlines()
        new_tasks = [
            updates[item[0]] if item[0] in updates else tasks[item[0]]
            for item in enumerate(tasks)
        ]
        print(new_tasks)
        f.seek(0)
        for task in new_tasks:
            f.write(f"{task.strip()}\n")
        f.truncate()
        f.seek(0)
        new_hash = sha256(f.read().encode(encoding="UTF-8")).hexdigest()
    updated_tasks = [value for value in updates.values()]
    return TasksUpdated(
        tasks=updated_tasks, file=file, prior_hash=prior_hash, new_hash=new_hash
    )
