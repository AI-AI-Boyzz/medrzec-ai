<script lang="ts">
	const API_BASE_URL = 'http://127.0.0.1:8000';

	interface Message {
		text: string;
		outgoing: boolean;
	}

	let chat_id: string | null = null;
	let messages: Message[] = [];
	let input = '';

	async function startChat(): Promise<[string, string]> {
		const response = await fetch(`${API_BASE_URL}/start-chat`, { method: 'POST' });
		const json = await response.json();
		return [json['chat_id'], json['message']];
	}

	async function sendMessage(chat_id: string, user_message: string): Promise<string[]> {
		const response = await fetch(`${API_BASE_URL}/send-message`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ chat_id, user_message })
		});

		const json = await response.json();
		return json['messages'];
	}

	async function onStart() {
		const result = await startChat();
		chat_id = result[0];
		messages.push({ text: result[1], outgoing: false });
		messages = messages;
	}

	async function onSubmit() {
		let trimmedInput = input.trim();
		if (trimmedInput === '') return;
		if (chat_id === null) return;

		input = '';
		messages.push({ text: trimmedInput, outgoing: true });
		messages = messages;

		messages.push(
			...(await sendMessage(chat_id, trimmedInput)).map((message) => {
				return { text: message, outgoing: false };
			})
		);
		messages = messages;
	}
</script>

<div class="chat">
	<div class="message-history">
		{#if chat_id === null}
			<button on:click={onStart}>Start!</button>
		{:else}
			{#each messages as message}
				<p class={message.outgoing ? 'outgoing' : 'incoming'}>{message.text}</p>
			{/each}
		{/if}
	</div>
	<form on:submit|preventDefault={onSubmit}>
		<input type="text" bind:value={input} placeholder="Send a message…" />
	</form>
</div>

<style>
	.chat {
		display: flex;
		flex-direction: column;
		justify-content: flex-end;
		width: calc(100% - 4em);
		max-width: 100ch;
		height: calc(100% - 4em);
		padding: 1em;
		border: 0.25rem solid black;
		border-radius: 1em;
		background-color: white;
	}

	.message-history {
		overflow-y: auto;
	}

	p {
		padding: 1em;
		width: fit-content;
		max-width: 75%;
		border-radius: 1em;
		border: 0.125em solid black;
		white-space: pre-wrap;
		overflow-anchor: none;
	}

	.outgoing {
		background-color: #ffdc79;
		margin-left: auto;
	}

	.incoming {
		color: white;
		background-color: #8f73ff;
	}

	input {
		width: 100%;
		padding: 1em;
		border-radius: 1em;
		border: 0.125em solid black;
	}
</style>
