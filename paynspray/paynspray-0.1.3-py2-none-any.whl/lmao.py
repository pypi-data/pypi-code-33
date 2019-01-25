import re

def dogsay(text, width = 39):
    """Returns an ASCII image of a dog saying the provided text"""
    text_lines = re.findall(".{1,%d}" % (width - 4), str(text))
    lengths = map(lambda a: len(a), text_lines)
    lengths.sort()
    max_length = int(lengths[len(lengths) - 1])
    cloud_parts = []
    cloud_parts.append(" {}".format(('_' * (max_length + 2))))
    if len(text_lines) == 1:
        cloud_parts.append("< {} >".format(text))
    else:
        cloud_parts.append("/ {} \\".format(str(text_lines[0]).ljust(max_length, ' ')))
        if len(text_lines) > 2:
            for line in text_lines[1:(1 + (len(text_lines) - 2))]:
                cloud_parts.append("| {} |".format(str(line).ljust(max_length, ' ')))
        cloud_parts.append("\\ {} /".format(str(text_lines[len(text_lines) - 1]).ljust(max_length, ' ')))
    cloud_parts.append(" {}".format(('-' * (max_length + 2))))
    
    doggo = """     \\     .--.
      \\  _/ee/ \\
        (T_, \\_/      ,
           )="`------.))
          o|      /   /
            \\  /__\\  (\\
            |\\ \\  _/ / \\
           (_(_/ (__/(_/"""
    cloud_parts.append(doggo)
    return "\n".join(cloud_parts)