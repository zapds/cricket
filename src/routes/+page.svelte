<script>
	import { Button } from "$lib/components/ui/button";
	import { Input } from "$lib/components/ui/input";
	import { ScrollArea } from "$lib/components/ui/scroll-area";
	import { onMount, onDestroy } from "svelte";

	export let data;


	let worker = null;

	let gameId = null;
	
	let oppScore = 0;
	let oppNick = null;
	let oppId = null;
	
	let myScore = 0;
	let myNick = null;
	let myTurn = false;
	let myId = null;
	
	let stage = "preGame";
	let serverMsg = '';
	let chatInput = '';
	let chatFocus = false;

	let chatMsgs = [
		// {author: 'zap', content: 'hello'},
		// {author: 'zap', content: 'hello world'},
		// {author: 'player2', content: 'hello world'},
	];
	
	if (data.url.searchParams.has('gameId')) {
		gameId = data.url.searchParams.get('gameId');
	}
	onMount(() => {

		
		worker = new Worker(new URL("../../lib/worker.js", import.meta.url));
		worker.postMessage({cmd: "connect"});

		worker.onmessage = (event) => {
			const eData = event.data;
			console.log('recv ', eData);

			if (eData.event == "recv") {
				const data = JSON.parse(eData.data);
				if (data.type == "chatGlobal") {
					chatMsgs = [...chatMsgs, {author: data.author, content: data.content}];
				}

				if (data.type == "gameStarted") {
					const opp = data.opp;
					oppNick = opp.nick;
					oppId = opp.id;
					stage = 'inGame';
					chatMsgs = [...chatMsgs, {author: '[server]', content: `${opp.nick} joined the game`}];
					
				}

				if (data.type == "gameEnded") {
					serverMsg = data.message;
					stage = "postGame"
					chatMsgs = [...chatMsgs, {author: '[server]', content: data.message}];
				}
			}
			
			if (eData.event == "open") {
				chatMsgs = [...chatMsgs, {author: '[server]', content: 'Connected to server'}];
			}

			if (eData.event == "close") {
				chatMsgs = [...chatMsgs, {author: '[server]', content: `Connection closed [${eData.code}]: ${eData.reason}`}];
				serverMsg = `Connection closed [${eData.code}]: ${eData.reason}`
				stage = "postGame"
			}

			if (eData.event == "error") {
				chatMsgs = [...chatMsgs, {author: '[server]', content: 'Connection error'}];
				console.log('ws error: ', eData.obj);
			}

		
		}
 
	})

	function waitForData() {
		return new Promise((resolve) => {
			const listener = (event) => {
				if (event.data.event == "recv") {
					const data = JSON.parse(event.data.data);
					worker.removeEventListener("message", listener);
					resolve(data);
				}
			}
			worker.addEventListener("message", listener);
		});
	}

	function send(data) {
		worker.postMessage({'cmd': 'send', 'msg': JSON.stringify(data)});
	}

	function sendChatMsg(event) {
		event.preventDefault();
		if (!gameId) {
			chatMsgs = [...chatMsgs, {author: '[server]', content: 'Create/join a game to chat!'}];
			return;
		}
		send({
			type: 'chatGlobal',
			content: chatInput,
			author: myNick,
		});
		chatInput = '';
	}

	// async function login() {
	// 	send({
	// 		type: 'login',
	// 		nick: myNick,
	// 		gameSet: false,
			
	// 	});
	// 	const data = await waitForData();
	// 	myId = data.userId;
	// 	serverMsg = data.message;
	// 	stage = "findGame";
	// 	chatMsgs = [...chatMsgs, {author: '[server]', content: 'Logged in'}];
	// }

	async function handleCreateGame() {
		send({
			type: 'createGame',
			nick: myNick,

		})
		const data = await waitForData();
		serverMsg = data.message;
		gameId = data.gameId;
		myId = data.playerId;
		stage = 'waitingForOpp';
		chatMsgs = [...chatMsgs, {author: '[server]', content: `Game created ${gameId}`}];
	}

	async function handleJoinGame() {
		send({
			type: 'joinGame',
			nick: myNick,
			gameId: gameId,
		})
		const data = await waitForData();
		serverMsg = data.message;

	}
</script>

<div class="absolute z-[100] bg-background rounded-md bottom-0 left-0 flex flex-col justify-end overflow-y-auto {chatFocus ? 'h-72' : 'h-8'} md:h-72 w-screen md:w-96">
	<ScrollArea>
		{#each chatMsgs as msg}
			<div class="text-sm font-light"><span class="font-semibold">{msg.author}: </span>{msg.content}</div>
		{/each}
	</ScrollArea>
	<form on:submit={sendChatMsg}>
		<Input on:focusin={() => chatFocus = true} on:focusout={() => chatFocus = false} class="select-none mt-1" bind:value={chatInput} placeholder="Send a message" />
	</form>
</div>

{#if (stage == 'preGame')}
	<div class="h-screen flex flex-col items-center gap-8">
		<h1 class="text-8xl">Cricket</h1>
		<p>Online multiplayer inspired by the original hand-cricket game.</p>
		<div class="flex flex-col items-center gap-4">
			<Input class="w-min" autofocus bind:value={myNick} placeholder="Nickname" />
			<Button on:click={handleCreateGame} type="submit">Create Game</Button>

		</div>
		<div class="flex flex-col md:flex-row gap-2">
			<Input class="w-min" bind:value={gameId} placeholder="Game ID" />
			<Button on:click={handleJoinGame} type="submit">Join Game</Button>	
		</div>
	</div>
{:else if (stage == 'waitingForOpp')}
	<div class="h-screen flex flex-col items-center gap-8">
		<h1 class="text-8xl">Cricket</h1>
		<p>Online multiplayer inspired by the original hand-cricket game.</p>

		<h2 class="text-4xl font-semibold">Waiting for opponent.</h2>
		<h3 class="text-4xl">Game ID: {gameId}</h3>
		<img alt="game join QR" src="http://api.qrserver.com/v1/create-qr-code/?data={data.url.href}?gameId={gameId}&size=100x100">

	</div>
{:else if (stage == "inGame")}
	<div class="h-screen flex flex-col items-center gap-8">
		<h1 class="text-8xl">Cricket</h1>
		<p>Online multiplayer inspired by the original hand-cricket game.</p>

		<h2 class="text-4xl font-semibold">In Game!</h2>
		<h3 class="text-4xl">Game ID: {gameId}<br>Opponent: {oppNick}<br>Opponent ID: {oppId}</h3>

	</div>

{:else if (stage == "postGame")}
	<div class="h-screen flex flex-col items-center gap-8">
		<h1 class="text-8xl">Cricket</h1>
		<p>Online multiplayer inspired by the original hand-cricket game.</p>

		<h2 class="text-4xl font-semibold">Game Over</h2>
		<h3 class="text-4xl">{serverMsg}</h3>
	</div>

{/if}

