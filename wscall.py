#!/usr/bin/env python
# -*- coding: utf-8 -*-
# mode: python; space-indent on; indent-width 4; mixedindent off; indent-mode cstyle;
# kate: space-indent on; indent-width 4; mixedindent off; indent-mode cstyle;

import json
import websocket
import asyncio

class WSCall:
    """
    Creates a very thin generic wrapper around WebSockets that allows to make
    request/response function calls.

    This is a direct port of WSCall from JavaScript to Python,
    and compatible with it.

    It implements:
    - The notion of paths to call a specific function on the other end
    - The notion of a response to a call, or an exception
    - async waiting for the response

    To expose a function, you `register()` it,
    which allows the other side to call it.
    To call a function on the other side, you use `await makeCall()`.

    E.g. server:
    def user(arg):
    ...
    register("/user", user)
    client:
    result = await makeCall("/user", { name: "Fred" })
    result == "I've seen Fred before, yes"
    whereas:
    await makeCall("/user", { license: "4" })
    throws an exception with .message == "I don't know what you're talking about"
    """
    lastID = 0
    # Calls made from here to the other side, and not yet returned
    # ID -> {Future}
    callsWaiting = {}
    # functions implemented on this side and exported,
    # to be called from the other side
    # path {str} -> {function}
    functions = {}

    def __init__(self, websocket):
        if not callable(websocket.send):
            raise Exception("Need websocket")
        self.websocket = websocket

    async def start(self)
        # process incoming messages until client disconnects
        async for message in self.websocket:
            await self._incomingMessage(message)

    def register(self, path, func):
        """
        @param path {str}
        @param func {function}
        """
        if not callable(func):
            raise Exception("Need a function")
        self.functions[path] = func

    # message {JSON as str}
    async def _incomingMessage(self, message):
        try:
            message = json.loads(message)
        except:
            return
        if not (hasattr(message, "id") or hasattr(message, "path") or hasattr(message, "success")):
            return
        if hasattr(message, "success"):
            self._response(message)
            return

        func = self.functions[message.path]
        if not callable(func):
            raise Exception(path + " is not defined")
        try:
            result = func(message.arg)
            if asyncio.iscoroutinefunction(result):
                result = await result
            self.websocket.send(json.dumps({
                id: message.id,
                success: True,
                result: result,
            }))
        except Exception as ex:
            self.websocket.send(json.dumps({
                id: message.id,
                success: False,
                message: str(ex),
                code: type(ex),
            }))

    def makeCall(self, path, arg):
        """
        Calls a function on other side
        @param path {str}   like the path component of a HTTP URL.
           E.g. "/contact/call/" or "register".
           Must match the registration on the other side exactly, including leading slash or not.
        @param arg {Dict}   arguments for the function call
        @returns {Future} waits until the call returns with a result or Exception
        """
        if not type(path) is str and len(path) > 0:
            raise Exception("Need path")
        id = self.generateID()
        callWaiting = asyncio.get_running_loop().create_future()
        self.callsWaiting[id] = callWaiting
        self.websocket.send(json.dumps({
            id: id,
            path: path,
            arg: arg,
        }))
        return callWaiting
        # message will be processed on the other side
        # then they will send us a response with message.result
        # which then will mark the future as done, so
        # the caller can await callWaiting

    def _response(self, message):
        if not type(message.success) is bool:
            raise Exception("success must be a boolean")
        callWaiting = self.callsWaiting[message.id]
        del self.callsWaiting[message.id]
        if not asyncio.isfuture(callWaiting):
            raise Exception("Got a response for call ID " + message.id + ", but we did not make such a call, or we already got the response for it")
        if message.success:
            callWaiting.set_result(message.result)
        else:
            callWaiting.set_exception(RemoteException(message.message, message.code))

    def generateID(self):
        return self.lastID++


class RemoteException(Exception):
    def __init__(self, message, code):
        super().__init__(message)
        self.code = code
