import json

from docloud.job import JobClient

from trucking.model import ProblemEncoder, solution_decoder
from trucking.factory import ProblemFactory

"""This sample demonstrates how you can encode your object model
as JSON and how to decode DOcloud JSON output as objects.
"""
if __name__ == '__main__':
    url = "Paste your base URL"
    api_key = "Paste your api key"
    
    client = JobClient(url, api_key)
    
    factory = ProblemFactory()
    pb = factory.createSampleProblem()

    # encode the problem using the specified encoder (which extends json.JSONEncoder)
    data = json.dumps(pb, cls=ProblemEncoder).encode('utf-8')

    # submit the model truck.mod for execution,
    # using the Problem encoded as JSON for data
    # then download result once the execution is done
    # and finally delete the job
    resp = client.execute(input=["models/truck.mod",
                                 {'name': "truck.json",
                                  'data': data}],
                          output="results.json",
                          gzip=True,
                          load_solution=True,
                          delete_on_completion=True)
    
    # decode the solution using the solution decoder
    result = json.loads(resp.solution.decode("utf-8"),
                        object_hook=solution_decoder)

    result.displaySolution()
