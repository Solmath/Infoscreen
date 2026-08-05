export interface RawDeparture {
	line: string;
  destination: string;
	direction: string;
	minutes: number;
}

export interface Departure extends RawDeparture {
	station: string;
}

export interface DeparturesResponse {
	departures: RawDeparture[];
	meta: { stale: boolean };
}

export interface StationsResponse {
	stations: string[];
}
