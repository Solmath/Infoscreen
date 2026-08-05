<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import type { BoardConfig, Departure, DeparturesResponse } from './lib/types';
	import DepartureBoard from './DepartureBoard.svelte';

	const POLL_INTERVAL_MS = 30_000;

	let boards = $state<BoardConfig[]>([]);
	let departures = $state<Departure[]>([]);
	let stationErrors = $state<Record<string, string | null>>({});
	let statusMessage = $state<string | null>(null); // null = hide the banner

	async function fetchBoards() {
		const res = await fetch('/api/boards');
		if (!res.ok) throw new Error(`HTTP ${res.status}`);

		const data: { boards: BoardConfig[] } = await res.json();
		boards = data.boards;
	}

	async function fetchDepartures() {
		const stations = [...new Set(boards.map((b) => b.station))];
		if (stations.length === 0) return;

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

	onMount(async () => {
		await fetchBoards();
		fetchDepartures(); // first load, no need to wait for the interval
		intervalId = setInterval(fetchDepartures, POLL_INTERVAL_MS);
	});

	onDestroy(() => clearInterval(intervalId));
</script>

{#if statusMessage}
	<div class="status-banner">{statusMessage}</div>
{/if}

<div class="boards-grid">
	{#each boards as board (board.title ?? board.station)}
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
		grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
		gap: 2rem;
	}
</style>
