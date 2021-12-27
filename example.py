            
import logging
from datetime import datetime
from src.recon_client import ReconSession

# onReady handler         
def onReady(tools):
    logging.debug("Session established [%s]" % str(datetime.now()))
    print("Session ready!")

# main message handler
def messageHandler_all(ws, message):
    print("\n\nGOT MESSAGE:\n", message) 
    
def messageHandler_geoIp(result):
    print("\n\nGeo-IP Result: \n", result)

api_key = "YOUR_API_KEY"
rs = ReconSession(messageHandler_all, apiKey = api_key, onReady = onReady, api = "wss://test.recon.us.com:2096")
rs.tool_exec('geoip', 'google.com', handler = messageHandler_geoIp)
          
