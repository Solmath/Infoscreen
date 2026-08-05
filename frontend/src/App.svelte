<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import type { Departure, DeparturesResponse, StationsResponse } from './lib/types';
	import DepartureBoard from './DepartureBoard.svelte';

	const POLL_INTERVAL_MS = 30_000;

	let stations = $state<string[]>([]);
	let departures = $state<Departure[]>([]);
	let statusMessage = $state<string | null>(null); // null = hide the banner

	async function fetchStations() {
		const res = await fetch('/api/stations');
		if (!res.ok) throw new Error(`HTTP ${res.status}`);

		const data: StationsResponse = await res.json();
		stations = data.stations;
	}

	async function fetchDepartures() {
		try {
			const results = await Promise.all(
				stations.map(async (station) => {
					const res = await fetch(`/api/departures?station=${encodeURIComponent(station)}`);
					if (!res.ok) throw new Error(`HTTP ${res.status}`);

					const data: DeparturesResponse = await res.json();
					return { station, data };
				})
			);

			departures = results.flatMap(({ station, data }) =>
				data.departures.map((dep) => ({ ...dep, station }))
			);
			statusMessage = results.some(({ data }) => data.meta.stale)
				? 'Showing last known departures -- EFA is unreachable'
				: null;
		} catch (err) {
			// Leave the last successfully rendered list on screen, just flag it.
			statusMessage = 'Connection issue -- showing last known departures';
			console.error('Poll failed:', err);
		}
	}

	let intervalId: ReturnType<typeof setInterval> | undefined;

	onMount(async () => {
		await fetchStations();
		fetchDepartures(); // first load, no need to wait for the interval
		intervalId = setInterval(fetchDepartures, POLL_INTERVAL_MS);
	});

	onDestroy(() => clearInterval(intervalId));
</script>

{#if statusMessage}
	<div class="status-banner">{statusMessage}</div>
{/if}

<!-- {#each stations as station (station)}
	<DepartureBoard {departures} {station} title={station} />
{/each} -->

<div class="boards-grid">
	<DepartureBoard {departures} station="Dürrlewang" line="U12" title="U12 Dürrlewang" count={5} />
	<DepartureBoard
		{departures}
		station="Rohr"
		line={['S1', 'S2', 'S3']}
		title="S1/S2/S3 Rohr"
    direction="H"
    count={5}
	/>
	<DepartureBoard
		{departures}
		station="Vaihingen"
		line={['S1', 'S2', 'S3']}
		title="S1/S2/S3 Vaihingen"
    direction="R"
    count={5}
	/>
</div>

<style>
	.status-banner {
		background: #7a1f1f;
		color: #fff;
		padding: 0.75rem 1rem;
		margin-bottom: 1rem;
		border-radius: 4px;
		font-size: 1.1rem;
	}

	.boards-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
		gap: 2rem;
	}
</style>
