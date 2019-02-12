
import json

name = 'ringcentral_bot_framework_extension_botinfo'

def botGotPostAddAction(
  bot,
  groupId,
  creatorId,
  user,
  text,
  dbAction,
  handledByOtherExtension
):
  """
  bot got group chat message: text
  bot extension could send some response
  return True when bot send message, otherwise return False
  """
  if handledByOtherExtension or not f'![:Person]({bot.id})' in text:
    return False

  if f'![:Person]({bot.id}) bot info' == text:
    botInfo = bot.platform.get('/restapi/v1.0/account/~/extension/~')
    txt = json.loads(botInfo.text)
    txt = json.dumps(txt, indent=2)
    msg = f'![:Person]({creatorId}) bot info json is:\n' + txt

    bot.sendMessage(
      groupId,
      {
        'text': msg
      }
    )
    return True
  else:
    return False