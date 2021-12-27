from json import dumps, loads
from uuid import uuid1
from datetime import datetime
import websocket
from threading import Thread
import logging

logger = logging.basicConfig(level=logging.DEBUG, filename="recon_client.log")

def genID():
    return str(uuid1())

# Main Object
class ReconSession(object):
    def __init__(self, messageHandler, apiKey = None, onReady = None, api = "wss://recon.us.com:8443"):
        
        # Important session variables
        self.tools        = None
        self.myInfo       = None
        self.promises     = {}
        self.apiKey       = apiKey
        self.sessionReady = False
        self.sessionUUID  = None
        self.api          = api
        
        # Main function to handle messages
        self.onMessage = None
        def onMessage(_websocket, _message):
            
            # log the socket message
            logging.debug("Incoming Socket Message: " + _message)
            
            # Message object
            message = loads(_message)
            _action = message.get('action')
            
            # Save active tools list, automatically
            if _action == 'init_event':
                # Active Tools
                self.tools        = message['activeTools']
                # My Info
                self.myInfo       = message['myInfo']
                # Session UUID
                self.sessionUUID  = message['uuid']
                # Session Ready
                self.sessionReady = True
                
                # Call the user-defined onReady function, if defined
                if onReady is not None:
                    onReady(self.tools)
                    
            # Handle promises
            if _action == 'promise_fulfillment':
                if message['promise'] in self.promises:
                    if self.promises[message['promise']] is not None:
                        self.promises[message['promise']](message['result'])
                    del self.promises[message['promise']]
            
            # User-defined function to handle messages - AUXILLARY FEATURE, NOT REQUIRED.
            # Promise-handlers should be used to handle messages from the server instead.
            messageHandler(_websocket, message)
                
        # Set the onMessage function
        self.onMessage = onMessage
        
        # log the socket message
        logging.debug("Socket App Starting...")
        
        self.wsapp     = websocket.WebSocketApp(
            self.api,
            on_message=onMessage
            )
        
        def clientThread():
            # Start server
            self.wsapp.run_forever()
            
        # Start the client session on a new thread.
        self._thread = Thread(target=clientThread)
        
        # Start the client thread
        self._thread.start()
        
        # execute a tool
        def tool_exec(tool, value, handler = None):
            
            # log the socket message
            logging.debug("Executing Tool [%s] with value [%s]" % (tool, value))
        
            # Ensure the session is alive
            if self.wsapp.sock is None:
                raise Exception('Client-Server socket has closed prematurely for an unknown reason!')
            
            # Ensure the session is ready                        
            if self.sessionReady:                
                message                  = {}
                message['uuid']          = self.sessionUUID
                message['action']        = 'toolkit'
                message['apiKey']        = self.apiKey
                message['tool']          = tool
                message['input']         = value
                promiseID                = genID()
                self.promises[promiseID] = handler
                message['promise']       = promiseID
                logging.debug("Tool Executed: " + dumps(message))
                self.wsapp.send(dumps(message))
            else:
                raise Exception('tool_execution attemtped while session not ready!')
            
        self.tool_exec = tool_exec
        
        # wait until the session is ready
        while 1:
            if self.sessionReady:
                break
            
            

        
        

        



