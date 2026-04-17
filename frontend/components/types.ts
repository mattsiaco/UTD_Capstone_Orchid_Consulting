export interface PropertyData {
  yearBuilt:        number | null;
  constructionType: string | null;
  squareFootage:    number | null;
  numBedrooms:      number | null;
  numBathrooms:     number | null;
  numFloors:        number | null;
  roofType:         string | null;
  foundationType:   string | null;
  floodZone:        string | null;
  hazardRiskZone:   string | null;
}

export interface NeighborhoodData {
  medianHouseholdIncome: number | null;
  unemploymentRate:      number | null;
  schoolRatings:         number | null;
  crimeStatistics:       number | null;
  homeownershipRate:     number | null;
}

export interface MarketData {
  populationGrowth:         number | null;
  medianHomeValue:          number | null;
  homePriceAppreciationRate:number | null;
  daysOnMarket:             number | null;
  rentPrices:               number | null;
  zoningInformation:        string | null;
}

export interface EnrichResponse {
  property:     PropertyData;
  neighborhood: NeighborhoodData;
  market:       MarketData;
}
