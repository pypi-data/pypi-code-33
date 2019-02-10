import yaml
import pytz

def getUserSubmissionTimes(users, submissions_file):
    # Note that this supports multi-user submissions too
    with open(submissions_file, "r") as f:
        data = yaml.safe_load(f)

    gtid_timestamp_dict = {}

    for submission in data.values():
        timestamp = submission[":created_at"]

        # Note that Gradescope timestamps are UTC
        # TODO: This might cause issues if they change that
        timestamp = pytz.utc.localize(timestamp)

        people = submission[":submitters"]
        for person in people:
            gtid = person[':sid']

            # Make sure we store the guy's latest submission for violation checks
            existingSub = timestamp
            if gtid in gtid_timestamp_dict:
                existingSub = gtid_timestamp_dict[gtid]

            gtid_timestamp_dict[gtid] = max(timestamp, existingSub)

    # Finally convert it to an user -> timestamp dict
    return {x: gtid_timestamp_dict.get(x.gtID, None) for x in users}
