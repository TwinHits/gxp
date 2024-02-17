# GXP

This is the backend REST service for the Guild eXPerience loot system.

This loot system was used by <Gather Your Allies> Faerlina-US for the Wrath of the Lich King classic expansion experience.

Members gain GXP during raids, and each lockout rank will be calculated based on the member’s GXP. The intention is that higher ranks get priority on rolling for some gear for Main spec.

GXP supports using Discord's Raid Helper sign ups, attendance, boss kills, specialist roles, food and flask usage, and WarcraftLogs performance to gain GXP.

Every raid, GXP decays so that Raiders can't return at the same rank that they left.

## Local
To develop locally:

### Set up:
1. Install pipenv
2. `pipenv install`
3. Copy `.env_example`, rename to `.env`, and replace `REPLACE_ME` values.

### Start dev server:
1. `pipenv shell`
2. `python manage.py runserver`

## Deployment
https://aws.github.io/copilot-cli/docs/manifest/overview/
The AWS Stack is managed using AWS Copilot.
Use AWS Copilot CLI for changes
Deploy using `copilot deploy`. Mine is currently set up in WSL.
Make sure docker deskop is running.

## Adding Dependencies
- Install dependencies using `pipenv install <package>`
- Do not use a requirements.txt file
- Tag packages at explicit versions using ==
