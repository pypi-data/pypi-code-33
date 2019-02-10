
version = "1.1.1-b"


try:
    with open("requirements.txt", "r") as f:
        data = f.read()
        requirements = data.split('\n')
        for req in requirements:
            if req == "" or len(req) <= 2:
                index = requirements.index(req)
                requirements.pop(index)
except Exception:
    pass
