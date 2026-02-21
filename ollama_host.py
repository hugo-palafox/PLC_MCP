import asyncio
import json
import logging
import os
import sys
from typing import Any, List, Dict, Optional
from pathlib import Path

# MCP Client imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Ollama import
import ollama

# Configure logging to stderr
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("ollama-host")

# Custom Ollama Client with longer timeouts for stability
# Increase timeout to 120s to handle slow model responses on Windows
client = ollama.Client(host='http://127.0.0.1:11434', timeout=120)

# Project paths
BASE_DIR = Path(r"c:\Users\hugod\Documents\Projects\PLC_MCP\Core")
SERVER_SCRIPT = BASE_DIR / "server.py"
VENV_PYTHON = BASE_DIR / ".venv" / "Scripts" / "python.exe"

class OllamaMCPHost:
    def __init__(self, model: str = "deepseek-r1:latest"):
        self.model = model
        self.session: Optional[ClientSession] = None
        self.tools: List[Dict[str, Any]] = []
        self._exit_stack = None

    async def connect_to_server(self):
        """Spawns the MCP server and establishes a session."""
        # Force unbuffered python and LIVE mode for real PLC data
        server_env = os.environ.copy()
        server_env["PYTHONUNBUFFERED"] = "1"
        server_env["PLC_MODE"] = "LIVE"  # Changed to LIVE mode
        server_env["PYTHONPATH"] = str(BASE_DIR)

        server_params = StdioServerParameters(
            command=str(VENV_PYTHON),
            args=["-u", str(SERVER_SCRIPT)],
            env=server_env
        )
        
        logger.info(f"Connecting to MCP server: {SERVER_SCRIPT}")
        
        # Capture the exit stack to manage clean exits
        from contextlib import AsyncExitStack
        self._exit_stack = AsyncExitStack()
        
        try:
            # Entering stdio_client
            read, write = await self._exit_stack.enter_async_context(stdio_client(server_params))
            self.session = await self._exit_stack.enter_async_context(ClientSession(read, write))
            
            logger.info("Initializing session...")
            await asyncio.wait_for(self.session.initialize(), timeout=15.0)
            
            logger.info("Listing tools...")
            mcp_tools = await asyncio.wait_for(self.session.list_tools(), timeout=10.0)
            
            self.tools = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema,
                    },
                }
                for tool in mcp_tools.tools
            ]
            logger.info(f"Connected! Found {len(self.tools)} tools.")
            
        except asyncio.TimeoutError:
            logger.error("Timed out while connecting to MCP server.")
            await self.cleanup()
            raise
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            await self.cleanup()
            raise

    async def chat_loop(self):
        """Main interaction loop."""
        print(f"\n--- Industrial PLC Bridge - LIVE MODE (Model: {self.model}) ---")
        print("⚡ Connected to REAL PLC at 199.4.42.250")
        print("🧠 DeepSeek AI - Enhanced reasoning for industrial controls")
        print("Type 'exit' to quit. Ask anything about your machine data.")
        
        messages = [
            {"role": "system", "content": "You are an Industrial Controls AI with access to LIVE PLC data. Think step-by-step when analyzing requests. IMPORTANT: When user asks to 'read all tags' or 'show values', use read_all_oee_tags. When they ask to 'list tags' or 'what tags exist', use list_plc_tags. Always use tools before answering to get current data. Analyze patterns and provide insights. Be concise but thorough."}
        ]
        
        while True:
            try:
                user_input = await asyncio.to_thread(input, "\nUser: ")
                user_input = user_input.strip()
                
                if user_input.lower() in ["exit", "quit"]:
                    break
                if not user_input:
                    continue
                
                messages.append({"role": "user", "content": user_input})
                
                # Fetch response from Ollama (run in thread to avoid blocking loop)
                try:
                    response = await asyncio.to_thread(
                        client.chat,
                        model=self.model,
                        messages=messages,
                        tools=self.tools,
                    )
                except Exception as e:
                    logger.error(f"Failed to communicate with Ollama: {e}")
                    print(f"\n[Error] Lost connection to Ollama. Please ensure it's running.")
                    continue
                
                # Process tool calls
                while response.get('message', {}).get('tool_calls'):
                    tool_calls = response['message']['tool_calls']
                    messages.append(response['message'])
                    
                    for tool_call in tool_calls:
                        func_name = tool_call['function']['name']
                        func_args = tool_call['function']['arguments']
                        
                        logger.info(f"LLM requesting tool: {func_name}({func_args})")
                        
                        try:
                            # Call the MCP tool
                            result = await self.session.call_tool(func_name, arguments=func_args)
                            
                            # Convert result content to string for LLM
                            content_text = ""
                            if hasattr(result, 'content'):
                                # FastMCP/MCP results usually have a 'content' list of TextContent/ImageContent
                                content_list = []
                                for item in result.content:
                                    if hasattr(item, 'text'):
                                        content_list.append(item.text)
                                    else:
                                        content_list.append(str(item))
                                content_text = "\n".join(content_list)
                            
                            messages.append({
                                "role": "tool",
                                "content": content_text,
                            })
                        except Exception as e:
                            logger.error(f"Tool error: {e}")
                            messages.append({
                                "role": "tool",
                                "content": f"Error executing tool: {str(e)}",
                            })

                    # Get updated response from LLM after tool results
                    try:
                        response = await asyncio.to_thread(
                            client.chat,
                            model=self.model,
                            messages=messages,
                            tools=self.tools,
                        )
                    except Exception as e:
                        logger.error(f"Ollama connection error during tool follow-up: {e}")
                        break

                final_reply = response['message']['content']
                print(f"\nAssistant: {final_reply}")
                messages.append(response['message'])

            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Interaction error: {e}")

    async def cleanup(self):
        if self._exit_stack:
            await self._exit_stack.aclose()
            logger.info("Shutdown complete.")

async def main():
    host = OllamaMCPHost()
    try:
        await host.connect_to_server()
        await host.chat_loop()
    finally:
        await host.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
