from modules.utils import decodeVar
""" 
debugger for the scripts.

NOTE: this does not make sure the script is run properly,
    but only that the keywords are spelled correctly, and
    each command has the required number of keywords,
    which is HANDY.

"""

def debug(code: list) -> bool:
    """ returns true if the script is free of bugs else false """
    
    if not code or code is None: return False      # no pass for empty script

    # define allowed keywords in commands
    val = {
        1: [
            'click', 'open', 'wait', 'key', 'show', 'cmd'
        ],
        2: [
            'left', 'right', 'double',
            'file', 'link',
            'time', 'img', 'key', 'click',
            'type', 'press'
        ],
        3: [
            'coord', 'img'
        ]
    }
    # define positions at which cmd keywords end
    keywEnd = {
        'click': 3,
        'open': 2,
        'wait': 2,
        'key': 2,
        'show': 1,
        'cmd': 1
    }

    # extract keywords from commands
    for command in code:
        firstKeyw = ''
        for idx, keyw in enumerate(command):
            idx += 1       # using 1-based indexing
            if idx == 1: firstKeyw = keyw

            # if cmd was supposed to have a keyword here
            if idx <= keywEnd[firstKeyw]:
                if decodeVar(keyw) not in val[idx]:        # and this is not a keyword
                    return False
            else:   # if cmd was supposed to have a var here
                if not keyw.startswith("<") or not keyw.endswith(">"):
                    return False
            
    return True
