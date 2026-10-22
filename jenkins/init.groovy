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
if (j.getItem('booking-analysis') == null) {
  def job = j.createProject(WorkflowJob, 'booking-analysis')
  def scm = new GitSCM('https://github.com/Eager-coder/booking-devops-assignment-5.git')
  scm.setBranches([new hudson.plugins.git.BranchSpec('*/main')])
  job.setDefinition(new CpsScmFlowDefinition(scm, 'Jenkinsfile'))
  job.save()
}
j.save()
