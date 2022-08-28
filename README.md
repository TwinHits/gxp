** GXP ** 
This is the backend REST service for the Guild eXPerience loot system.
Python 3.10.6

** Local **
To develop locally:
1. Install pipenv
2. pipenv install
3. pipenv shell
4. python manage.py runserver

** Deployment **
https://aws.github.io/copilot-cli/docs/manifest/overview/
The AWS Stack is managed using AWS Copilot.
Use AWS Copilot CLI for changes
Deploy using `copilot deploy`

** Adding Dependencies **
- Install dependencies using `pipenv install <package>`
- Do not use a requirements.txt file
- Tag packages at explicit versions using ==

    