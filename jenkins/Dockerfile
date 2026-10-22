FROM docker:cli AS dockercli
FROM jenkins/jenkins:lts-jdk21
USER root
COPY --from=dockercli /usr/local/bin/docker /usr/local/bin/docker
RUN jenkins-plugin-cli --plugins workflow-aggregator git pipeline-stage-view
COPY init.groovy /usr/share/jenkins/ref/init.groovy.d/setup.groovy
USER jenkins
