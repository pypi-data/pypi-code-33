"""The workflows"""
BUGTRACK_WORKFLOW = \
        {'__1__': ['new'],
         'new': ['confirmed', 'wont_fix', 'backlog', 'cancelled'],
         'confirmed': ['in_progress', 'wont_fix', 'worksforme', 'backlog', 'postponed', 'cancelled'],
         'reopened': ['in_progress', 'wont_fix', 'worksforme', 'backlog', 'postponed', 'cancelled'],
         'in_progress': ['reopened', 'wont_fix', 'fixed', 'backlog', 'postponed', 'worksforme'],
         'wont_fix': ['reopened', 'closed'],
         'fixed': ['reopened', 'backlog', 'uploaded_to_git', 'deployed_to_staging'],
         'worksforme': ['reopened', 'closed'],
         'uploaded_to_git': ['reopened', 'verified_in_git'],
         'verified_in_git': ['deployed_to_staging'],
         'deployed_to_staging': ['reopened', 'verified_in_staging'],
         'verified_in_staging': ['deployed_to_production', 'closed'],
         'deployed_to_production': ['reopened', 'closed'],
         'postponed': ['confirmed', 'reopened', 'in_progress'],
         'cancelled': [],
         'closed': [],
        }