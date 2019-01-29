import json
from pathlib import Path
from gramhopper.configuration import configuration_dir
from gramhopper.handlers.handler import Handler
from gramhopper.responses import Responses
from gramhopper.triggers import Triggers


with open(Path(configuration_dir(), 'users.json'), 'r') as users_file:
    users = json.load(users_file)

hearts = ['❤', '💛', '💚', '💙', '💜', '🖤']
COOP_GIF_URL = 'https://media.giphy.com/media/3o6Zt9bsidO7reLQPe/giphy.gif'
palti_reactable_adjectives = ['יפה', 'מושלם', 'נהדר']
palti_you_are_regex = '^(?:' + 'זה ' + ')?(' + '|'.join(palti_reactable_adjectives) + ')$'
whorehouses_inputs = ['ביטוח לאומי', 'שלישות', 'משא"ן', 'בית זונות', 'דואר ישראל', 'רכבת ישראל', 'הגנ"ק', 'משו"ב', "מחנה ידין"]
# Reaction is sampled uniformly from this list. Repetition is used to change each reaction's probability.
whorehouses_replies = (['1500 שקל קנס'] * 4) + ['#להפריט']

rule_handlers = [
    Handler(Triggers.text.has_exact_word('סתום'), Responses.preset.reply('גום')),
    Handler(Triggers.text.has_exact_word('גום'), Responses.preset.reply('סתום')),
    Handler(Triggers.text.has_exact_word(['Yafe', 'yafe']), Responses.preset.reply('רמאי מסריח')),
    Handler(Triggers.text.has_substring(hearts), Responses.preset.message(hearts)),
    Handler(Triggers.text.has_substring(whorehouses_inputs), Responses.preset.reply(whorehouses_replies)),
    Handler(Triggers.text.regexp('^(לול)$'), Responses.preset.document(COOP_GIF_URL), probability=0.3),
    Handler(Triggers.text.regexp(palti_you_are_regex), Responses.match.message('אתה {0}'), probability=0.4),
    Handler(Triggers.filter.user(users['palti']) & Triggers.text.regexp('^(חח)$'), Responses.preset.reply('בטח אתה כותב לי שני ח\' יא זונה קטנה')),
    Handler(Triggers.filter.user(users['ravid']) & Triggers.filter.video_note, Responses.preset.message('#רביד_מסריטה')),
    Handler(Triggers.event_streak(counting_event_trigger=Triggers.filter.user(users['palti']),
                                  resetting_event_trigger=None,
                                  streak_timeout_sec=60,
                                  event_count=5),
            Responses.preset.message('יואווו פלטי סתום כבר סתוםםם')),
]
