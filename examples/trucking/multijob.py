from concurrent.futures import ThreadPoolExecutor
import json
import threading

from docloud.job import JobClient
from docloud.status import JobExecutionStatus
from trucking.model import ProblemEncoder, solution_decoder
from trucking.factory import ProblemFactory



class CountDownLatch(object):
    """Implements a count down latch."""
    def __init__(self, count=1):
        self.count = count
        self.lock = threading.Condition()

    def count_down(self):
        self.lock.acquire()
        self.count -= 1
        if self.count <= 0:
            self.lock.notifyAll()
        self.lock.release()

    def await(self):
        self.lock.acquire()
        while self.count > 0:
            self.lock.wait()
        self.lock.release()
        
        
class ControllerMultiJob:
    """ This controller submit single job asynchronously. """
    def __init__(self, url, api_key, concurrent_jobs):
        """ Creates a new controller to submit job asynchronously.
        
        Args:
            url: The DOcloud url.
            api_key: The DOcloud api key.
            concurrent_jobs: The number of concurrently submitted jobs.
        """
        self.nb_threads = concurrent_jobs
        self.client = JobClient(url, api_key)
        
        # This is the opl model file
        self.mod_file = "models/truck.mod"
        # The executor
        self.executor = ThreadPoolExecutor(self.nb_threads)
        
    def shutdown(self):
        self.executor.shutdown()

    def submitJob(self, pb, responses, latch):
        """Asynchronously submits a single job.
        
        Once the job has finished running, the latch is decreased.
        
        Args:
            pb: The ``Problem`` to submit and run.
            responses: A list of responses where the response for this ``pb`` is added.
            latch: The latch to decrease once the ``Problem`` has been solved.
        """
        def submitAndCountdown(pb, responses, latch):            
            # Encodes the problem using the specified encoder (which extends 
            # json.JSONEncoder)
            data = json.dumps(pb, cls=ProblemEncoder).encode('utf-8') 
            print("Running %s" % pb.problem_id)    
            resp = self.client.execute(input=[{'name': "truck.mod",
                                               'filename': self.mod_file},
                                              {'name': "truck.json",
                                               'data': data}],
                                       gzip=True,
                                       load_solution=True,
                                       delete_on_completion=True,
                                       parameters={'oaas.client.problem.id': pb.problem_id})
            responses.append(resp)
            latch.count_down()
        self.executor.submit(submitAndCountdown, pb, responses, latch)

if __name__ == '__main__':
    url = "Paste your base URL"
    api_key = "Paste your api key"
    # Number of jobs to be submitted
    NB_JOBS = 5
    # Number of jobs submitted concurrently
    NB_CONCURRENT = 3
    # Creates the ControllerLauncherTest
    ctrl = ControllerMultiJob(url, api_key, NB_CONCURRENT)
    
    # Holds the results
    responses = []
    
    # Latch used to know when all the jobs are processed
    latch = CountDownLatch(NB_JOBS)
    
    # The factory is used to generate problems with random shipments
    pbFactory = ProblemFactory()
    
    # Creates and submits all jobs to server
    for i in range(NB_JOBS):
        problem_id = "Problem #%d" % i
        print("Creating and submitting problem {0}".format(i))
        pb = pbFactory.createProblemWithRandomShipments(1, 300 + i * 50, 100 + i * 20)
        pb.problem_id = problem_id
        ctrl.submitJob(pb, responses, latch)
        
    # Waits for all jobs to complete
    latch.await()
    
    # Processes responses
    for resp in responses:
        problem_id = resp.job_info["parameters"]["oaas.client.problem.id"]
        if resp.execution_status is JobExecutionStatus.PROCESSED:
            solution = json.loads(resp.solution.decode("utf-8"),
                                  object_hook=solution_decoder)
            print("{0} --> TOTAL COST = {1}".format(problem_id, solution.result))
        elif resp.execution_status is JobExecutionStatus.FAILED:
            message = resp.job_info["failure"]["message"]
            print("{0} --> FAILED = {1}".format(problem_id, message))

    
    ctrl.shutdown()
