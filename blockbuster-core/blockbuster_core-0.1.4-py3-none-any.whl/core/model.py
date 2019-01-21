"""Classes to represent tasks and the events which cause them to change state.

These classes have no dependencies on any other component of the blockbuster
namespace.
"""
from abc import ABCMeta
from datetime import datetime

from blockbuster.core import DATE_FORMAT
from marshmallow import Schema, fields, pre_dump


class Task:
    """
    Parameters
    ----------
    description:
        Text to describe the task
    done:
        True if the task has been completed
    priority:
        By convention, a single upper case character to indicate priority level
    completed_at:
        The date on which the task was completed
    created_at:
        The date on which the task was created
    projects:
        A list of project tags (denoted by a + prefix in the text definition)
    contexts:
        A list of context tags (denoted by a @ prefix in the text definition)
    tags:
        A dict of user defined tag keys and values
    """

    def __init__(
        self,
        description,
        done=False,
        priority=None,
        completed_at=None,
        created_at=None,
        projects=None,
        contexts=None,
        tags=None,
    ):
        self.description = description
        self.done = done
        self.priority = priority
        self.completed_at = completed_at
        self.created_at = created_at or datetime.now().date()
        self.projects = projects or []
        self.contexts = contexts or []
        self.tags = tags or {}

    def __repr__(self):
        result = "blockbuster.core.model.Task("
        result += f'description="{self.description}", '
        result += f"done={self.done}, "
        result += f'priority="{self.priority}", '
        result += f"completed_at={repr(self.completed_at)}, "
        result += f"created_at={repr(self.created_at)}, "
        result += f"projects={self.projects}, "
        result += f"contexts={self.contexts}, "
        result += f"tags={self.tags})"
        return result

    def __str__(self):
        optional_prefixes = ""
        minimal_text = f"{self.created_at.strftime(DATE_FORMAT)} {self.description}"
        optional_suffixes = ""

        if self.done:
            optional_prefixes += "x "

        if self.priority:
            optional_prefixes += f"({self.priority}) "

        if self.completed_at:
            optional_prefixes += f"{self.completed_at.strftime(DATE_FORMAT)} "

        for project in self.projects:
            if project:
                optional_suffixes += f" +{project}"

        for context in self.contexts:
            if context:
                optional_suffixes += f" @{context}"

        for key, value in self.tags.items():
            optional_suffixes += f" {key}:{value}"

        return optional_prefixes + minimal_text + optional_suffixes


class EventSchema(Schema):
    """A marshmallow schema to serialise an Event instance.

    The schema provides the the 'dump' and 'dumps' methods to serialise
    event objects to a Python dictionary and JSON string respectively.
    """

    event_type = fields.Str()
    occurred_at = fields.DateTime()
    tasks = fields.List(fields.Str())
    file = fields.Str()
    prior_hash = fields.Str()
    new_hash = fields.Str()

    @pre_dump
    def add_event_type(self, item):
        """Add the fully qualified name of the Event class to the object being serialised."""
        item.event_type = f"{__name__}.{item.__class__.__qualname__}"
        return item


class Event:
    __metaclass__ = ABCMeta
    schema = EventSchema(strict=True)

    def __init__(self, tasks, file, prior_hash, new_hash):
        self.occurred_at = datetime.now()
        self.tasks = tasks
        self.file = file
        self.prior_hash = prior_hash
        self.new_hash = new_hash

    def __str__(self):
        return self.schema.dumps(self).data

    def to_dict(self):
        return self.schema.dump(self).data


class TasksAdded(Event):
    pass


class TasksUpdated(Event):
    pass


class TasksDeleted(Event):
    pass
