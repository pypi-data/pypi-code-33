class HTMLgen:
    """
        FUNCTIONS:
            class HTMLgen(head=False, tail=False, lang="en", docType="html").tag()

        EXAMPLE:
            page = HTMLgen(True, True)
            page.title("This is the page Title", scripts="foo.js bar.js", css="styles.css nav.css")
            page.body.add(page.tag("h1", "This is a header 1 line"))
            page.body.add("This is another line")

            page.return_html()

            ```
                <!DOCTYPE html>
                <html lang="en">
                    <head>
                        <title>This is the page Title</title>
                        <link rel="stylesheet" href="styles.css">
                        <link rel="stylesheet" href="nav.css">
                        <script src="foo.js"></script>
                        <script src="bar.js"></script>
                    </head>
                <body>
                    <h1>This is a header 1 line</h1>

                    This is another line
                </body>
                </html>
            ```

    """

    def __init__(self, head=False, tail=False, lang="en", docType="html"):
        self.head = head
        self.tail = tail
        self.page = {}
        self.body = self.createBody()

        if self.head:
            self.page["head"] = "<!DOCTYPE "+docType+">\n"
            self.page["head"] = self.page["head"]+"<html lang=\""+lang+">\n"

        if self.tail:
            self.page["tail"] = '</html>'


    def __exit__(self, exception_type, exception_value, traceback):
        return_html(self)

    def title(self, title, scripts=None, css=None):
        output = "\t<head>\n"
        output = output + "\t\t<title>"+title+"</title>\n"
        if css:
            if " " in css:
                css = css.split(' ')
                for i in css:
                    output = output + "\t\t<link rel=\"stylesheet\" href=\""+i+"\">\n"
            else:
                output = output + "\t\t<link rel=\"stylesheet\" href=\""+css+"\">\n"
        if scripts:
            if " " in scripts:
                scripts = scripts.split(' ')
                for script in scripts:
                    output = output + "\t\t<script src=\""+script+"\"></script>\n"
            else:
                output = output + "\t\t<script src=\""+scripts+"\"></script>\n"
            
        output = output + "\t</head>\n"

        self.page["header"] = output

    def tag(self, tag, content=False, close=True):
        output = "<"+tag+">"
        if content:
            output = output+content
        if close:
            output = output+"</"+tag+">\n"
        else:
            output = output+"\n"

        return output


    def createBody(self):
        return HTMLgen.bodycontent(self)


    class bodycontent:
        def __init__(self, body):
            self.body = body
            self.content = []

        def add(self, content):
            self.content.append(content)


    def return_html(self):
        output = ""
        if "head" in self.page:
            output = output + self.page["head"]
        if "header" in self.page:
            output = output + self.page["header"]
        if self.body.content:
            output = output + self.tag(tag="body", close=False)
            for i in self.body.content:
                output = output + "\t" + i + "\n"
            output = output + self.tag(tag="/body", close=False)
        if "tail" in self.page:
            output = output + self.page["tail"]

        return output