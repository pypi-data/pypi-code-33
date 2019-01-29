def get_cases( _writer_name ):
    from sxsxml_tests.cases import cases
    commands = []
    current = None
    for line in cases.split( "\n" ):
        if not line:
            continue
        elif line.startswith( "**" ):
            line = line[2:].strip()
            
            if "=" in line:
                nam, _, val = line.partition( "=" )
                if nam.strip() == _writer_name:
                    current[1] = val.strip()
            else:
                current = [line.strip( " *" ).lower(), "", []]
                commands.append( current )
        else:
            current[2].append( line )
    return commands