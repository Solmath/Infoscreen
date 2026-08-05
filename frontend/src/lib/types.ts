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
	meta: { stale: boolean; error: string | null };
}

export interface StationsResponse {
	stations: string[];
}

export interface BoardConfig {
	station: string;
	line?: string | string[];
	direction?: string;
	title?: string;
	count?: number;
}
