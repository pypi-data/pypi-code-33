import io
import xlsxwriter
from django.utils import formats


def generate_excel_file(episodes):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {"in_memory": True})

    title_format = workbook.add_format()
    title_format.set_bold()
    title_format.set_font_size(13)

    bold_format = workbook.add_format()
    bold_format.set_bold()

    subtle_format = workbook.add_format()
    subtle_format.set_italic()
    subtle_format.set_font_size(9)

    for e in episodes:
        days = e.day_list()

        ws = workbook.add_worksheet(name=e.name.replace("/", "_"))

        ws.write(0, 0, e.name, title_format)
        ws.write(1, 0, f"{e.begin:%d.%m.} bis {e.end:%d.%m.%Y}", title_format)
        ws.write(
            3,
            0,
            "Hinweis: Diese Datei wird automatisch erzeugt, bitte nicht manuell bearbeiten.",
            subtle_format,
        )

        ws.write_row(5, 4, [formats.date_format(d, "D.") for d in days], subtle_format)
        ws.write_row(6, 0, ["Name", "Status", "RS", "EH"], bold_format)
        ws.write_row(6, 4, [formats.date_format(d, "d.m.") for d in days], bold_format)
        ws.write(6, len(days) + 4, "Bemerkung", bold_format)

        r = 7
        for a in e.applications.all():
            ws.write(r, 0, a.user.name)
            ws.write(r, 1, a.get_application_status_display())
            ws.write(r, 2, "✅" if a.drsa_ok else "❌")
            ws.write(r, 3, "✅" if a.eh_ok else "❌")

            dl = a.day_list()
            ws.write_row(r, 4, [a.role if d in dl else " " for d in days])

            ws.write(r, len(days) + 4, a.comment if a.comment else "", subtle_format)

            r += 1

        ws.write(r, 0, "Anzahl", bold_format)
        ws.write_row(r, 4, [d[1] for d in e.day_list_ct()], bold_format)

        ws.set_column(0, 1, width=22)
        ws.set_column(2, 3, width=4)
        ws.set_column(4, len(days) + 3, width=6)

    workbook.close()

    # Rewind the buffer.
    output.seek(0)
    return output
