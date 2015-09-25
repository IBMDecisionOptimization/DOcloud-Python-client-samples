from docloud.job import JobClient

if __name__ == '__main__':
    url = "Paste your base URL"
    api_key = "Paste your api key"
    
    client = JobClient(url, api_key)
    
    resp = client.execute(input=["models/truck.dat",
                                 "models/truck.mod"],
                          output="results.json")
