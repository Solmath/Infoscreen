<script lang="ts">
	import type { Departure } from './lib/types';

	interface Props {
		departures: Departure[];
		station?: string | null;
		line?: string | string[] | null;
		direction?: string | null;
		title?: string;
		count?: number;
		error?: string | null;
	}

	let {
		departures,
		station = null,
		line = null,
		direction = null,
		title = '',
		count = Infinity,
		error = null
	}: Props = $props();

	let lines = $derived(line === null ? null : Array.isArray(line) ? line : [line]);

	let filtered = $derived(
		departures.filter(
			(d) =>
				(station === null || d.station === station) &&
				(lines === null || lines.includes(d.line)) &&
				(direction === null || d.direction === direction)
		)
	);
</script>

<div class="board">
	{#if title}<h2>{title}</h2>{/if}
	{#if error}
		<p class="board-error">{error}</p>
	{:else}
		<ul class="departures-list">
			{#each filtered.slice(0, count) as dep, i (i)}
				<li class="departure-row">
					<span class="line">{dep.line}</span>
					<span class="destination">{dep.destination}</span>
					<span class="minutes">{dep.minutes} min</span>
				</li>
			{/each}
		</ul>
	{/if}
</div>

<style>
	.board {
		border: 1px solid #2a2f36;
		border-radius: 8px;
		padding: 1rem 1.5rem;
	}

	.departures-list {
		list-style: none;
		margin: 0;
		padding: 0;
	}

	.departure-row {
		display: flex;
		align-items: center;
		gap: 1.5rem;
		padding: 1rem 0;
		border-bottom: 1px solid #2a2f36;
		font-size: 2rem;
	}

	.departure-row:last-child {
		border-bottom: none;
	}

	.board-error {
		color: #ff6b6b;
		margin: 0;
	}

	.line {
		font-weight: bold;
		width: 4ch;
		color: #ffcc00;
	}

	.destination {
		flex: 1;
	}

	.minutes {
		font-variant-numeric: tabular-nums;
	}
</style>
