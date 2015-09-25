import random
from trucking.model import *

class ProblemFactory(object):
    """Factory class for creation of Problem instances.
    """    
    
    def createProblemMasterData(self, spokeByName):
        """This creates a problem with its master data.
        
        This problem is used as the initial model for the samples.
        """
        pb = Problem()

        A = Spoke("A", 360, 1080)
        B = Spoke("B", 400, 1150)
        C = Spoke("C", 380, 1200)
        D = Spoke("D", 340, 900)
        E = Spoke("E", 420, 800)
        F = Spoke("F", 370, 1070)

        spokes = [A, B, C, D, E, F]
        for s in spokes:
            spokeByName[s.name] = s
        pb.spokes.extend(spokes)
                
        G = Hub("G")
        H = Hub("H")
        
        hubs = [G, H]
        pb.hubs.extend(hubs)

        SmallTruck = TruckType("SmallTruck", 400, 10, 55)
        BigTruck = TruckType("BigTruck", 700, 15, 45)

        truckTypes = [SmallTruck, BigTruck]
        pb.truckTypes.extend(truckTypes)

        loadTimes = [LoadTime(G, SmallTruck, 30),
                     LoadTime(G, BigTruck, 55), 
                     LoadTime(H, SmallTruck, 35),
                     LoadTime(H, BigTruck, 50)]
        pb.loadTimes.extend(loadTimes)

        routes = [
            Route(A, G, 200),
            Route(A, H, 50),
            Route(B, G, 120),
            Route(B, H, 100),
            Route(C, H, 110),
            Route(D, G, 70),
            Route(D, H, 100),
            Route(E, G, 120),
            Route(E, H, 100),
            Route(F, H, 105)
        ]
        pb.routes = routes
        return pb
    
    
    def createSampleProblem(self):
        """This creates a problem with the default master data and a sample
        shipment set.
        """
        spokeByName = {}
        pb = self.createProblemMasterData(spokeByName)

        A = spokeByName["A"]
        B = spokeByName["B"]
        C = spokeByName["C"]
        D = spokeByName["D"]
        E = spokeByName["E"]
        F = spokeByName["F"]

        shipments = [
            Shipment(A, B, 300),
            Shipment(A, C, 250),
            Shipment(A, D, 350),
            Shipment(A, E, 145),
            Shipment(A, F, 300),
            Shipment(B, A, 185),
            Shipment(B, C, 200),
            Shipment(B, D, 221),
            Shipment(B, E, 263),
            Shipment(B, F, 197),
            Shipment(C, A, 143),
            Shipment(C, B, 178),
            Shipment(C, D, 258),
            Shipment(C, E, 221),
            Shipment(C, F, 106),
            Shipment(D, A, 75),
            Shipment(D, B, 135),
            Shipment(D, C, 245),
            Shipment(D, E, 283),
            Shipment(D, F, 155),
            Shipment(E, A, 123),
            Shipment(E, B, 234),
            Shipment(E, C, 143),
            Shipment(E, D, 78),
            Shipment(E, F, 107),
            Shipment(F, A, 201),
            Shipment(F, B, 157),
            Shipment(F, C, 169),
            Shipment(F, D, 212),
            Shipment(F, E, 104),
        ]
        pb.shipments.extend(shipments)
        return pb
    
    
    def createProblemWithRandomShipments(self, seed, mean_qty, standard_deviation):
        """Returns a ``Problem`` instance using a fixed logistic network but
        with randomly generated ``Shipment`` orders.
        
               
        Args:
            seed: Seed for random value generator
            mean_qty: Mean value for generating ``Shipment`` quantities
            standard_deviation: Standard deviation value for generating 
               ``Shipment`` quantities
        Returns:
            The generated ``Problem`` instance
        """
        random.seed(seed)
        spokeByName = {}
        pb = self.createProblemMasterData(spokeByName)
        MIN_QTY = 50
        for source in spokeByName.values():
            for destination in spokeByName.values(): 
                if (source != destination): 
                    quantity = (int)(random.gauss(0,1) *
                                     standard_deviation + mean_qty)
                    quantity = MIN_QTY if quantity < MIN_QTY else quantity
                    pb.shipments.append(Shipment(source, destination, quantity))
        return pb
