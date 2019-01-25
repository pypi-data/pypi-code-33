import random, struct

UpperAlpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
LowerAlpha = "abcdefghijklmnopqrstuvwxyz"
Numerals = "0123456789"
Base32 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
Base64 = UpperAlpha + LowerAlpha + Numerals + '+/'
Base64Url = UpperAlpha + LowerAlpha + Numerals + '-_'
Alpha = UpperAlpha + LowerAlpha
AlphaNumeric = Alpha + Numerals
HighAscii = struct.pack("128B", *range(0x80, 0xff + 1))
LowAscii = struct.pack("32B", *range(0x00, 0x1f + 1))
DefaultWrap = 60
AllChars = struct.pack("256B", *range(0x00, 0xff + 1))
Punctuation = struct.pack("31B", *(range(0x21, 0x2f + 1) + range(0x3a, 0x3F + 1) + range(0x5b, 0x60 + 1) + range(0x7b, 0x7e + 1)))

TLDs = ['com', 'net', 'org', 'gov', 'biz', 'edu']

States = [
    "AK", "AL", "AR", "AZ", "CA", "CO", "CT", "DE", "FL", "GA", "HI",
    "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN",
    "MO", "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH",
    "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA",
    "WI", "WV", "WY"
    ]
    
Surnames = [
      "adams", "alexander", "allen", "anderson", "bailey", "baker", "barnes",
      "bell", "bennett", "brooks", "brown", "bryant", "butler", "campbell",
      "carter", "clark", "coleman", "collins", "cook", "cooper", "cox",
      "davis", "diaz", "edwards", "evans", "flores", "foster", "garcia",
      "gonzales", "gonzalez", "gray", "green", "griffin", "hall", "harris",
      "hayes", "henderson", "hernandez", "hill", "howard", "hughes", "jackson",
      "james", "jenkins", "johnson", "jones", "kelly", "king", "lee", "lewis",
      "long", "lopez", "martin", "martinez", "miller", "mitchell", "moore",
      "morgan", "morris", "murphy", "nelson", "parker", "patterson", "perez",
      "perry", "peterson", "phillips", "powell", "price", "ramirez", "reed",
      "richardson", "rivera", "roberts", "robinson", "rodriguez", "rogers",
      "ross", "russell", "sanchez", "sanders", "scott", "simmons", "smith",
      "stewart", "taylor", "thomas", "thompson", "torres", "turner", "walker",
      "ward", "washington", "watson", "white", "williams", "wilson", "wood",
      "wright", "young"
    ]
    
Names_Male = [
      "aaron", "adam", "alan", "albert", "andrew", "anthony", "antonio",
      "arthur", "benjamin", "billy", "bobby", "brandon", "brian", "bruce",
      "carl", "carlos", "charles", "chris", "christopher", "clarence", "craig",
      "daniel", "david", "dennis", "donald", "douglas", "earl", "edward",
      "eric", "ernest", "eugene", "frank", "fred", "gary", "george", "gerald",
      "gregory", "harold", "harry", "henry", "howard", "jack", "james", "jason",
      "jeffrey", "jeremy", "jerry", "jesse", "jimmy", "joe", "john", "johnny",
      "jonathan", "jose", "joseph", "joshua", "juan", "justin", "keith",
      "kenneth", "kevin", "larry", "lawrence", "louis", "mark", "martin",
      "matthew", "michael", "nicholas", "patrick", "paul", "peter", "philip",
      "phillip", "ralph", "randy", "raymond", "richard", "robert", "roger",
      "ronald", "roy", "russell", "ryan", "samuel", "scott", "sean", "shawn",
      "stephen", "steve", "steven", "terry", "thomas", "timothy", "todd",
      "victor", "walter", "wayne", "william", "willie"
    ]
    
Names_Female = [
      "alice", "amanda", "amy", "andrea", "angela", "ann", "anna", "anne",
      "annie", "ashley", "barbara", "betty", "beverly", "bonnie", "brenda",
      "carol", "carolyn", "catherine", "cheryl", "christina", "christine",
      "cynthia", "deborah", "debra", "denise", "diana", "diane", "donna",
      "doris", "dorothy", "elizabeth", "emily", "evelyn", "frances", "gloria",
      "heather", "helen", "irene", "jacqueline", "jane", "janet", "janice",
      "jean", "jennifer", "jessica", "joan", "joyce", "judith", "judy", "julia",
      "julie", "karen", "katherine", "kathleen", "kathryn", "kathy", "kelly",
      "kimberly", "laura", "lillian", "linda", "lisa", "lois", "lori", "louise",
      "margaret", "maria", "marie", "marilyn", "martha", "mary", "melissa",
      "michelle", "mildred", "nancy", "nicole", "norma", "pamela", "patricia",
      "paula", "phyllis", "rachel", "rebecca", "robin", "rose", "ruby", "ruth",
      "sandra", "sara", "sarah", "sharon", "shirley", "stephanie", "susan",
      "tammy", "teresa", "theresa", "tina", "virginia", "wanda"
    ]
    
def rand_base(length, bad, *foo):
    """Random text generator"""
    list_one = list((struct.unpack("{}B".format(len("".join(foo))), "".join(foo))))
    list_two = list((struct.unpack("{}B".format(len(str(bad))), str(bad))))
    
    cset = [x for x in list_one if x not in list_two]
    cset = list(set(cset))
    
    outp = []
    
    if len(cset) == 0:
        return ""
        
    for i in range(0, length):
        outp.append(random.choice(cset))
        
    return struct.pack("{}B".format(length), *outp)
    
def rand_text(length, bad = '', chars = AllChars):
    """Returns random bytes of data"""
    foo = chars.split()
    return rand_base(length, bad, *foo)

def rand_char(bad = '', chars = AllChars):
    """Returns a random character"""
    return rand_text(1, bad, chars)
    
def rand_text_alpha(length, bad = ''):
    """Returns random bytes of alphabetical data"""
    foo = []
    foo = foo + list(UpperAlpha)
    foo = foo + list(LowerAlpha)
    return rand_base(length, bad, *foo)
    
def rand_text_alpha_lower(length, bad = ''):
    """Returns random bytes of lowercase alphabetical data"""
    foo = []
    foo = foo + list(LowerAlpha)
    return rand_base(length, bad, *foo)
    
def rand_text_alpha_upper(length, bad = ''):
    """Returns random bytes of uppercase alphabetical data"""
    foo = []
    foo = foo + list(UpperAlpha)
    return rand_base(length, bad, *foo)
    
def rand_text_alphanumeric(length, bad = ''):
    """Returns random bytes of alphanumeric data"""
    foo = []
    foo = foo + list(UpperAlpha)
    foo = foo + list(LowerAlpha)
    foo = foo + list(Numerals)
    return rand_base(length, bad, *foo)
    
def rand_text_hex(length, bad = ''):
    """Returns random bytes of alphanumeric hex data"""
    foo = []
    foo = foo + list(Numerals)
    foo = foo + list(LowerAlpha[0:6])
    return rand_base(length, bad, *foo)
    
def rand_text_numeric(length, bad = ''):
    """Returns random bytes of numeric data"""
    foo = list(Numerals)
    return rand_base(length, bad, *foo)

def rand_hostname():
    """Returns a random domain name"""
    host = []
    for i in range(0, random.randrange(3) + 1):
        host.append(rand_text_alphanumeric(random.randrange(10) + 1))
        
    host.append(random.choice(TLDs))
    return '.'.join(host).lower()
    
def rand_state():
    """Returns a random US state name"""
    return random.choice(States)
    
def rand_surname():
    """Returns a random last name"""
    return random.choice(Surnames)
    
def rand_name():
    """Returns a random male or female name"""
    if random.randrange(10) % 2 == 0:
        return random.choice(Names_Male)
    else:
        return random.choice(Names_Female)
        
def rand_name_male():
    """Returns a random male name"""
    return random.choice(Names_Male)
    
def rand_name_female():
    """Returns a random female name"""
    return random.choice(Names_Female)
    
def rand_mail_address():
    """Returns a random email address"""
    return str(rand_name() + '.' + rand_surname() + '@' + rand_hostname())
    
def rand_guid():
    """Returns a random GUID"""
    return "{" + "{}".format("-".join(map(lambda a: rand_text_hex(a), [8, 4, 4, 4, 12]))) + "}"    

def to_rand_case(string):
    """Randomizes capitalization of a string"""
    buf = []
    for i in range(0, len(string)):
        if random.randrange(2) == 0:
            buf.append(string[i].upper())
        else:
            buf.append(string[i].lower())
    return "".join(buf)
    
