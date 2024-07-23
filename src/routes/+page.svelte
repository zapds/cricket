<script>
	import { Button } from "$lib/components/ui/button";
	import { Input } from "$lib/components/ui/input";
</script>


<div class="h-screen flex flex-col items-center mt-24 gap-8">
	<h1 class="text-8xl">Cricket</h1>
	<p>Online multiplayer inspired by the original hand-cricket game.</p>
	<form class="flex flex-col items-center gap-4">
		<Input class="w-min" autofocus placeholder="Nickname" />
		<Button type="submit">Play</Button>

	</form>
</div>