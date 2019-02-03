import conficus


def test_config_format(format_cfg):
    config = conficus._coerce(format_cfg)
    assert str(config) == '''[config] debug: True
[config] password: **********
[config] numbers.integer.value: 1
[config] numbers.float.value: 2.0
[config] sequence.empty-list.value: []
[config] sequence.empty-tuple.value: ()
[config] sequence.lists.short: [1, 2, 3, 4]
[config] sequence.lists.long: [
    Abagail had short hair
    Johnathan wore his far too long
    Isabelle was terribly frightened of very small horses
    And Henry ate the canned beans until they were all gone!]
[config] datetimes.datetime.value: 2017-05-31 10:00:00
[config] datetimes.date.value: 2017-05-31 00:00:00
[config] datetimes.time.value: 1900-01-01 10:15:02
[config] strings.short_string: unquoted string
[config] strings.string_with_spaces:  a quoted string preserves white space 
[config] strings.multiline_string: This is a multiline
   string with an
   indent.
[config] strings.text: This is a much longer text block
that we want to preserve but keep
readable in our configuration file.
We can used this for email body
text, and things like that.'''
