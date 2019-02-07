class RemoveMethod(object):
    DONT_REMOVE, FROM_SC, FROM_CONN, FROM_BOTH = range(4)


RemoveMethods = (
    (RemoveMethod.DONT_REMOVE, 'Dont remove'),
    (RemoveMethod.FROM_SC, 'Remove from Singular Center'),
    (RemoveMethod.FROM_CONN, 'Remove from Connector'),
    (RemoveMethod.FROM_BOTH, 'Remove from Singular Center and Connector'),
)


class ActivityType(object):
    TASK, EVENT, FIXED_TIME = range(3)


ActivityTypes = (
    (ActivityType.TASK, 'Task'),
    (ActivityType.EVENT, 'Event'),
    (ActivityType.FIXED_TIME, 'Fixed Time'),
)


class ActivityStatus(object):
    IN_BACKLOG, READY, SCHEDULED, DONE, CHECK = range(5)


ActivityStatuses = (
    ActivityStatus.IN_BACKLOG, 'In Backlog',
    ActivityStatus.READY, 'Ready',
    ActivityStatus.SCHEDULED, 'Scheduled',
    ActivityStatus.DONE, 'Done',
    ActivityStatus.CHECK, 'Check',
)


class UserStatus:
    ASKED, CONFIRMED, REJECTED = range(3)


UserStatuses = (
    (UserStatus.ASKED, 'ASKED'),
    (UserStatus.CONFIRMED, 'CONFIRMED'),
    (UserStatus.REJECTED, 'REJECTED'),
)


class RepeatMode:
    SINGLE, EVERY, AFTER = range(3)


RepeatModes = (
    (RepeatMode.SINGLE, 'SINGLE'),
    (RepeatMode.EVERY, 'EVERY'),
    (RepeatMode.AFTER, 'AFTER'),
)


class UserRole:
    SUPERVISOR = 'SUPERVISOR'
    EXECUTOR = 'EXECUTOR'


UserRoles = (
    (UserRole.SUPERVISOR, 'SUPERVISOR'),
    (UserRole.EXECUTOR, 'EXECUTOR')
)
