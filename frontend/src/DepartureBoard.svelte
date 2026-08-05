<script lang="ts">
	import type { Departure } from './lib/types';

	interface Props {
		departures: Departure[];
		station?: string | null;
		line?: string | null;
		direction?: string | null;
		title?: string;
	}

	let { departures, station = null, line = null, direction = null, title = '' }: Props = $props();

	let filtered = $derived(
		departures.filter(
			(d) =>
				(station === null || d.station === station) &&
				(line === null || d.line === line) &&
				(direction === null || d.direction === direction)
		)
	);
</script>

{#if title}<h2>{title}</h2>{/if}
<ul class="departures-list">
	{#each filtered as dep, i (i)}
		<li class="departure-row">
			<span class="line">{dep.line}</span>
			<span class="direction">{dep.direction}</span>
			<span class="minutes">{dep.minutes} min</span>
		</li>
	{/each}
</ul>

<style>
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

	.line {
		font-weight: bold;
		width: 4ch;
		color: #ffcc00;
	}

	.direction {
		flex: 1;
	}

	.minutes {
		font-variant-numeric: tabular-nums;
	}
</style>
