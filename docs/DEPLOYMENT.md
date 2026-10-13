# Deployment record

Verified on October 13, 2026.

- Website: http://swe1-app-ailunc.us-east-2.elasticbeanstalk.com/polls/
- Repository: https://github.com/ailunc/swe1-app
- Region: us-east-2.
- Elastic Beanstalk application: `swe1-app`.
- Environment: `swe1-app-env`, Standard web server, single instance.
- Platform: Amazon Linux 2023 v4.13.10, Python 3.13.
- Application instance: `t3.micro`; no load balancer.
- Database: `swe1-app-db`, RDS PostgreSQL, `db.t4g.micro`, single AZ, 20 GiB gp3, encrypted and not publicly accessible.
- Database access: TCP 5432 from the application security group only.
- Deployed application version: `polls-a2a21708f147`.
- Infrastructure health: Ready / Green / Ok.

## Validation

The source passed 18 automated tests and Django configuration/migration checks. The deployment bundle was validated by Elastic Beanstalk. The actual anonymous public site was opened in a separate browser, a choice was submitted, and the result increased from zero to one vote. The production database is independent of application instance replacement.

## Credentials and access

Production secrets and database credentials are configured privately in AWS. They are not present in this repository or its deployment ZIP. AWS CLI access used a temporary console-based session rather than a new long-term access key. Basic admin registration is included in the code; no public admin password is supplied. Configure HTTPS before using admin credentials on the public site.

## Costs and cleanup

At deployment, the account remained on AWS's free plan. Current AWS list prices for the selected compute instances were $0.0104/hour for EC2 and $0.016/hour for RDS, before storage, public IPv4, other usage, discounts and credits. The application remains running for grading and continues using resources.

Keep the website available until grading is complete. Afterwards, terminate the Elastic Beanstalk environment and separately clean up its independent RDS database, snapshots and deployment storage if no longer needed. Database deletion protection is enabled; review and save any needed data before changing it. Removing the application environment alone does not remove its independent database.
