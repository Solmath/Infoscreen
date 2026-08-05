<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import type { Departure, DeparturesResponse } from './lib/types';
	import DepartureBoard from './DepartureBoard.svelte';

	const POLL_INTERVAL_MS = 30_000;

	interface BoardConfig {
		station: string;
		line?: string | string[];
		direction?: string;
		title?: string;
		count?: number;
	}

	// Each board queries its own station directly -- stations no longer need to be
	// pre-registered in EFA_STATIONS just to appear on screen.
	const boards: BoardConfig[] = [
		{ station: 'Dürrlewang', line: 'U12', title: 'U12 Dürrlewang', count: 5 },
		{ station: 'Rohr', line: ['S1', 'S2', 'S3'], direction: 'H', title: 'S1/S2/S3 Rohr', count: 5 },
		{
			station: 'Vaihingen',
			line: ['S1', 'S2', 'S3'],
			direction: 'R',
			title: 'S1/S2/S3 Vaihingen',
			count: 5
		},
		{ station: 'foobar' }
	];

	const stations = [...new Set(boards.map((b) => b.station))];

	let departures = $state<Departure[]>([]);
	let stationErrors = $state<Record<string, string | null>>({});
	let statusMessage = $state<string | null>(null); // null = hide the banner

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
			stationErrors = Object.fromEntries(
				results.map(({ station, data }) => [station, data.meta.error])
			);
			statusMessage = results.some(({ data }) => data.meta.stale && !data.meta.error)
				? 'Showing last known departures -- EFA is unreachable'
				: null;
		} catch (err) {
			// Leave the last successfully rendered list on screen, just flag it.
			statusMessage = 'Connection issue -- showing last known departures';
			console.error('Poll failed:', err);
		}
	}

	let intervalId: ReturnType<typeof setInterval> | undefined;

	onMount(() => {
		fetchDepartures(); // first load, no need to wait for the interval
		intervalId = setInterval(fetchDepartures, POLL_INTERVAL_MS);
	});

	onDestroy(() => clearInterval(intervalId));
</script>

{#if statusMessage}
	<div class="status-banner">{statusMessage}</div>
{/if}

<div class="boards-grid">
	{#each boards as board (board.title)}
		<DepartureBoard
			{departures}
			station={board.station}
			line={board.line}
			direction={board.direction}
			title={board.title}
			count={board.count}
			error={stationErrors[board.station] ?? null}
		/>
	{/each}
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
