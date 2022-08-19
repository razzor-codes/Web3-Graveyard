import sys
import click
import os
import json
import requests
import subprocess
from datetime import datetime


def get_token():
    try:
        with open(os.path.expanduser('~/.graveyard/creds.json'), 'rt') as creds:
            return json.load(creds)['github_auth']
    except FileNotFoundError:
        return None
    except:
        return None

def validate_token(token):
    click.echo('Validating Auth Token!')
    response = requests.get('https://api.github.com/user', headers={
        'Authorization': f'token {token}',
    })
    if response.status_code != 200:
        click.echo(colored(255,0,0,'Invalid token \u26A0'))
        click.echo(f'Reason:{colored(255,0,0,response.text)}')
        sys.exit(0)
    else:
        click.echo(colored(0,255,0,'Validated! \u2713'))
        return response

def fetch_database():
    response = requests.get('https://api.github.com/repos/razzor-codes/Web3-Graveyard/contents/assets/exploit-database.json', headers={
        'Accept': 'application/vnd.github.raw+json',
    })
    if response.status_code != 200:
        sys.exit(0)
    else:
        return json.loads(response.text)

def check_existence(project_name):
    response = requests.get('https://api.github.com/repos/razzor-codes/Web3-Graveyard/contents/assets/exploit-database.json', headers={
        'Accept': 'application/vnd.github.raw+json',
    })
    if response.status_code == 200:
        hacks = json.loads(response.text)
    else:
        click.echo(colored(255,0,0,'Failure Fetching Database \u26A0'))
        sys.exit(0)
    try:    
        keys = list(hacks.keys())
        if project_name.strip() in keys: 
            return True 
        else:
            return False
    except:
        click.echo(colored(255,0,0,'Key Error in Database \u26A0'))
        sys.exit(0)


@click.group()
@click.option('-t','--token', default=get_token(), metavar='', help='Override the saved github auth token.')
@click.pass_context
def cli(ctx, token):
    
    """\033[91mLets make web3 a better place \033[0m \b\n
     Author: \033[94m@razzor_tweet\033[0m"""

    ctx.ensure_object(dict)
    ctx.obj['token'] = token

@cli.command('auth', help='Enter github authentication token')
@click.argument('token')
def auth(token):
     
    file_path = os.path.expanduser('~/.graveyard/creds.json')
    exist = os.path.exists(file_path)

    if not exist:
        os.makedirs(os.path.expanduser('~/.graveyard'))

    validate_token(token)

    with open(os.path.expanduser('~/.graveyard/creds.json'), 'wt') as creds:
        json.dump({
            'github_auth' : token
        }, creds)

    return click.echo(f"{colored(0,255,0,'Token Registerd at')}{file_path} \u2713")

@cli.command('graveOf', help='Get Exploit Details')
@click.argument('project_name')
def hack(project_name):
    
    hacks = fetch_database()
    try:
        hack = hacks[project_name.strip().lower()]
        Date = hack['Date']
        loss = hack['Estimated Loss']
        attacker_addresses = hack["Attacker's Address"]
        attacker_contracts = hack["Attacker's Contract"]
        project_contracts = hack['Project Contracts'].keys()
        postmortems = hack['Postmortem/Analysis']
        PoC = hack['PoC']
        Chain = hack['Chain']
        bug_type = hack['Bug Type'][0]
        project_type = hack['Project Type']
        tags = hack['Tags']
        note = hack['Note'].replace("<br/>","")

        click.echo(colored(255,0,0, project_name.upper() + ' \u26A0'))
        click.echo(f'{colored(0,255,0,"Date")}: {Date}')
        click.echo(f'{colored(0,255,0,"Estimated Loss")}: {loss}')
        click.echo('Attacker(s) Addresses:')
        for cont in attacker_addresses:
            click.echo(colored(0,255,0,'\u2937 '+cont.split("'_blank'>")[1].split('<')[0]))
        
        click.echo('Attacker(s) Contracts:')
        for cont in attacker_contracts:
            click.echo(colored(0,255,0,'\u2937 '+cont.split("'_blank'>")[1].split('<')[0]))

        click.echo('Project Contracts:')
        for cont in project_contracts:
            address = hack['Project Contracts'][cont].split("'_blank'>")[1].split('<')[0]
            click.echo(f"{colored(0,255,0,cont)}: {address}")
        
        click.echo('Postmortem/Analysis:')
        for url in postmortems:
            click.echo(colored(0,255,0,'\u2937 '+url.split("href='")[1].split("' target")[0]))

        click.echo('PoCs:')
        for url in PoC:
            click.echo(colored(0,255,0,'\u2937 '+url.split("href='")[1].split("' target")[0]))

        click.echo(f'{colored(0,255,0,"Chain")}: {Chain}')
        click.echo(f'{colored(0,255,0,"Bug Type")}: {bug_type}')
        click.echo(f'{colored(0,255,0,"Project Type")}: {project_type}')
        click.echo(f'{colored(0,255,0,"Tags")}: {tags}')
        click.echo(f'{colored(0,255,0,"Note")}: {note}')

    except KeyError:
        return click.echo(colored(255,0,0,f'Project {project_name.strip()} Not Found \u26A0'))    
    
@cli.command('update', help='Update database with new hacks')
@click.argument('project_name')
@click.pass_context
def update(ctx, project_name):
    token = ctx.obj['token']

    click.echo(f'{project_name.strip()} already exists in database?')

    exists = check_existence(project_name)

    if exists:
        return click.echo(colored(255,0,0,f'Redundant Project {project_name.strip()} \u26A0'))
    else:
        click.echo(colored(0,255,0,f'{project_name.strip()} does not exist. Good to go! \u2713'))

    if token is None:
        return click.echo(colored(255,0,0,'No authentication token found. Authenticate first \u26A0'))
    else:        
        response = validate_token(token)

    username = json.loads(response.text)['login']

    click.echo('Fork Exists?')
    response = requests.get(f'https://api.github.com/repos/{username}/Web3-Graveyard', headers={
        'Authorization': f'token {token}',
    })

    forkInfo = json.loads(response.text)
    needSync = True
    if response.status_code == 404:
        click.echo(colored(255,0,0,'No Fork Found for Web3-Graveyard. Creating one! \u26A0'))

        tryForking = requests.post('https://api.github.com/repos/razzor-codes/Web3-Graveyard/forks', headers={
        'Accept' : 'application/vnd.github+json',
        'Authorization': f'token {token}',
        })

        if tryForking.status_code != 202:
            click.echo(colored(255,0,0,'Forking Error \u26A0'))
            click.echo(f'Reason:{colored(255,0,0,tryForking.text)}')
            sys.exit(0)
        else:
            click.echo(colored(0,255,0,'Fork Created \u2713'))
            needSync = False

    elif response.status_code == 200:
        if forkInfo['fork'] and forkInfo['parent']['owner']['login'] == 'razzor-codes':
            click.echo(colored(0,255,0,'Fork Exists. Skipping Step! \u2713'))
            click.echo('Should Sync Fork?')
            postdata = '{"branch":"main"}'
            merge_upstream = requests.post(f'https://api.github.com/repos/{username}/Web3-Graveyard/merge-upstream', data=postdata, headers={
                'Accept' : 'application/vnd.github+json',
                'Authorization': f'token {token}'
                })
        else:
            return click.echo(colored(255,0,0,"Unknown fork! Delete any other forks of Web3-Graveyard and try again \u27A0"))

    dir_path = os.path.expanduser('~/.graveyard/Web3-Graveyard')
    exist = os.path.exists(dir_path)
    remoteBase = 'https://github.com/razzor-codes/Web3-Graveyard.git'
    upstream = f'upstream\t{remoteBase} (fetch)'

    if not exist:
        os.makedirs(os.path.expanduser('~/.graveyard'), exist_ok=True)
        subprocess.check_output(["git", "clone", f'https://{token}@github.com/{username}/Web3-Graveyard.git', os.path.expanduser('~/.graveyard/Web3-Graveyard')])
        click.echo(colored(0,255,0,'Set up Local Fork \u2713'))
        current_dir = os.getcwd()
        os.chdir(dir_path)
        subprocess.check_output(['git', 'remote', 'add', 'upstream', remoteBase])
        click.echo(colored(0,255,0,'Added upstream \u2713'))
        os.chdir(current_dir)


    git_uptodate_message = 'This branch is not behind the upstream'
    git_merged = 'Successfully fetched'
    git_merge_conflict = 'There are merge conflicts'
    if needSync:
        if merge_upstream.status_code == 200:
            if git_uptodate_message in merge_upstream.text:
                click.echo(colored(0,255,0,'Fork already synced! \u2713'))
                pass
            elif git_merged in merge_upstream.text:
                click.echo(colored(0,255,0,'Synced Successfully! \u2713'))
                click.echo("Pulling latest code!")
                current_dir = os.getcwd()
                os.chdir(dir_path)
                subprocess.check_output(["git","pull"])
                os.chdir(current_dir)
                click.echo(colored(0,255,0,'Changes Saved! \u2713'))
            else:
                return click.echo(colored(255,0,0,'Problem with merge. Debug merge-stream! \u26A0'))

        elif merge_upstream.status_code == 409 and git_merge_conflict in merge_upstream.text:
            click.echo(colored(255,0,0,f'Merge Conflict \u26A0'))
            click.echo('Attempting Hard Reset')
            current_dir = os.getcwd()
            os.chdir(dir_path)
            remotes = subprocess.check_output(['git','remote','-v']).decode('UTF-8')
            if upstream not in remotes:
                subprocess.check_output(['git', 'remote', 'add', 'upstream', remoteBase])
                click.echo(colored(0,255,0,'Missing Upstream. Added \u2713'))

            subprocess.check_output(['git', 'fetch', 'upstream'])
            subprocess.check_output(['git', 'checkout', 'main'])
            subprocess.check_output(['git', 'reset', '--hard', 'upstream/main'])
            subprocess.check_output(['git', 'push', 'origin', 'main', '--force'])
            click.echo(colored(0,255,0,'Hard Reset Completed \u2713'))
            os.chdir(current_dir)

        else:
            return click.echo(colored(255,0,0,f'Unknown Problem with Merge {merge_upstream.text} \u26A0'))

    else:
        click.echo(colored(0,255,0,'New Fork has been created. Skipping Sync! \u2713'))

    click.echo('\n Submit Details')
    click.echo(colored(0,255,0,' \u2937 Project Name') + f': {project_name}')
    Date = click.prompt(colored(0,255,0,' \u2937 Date')).strip()
    try:
        Date = datetime.strptime(Date, "%d %B %Y")
    except ValueError:
        return click.echo(colored(255,0,0,'Incorrect Date Format. Stick to %d Month %Y (7 July 2022)'))
 
    loss = click.prompt(colored(0,255,0,' \u2937 Estimated Loss')).strip()
    attacker_address = click.prompt(colored(0,255,0,' \u2937 Attacker(s) Addresses')).split(',')
    attacker_contract = click.prompt(colored(0,255,0,' \u2937 Attacker(s) Contracts')).split(',')
    project_contracts_names = click.prompt(colored(0,255,0,' \u2937 Project Contracts Names')).split(',')
    project_contracts_names = [name.strip() for name in project_contracts_names]
    project_contracts_addresses = []
    try:
        for cont_name in project_contracts_names:
            address = click.prompt(colored(0,255,0, f'\t \u2937 {cont_name.strip()}')).strip()
            project_contracts_addresses.append("<a href='" + address + "' target='_blank'>" + address.split('address/')[1] + "</a>")
    except:
        return click.echo(colored(255,0,0,'Invalid Data Provided \u26A0 \nTips:\n1)Addresses must be complete url links from block explorers '))

    postmortems = click.prompt(colored(0,255,0,' \u2937 Postmortems')).split(',')
    PoC = click.prompt(colored(0,255,0,' \u2937 PoC(s)')).split(',')
    Chain = click.prompt(colored(0,255,0,' \u2937 Chain')).strip()
    Bug_Type_Issue = click.prompt(colored(0,255,0,' \u2937 Bug Type')).strip()
    Bug_Type_Image = click.prompt(colored(0,255,0,' \u2937 Image URL highlighting issue')).strip()
    Project_Type = click.prompt(colored(0,255,0,' \u2937 Project Type')).strip()
    Tags = click.prompt(colored(0,255,0,' \u2937 Tags')).split(',')
    Tags = [tag.strip() for tag in Tags]
    Note = click.prompt(colored(0,255,0,' \u2937 Any Additional Note')).strip()

    try: 
        with open(os.path.expanduser('~/.graveyard/Web3-Graveyard/assets/exploit-database.json'), 'rt') as file:
            database = json.load(file)
    except FileNotFoundError:
        return click.echo(colored(255,0,0,'Local Database Missing \u26A0'))
    try:
        database[project_name.strip().lower()] = {
            "Date" : Date,
            "Estimated Loss" : loss,
            "Attacker's Address": [ "<a href='" + address.strip() + "' target='_blank'>" + address.strip().split('address/')[1] + "</a>" for address in attacker_address],
            "Attacker's Contract" : [ "<a href='" + address.strip() + "' target='_blank'>" + address.strip().split('address/')[1] + "</a>" for address in attacker_contract],
            "Project Contracts" : dict(zip(project_contracts_names,project_contracts_addresses)),
            "Postmortem/Analysis" : [ "<a href='" + post.strip() + "' target='_blank'>" + post.strip() + "</a>" for post in postmortems],
            "PoC" : [ "<a href='" + poc.strip() + "' target='_blank'>" + poc.strip() + "</a>" for poc in PoC],
            "Chain" : Chain,
            "Bug Type" : [Bug_Type_Issue, "<br/><img src='" + Bug_Type_Image + "' width='70%' height='30%'/>"],
            "Project Type" : Project_Type,
            "Tags" : Tags,
            "Note" : Note
        }

        with open(os.path.expanduser('~/.graveyard/Web3-Graveyard/assets/exploit-database.json'), 'wt') as file:
            json.dump(database,file, indent=4)

        try:
            current_dir = os.getcwd()
            os.chdir(dir_path)
            subprocess.check_output(['git', 'add', 'assets/exploit-database.json'])
            subprocess.check_output(['git', 'commit', '-m', f'New Hack {project_name.strip()}',f'--author="{username} <>"'])
            subprocess.check_output(['git','push'])
            click.echo(colored(0,255,0,'Pushed Changes to the fork \u2713'))
            os.chdir(current_dir)
        except:
            return click.echo(colored(255,0,0,'Problem with pushing data \u26A0'))

        postdata = '{"title":"' + f'New Hack {project_name.strip()}", "head":"{username}:main","base":"main"'
        pull_request = requests.post(f'https://api.github.com/repos/razzor-codes/Web3-Graveyard/pulls', data=postdata, headers={
            'Accept' : 'application/vnd.github+json',
            'Authorization': f'token {token}'
            })
        
        if pull_request.status_code != 201:
           click.echo(pull_request.text)
           return click.echo(colored(255,0,0,'Pull Request Failed \u26A0'))


        click.echo(colored(0,255,0,'Triggered a pull request \u2713'))

    except:
        return click.echo(colored(255,0,0,'Invalid Data Provided \u26A0 \nTips:\n1)Addresses must be complete url links from block explorers '))

@cli.command('find', help='Find projects with which an address was involved')
@click.argument('address')
def find(address):
    if len(address) != 42:
        return click.echo(colored(255,0,0,'Unknown address format \u26a0'))

    hacks = fetch_database()
    Projects = []
    for hack in hacks.keys():
        for attacker in hacks[hack]["Attacker's Address"] + hacks[hack]["Attacker's Contract"] + list(hacks[hack]['Project Contracts'].values()):
            if address.lower() in attacker.lower():
                if hack not in Projects:
                    Projects.append(hack)
    if Projects:                
        return click.echo(colored(0,255,0,f'Found involved with {Projects}'))
    else:
        return click.echo(colored(255,0,0,'Not Found in the database. Mind adding it'))

@cli.command('range', short_help='Find project in range')
@click.option('-s', '--start', metavar= "",default= "1 January 2020",help='Start date')
@click.option('-e', '--end', metavar= "", default="31 December 2023",help='End date')
def range(start, end):
    """
    Find hacks happened within a given range \b \n
    \033[91mExample: \033[0m \n 
    python3 gravedigger.py range -s "1 August 2022" -e "7 August 2022"
    """
    hacks = fetch_database()
    try:
        start = datetime.strptime(start, "%d %B %Y")
        end = datetime.strptime(end, "%d %B %Y")
    except ValueError:
        return click.echo(colored(255,0,0,'Incorrect Date Format. Stick to %d Month %Y (7 July 2022)'))
    Projects = []
    for hack in hacks.keys():
        date = datetime.strptime(hacks[hack]['Date'], "%d %B %Y")
        if date >= start and date <= end:
            Projects.append(hack)
    
    if Projects:                
        return click.echo(colored(0,255,0,f'The hacks happened within the range are \n {Projects}'))
    else:
        return click.echo(colored(255,0,0,'No hacks found within the selected raange. Pick a different start/end date'))



def colored(r, g, b, text):
    return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(r, g, b, text)

if __name__ == '__main__':
    cli()