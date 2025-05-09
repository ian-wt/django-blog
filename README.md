# django-blog
[![codecov](https://codecov.io/github/ian-wt/django-blog/graph/badge.svg?token=44P1F40HXX)](https://codecov.io/github/ian-wt/django-blog)

## Setup

To get up and running, follow these steps:

### Configure Environment Variables

Create a .env file in the project root and add the following:

```text
DJANGO_SECRET_KEY=not-a-secure-secret-key
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1,http://0.0.0.0

POSTGRES_REQUIRE_SSL=false
POSTGRES_DB=devdb
POSTGRES_USER=devuser
POSTGRES_PASSWORD=not-a-secure-password
POSTGRES_MIGRATOR=devmigrator
POSTGRES_MIGRATOR_PASS=not-a-secure-password
DB_HOST=db
DB_PORT=5432
DB_ENGINE=django.db.backends.postgresql

```

These values will allow you to begin working in development.

**Important!** Do NOT use in production.

Use Django's get_random_secret_key() function to generate a secure key.

```python
# from a python shell

from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

See [Django Deployment Checklist](https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/#) 
for more information.

Also, the environment variable names are important if you decide to use the postgres image. For example, you need to use:
```text
POSTGRES_PASSWORD
```
Otherwise the db image won't pick up your environment variables.

See [Docker Postgres Docs](https://hub.docker.com/_/postgres) for more information on env vars.

### Configure WSGI -OR- ASGI

By default, this project is set up to deploy as a wsgi application. In development, the native Django development server is used so you get hot reloads and you don't have to restart the server to reflect code changes. In production the application will run on gunicorn. This is conditionally managed with the arg 'DEV=true' in compose.yaml which will override the 'DEV=false' in the Dockerfile. The 'DEV' arg is read in entrypoint.sh and the corresponding server is started.

If you want to build an asgi application, you need to update:

* requirements.txt -> comment out (or remove) gunicorn from requirements.txt and uncomment daphne (assuming you want to use daphne as your asgi server)
* entrypoint.sh -> uncomment the command to start the daphne server and comment out (or remove) the command to start the gunicorn server.
* settings.py && asgi.py -> these files will need additional config; consult Django docs.

### Database

The project is set up to use postgresql by default, even in development. When the database first starts, scripts/init-db.sh will configure the db consistent with the credentials provided in the .env file.

The data is stored on a persistent volume so your dev data will be preserved after you stop your service.

To clear the volume and start with a fresh db you can run:
```bash
docker compose down -v
```

While compose will call scripts/migrate.sh so you don't need to migrate manually, you do still need create your migrations manually with:
```bash
docker compose run app python manage.py makemigrations
```

(assuming your service is named 'app')

Last, the compose call stack also runs a scripts/fixtures.sh (empty by default) where you can drop in fixtures you've registered in your settings.py file. This is convenient for a users.json (or similar) so if you remove your volume, you don't have to start over filling out a user in shell.

### Other Configurations

Both the host port and the container port are configured to run 8000. A default port for the container is provided in entrypoint.sh and there's nothing passed as an environment variable by default since if you're running one server per container, the container port doesn't really matter.

I left a commented section for an environment variable so if you do want to change it, you're making changes in one place:
```yaml
    ports:
      - "8000:8000"
#    environment:
#      - PORT=8000
```

If you want to run a multi-service / multi-server approach, update the left side of the 'ports' mapping to a unique value between services. Ex., start the gunicorn on 8000 & start daphne on 8001.

## Working With CSS

This projects is set up to compile a main.css file using sass. While I still rely on Django's static file management to handle template-specific css, I define standard components and introduce third-party items (Bootstraps grid layout) with sass to make development easy.

To handle sass, I have node installed along with dart-sass in the development builds of both Dockerfiles.

The independent Dockerfiles exist to allow flexibiltiy in development. Use one or the other and specify your choice in compose.yaml.

There are two built-in ways to run dart-sass:

1) Start the process independently and outside the container. eg from the project root start the sass process. The app directory containing the sass is mounted in compose so this process can occur outside the container. Or;

2) Run the process in parallel with the development server from within the container. This is the approach contemplated by the second Dockerfile "Dockerfile.multistage" which has independent stages for production and development. In the development stage, the package/lock.json files are copied in and node/dart-sass are installed. The process is then run from the compose.yaml file. This way, you only need a single terminal to see the log outputs from both the sass process and the development server.

The only adjustment needed to choose between these Dockerfiles is to update compose.yaml in two places.

First, specify which Dockerfile to use by name under build. If you're using the multistage build, you also have to specify a target. In the single stage build this is optional since Docker will run all stages (with the result based on the final stage) without a target specified.

Then, update the command directive to either include the sass process or exclude it. The multistage build should have the sass process included since it installs node and dart-sass.

I've entered both ways. Just comment out the way you don't want to go.

If you're trying to access container logs, either with or without sass, that's:

```bash
docker logs -f <container_name>
```

## Different IDEs

Normally, I use Pycharm which uses a native approach to setting up the python environment in Docker (only in the Professional version of Pycharm I believe).

However, in recent years I (and everyone else) am using a bit more Cursor (VSCode), so I've included a simple dev container setup to work with these IDEs. If you're not in an environment that supports dev containers, just delete the .devcontainers directory. 

Otherwise,you can start your dev container from Cursor / VSCode using:

```bash
CMD + Shift + P
```

And select "Dev Containers: Rebuild and Reopen In Container"

Since the dev containers approach uses the compose.yaml, you'll have the development server already running as well as the sass process going (if you're using the multistage). Open this in a seperate terminal instance since you can't access this from within the container.

Of course, you could always opt for running ```python manage.py runserver``` from within the dev container. You just may have to specify a different port if you don't prevent compose from running it's own server.

