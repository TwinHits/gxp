# GXP
This is the backend REST service for the Guild eXPerience loot system.

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

## Adding Dependencies
- Install dependencies using `pipenv install <package>`
- Do not use a requirements.txt file
- Tag packages at explicit versions using ==