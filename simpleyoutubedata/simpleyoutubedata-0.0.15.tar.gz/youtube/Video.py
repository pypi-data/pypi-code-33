if __name__ == "__main__":
    raise

class Video:
    OtherProps = {}

    def __init__(self, data):
        for x in data:
            if type(data[x]) != dict:
                self.OtherProps[x] = data[x]
                continue

            for y in data[x]:
                setattr(self, y, data[x][y])

        if self.title == "Private video" and self.description == "This video is private.":
            self.private = True
        else:
            self.private = False

        self.OriginalData = data
