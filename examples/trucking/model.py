from collections import namedtuple
import json


# tuples to define a problem
Parameters = namedtuple('Parameters', ['maxTrucks', 'maxVolume'])
Location = namedtuple('Location', ['name'])
Hub = namedtuple('Hub', ['name'])
Spoke = namedtuple('Spoke', ['name', 'minDepTime', 'maxArrTime'])
TruckType = namedtuple('TruckType', ['truckType', 'capacity', 'costPerMile', 'milesPerHour'])
LoadTime = namedtuple('LoadTime',['hub', 'truckType', 'loadTime'])
Route = namedtuple('Route', ['spoke','hub','distance'])
Shipment = namedtuple('Shipment', ['origin', 'destination', 'totalVolume'])

class Problem(object):
    """Class used as a container to collect information for a problem
    instance to be processed by the ``truck.mod`` model.
    """
    def __init__(self):
        self.problem_id = None
        self.parameters = Parameters(100, 5000)
        self.hubs = []
        self.spokes = []
        self.truckTypes = []
        self.loadTimes = []
        self.routes = []
        self.shipments = []
 
    
class ProblemEncoder(json.JSONEncoder):
    """A custom encoder to encode the ``Problem`` in JSON.
    
    The default json encoder encodes instances of ``namedtuple`` as list, while
    DOcloud expects model data to be ``dict``.
    
    This custom encoder makes sure that each named tuple is encoded
    as a ``dict`` of (key,value) pairs.
    
    Additionally, for tuples with fields that are foreign keys, we encode
    just the name of the external object instead of the full object.
    """
    def default(self, obj):
        if (isinstance(obj, Problem)):
            def encodeRoute(obj):
                return {'spoke': obj.spoke.name,
                        'hub': obj.hub.name,
                        'distance': obj.distance
                        }
            def encodeLoadTime(obj):
                return {'hub': obj.hub.name,
                        'truckType': obj.truckType.truckType,
                        'loadTime': obj.loadTime
                        }
            def encodeShipment(obj):
                return {'origin': obj.origin.name,
                        'destination': obj.destination.name,
                        'totalVolume': obj.totalVolume
                        }
            # spokes and truckTypes are correctly encoded by just converting
            # the fields into a dict
            return {'Parameters': obj.parameters._asdict(),
                    'Hubs': [h._asdict() for h in obj.hubs],
                    'Spokes': [h._asdict() for h in obj.spokes],
                    'TruckTypes': [h._asdict() for h in obj.truckTypes],
                    'LoadTimes': [encodeLoadTime(h) for h in obj.loadTimes],
                    'Routes': [encodeRoute(h) for h in obj.routes],
                    'Shipments': [encodeShipment(h) for h in obj.shipments]
                    }
        return json.JSONEncoder.default(self, obj)
 

# tuples for post processing (result processing)
Result = namedtuple('Result', ['totalCost'])        
NbTrucksOnRouteRes = namedtuple('NbTrucksOnRouteRes', 
                                ['spoke', 'hub', 'truckType', 'nbTruck'])
VolumeThroughHubOnTruckRes = namedtuple('VolumeThroughHubOnTruckRes',
                                        ['origin', 'hub', 'destination', 'truckType', 'quantity'])
AggregatedReport = namedtuple('AggregatedReport',
                              ['spoke', 'hub', 'truckType', 'quantity'])



class Solution(object):
    def __init__(self, dct):
        self.result = None
        self.nbTrucksOnRouteRes = None
        self.inVolumeThroughHubOnTruckRes = None
        self.outVolumeThroughHubOnTruckRes = None
        self.inBoundAggregated = None
        self.ouBoundAggregated = None
        
        if dct is not None:
            # we need this to help decode named tuples
            def decodeNamedTuple(tuple_name, dct):
                return namedtuple(tuple_name, dct.keys())(*dct.values())         
            # decode all expected fields    
            self.result = decodeNamedTuple('Result', dct['Result'])
            self.nbTrucksOnRouteRes = [decodeNamedTuple('NbTrucksOnRouteRes', x)
                                       for x in dct['NbTrucksOnRouteRes']]
            self.inVolumeThroughHubOnTruckRes = [decodeNamedTuple('VolumeThroughHubOnTruckRes', x)
                                                 for x in dct['InVolumeThroughHubOnTruckRes']]
            self.outVolumeThroughHubOnTruckRes = [decodeNamedTuple('VolumeThroughHubOnTruckRes', x)
                                                  for x in dct['OutVolumeThroughHubOnTruckRes']]
            self.inBoundAggregated = [decodeNamedTuple('AggregatedReport', x)
                                      for x in dct['InBoundAggregated']]
            self.outBoundAggregated = [decodeNamedTuple('AggregatedReport', x)
                                       for x in dct['OutBoundAggregated']]
    

    
    @staticmethod
    def canDecodeFrom(dct):   
        """Returns True if a ``Solution`` can be decoded from the specified
        dict.
        """
        return "Result" in dct 
    
    def printSeparatorLine(self):
        """Utility method to print a line of separators"""
        print("-" * 80)
        
    def displaySolution(self):
        print("Total cost = %f" % self.result.totalCost)
        self.printSeparatorLine()
        for invol in self.inVolumeThroughHubOnTruckRes:
            print("Using: {truckType} \t--> from: {origin} "
                  "to Hub: {hub} (shipment destination: {destination}) --> "
                  "shipped quantity = {quantity}".format(**invol._asdict()))
        self.printSeparatorLine()
        for outvol in self.outVolumeThroughHubOnTruckRes:
            print("Using: {truckType} \t--> from Hub: {hub} "
                  "to: {destination} (shipment source: {origin}) --> "
                  "shipped quantity = {quantity}".format(**outvol._asdict()))
        self.printSeparatorLine()
        for truck in self.nbTrucksOnRouteRes:
            print("{nbTruck} truck(s) of type: {truckType} "
                  "are assigned to route: Spoke {spoke} <--> Hub {hub}"
                  .format(**truck._asdict()))
        self.printSeparatorLine()
        for iba in self.inBoundAggregated:
            print("Aggregated quantity transported from Spoke: {spoke} "
                  "to Hub: {hub} using truck type: {truckType} \t= {quantity}"
                  .format(**iba._asdict()))
        self.printSeparatorLine()
        for oba in self.outBoundAggregated:
            print("Aggregated quantity transported from Hub: {hub} "
                  "to Spoke: {spoke} using truck type: {truckType} \t= {quantity}"
                  .format(**oba._asdict()))
        self.printSeparatorLine()

        


def solution_decoder(dct):
    if Solution.canDecodeFrom(dct):
        return Solution(dct)
    return dct
