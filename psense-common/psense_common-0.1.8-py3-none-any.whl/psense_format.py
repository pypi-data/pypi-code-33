from datetime import datetime
import re


class psense_exp_title:
    def __init__(self):
        # process experiment Information
        self.typeof_study = dict({
            'H': 'Clinical',
            'A': 'Pre-Clinical',
            'F': 'Flow System',
            'B': 'Beaker'
        })

        self.typeof_sensor = dict({
            'G': 'Glucose',
            'O': 'Oxygen',
            'L': 'Lactate',
            'K': 'Ketone',
            'T': 'Temperature',
            'X': 'Other'
        })
        self.typeof_electrode = dict({
            'C': 'Circular',
            'R': 'Rectangular',
            'O': 'Other'
        })
        self.typeof_stack = dict({
            'R': 'Ring',
            'P': 'Planar'
        })
        self.typeof_process = dict({
            'S': 'Standard',
            'V': 'Volcano'
        })
        self.typeof_extras = dict({
            'C': 'Catalase',
            'P': 'Peroxidase',
            'X': 'None'
        })

    def decode(self, expid):
        res = []
        try:
            regions = expid.upper().split('-')

            # simple validation
            for i in range(len(regions), 5):
                regions.append('')

            if len(regions[0]) > 4:
                study = dict({
                    'start': datetime.strptime('{}-{}-{}'.format(regions[0][:2], max(ord(regions[0][2:3]) - 64, 1), max(1, int(regions[0][3:5]))), '%y-%m-%d').date().isoformat(),
                    'type': self.typeof_study.get(regions[0][5:6]),
                    'run': regions[0][7:9],
                    'device': regions[0][9:]
                })
            else:
                study = []

            if len(regions[2]) > 0:
                sensor = dict({
                    'code': '{}-{}-{}'.format(regions[1], regions[2], regions[3]),
                    'type': self.typeof_sensor.get(regions[4][:1]),
                    'vsn': regions[4][1:3],
                    'electrode': self.typeof_electrode.get(regions[4][3:4]),
                    'stack': self.typeof_stack.get(regions[4][4:5]),
                    'process': self.typeof_process.get(regions[4][5:6]),
                    'extras': self.typeof_extras.get(regions[4][6:7], regions[4][6:7])
                })
            else:
                sensor = []

            res = dict(study=study, sensor=sensor)
        except:
            pass

        return res


"Simple IO Functions"


def yn_input(message, default='y'):
    "collect a yes/no answer from input"
    choices = 'Y/n' if default.lower() in ('y', 'yes') else 'y/N'
    choice = input("{} ({}) ".format(message, choices))
    values = ('y', 'yes', '') if choices == 'Y/n' else ('y', 'yes')
    return choice.strip().lower() in values


def answer_input(message, choices, default='0', is_required=True):
    "collect a typed answer from input (regex response validation)"
    is_valid = False

    if isinstance(choices, list):
        while not is_valid:
            choice_str = ", ".join(choices)
            choice = input("%s (%s)".format(message, choice_str)).strip().upper()
            if len(choice) == 0 and not is_required:
                return default
            elif (len(choice) > 0 and choice in choices):
                return choice

            print('Invalid Input')

    elif isinstance(choices, str):
        while not is_valid:
            choice = input(message).strip().upper()
            if len(choice) == 0 and not is_required:
                return default
            elif (len(choice) > 0 and
                  choice in str(re.search(r'{}'.format(choices.upper()), choice))):

                return choice

            print('Invalid Input')

    assert(False)


def exptype_input():
    "selection of experiment type"
    message = '\nSelect experiment type and press enter\n\t[1] Start a new sensor (default)\n\t[2] Resume an existing sensor\n > '
    isvalid = False
    while not isvalid:
        choice = input(message).strip()
        if choice is '':
            return True
        elif choice.isnumeric():
            choice = int(choice)
            if choice == 2:
                return False
            else:
                return True
        else:
            print('Invalid input.')


def setup_new_experiment(device):
    "generate a new experiment id"
    assert isinstance(device, str), "device must be of type string"

    exp_beaker = answer_input(
        'Specify the test system [B1]: ', '([BF][0-9]|AN|HU){1}', 'ZZ', True)
    exp_run = int(answer_input('Specify the run number [1]: ', '[0-9]{1}', 1, False))
    exp_lot_we = int(answer_input('WE Lot # (required): ', '[0-9]{1,4}', 1, True))
    exp_lot_re = int(answer_input('CE/RE Lot # [000]: ', '[0-9]{0,3}', 0, False))
    exp_lot_sn = answer_input('Sensor ID [00]: ', '[A-Z0-9]{0,2}', '00', False)
    exp_type = answer_input(
        'Sensor Type ([G]lucose, (O)xygen, (L)actate, (K)etone, (T)emp)', '[GOLKT]', 'G', False)
    exp_vsn = int(answer_input(
        'VSN Substrate Design ([1], 9, etc)', '[0-9]{1,2}', '1', False))

    exp_discs = input('Circular electrodes (vs. Rectangular)? [Y/n]').strip().upper()
    if not(exp_discs == 'N' or exp_discs == 'NO'):
        exp_discs = 'C'
    else:
        exp_discs = 'R'
    exp_planar = input('Planar substrate (vs. Ring)? [Y/n]').strip().upper()
    if not(exp_planar == 'N' or exp_planar == 'NO'):
        exp_planar = 'P'
    else:
        exp_planar = 'R'
    exp_volcano = input('Volcano process (vs Standard)? [Y/n]').strip().upper()
    if not(exp_volcano == 'N' or exp_volcano == 'NO'):
        exp_volcano = 'V'
    else:
        exp_volcano = 'S'
    exp_addendum = input('Additional Flag (1 character) [X]').strip().upper()
    if len(exp_addendum) == 0:
        exp_addendum = 'X'
    elif len(exp_addendum) > 1:
        exp_addendum = string(exp_addendum)[0]

    expid = '{}{}{}{}{:02d}{:0>3.3}-{:04d}-{:03d}-{:.2}-{}{:02d}{}{}{}{}'.format(
        datetime.now().strftime('%y'),
        chr(int(datetime.now().strftime('%m')) + 64),
        datetime.now().strftime('%d'),
        exp_beaker,
        exp_run,
        device,
        exp_lot_we,
        exp_lot_re,
        exp_lot_sn.zfill(2),
        exp_type,
        exp_vsn,
        exp_discs,
        exp_planar,
        exp_volcano,
        exp_addendum).strip().upper()

    print('> done with data input. ')
    print('Experiment ID: {}'.format(expid))

    return expid
