#!/usr/bin/env python
# -*- coding: utf-8 -*-
# mode: python; space-indent on; indent-width 4; mixedindent off; indent-mode cstyle;
# kate: space-indent on; indent-width 4; mixedindent off; indent-mode cstyle;

import asyncio
import websockets
import wscall

kPiaCoreURL = "http://localhost:12778"

class WSApp:
    """
    Wraps a Pia voice app as a WebSocket client.
    We will connect to Pia core over a WebSocket,
    register our app, and then wait for calls from the core
    to the intents.

    Reads the basic intents and commands from a JSON file.
    Then loads the app and lets it add the available values
    for each type.
    Then we register our app with the Pia core.

    This is a direct port of wsApp from JavaScript to Python.
    """

    async def start(self):
        websocket = async with websockets.connect(kPiaCoreURL)
        wsCall = WSCall(websocket)
        await wsCall.start()

async def start():
    wsApp = WSApp()
    await wsApp.start()

asyncio.get_event_loop().run_until_complete(start())
