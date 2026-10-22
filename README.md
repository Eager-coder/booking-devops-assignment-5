# Room booking research CI/CD
Assignment 5 · Sultan Turan · CSE-2502M

A small continuation of the [Assignment 3 CSV tool](https://github.com/Eager-coder/scientific-csv-summary-assignment-3), supporting the university room-booking pilot described in Assignment 4. The project summarises **synthetic** booking durations; it is not the full booking service and does not measure occupancy or utilisation.

## Run and test
Python 3.12; standard library only.

```sh
python3 -m unittest discover -s tests -v
python3 summary.py data/bookings.csv --column duration_minutes --output result.json
docker build -t booking-analysis:local .
docker run --name booking-example booking-analysis:local
docker cp booking-example:/tmp/result.json ./result.json
docker rm booking-example
```

Expected: 5 bookings, mean 72 minutes, median 60, min 30, max 120, sample SD approximately 34.2053 minutes. JSON includes the SHA-256 of the original CSV. No personal records are included. The generic numeric processor accepts negative values; a real booking export must separately validate positive durations and booking status. It rejects invalid/nonfinite values, duplicate headers, extra fields, and fewer than two observations. Tests cover those cases, CLI failures, source-file protection and known results.

## Start Jenkins
Docker Desktop with Compose is required. Ports 8085 and 8086 must be free.

```sh
python3 -c 'import secrets; from pathlib import Path; p=Path(".env"); p.write_text("JENKINS_ADMIN_PASSWORD="+secrets.token_urlsafe(24)+"\n"); p.chmod(0o600)'
docker compose up -d --build
```

Open http://localhost:8085 and log in as `student`, using the password in your local `.env`. Never commit this file. Wait for Jenkins to finish starting. The bootstrap script creates the `booking-analysis` Pipeline from SCM using this repository's `main` branch and `Jenkinsfile`. Click **Build Now** once to register its trigger.

Jenkins checks GitHub once per minute. Subsequent pushed commits trigger CI automatically while Jenkins is running. Local unpushed commits cannot trigger a remote SCM build. When polling groups commits, `scripts/test-commits.sh` runs the unit suite against **each commit since the last successful build** before building the latest image. An uncorrected failed intermediate commit requires a deliberate history correction or baseline reset; it is not silently skipped. The initial build tests the checked-out commit.

Pipeline stages:
1. Unit tests: nine tests, including invalid-input subcases, in the pinned Python container.
2. Build Docker image: digest-pinned base, non-root runtime user, full Git SHA image tag and revision label.
3. Reproduce analysis: execute the image and archive JSON, Git SHA and local image ID.
4. Deploy to local test server: start the same image serving the generated JSON on http://localhost:8086/result.json and check its count and mean over HTTP.

The test container is the optional CD demonstration. It is replaced only after preceding stages pass. Replacement has a short outage and no automatic rollback; for a failed deployment, inspect the console and redeploy a prior successful SHA using the run command in the Jenkinsfile. This is a local test service, not a production server.

## Local lab boundary and cleanup
Jenkins is bound to loopback and requires login. It runs as root with the Docker socket to keep this single-user lab small; trusted pipeline code can control the Docker host. Do not expose it publicly or execute untrusted pull requests. A shared installation should use isolated agents and narrower permissions. No registry push, cloud resources, Kubernetes cluster, or GitHub Actions substitution is required.

```sh
docker compose down
docker rm -f assignment5-test
```

Jenkins history stays in the named Compose volume. The Python base is pinned by manifest digest; record actual architecture/Python version for reproduction. Jenkins and plugin tags resolve at setup time and may change. Research reproducibility also needs unchanged input bytes, correct units and valid interpretation; containers alone cannot establish validity.

## Submission
Reports are in `submission/`; actual Jenkins screenshots and build logs are in `evidence/`. Refer to the practical report for the demonstrated builds. The initial setup script and Compose file reproduce the job on another Docker host. The reused CSV implementation and seven original test methods retain their MIT license; two booking-specific test methods and the Docker/Jenkins workflow were added for Assignment 5.

## Verified environment
The demonstration on 22 October 2026 used Jenkins 2.580.1, Docker Engine 29.8.2 (arm64), and Python 3.12.15 inside the pinned image. The reference CSV has SHA-256 `008e253486ccc71feddf9fa48bcbeee353e319b0d3c803f8f2251673f43a291d`. Re-running on another architecture may select a different platform image from the same pinned multi-platform manifest.
