/************************************************************************************

  OPL Model for Trucking Problem

**************************************************************************************/

tuple parameters {
	int maxTrucks;	// Maximum # of trucks for each type on a route
	int maxVolume;	// Maximum Volume of goods that can be handled 
					//  on each path for each type of trucks
}
parameters Parameters = ...;

int MaxTrucks = Parameters.maxTrucks;
int MaxVolume = Parameters.maxVolume;

tuple location {
  key string name;
}
{location} Hubs = ...;
{string} HubIds = {h.name | h in Hubs};

tuple spoke {
  key string name;
  int     minDepTime; // Earliest departure time at spoke 
  int     maxArrTime; // Latest arrive time at spoke
};   

{spoke} Spokes = ...;
{string} SpokeIds = {s.name | s in Spokes};
spoke Spoke[SpokeIds] = [s.name : s | s in Spokes];

// Make sure the data is consistent: latest arrive time >= earliest departure time
assert forall(s in SpokeIds) Spoke[s].maxArrTime > Spoke[s].minDepTime;

tuple truckType {
  key string truckType;
  int   capacity;
  int   costPerMile;  
  int   milesPerHour; //speed
}

{truckType} TruckTypes = ...;
{string} TruckTypeIds = {ttis.truckType | ttis in TruckTypes};
truckType TruckTypeInfos[TruckTypeIds] = [tti.truckType : tti | tti in TruckTypes];

tuple loadTimeInfo {
  key string hub;
  key string truckType;
  int loadTime;
}
{loadTimeInfo} LoadTimes = ...;
int LoadTime[HubIds][TruckTypeIds] = [lt.hub : [lt.truckType : lt.loadTime] | lt in LoadTimes]; // in minutes; loadTime = unloadTime

tuple routeInfo {
  key string   spoke;
  key string   hub;
  int      distance;  // in miles
}
{routeInfo} Routes = ...;

// The following assertion is to make sure that the spoke 
// in each route is indeed in the set of Spokes.
assert forall(r in Routes : r.spoke not in SpokeIds) 1 == 0;

// The following assertion is to make sure that the hub
// in each route are indeed in the set of Hubs.
assert forall(r in Routes : r.hub not in HubIds) 1 == 0;

tuple triple {
  string origin;
  string hub;
  string destination;
}

{triple} Triples =  // feasible pathes from spokes to spokes via one hub  
{<r1.spoke,r1.hub,r2.spoke> | r1,r2 in Routes : r1 != r2 && r1.hub == r2.hub};
 
tuple shipment {
  key string   origin;
  key string   destination;
  int       totalVolume;
}
{shipment} Shipments = ...;

// The following assertion is to make sure that the origin 
// of each shipment is indeed in the set of Spokes.
assert forall(s in Shipments : s.origin not in SpokeIds) 1 == 0;

// The following assertion is to make sure that the destination 
// of each shipment is indeed in the set of Spokes.
assert forall(s in Shipments : s.destination not in SpokeIds) 1 == 0;


// the earliest unloading time at a hub for each type of trucks  
int EarliestUnloadingTime[r in Routes][t in TruckTypeIds] = ftoi(ceil(LoadTime[r.hub][t] +
			Spoke[r.spoke].minDepTime + 60*r.distance/TruckTypeInfos[t].milesPerHour));
// the latest loading time at a hub for each type of trucks
int LatestLoadingTime[r in Routes][t in TruckTypeIds] = ftoi(floor(Spoke[r.spoke].maxArrTime -
			LoadTime[r.hub][t] - 60*r.distance/TruckTypeInfos[t].milesPerHour));

// Compute possible truck types that can be assigned on a route
// A type of truck can be assigned on a route only if it can make it to the hub and back 
//  before the max arrival time at the spoke.
int PossibleTruckOnRoute[r in Routes][t in TruckTypeIds] =  (EarliestUnloadingTime[r][t] < LatestLoadingTime[r][t]) ? 1 : 0;


dvar int+ TruckOnRoute[Routes][TruckTypeIds] in 0..MaxTrucks;

// This represents the volumes shipped out from each hub 
// by each type of trucks on each triple
// The volumes are distinguished by trucktypes because trucks of different types 
// arrive at a hub at different times and the timing is used in defining 
// the constraints for volume availability for the trucks leaving the hub. 
dvar int+ OutVolumeThroughHubOnTruck[Triples][TruckTypeIds] in 0..MaxVolume;

// This represents the volume shipped into each hub by each type of trucks on each triple
// It is used in defining timing constraints. 
dvar int+ InVolumeThroughHubOnTruck[Triples][TruckTypeIds] in 0..MaxVolume;

dexpr float TotalCost = 
  sum(r in Routes, t in TruckTypeIds) 2*r.distance*TruckTypeInfos[t].costPerMile*TruckOnRoute[r][t];
  
minimize TotalCost;

subject to {
  // The # of trucks of each type should be less than "maxTrucks", and if a type of truck 
  // is impossible for a route, its # should be zero 
  forall(r in Routes, t in TruckTypeIds)
    ctMaxTruck: 
      TruckOnRoute[r][t] <= PossibleTruckOnRoute[r][t]*MaxTrucks;

  // On each route s-h, the total inbound volume carried by trucks of each type 
  // should be less than the total capacity of the trucks of this type.
  forall(<s,h,dist> in Routes, t in TruckTypeIds)
    ctInCapacity: 
      sum(<s,h,dest> in Triples) InVolumeThroughHubOnTruck[<s,h,dest>][t] 
         <= TruckOnRoute[<s,h,dist>][t]*TruckTypeInfos[t].capacity;
         
  // On each route s-h, the total outbound volume carried by each truck type should be less than 
  // the total capacity of this type of truck.

  forall(<s,h,dist> in Routes, t in TruckTypeIds)
    ctOutCapacity:      
      sum(<o,h,s> in Triples) OutVolumeThroughHubOnTruck[<o,h,s>][t]
           <= TruckOnRoute[<s,h,dist>][t]*TruckTypeInfos[t].capacity;
   
  // On any triple, the total flows in the hub = the total flows out the hub
  forall (tr in Triples) 
    ctFlow: 
      sum(t in TruckTypeIds) InVolumeThroughHubOnTruck[tr][t]
        == sum(t in TruckTypeIds) OutVolumeThroughHubOnTruck[tr][t];
   
  // The sum of flows between any origin-destination pair via all hubs is equal to the shipment between the o-d pair.
  forall (<o,d,v> in Shipments )
    ctOrigDest: 
      sum(t in TruckTypeIds, <o,h,d> in Triples) InVolumeThroughHubOnTruck[<o,h,d>][t] == v;
   
          
  // There must be enough volume for a truck before it leaves a hub. 
  // In another words, the shipments for a truck must arrive 
  // at the hub from all spokes before the truck leaves.
  // The constraint can be expressed as the following:
  // For each route s-h and leaving truck of type t:
  // Cumulated inbound volume arrived before the loading time of the truck >=
  // Cumulated outbound volume upto the loading time of the truck(including the shipments being loaded).    
  forall (<s,h,dist> in Routes, t in TruckTypeIds)  
    ctTiming: 
      sum (<o,h,s> in Triples, t1 in TruckTypeIds, <o,h,dist1> in Routes :
          // The expression below defines the indices of the trucks unloaded before truck t starts loading.  
          EarliestUnloadingTime[<o,h,dist1>][t1] <= LatestLoadingTime[<s,h,dist>][t]) 
          InVolumeThroughHubOnTruck[<o,h,s>][t1] >=
      sum (<o,h,s> in Triples, t2 in TruckTypeIds, <o,h,dist2> in Routes : 
          // The expression below defines the indices of the trucks left before truck t starts loading.
          LatestLoadingTime[<o,h,dist2>][t2] <= LatestLoadingTime[<s,h,dist>][t]) 
          OutVolumeThroughHubOnTruck[<o,h,s>][t2];
}

/************************************************************
       POST-PROCESSING                                    
*************************************************************/
// Post processing: result data structures are exported as post-processed tuple or tuple sets
// Solve objective value
tuple result {
  float totalCost;
}
result Result = <TotalCost>;

// Number of trucks assigned to each route, for each truck type
tuple nbTrucksOnRouteRes {
  key string	spoke;
  key string	hub;
  key string	truckType;
  int			nbTruck;
}
{nbTrucksOnRouteRes} NbTrucksOnRouteRes = {<r.spoke, r.hub, t, TruckOnRoute[r][t]> | r in Routes, t in TruckTypeIds : TruckOnRoute[r][t] > 0};

// Volume shipped into each hub by each type of trucks and each pair (origin, destination)
tuple volumeThroughHubOnTruckRes {
  key string	origin;
  key string	hub;
  key string	destination;
  key string	truckType;
  int			quantity;
}
{volumeThroughHubOnTruckRes} InVolumeThroughHubOnTruckRes =
	{<tr.origin, tr.hub, tr.destination, t, InVolumeThroughHubOnTruck[tr][t]> | tr in Triples, t in TruckTypeIds : InVolumeThroughHubOnTruck[tr][t] > 0};

// Volume shipped from each hub by each type of trucks and each pair (origin, destination)
{volumeThroughHubOnTruckRes} OutVolumeThroughHubOnTruckRes =
	{<tr.origin, tr.hub, tr.destination, t, OutVolumeThroughHubOnTruck[tr][t]> | tr in Triples, t in TruckTypeIds : OutVolumeThroughHubOnTruck[tr][t] > 0};

tuple aggregatedReport {
  key string spoke;
  key string hub;
  key string truckType;
  int        quantity;
}
{aggregatedReport} InBoundAggregated = {<r.spoke, r.hub, t, sum(tr in Triples : tr.origin == r.spoke && tr.hub == r.hub) InVolumeThroughHubOnTruck[tr][t]> | r in Routes, t in TruckTypeIds : TruckOnRoute[r][t] > 0};
{aggregatedReport} OutBoundAggregated = {<r.spoke, r.hub, t, sum(tr in Triples : tr.destination == r.spoke && tr.hub == r.hub) OutVolumeThroughHubOnTruck[tr][t]> | r in Routes, t in TruckTypeIds : TruckOnRoute[r][t] > 0};
