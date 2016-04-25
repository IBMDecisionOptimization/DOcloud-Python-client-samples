# IBM Decision Optimization on Cloud Python Client samples

IBM Decision Optimization on Cloud (DOcplexcloud) allows you to solve optimization
problems on the cloud without installing or configuring a solver. We handle
the connection so that you can jump into coding faster.

This documentation describes the IBM DOcplexcloud Python Client samples.

The Python Client samples demonstrate how to use the Python Client to submit a problem to the IBM Decision Optimization on Cloud service.

## Requirements

This library requires Python  version 2.7.9 (or later), or 3.4 (or later).

## Install the library

Before you run the samples, you must install the IBM Decision Optimization on Cloud Python Client.

```
    pip install docloud
```

## Sample contents

The sample consists of an archive which contains a directory called `examples` containing subdirectories. The `models/` directory contains the OPL `.dat` and `.mod` files, as well as other models for the examples. The `trucking/`  directory contains the following sample files :
* `truck_basic.py` contains the code for running the basic trucking sample
* `truck_more_options.py` contains the code for running the trucking sample with more options
* `trucking_json.py` contains the code for running the trucking sample with JSON streaming
* `model.py` contains `namedtuples` and classes to define the problem
* `factory.py` contains a problem factory for the samples
* `multijob.py` contains the code for running multiple jobs concurrently using the same model, but with different data.

Additionaly, the `parallel_solve/` directory contains the Parallel Solve example.

## Dependencies

These third-party dependencies are installed with ``pip``
* requests
* enum34
* six

## License

This library is delivered under the  Apache License Version 2.0, January 2004 (see LICENSE.txt).

## To run the basic sample
* Paste your base URL and API Key (clientID) in the `truck_basic.py` file
* In a command prompt, navigate to the `examples` directory that contains the subdirectory `trucking` and type:
`python trucking/truck_basic.py` 

You can see the solution in the `results.json` file. Here is an extract of the sample results:
```
{
  "Result" : {
    "totalCost" : 29750.0
  },
  "OutBoundAggregated" : [ {
    "spoke" : "A",
    "hub" : "H",
    "truckType" : "BigTruck",
    "quantity" : 727
  }, {
    "spoke" : "B",
    "hub" : "H",
    "truckType" : "SmallTruck",
    "quantity" : 335
  }, {
    "spoke" : "B",
    "hub" : "H",
    "truckType" : "BigTruck",
    "quantity" : 669
  }, {
    "spoke" : "C",
    "hub" : "H",
    "truckType" : "SmallTruck",
    "quantity" : 308
  }, {
    "spoke" : "C",
    "hub" : "H",
    "truckType" : "BigTruck",
    "quantity" : 699
  }, 
.
.
.
```  
# To run the sample with more options
* Paste your base URL and API Key (clientID) in the `truck_more_options.py` file
* In a command prompt, navigate to the `examples` directory that contains the subdirectory `trucking` and type:
`python trucking/truck_more_options.py` 

As well as the solution results file, you can also see the log from the solve engine in the `solver.log` file.

## To run the sample with JSON encoding
* Paste your base URL and API Key (clientID) in the `truck_json.py` file
* In a command prompt, navigate to the `examples` directory that contains the subdirectory `trucking` and type:
`python trucking/truck_json.py` 

You can see the solution in the `results.json` file.


## To run multiple job requests from the same model with different data
* If you are using Python 2, install the `futures` package to run this sample. Type:
`   pip install futures`
* Paste your base URL and API Key (clientID) in the `multijob.py` file
* In a command prompt, navigate to the `examples` directory that contains the subdirectory `trucking` and type:
`   python trucking/multijob.py`

## To run the parallel solve example
* This sample shows how you can build a Python application that uses the parallel solve feature of the IBM Decision Optimization on Cloud service. This feature is only available in Reserved Bare Metal subscription.
* If you are using Python 2, install the `futures` package to run this sample. Type:
`   pip install futures`
* Paste your base URL and API Key (clientID) in the `parallel_multi_seed.py` file
* In a command prompt, navigate to the `examples` directory that contains the subdirectory `trucking` and type:
`   python parallel_solve/parallel_multi_seed.py`
 
## Trucking sample project description
A shipping company uses a dispatching system to schedule its truck fleet. The dispatching system collects orders from the order management system, assigns the orders to trucks, and schedules the departures and deliveries. Its functions include generating bills of lading, loading tables, route maps for the drivers' GPS, and departure time-tables. It also updates the order management system with projected delivery windows, which in turn, informs the recipients. Currently, the assignment of orders to trucks, which defines the truck routes, is done heuristically, using a set of business rules that the company has found to be effective in the past. However, the VP of Operations believes that substantial cost savings and on-time performance improvements might be achievable with a more systematic routing algorithm. The company's Operations Research department has created such an algorithm using IBM Decision Optimization on Cloud. The IT department now has been tasked to deploy this routing algorithm integrated in the dispatching system.

A shipping company has a hub and spoke system. The shipments to be delivered are specified by an originating spoke, a destination spoke, and a shipment volume. The trucks have different types defined by a maximum capacity, a speed, and a cost per mile. The model is to assign the right number of trucks to each route in order to minimize the cost of transshipment and meet the volume requirements. There is a minimum departure time and a maximum return time for trucks at a spoke, and a load and unload time at the hub. Trucks of different types travel in different speeds. Therefore, shipments are available at each hub in a timely manner. Volume availability constraints are considered, that is, the shipments that will be carried back from a hub to a spoke by a truck must be available for loading before the truck leaves.

The assumptions are: 
* exactly the same number of trucks that go from spoke to hub return from hub
  to spoke
* each truck arrives at a hub as early as possible and leaves as late as possible
* the shipments can be broken arbitrarily into smaller packages and  shipped through different paths
