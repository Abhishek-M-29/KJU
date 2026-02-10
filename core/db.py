import requests
import json
import logging
import uuid
from core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

class MCPConnection:
    _instance = None
    _session_id = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MCPConnection, cls).__new__(cls)
        return cls._instance

    def connect(self):
        try:
             logger.info("Initializing MCP Session...")
             headers = {"Accept": "text/event-stream"}
             
             # 1. Get Session ID via SSE endpoint
             with requests.get(settings.MCP_SERVER_URL, headers=headers, stream=True, timeout=10) as r:
                 self._session_id = r.headers.get("mcp-session-id")
                 if not self._session_id:
                     logger.warning(f"No mcp-session-id received. Status: {r.status_code}")
                     r.raise_for_status() 

             logger.info(f"MCP Session ID: {self._session_id}")
             
             # Headers for subsequent requests
             post_headers = {
                "Content-Type": "application/json", 
                "Accept": "application/json, text/event-stream",
                "mcp-session-id": self._session_id
             }

             # 2. Send 'initialize' request
             init_payload = {
                 "jsonrpc": "2.0",
                 "method": "initialize",
                 "params": {
                     "protocolVersion": "2024-11-05",
                     "capabilities": {},
                     "clientInfo": {"name": "kg-rag-client", "version": "1.0"}
                 },
                 "id": "init-1"
             }
             r_init = requests.post(settings.MCP_SERVER_URL, json=init_payload, headers=post_headers, timeout=10)
             r_init.raise_for_status()
             
             # 3. Send 'notifications/initialized'
             notify_payload = {
                 "jsonrpc": "2.0",
                 "method": "notifications/initialized"
             }
             requests.post(settings.MCP_SERVER_URL, json=notify_payload, headers=post_headers, timeout=10)
             
             logger.info("MCP Session Initialized Successfully")

        except Exception as e:
            logger.error(f"Failed to connect to MCP: {e}")
            raise

    def verify_connectivity(self):
        # Could implement a ping to the MCP server if needed
        pass

    def query(self, cypher_query: str, parameters: dict = None):
        """
        Executes a Cypher query via the MCP server.
        Note: The current MCP tool `ExcecuteQuery_Neo4j` does not support separate parameters.
        """
        if not self._session_id:
            self.connect()

        logger.info(f"Executing Query via MCP: {cypher_query[:50]}...")
        
        # Construct JSON-RPC payload
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "ExcecuteQuery_Neo4j",
                "arguments": {
                    "cypher_query": cypher_query
                }
            },
            "id": str(uuid.uuid4())
        }

        try:
            headers = {
                "Content-Type": "application/json", 
                "Accept": "application/json, text/event-stream",
                "mcp-session-id": self._session_id
            }
            response = requests.post(settings.MCP_SERVER_URL, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse SSE response
            data = None
            for line in response.text.splitlines():
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        break
                    except json.JSONDecodeError:
                        continue
            
            if not data:
                # If no SSE data found, try raw JSON (in case server behaves differently)
                try:
                    data = response.json()
                except:
                    raise Exception(f"Invalid response format: {response.text[:100]}")

            if "error" in data:
                # Clean error message logging
                logger.error(f"MCP Server Error: {data['error']}")
                raise Exception(f"MCP Error: {data['error']}")
            
            # Extract result.
            result = data.get("result")
            
            # If the result is a dict containing 'content' (Standard MCP), try to parse it
            if isinstance(result, dict) and "content" in result:
                 content_list = result["content"]
                 for item in content_list:
                     if item.get("type") == "text":
                         try:
                             # Some tools return JSON string inside text
                             text_content = item["text"]
                             # If it looks like a list/dict, parse it
                             if text_content.strip().startswith(('[', '{')):
                                return json.loads(text_content)
                             return text_content
                         except json.JSONDecodeError:
                             pass
            
            # Fallback: return the result as is
            return result
                 
        except Exception as e:
            logger.error(f"MCP Query execution failed: {e}")
            raise 

    def close(self):
        pass
