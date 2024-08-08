from aiohttp import web
import aiohttp
import asyncio
import async_timeout
import os
import json


globalLobby = []

games = {}


class Player:
    def __init__(self, id, ws, nick, game):
        self.id = id
        self.ws = ws
        self.nick = nick
        self.game = game

    def __eq__(self, other):
        return self.id == other.id
    
    def to_json(self):
        return {"id": self.id, "nick": self.nick}
    

class Game:
    def __init__(self, id, player1, player2=None):
        self.id = id
        self.player1 = player1
        self.player2 = player2
        self.players = [player1, player2] if player2 else [player1]

    def __eq__(self, other):
        return self.id == other.id
    
    async def handle_msg(self, data, player):
        pass

    def other(self, player):
        if player == self.player1:
            return self.player2
        else:
            return self.player1
    


async def handler(request):
    print("New websocket connection")
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    player = None
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            try:
                data = json.loads(msg.data)
            except:
                await ws.send_json({"error": "Invalid JSON"})
                continue
            print("Received message: ", msg.data)
            # if data['type'] == "login":
            #     player = Player(os.urandom(4).hex(), ws, data['nick'], None)
            #     globalLobby.append(player)
            #     await ws.send_json({'userId': player.id, 'message': 'Logged in'}) 
            #     continue
            if data["type"] == "chatGlobal":
                for player in globalLobby:
                    await player.ws.send_json(data)
                continue
            if data["type"] == "chatGame":
                game_id = data['gameId']
                try:
                    game = games[game_id]
                except:
                    await ws.send_json({"error": "Game not found"})
                    continue
                if player in game.players:
                    await game.player1.ws.send_json(data)
                    await game.player2.ws.send_json(data)
                    continue

            if data["type"] == "createGame":
                game = Game(os.urandom(4).hex(), player)
                games[game.id] = game
                player = Player(os.urandom(4).hex(), ws, data['nick'], game)
                game.player1 = player
                player.game = game
                globalLobby.append(player)
                await ws.send_json({"type": "gameCreated", "gameId": game.id, "playerId": player.id})
                continue

            if data["type"] == "joinGame":
                game_id = data['gameId']
                player = Player(os.urandom(4).hex(), ws, data['nick'], None)
                try:
                    game = games[game_id]
                except:
                    await ws.send_json({"message": "Game not found"})
                    continue
                if game.player1 == player:
                    await ws.send_json({"message": "You are already in this game"})
                    continue
                if len(game.players) == 2:
                    await ws.send_json({"message": "Game is full"})
                    continue
                game.player2 = player
                player.game = game
                globalLobby.append(player)
                await game.player1.ws.send_json({"type": "gameStarted", "gameId": game.id, "opp": game.player2.to_json()})
                await game.player2.ws.send_json({"type": "gameStarted", "gameId": game.id, "opp": game.player1.to_json()})

            if data["type"] == "gameMsg":
                game_id = data['gameId']
                try:
                    game = games[game_id]
                except:
                    await ws.send_json({"error": "Game not found"})
                    continue
                ret = await game.handle_msg(player, data)
                continue

    
    print("Websocket connection closed")
    if player:
        try:
            globalLobby.remove(player)
        except ValueError:
            pass
        if player.game:
            player2 = game.other(player)
            if not player2:
                return
            await player2.ws.send_json({"type": "gameEnded", "message": "Opponent disconnected"})
            player2.game = None
            del games[player.game.id]



async def ping(request):
    return aiohttp.web.Response(text='pong')

if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    app = web.Application()
    app.router.add_route('GET', '/', handler)
    app.router.add_route('GET', '/ping', ping)
    aiohttp.web.run_app(app, port=8080)
