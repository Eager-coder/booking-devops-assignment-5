import jenkins.model.Jenkins
import hudson.security.HudsonPrivateSecurityRealm
import hudson.security.FullControlOnceLoggedInAuthorizationStrategy
import org.jenkinsci.plugins.workflow.job.WorkflowJob
import org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition
import hudson.plugins.git.GitSCM

def j = Jenkins.get()
def realm = new HudsonPrivateSecurityRealm(false)
realm.createAccount('student', System.getenv('JENKINS_ADMIN_PASSWORD'))
j.setSecurityRealm(realm)
def auth = new FullControlOnceLoggedInAuthorizationStrategy()
auth.setAllowAnonymousRead(false)
j.setAuthorizationStrategy(auth)
j.setNumExecutors(1)
  def job = j.getItem('booking-analysis') ?: j.createProject(WorkflowJob, 'booking-analysis')
  def scm = new GitSCM('https://github.com/Eager-coder/booking-devops-assignment-5.git')
  scm.getBranches().get(0).setName('*/main')
  job.setDefinition(new CpsScmFlowDefinition(scm, 'Jenkinsfile'))
  job.save()
j.save()
