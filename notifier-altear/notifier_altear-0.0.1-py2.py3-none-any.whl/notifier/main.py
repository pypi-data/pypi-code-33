'''
MIT License

Copyright (c) 2019, Andre Telfer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
import click
import json
import logging
import os
import pkg_resources
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#
# Declarations
#
sender = "Notification Bot"
log_file = pkg_resources.resource_filename(__name__, 'resources/notifier.log')
config_path = pkg_resources.resource_filename(__name__, 'resources/config.json')
splash_art = """
               .-'''-.                                       
              '   _    \                                     
   _..._    /   /` '.   \       .--.                         
 .'     '. .   |     \  '       |__|     _.._.-.          .- 
.   .-.   .|   '      |  '  .|  .--.   .' .._|\ \        / / 
|  '   '  |\    \     / / .' |_ |  |   | '     \ \      / /  
|  |   |  | `.   ` ..' /.'     ||  | __| |__    \ \    / /   
|  |   |  |    '-...-'`'--.  .-'|  ||__   __|    \ \  / /    
|  |   |  |               |  |  |  |   | |        \ `  /     
|  |   |  |               |  |  |__|   | |         \  /      
|  |   |  |               |  '.'       | |         / /       
|  |   |  |               |   /        | |     |`-' /        
'--'   '--'               `'-'         |_|      '..'         
"""

#
# Setup
#
logger = logging.getLogger('notifier-altear')
logger.setLevel(logging.DEBUG)

# create log file handler
fh = logging.FileHandler(log_file)
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

# create stream handler (console output)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

# set format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)

logger.info(splash_art)
logger.info(f"Log file being saved to {log_file}")

# load configuration\
def ensure_valid_config(config):
    '''
    Ensure the config dictionary has the required structure

    :param config:
    :return:
    '''

    valid_structure = {
        'username': '',
        'password': '',
        'server': 'smtp.gmail.com',
        'port': 465,
        'recipients': '',
        'subject': '',
        'content': ''
    }
    valid_structure.update(config)
    return valid_structure

def read_config(path):
    '''
    Read the configuration file if it exists, and return a valid config structure

    :param path:
    :return:
    '''
    if os.path.exists(config_path):
        with open(config_path, 'r') as fp:
            config = json.load(fp)
    else:
        config = {}
    return ensure_valid_config(config)

def write_conifg(config, path):
    '''
    Write to the configuration file

    :param config:
    :param path:
    :return:
    '''
    logger.info("Updating config file")
    dir_path = os.path.dirname(path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    with open(path, 'w') as fp:
        json.dump(config, fp, indent=4)

config = read_config(config_path)

#
# Body
#
@click.group(invoke_without_command=True)
@click.pass_context
@click.option('-r', '--recipients', default=config['recipients'], multiple=True, help='The message recipients.')
@click.option('-s', '--subject', default=config['subject'], help='The message subject.')
@click.option('-c', '--content', default=config['content'], help='The message content.')
def cli(ctx, recipients, subject, content):
    '''
    Command group for sending messages.

    By default this will attempt to send a message unless further commands are specified.
    '''

    if ctx.invoked_subcommand is None:
        # connect to email smtp server
        server = smtplib.SMTP_SSL(str(config['server']), int(config['port']))
        server.ehlo()
        server.login(str(config['username']), str(config['password']))

        # construct the message
        notification = MIMEMultipart()
        text = MIMEText(content)
        notification.attach(text)
        notification['Subject'] = subject
        notification['To'] = ', '.join(recipients)
        notification['From'] = sender

        # send the message
        server.send_message(notification)
        logger.info(f"Message sent to {','.join(recipients)}")

@cli.command()
def configure():
    '''
    Set options such as
    - the email account that messages will be sent from
    - the smtp server that messages will be sent from
    - default recipients
    - default message contents
    :return:
    '''
    config['server'] = click.prompt(f'Enter the smtp server', default=config["server"], type=str)
    config['port'] = click.prompt(f'Enter the smtp port', default=config["port"])
    config['username'] = click.prompt( f'Enter the email username for the bot to send notifications from',
        default=config["username"], type=str)
    config['password'] = click.prompt(f'Enter the email password for the bot to send notifications from',
        default=config["password"], type=str)
    while True:
        recipients = click.prompt(f'Enter the default recipients, comma separated', default=config["recipients"])
        if isinstance(recipients, list):
            config['recipients'] = recipients
            break
        elif isinstance(recipients, str):
            config['recipients'] = list(map(lambda x:x.strip(), recipients.split(',')))
            break
        else:
            logger.warning("Could not update recipient list! Please use a comma separated addresses")
    config['subject'] = click.prompt(f'Enter the default message subject', default=config["subject"])
    config['content'] = click.prompt(f'Enter the default message content', default=config["content"])

    if click.confirm("Confirm save?"):
        write_conifg(config, config_path)

