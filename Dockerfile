FROM python:3.10.6

# Copy the code over statically from working directory to freeze the code in it's current state
WORKDIR /gxp
COPY . /gxp

# You need to use --deploy flag, so your build will fail if your Pipfile.lock is out of date
# You need to use --ignore-pipfile, so it won't mess with our setup
# And then prefix all calls to python with pipenv run, e.g. CMD ["pipenv", "run", "python", "hello.py"]
RUN pip install pipenv
RUN ls -la /gxp
RUN pipenv install --deploy --ignore-pipfile

# What to run when docker-compose up is run and the above image is built
CMD ["./entryPoint.sh"]