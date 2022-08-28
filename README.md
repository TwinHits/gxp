** Local **
To develop locally:
Install pipenv
pipenv install
pipenv shell
python manage.py runserver

** Deployment **
https://aws.github.io/copilot-cli/docs/manifest/overview/
The AWS Stack is managed using AWS Copilot.
Use AWS Copilot CLI for changes
Deploy using `copilot deploy`

** Adding Dependencies **
Install dependencies using `pipenv install <package>`
Do not use a requirements.txt file
Tag packages at explicit versions using ==

