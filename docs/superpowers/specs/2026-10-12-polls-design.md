# swe1-app implementation design

## Assignment and outcome

Complete Django 5.2 tutorial Parts 1–4, including the final generic views, and publish the working polls application in the student's personal AWS account. Commit the code to a personal GitHub repository named `swe1-app`. The two submission links must be accessible to the course team.

## Scope and structure

Use one Django project (`mysite`) and one app (`polls`). Keep the tutorial's Question and Choice models, admin registration, migrations, URL namespace, and index/detail/results templates. Use straightforward English pages and a small shared stylesheet. Avoid extra frameworks and unrelated features.

Public flow: `/polls/` lists questions; a question page displays choices; a POST with a CSRF token records a vote using a database-side increment; the response redirects to the results page. Missing questions return 404. A submission without a valid choice redisplays the form with a helpful error. `/` redirects to `/polls/`. Admin remains available for the owner to manage questions.

Provide an idempotent management command to create a sample question and choices. It must not reset existing votes. Do not invent personal information, author declarations, or a history of work.

## Deployment

Pin Django within the 5.2 release series and use a compatible supported Python platform. Include dependencies, an Elastic Beanstalk WSGI configuration, static file configuration, and instructions for migrations and sample data. Read production secrets and allowed hosts from environment variables; require a production secret when debug mode is disabled. Keep credentials and local environments out of Git.

Local development uses SQLite. The recommended deployed database is PostgreSQL with storage independent of application instances, so deployments do not erase questions or votes. Actual database provisioning and deployment configuration depend on the student's existing AWS account and course deployment instructions; do not claim an online application exists before verifying its actual URL.

## Verification and handoff

Verify migrations, Django system checks, listing and detail pages, successful voting, missing-choice errors, invalid question/choice handling, results, sample-data idempotency, and production configuration. Check the actual public website anonymously after deployment. Provide a README for setup/deployment and a Chinese walkthrough explaining models, views, templates, migrations, CSRF, and voting updates so the student can understand and change the implementation.

## External information still needed

Identify the student's GitHub account and AWS account access through existing authenticated tools or user-provided account details. Obtain the course deployment PDF if it imposes requirements beyond the pasted assignment. Never request passwords or access keys in chat. Confirm the actual deadline from the course schedule.

## Alternatives considered

1. Tutorial application plus Elastic Beanstalk and PostgreSQL: recommended for matching the assignment while retaining deployed data.
2. Tutorial application plus a single instance and SQLite: less setup, but instance replacement can lose data; only choose this with an explicit understanding of that limitation and any course guidance.

## Authorship

Keep code clear and explainable. The student should review, run, and make real choices about the application. Do not fabricate commits or claim that assisted work was entirely unaided. Follow the course's actual policy on outside assistance if supplied.
