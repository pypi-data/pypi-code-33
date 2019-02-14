"""
 .----------------.  .----------------.  .----------------.  .----------------.
| .--------------. || .--------------. || .--------------. || .--------------. |
| |  ____  ____  | || |  _________   | || | ____    ____ | || |   _____      | |
| | |_   ||   _| | || | |  _   _  |  | || ||_   \  /   _|| || |  |_   _|     | |
| |   | |__| |   | || | |_/ | | \_|  | || |  |   \/   |  | || |    | |       | |
| |   |  __  |   | || |     | |      | || |  | |\  /| |  | || |    | |   _   | |
| |  _| |  | |_  | || |    _| |_     | || | _| |_\/_| |_ | || |   _| |__/ |  | |
| | |____||____| | || |   |_____|    | || ||_____||_____|| || |  |________|  | |
| |              | || |              | || |              | || |              | |
| '--------------' || '--------------' || '--------------' || '--------------' |
 '----------------'  '----------------'  '----------------'  '----------------'
"""



line = "<br/>"

title = lambda title :"""
<span
        class="indexTitle"
        style="
          font-size: 96px;
          color:black;
          background-color:yellow;
          padding:20px;
          font-family: Georgia;"
>{TITLE}</span>
""".format(TITLE=title)


index = lambda items :line.join(["""
  <span>{TEXT}  ................... {INDEX}</span>""".format(TEXT=item, INDEX=index) for index, item in enumerate(items)])


from databricks.html.svg.arrow import down_arrow
from databricks.html.svg.quilmes import quilmes

def index(book):
  left = ""
  for index, item in enumerate(book):
    for title, subtitles in item.items():
      left += "<br/><span class='title'>{TEXT}  ................... {INDEX}</span>".format(TEXT=title, INDEX=index+1)
      for subtitle_index, subtitle in enumerate(subtitles):
        left += "<br/> &emsp; <span class='subtitle'>{TEXT}  ................... {INDEX}</span>".format(TEXT=subtitle, INDEX=str(index+1) + "." + str(subtitle_index))

  table = """
  <table style="width:100%">
    <tr>
      <td>{LEFT}</td>
      <td>{RIGHT}</td>
    </tr>
  </table>
  """.format(LEFT=left, RIGHT=quilmes)
  return table

section_title = lambda title:"""
    <p
        style="
        text-align: right;
        background-color: rgb(71, 85, 119);
        color: white;
        text-shadow: 2px 2px;
  "
     >
        <span
          style="
          font-size: 96px;
          font-family: Arial, Helvetica, sans-serif;">
                {TITLE}
        </span>
        {ARROW}
    </p>

    """.format(ARROW=arrow, TITLE=title)






book = [
  {
    "utils": [
      "load_csv",
      "load_temporary_tables"
    ]
  },
  {
    "KPI processors": [
      "process_DSC",
      "process_CMA",
      "process_VVMA",
      "process_VVMMAA",
      "process_VPPM"
    ]
  },
  {
    "example": [
      "run_all"
    ]
  }

]



subsection_groups = {}
def subsection_title(group, name):
  if group not in subsection_groups:
    subsection_groups[group] = 0
  n = current_subsections_of_group = subsection_groups[group]
  t = n + 1
  subsection_groups[group] = t



  return """
    <p
        style="
        text-align: center;
        background-color: rgb(71, 85, 119);
        color: white;
        "
     >
        <span
          style="
          font-size: 45px;
          font-family: Arial, Helvetica, sans-serif;">
                {GROUP} - {NAME}
        </span>
        <span
          style="
          font-size: 20px;
          color: rgb(40, 50, 78);
          font-family: Arial Black;">
              [{INDEX} out of TOTAL]
        </span>
    </p>

    """.format(ARROW=arrow, GROUP=group, NAME=name, INDEX=n)
