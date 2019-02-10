from github import Github


def issue(token, title, body):
    g = Github(token)

    try:
        repo = g.get_repo("tman540/T.A.R.B.S.-Engine")
    except Exception as e:
        print("Unable to log in")
        print(f"Error: {e}")
        exit()

    try:
        repo.create_issue(title=title, body=body, labels=["bug"])
        print("Issue successfully submitted!")

    except Exception as e:
        print("Unable to submit issue")
        print(f"Error: {e}")
        exit()


def feature(token, title, body):
    g = Github(token)

    try:
        repo = g.get_repo("tman540/T.A.R.B.S.-Engine")
    except Exception as e:
        print("Unable to log in")
        print(f"Error: {e}")
        exit()

    title = "Feature Request: " + title
    try:
        repo.create_issue(title=title, body=body, labels=["feature"])
        print("Feature successfully submitted!")

    except Exception as e:
        print("Unable to submit feature")
        print(f"Error: {e}")
        exit()
