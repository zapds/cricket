// onMount(() => {
		
//     ws = new WebSocket("wss://cricketserver.zapdos.me/");
    
//     ws.onopen = () => {
//         chatMsgs = [...chatMsgs, {author: '[server]', content: 'Connected to server'}];
//     };

//     ws.onmessage = (event) => {
//         const data = JSON.parse(event.data);
//         console.log('recv ', data);
//         if (data.type == "chatGlobal") {
//             chatMsgs = [...chatMsgs, {author: data.author, content: data.content}];
//         }

//         if (data.type == "gameStarted") {
//             const opp = data.opp;
//             oppNick = opp.nick;
//             oppId = opp.id;
//             stage = 'inGame';
//             chatMsgs = [...chatMsgs, {author: '[server]', content: `${opp.nick} joined the game`}];
            
//         }

//         if (data.type == "gameEnded") {
//             serverMsg = data.message;
//             stage = "postGame"
//             chatMsgs = [...chatMsgs, {author: '[server]', content: data.message}];
//         }

//         else 
    
//     }
    
//     ws.addEventListener("close", (event) => {
//         chatMsgs = [...chatMsgs, {author: '[server]', content: `Connection closed [${event.code}]: ${event.reason}`}];
//         serverMsg = `Connection closed [${event.code}]: ${event.reason}`
//         stage = "postGame"

//     })

//     ws.addEventListener("error", (event) => {
//         chatMsgs = [...chatMsgs, {author: '[server]', content: 'Connection error'}];
//         console.log('ws error: ', event);
//     });

// })

let ws = null;

onmessage = (event) => {
    console.log('worker recv')
    cmd = event.data.cmd;

    if (cmd == "connect") {
        ws = new WebSocket("wss://cricketserver.zapdos.me/");
        ws.onopen = () => {
            postMessage({'event': "open"});
        };

        ws.onmessage = (event) => {
            console.log('ws recv ', event.data);
            postMessage({'event': 'recv', 'data': event.data});
        };

        ws.addEventListener("close", (event) => {
            postMessage({'event': "close", 'code': event.code, 'reason': event.reason});
        });

        ws.addEventListener("error", (event) => {
            postMessage({'event': "error", 'obj': event});
        });
    }
    if (cmd == "send") {
        ws.send(event.data.msg);
    }

}