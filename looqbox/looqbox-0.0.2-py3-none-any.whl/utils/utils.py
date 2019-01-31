import random
import base64
import datetime
import itertools
import types
import string
from monthdelta import monthdelta
from looqbox.global_calling import GlobalCalling
from looqbox.integration.looqbox_global import Looqbox

__all__ = ["random_hash", "base64_encode", "base64_decode", "paste_if", "looq_format", "format_cnpj", "format_cpf",
           "title_with_date", "looq_map"]

# Calling global variable
GlobalCalling.set_looq_attributes(Looqbox())

def random_hash(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for pos in range(size))


def base64_encode(text):
    encoded_text = base64.b64encode(text.encode('utf-8')).decode('utf-8')

    return encoded_text


def base64_decode(text):
    decoded_text = base64.b64decode(text).decode('utf-8')

    return decoded_text


def paste_if(head, args=None, closure="", args_separator="|"):
    """
    Paste only if argument exists, otherwise returns None.

    :param head: Text to be inserted before the argument
    :param args: Value to be inserted after the head, if the value is None, the title will not be shown
    :param closure: Text to be inserted after the argument
    :param args_separator: Character string to separate the results
    :return: a string or None
    """
    if isinstance(args, dict):
        raise Exception("Dictionary not accept in paste_if")
    elif isinstance(args, list):
        args_with_sep = ""

        for arg in args[0:len(args) - 1]:
            args_with_sep = args_with_sep + str(arg) + args_separator

        return head + args_with_sep + args[-1] + closure

    elif isinstance(args, str):
        return head + args + closure
    else:
        return None


def looq_format(value, value_format=None):
    """
    Sets a value according to the specified format.

    :param value: Value to be formatted
    :param value_format: Format to be assigned to value. Formats allowed:
    * number:0
    * number:1
    * number:2
    * percent:0
    * percent:1
    * percent:2
    * date
    * datetime
    :return: A string formatted according to the value_format parameter
    """

    date_format = "%d/%m/%Y"
    datetime_format = "%d/%m/%Y %H:%M:%S"

    if value_format is None:
        raise Exception("Format not defined")

    if isinstance(value_format, types.FunctionType):
        return value_format(value)

    if value_format == "number:2":
        value = "{0:,.2f}".format(float(value))
        value = value.translate(str.maketrans(",.", ".,"))
    elif value_format == "number:1":
        value = "{0:,.1f}".format(float(value))
        value = value.translate(str.maketrans(",.", ".,"))
    elif value_format == "number:0":
        value = "{0:,.0f}".format(float(value))
        value = value.translate(str.maketrans(",.", ".,"))
    elif value_format == "percent:2":
        value = "{0:.2%}".format(value)
    elif value_format == "percent:1":
        value = "{0:.1%}".format(value)
    elif value_format == "percent:0":
        value = "{0:.0%}".format(value)
    elif value_format == "Date" or value_format == "date":
        value = datetime.datetime.strftime(value, date_format)
    elif value_format == "Datetime" or value_format == "datetime":
        value = datetime.datetime.strftime(value, datetime_format)

    return value


def format_cnpj(cnpj_string):
    """
    Formats CNPJ to standard format.

    :param cnpj_string: Unformatted CNPJ (string)
    :return: A string in the CNPJ format XX.XXX.XXX/XXXX-XX
    """
    if not isinstance(cnpj_string, str):
        return ""

    if len(cnpj_string) == 13:
        cnpj_string = '0' + cnpj_string
    elif len(cnpj_string) > 14:
        raise Exception('Invalid CNPJ string: More than 14 digits')

    return cnpj_string[:2] + "." + cnpj_string[2:5] + "." + cnpj_string[5:8] + "/" + \
           cnpj_string[8:12] + '-' + cnpj_string[12:]


def format_cpf(cpf_string):
    """
    Formats CPF to standard format.

    :param cpf_string: Unformatted CPF (string)
    :return: A string in the CPF format XXX.XXX.XXX-XX
    """
    return cpf_string[:3] + "." + cpf_string[3:6] + "." + cpf_string[6:9] + '-' + cpf_string[9:]


def week_name(date, language=GlobalCalling.looq.language):
    if language == "pt-br":
        week_rule = ["seg", "ter", "qua", "qui", "sex", "sab", "dom"]
    elif language == "en-us":
        week_rule = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    elif language == "it":
        week_rule = ["lun", "mar", "mer", "gio", "ven", "sab", "do"]

    date_week_day = date.timetuple()[6]

    return week_rule[date_week_day]


def date_range_name(date_int, language=GlobalCalling.looq.language):
    initial_date = date_int[0]
    finish_date = date_int[1]

    date_range = None

    # Case Day
    if initial_date == finish_date:
        if language == "pt-br":
            date_range = week_name(initial_date) + " sem: " + str(initial_date.isocalendar()[1]) + "/" \
                         + str(initial_date.year)
        elif language == "en-us":
            date_range = week_name(initial_date) + " week: " + str(initial_date.isocalendar()[1]) + "/" \
                         + str(initial_date.year)
        elif language == "it":
            date_range = week_name(initial_date) + " week: " + str(initial_date.isocalendar()[1]) + "/" \
                         + str(initial_date.year)

    # Case Week
    if initial_date.timetuple()[6] == 0 and initial_date + datetime.timedelta(days=6) == finish_date:
        if language == "pt-br":
            date_range = "sem: " + str(initial_date.isocalendar()[1]) + " - " + str(initial_date.year)
        elif language == "en-us":
            date_range = "week: " + str(initial_date.isocalendar()[1]) + " - " + str(initial_date.year)
        elif language == "it":
            date_range = "week: " + str(initial_date.isocalendar()[1]) + " - " + str(initial_date.year)

    # Case Month
    if initial_date.day == 1 and initial_date + monthdelta(1) - datetime.timedelta(days=1) == finish_date:
        if language == "pt-br":
            date_range = "mês: " + str(initial_date.month) + "/" + str(initial_date.year)
        elif language == "en-us":
            date_range = "month: " + str(initial_date.month) + "/" + str(initial_date.year)
        elif language == "it":
            date_range = "mese: " + str(initial_date.month) + "/" + str(initial_date.year)

    # Case MTD
    if initial_date.day == 1 and initial_date.month == finish_date.month and datetime.datetime.now().strftime("%Y-%m-%d") == finish_date:
        if language == "pt-br":
            date_range = "mtd: " + str(initial_date.month) + "/" + str(initial_date.year)
        elif language == "en-us":
            date_range = "mtd: " + str(initial_date.month) + "/" + str(initial_date.year)
        elif language == "it":
            date_range = "mtd: " + str(initial_date.month) + "/" + str(initial_date.year)

    # Case Year
    if initial_date.day == 1 and initial_date.month == 1 \
            and initial_date + monthdelta(12) - datetime.timedelta(1) == finish_date:
        if language == "pt-br":
            date_range = "ano: " + str(initial_date.year)
        elif language == "en-us":
            date_range = "year: " + str(initial_date.year)
        elif language == "it":
            date_range = "ieri: " + str(initial_date.year)

    if date_range is None:
        return ""
    else:
        return " (" + date_range + ")"


def title_with_date(header=None, date_int=None, language=GlobalCalling.looq.language):
    """
    Writes a title for the specified date or date range.

    :param header: Text to be placed before the date
    :param date_int: Date(s) interval to be used in the title
    :param language: Title language
    :return: A title string
    """

    if language == "pt-br":
        var_day = " dia "
        var_from = " de "
        var_to = " a "
    elif language == "en-us":
        var_day = " day "
        var_from = " from "
        var_to = " to "
    elif language == "it":
        var_day = " gio "
        var_from = " dal "
        var_to = " al "

    if "00:00:00" in date_int[0] and "00:00:00" in date_int[1]:
        date_int[0] = datetime.datetime.strptime(date_int[0], '%Y-%m-%d %H:%M:%S').date()
        date_int[1] = datetime.datetime.strptime(date_int[1], '%Y-%m-%d %H:%M:%S').date() - datetime.timedelta(days=1)
    else:
        date_int[0] = datetime.datetime.strptime(date_int[0], '%Y-%m-%d').date()
        date_int[1] = datetime.datetime.strptime(date_int[1], '%Y-%m-%d').date()

    if isinstance(date_int[0], datetime.date) and isinstance(date_int[1], datetime.date):
        if date_int[0] == date_int[1]:
            date_result = header + " " + var_day + " " + \
                          looq_format(date_int[0], "Date") + date_range_name(date_int)
        else:
            date_result = header + " " + var_from + " " + looq_format(date_int[0], "Date") + var_to \
                          + looq_format(date_int[1], "Date") + date_range_name(date_int)
    else:
        if date_int[0] == date_int[1]:
            date_result = header + " " + var_day + " " + looq_format(date_int[0], "datetime")
        else:
            date_result = header + " " + var_from + " " + looq_format(date_int[0], "datetime") + var_to \
                          + looq_format(date_int[1])

    return date_result


def looq_map(function_arg, *args):
    """
    Apply function with the arguments defined.

    :param function_arg: Function to apply
    :param args: Function arguments
    :return: The output of the function
    """
    # Verify if it has arguments
    if len(args) == 1 and args[0] is None:
        return function_arg(None)

    # Transforming Nones into str to find the cartesian product
    args_list = list(args)
    for i in range(len(args_list)):
        if args_list[i] is None:
            args_list[i] = ["None"]
    args = tuple(args_list)

    # Finding the cartesian product of my *args
    args_possibilities_list = list(itertools.product(*args))

    # Transform tuple into list
    args_possibilities_list = list(args_possibilities_list[0])

    # Turning str None into None type again
    for i in range(len(args_possibilities_list)):
        if args_possibilities_list[i] == "None":
            args_possibilities_list[i] = None

    args_possibilities_list = [args_possibilities_list]

    # Dynamically sending all the possibilities to the function
    result = [function_arg(*arg_product) for arg_product in args_possibilities_list]

    return result[0]
