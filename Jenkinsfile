pipeline {
    agent any
    options {
        disableConcurrentBuilds()
        timeout(time: 10, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '15'))
    }
    triggers { pollSCM('* * * * *') }
    environment { PYTHON_IMAGE = 'python:3.12-slim@sha256:cb33f7f771ecec2ef1225cf39b159591a040391bd73e4c01f00fdfc4c47611d2' }
    stages {
        stage('Unit tests') {
            steps { sh 'sh scripts/test-commits.sh' }
        }
        stage('Build Docker image') {
            steps {
                sh 'docker build --label org.opencontainers.image.revision=$GIT_COMMIT -t booking-analysis:$GIT_COMMIT .'
            }
        }
        stage('Reproduce analysis') {
            steps {
                sh '''
                    mkdir -p results
                    id=$(docker create booking-analysis:$GIT_COMMIT)
                    trap 'docker rm -f "$id" >/dev/null 2>&1 || true' EXIT
                    docker start -a "$id"
                    test "$(docker inspect -f '{{.State.ExitCode}}' "$id")" = 0
                    docker cp "$id:/tmp/result.json" results/result.json
                    printf '%s\n' "$GIT_COMMIT" > results/commit.txt
                    docker image inspect booking-analysis:$GIT_COMMIT --format '{{.Id}}' > results/image-id.txt
                    cat results/result.json
                '''
            }
        }
        stage('Deploy to local test server') {
            steps {
                sh '''
                    docker rm -f assignment5-test 2>/dev/null || true
                    docker run -d --name assignment5-test -p 127.0.0.1:8086:8000 booking-analysis:$GIT_COMMIT sh -c 'mkdir -p /tmp/report && python summary.py data/bookings.csv --column duration_minutes --output /tmp/report/result.json && exec python -m http.server 8000 --directory /tmp/report'
                    docker exec assignment5-test python -c 'import json,time,urllib.request; time.sleep(2); r=json.load(urllib.request.urlopen("http://127.0.0.1:8000/result.json")); assert r["statistics"]["mean"] == 72; assert r["statistics"]["n"] == 5; print("Deployment smoke test passed: n=5, mean=72 minutes")'
                '''
            }
        }
    }
    post {
        success { archiveArtifacts artifacts: 'results/*', fingerprint: true }
    }
}
