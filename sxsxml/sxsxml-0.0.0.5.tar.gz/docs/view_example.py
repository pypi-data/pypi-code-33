from docutils import core, io


x = core.publish_parts(
        source="""
Title
=====

aaa

Title
=====

aaa

Subtitle
--------

aaa

Subtitle
--------

This is *italic*, **bold** and `citation` and ``teletype``.

* item
* item
* more
* more
* item
        """,
        writer_name='xml')["whole"]

if '<document source="&lt;string&gt;">' in x:
    x = x.split('<document source="&lt;string&gt;">',1 )[1]
else:
    x = x.split('<body>',1 )[1]
    x = x.split('</body>',1 )[0]
    



print(x)