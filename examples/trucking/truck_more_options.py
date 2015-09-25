from docloud.job import JobClient

if __name__ == '__main__':
    url = "Paste your base URL"
    api_key = "Paste your api key"
    
    client = JobClient(url, api_key)
    
    with open("models/truck.mod", "rb") as modFile:
        resp = client.execute(input=[{"name":"truck.mod",
                                      "file":modFile},
                                     "models/truck.dat"],
                              output="results.json",
                              log="solver.log",
                              gzip=True,
                              waittime=300,
                              delete_on_completion=True)
