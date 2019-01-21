"""Functions to create a Task instance from text in todo.txt format"""
import re
from datetime import datetime

from blockbuster.core.model import Task


def _done(todotxt):
    """
    Returns
    -------
    tuple
        boolean indicating whether the task is complete
        the todo.txt string stripped of any completed portion
    """
    done = todotxt.startswith("x")
    if done:
        todotxt = todotxt[1:].strip()
    return done, todotxt


def _priority(todotxt):
    """
    Returns
    -------
    tuple
        Any priority character
        The todo.txt string stripped of any priority character
    """
    regex = re.compile(r"\s*\((\S)\)")
    match = regex.search(todotxt)
    priority = None
    if match:
        priority = match.group(0).strip().lstrip("(").rstrip(")")
        todotxt = regex.sub("", todotxt).strip()
    return priority, todotxt


def _dates(todotxt):
    regex = re.compile(r"(?<!\S)(\s*\d{4}-\d{2}-\d{2})")
    match = regex.search(todotxt)
    dates = {"completed_at": None, "created_at": None}
    if match:
        matches = [item for item in regex.finditer(todotxt)]
        if len(matches) == 2:
            dates["completed_at"] = datetime.strptime(
                matches[0].group().strip(), "%Y-%m-%d"
            ).date()
            dates["created_at"] = datetime.strptime(
                matches[1].group().strip(), "%Y-%m-%d"
            ).date()
        else:
            dates["created_at"] = datetime.strptime(
                matches[0].group().strip(), "%Y-%m-%d"
            ).date()
        todotxt = regex.sub("", todotxt).strip()

    return dates, todotxt


def _projects(todotxt):
    regex = re.compile(r"\s+(\+\w+)")
    match = regex.search(todotxt)
    projects = None
    if match:
        projects = [
            item.group().strip().lstrip("+") for item in regex.finditer(todotxt)
        ]
        todotxt = regex.sub("", todotxt).strip()

    return projects, todotxt


def _contexts(todotxt):
    regex = re.compile(r"\s+(\@\w+)")
    match = regex.search(todotxt)
    contexts = None
    if match:
        contexts = [
            item.group().strip().lstrip("@") for item in regex.finditer(todotxt)
        ]
        todotxt = regex.sub("", todotxt).strip()

    return contexts, todotxt


def _tags(todotxt):
    regex = re.compile(r"\s+(\w+\:\S+)")
    match = regex.search(todotxt)
    tags = None
    if match:
        items = (item.group().strip() for item in regex.finditer(todotxt))
        tags = {item.split(":")[0]: item.split(":")[1] for item in items}
        todotxt = regex.sub("", todotxt).strip()

    if tags:
        tags = {
            key: (
                datetime.strptime(value, "%Y-%m-%d").date()
                if re.match(r"\d{4}-\d{2}-\d{2}$", value)
                else value
            )
            for key, value in tags.items()
        }

    return tags, todotxt


def create_task(todotxt):
    """Create a Task instance from a string in todo.txt format"""
    todotxt = todotxt.strip()

    task = {
        "description": None,
        "done": False,
        "priority": None,
        "completed_at": None,
        "created_at": None,
        "projects": None,
        "contexts": None,
        "tags": None,
    }

    task["done"], todotxt = _done(todotxt)
    task["priority"], todotxt = _priority(todotxt)
    task["tags"], todotxt = _tags(todotxt)
    task["projects"], todotxt = _projects(todotxt)
    task["contexts"], todotxt = _contexts(todotxt)
    dates, todotxt = _dates(todotxt)
    task["completed_at"] = dates["completed_at"]
    task["created_at"] = dates["created_at"]
    task["description"] = todotxt.strip()

    return Task(**task)
