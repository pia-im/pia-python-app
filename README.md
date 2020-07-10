A Pia voice app that is written in Python and
communicating with Pia using WebSockets.
This is implementing a WebSocket client, which calls the
Pia core = WebSocket server.

Include this module to create a Pia voice app that runs
as a separate process.

The protocol is based on WSCall. However, as voice app,
you don't need to see any of this. You just write the
intents JSON file and implement your functions.
The HTTP endpoint and URLs are all created by this library.
