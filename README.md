# swe1-app

[![Build status](https://app.travis-ci.com/ailunc/swe1-app.svg?branch=main)](https://app.travis-ci.com/github/ailunc/swe1-app)
[![Coverage Status](https://coveralls.io/repos/github/ailunc/swe1-app/badge.svg?branch=main)](https://coveralls.io/github/ailunc/swe1-app?branch=main)

A small Django polls application based on the official **Django 5.2 tutorial, Parts 1–4**. Visitors can choose a question, vote for an answer, and view the saved results. Django admin provides question and choice management.

## Live application

- [Open the polls application](http://swe1-app-ailunc.us-east-2.elasticbeanstalk.com/polls/)
- [Personal GitHub repository](https://github.com/ailunc/swe1-app)

Deployed on AWS Elastic Beanstalk with Python 3.13 and a private RDS PostgreSQL database. Anonymous access, voting, saved results and static assets were verified on October 13, 2026. Use the HTTP URL shown above; HTTPS is not configured for the default environment hostname.

## Run locally

Python 3.10 or newer is required; Python 3.13 is used for local verification.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_polls
python manage.py runserver
```

Open <http://127.0.0.1:8000/polls/>. The seed command creates one example question and three choices; running it again preserves existing votes.

To manage questions locally:

```bash
python manage.py createsuperuser
```

Then open <http://127.0.0.1:8000/admin/>. When creating a choice, select the question it belongs to. Admin customization beyond the tutorial's basic registration is outside the assignment scope.

## Verify

```bash
python -m pip install -r requirements-dev.txt
python -m black --check .
python -m flake8 .
python -m coverage run manage.py test --noinput
python -m coverage report
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py collectstatic --noinput
```

Tests cover listing, question links, voting, results, invalid selections, missing questions, CSRF enforcement, sample-data preservation, and required production configuration.

## Continuous integration

[Travis build history](https://app.travis-ci.com/github/ailunc/swe1-app) · [Coveralls reports](https://coveralls.io/github/ailunc/swe1-app)

`.travis.yml` runs Black, flake8, Django checks, and the test suite under coverage.py for pushes and pull requests. A formatting, lint, or test failure fails the build. The coverage report is uploaded to Coveralls. There is no minimum coverage percentage for this assignment.

Successful builds on `main` deploy to the existing `swe1-app-env` environment in `us-east-2`. Pull requests and other branches run the checks without deploying. The deployment ZIP contains only committed files, and Travis waits for Elastic Beanstalk to finish updating. AWS deployment credentials belong in Travis repository settings as hidden, main-only environment variables; database credentials remain in Elastic Beanstalk.

To fix formatting locally, run `python -m black .`, then rerun the checks above. Black and flake8 both use an 88-character line limit.

## Project layout

- `mysite/settings.py`: Django configuration and environment variables.
- `mysite/urls.py`: project routes; `/` redirects to `/polls/`.
- `polls/models.py`: `Question` and `Choice`.
- `polls/views.py`: generic list/detail/results views and the voting handler.
- `polls/templates/polls/`: HTML pages.
- `polls/migrations/`: database schema history.
- `.ebextensions/django.config`: Elastic Beanstalk startup and deployment commands.
- `docs/理解代码.md`: a Chinese walkthrough of the request and voting flow.

## Deploy to AWS Elastic Beanstalk

Use a current **Python 3.13 on Amazon Linux 2023** platform. Choose a single-instance environment for this small assignment rather than adding a load balancer. Review the current AWS account plan and resource costs before creating infrastructure.

The application uses **PostgreSQL in production**. A database outside the application instance preserves polls across deployments and instance replacement. Use a small RDS PostgreSQL instance in the same VPC; restrict its inbound database traffic to the application security group. Do not expose the database publicly. An independent RDS database has its own lifecycle and must be managed separately when cleaning up the application.

Set these environment properties before the first application deployment:

| Property | Value |
| --- | --- |
| `DJANGO_DEBUG` | `false` (also set by the deployment configuration) |
| `DJANGO_SECRET_KEY` | A privately generated random secret, never committed |
| `DJANGO_ALLOWED_HOSTS` | The actual EB hostname, with no `http://`, `https://` or path |
| `DATABASE_URL` | The private PostgreSQL connection URL, with escaped username/password and `?sslmode=require` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Optional; actual scheme and hostname when trusted cross-origin access is needed |
| `DJANGO_HTTPS` | `false` for a plain HTTP endpoint; `true` only after HTTPS is configured |

An EB-attached PostgreSQL database can instead supply `RDS_HOSTNAME`, `RDS_PORT`, `RDS_DB_NAME`, `RDS_USERNAME` and `RDS_PASSWORD`. Review its retention/deletion settings before creating it. The app refuses production startup without a secret and database configuration. `.env.example` lists the settings but is **not loaded automatically**.

`.ebextensions/django.config` sets `mysite.wsgi:application`, collects static files, and runs database migrations and seeding on the deployment leader. WhiteNoise serves the collected CSS and admin assets. Keep the database accessible before deployment commands run.

Two upload methods are supported:

1. Console: upload a ZIP with `manage.py`, `requirements.txt`, `mysite/`, `polls/`, and `.ebextensions/` directly at its root, with no enclosing folder. The generated `dist/swe1-app.zip` uses this layout.
2. EB CLI: install the CLI using the official instructions, run `eb init` inside this repository, select a compatible platform and your region, then create/configure the environment and deploy. Never copy an old tutorial's Python 3.7 platform command.

After deployment, open the exact returned public URL ending in `/polls/` in a private browser session. Choose an answer, submit it, and verify the results. An EC2 health status alone does not prove the polls work.

The default EB hostname may provide HTTP only. Submit the scheme that actually works; do not assume HTTPS works. Configure HTTPS before using admin credentials on the public site. Django's development server is only for local use.

## Assignment submission

For the CI assignment, submit these three URLs on Brightspace:

- [Travis dashboard](https://app.travis-ci.com/github/ailunc/swe1-app)
- [Deployed polls application](http://swe1-app-ailunc.us-east-2.elasticbeanstalk.com/polls/)
- [GitHub repository](https://github.com/ailunc/swe1-app)

Keep the application available until the course team finishes grading. The actual deployed URL must come from the created environment, not from this README's examples.

## References

- [Django tutorial Part 1](https://docs.djangoproject.com/en/5.2/intro/tutorial01/)
- [Django tutorial Part 2](https://docs.djangoproject.com/en/5.2/intro/tutorial02/)
- [Django tutorial Part 3](https://docs.djangoproject.com/en/5.2/intro/tutorial03/)
- [Django tutorial Part 4](https://docs.djangoproject.com/en/5.2/intro/tutorial04/)
- [AWS Django deployment guide](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-django.html)
- [EB CLI installation](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html#eb-cli3-install)
- [Django deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
