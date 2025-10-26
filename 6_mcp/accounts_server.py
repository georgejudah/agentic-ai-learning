# MCP ACCOUNTS SERVER
# ===================================================================
# This is an MCP (Model Context Protocol) server that provides trading account
# management tools and resources to AI agents. It demonstrates how to expose
# business logic as MCP tools that agents can use for financial operations.
#
# ARCHITECTURE:
# - Uses FastMCP framework for rapid MCP server development
# - Provides Tools: Functions agents can call (buy/sell shares, get balance)
# - Provides Resources: Data agents can access (account reports, strategies)
# - Communicates via STDIO with MCP clients (JSON-RPC protocol)
# ===================================================================

from mcp.server.fastmcp import FastMCP
from accounts import Account

# Initialize FastMCP server with a descriptive name
# This server will be discoverable by MCP clients as "accounts_server"
mcp = FastMCP("accounts_server")

# ===================================================================
# MCP TOOLS - Functions that AI agents can call
# ===================================================================
# Tools are the primary way agents interact with external systems.
# Each tool becomes available to agents that connect to this MCP server.

@mcp.tool()
async def get_balance(name: str) -> float:
    """Get the cash balance of the given account name.

    Args:
        name: The name of the account holder
    """
    return Account.get(name).balance

@mcp.tool()
async def get_holdings(name: str) -> dict[str, int]:
    """Get the holdings of the given account name.

    Args:
        name: The name of the account holder
    """
    return Account.get(name).holdings

@mcp.tool()
async def buy_shares(name: str, symbol: str, quantity: int, rationale: str) -> float:
    """Buy shares of a stock.

    Args:
        name: The name of the account holder
        symbol: The symbol of the stock
        quantity: The quantity of shares to buy
        rationale: The rationale for the purchase and fit with the account's strategy
    """
    return Account.get(name).buy_shares(symbol, quantity, rationale)

@mcp.tool()
async def sell_shares(name: str, symbol: str, quantity: int, rationale: str) -> float:
    """Sell shares of a stock.

    Args:
        name: The name of the account holder
        symbol: The symbol of the stock
        quantity: The quantity of shares to sell
        rationale: The rationale for the sale and fit with the account's strategy
    """
    return Account.get(name).sell_shares(symbol, quantity, rationale)

@mcp.tool()
async def change_strategy(name: str, strategy: str) -> str:
    """At your discretion, if you choose to, call this to change your investment strategy for the future.

    Args:
        name: The name of the account holder
        strategy: The new strategy for the account
    """
    return Account.get(name).change_strategy(strategy)

# ===================================================================
# MCP RESOURCES - Data that AI agents can access
# ===================================================================
# Resources provide read-only access to data. Agents can "read" these resources
# but cannot modify them directly - they must use tools for modifications.

@mcp.resource("accounts://accounts_server/{name}")
async def read_account_resource(name: str) -> str:
    """Resource providing complete account information and reports.

    URI Pattern: accounts://accounts_server/{name}
    Example: accounts://accounts_server/john

    Returns comprehensive account data including balance, holdings, transactions, etc.
    """
    account = Account.get(name.lower())
    return account.report()

@mcp.resource("accounts://strategy/{name}")
async def read_strategy_resource(name: str) -> str:
    """Resource providing the current investment strategy for an account.

    URI Pattern: accounts://strategy/{name}
    Example: accounts://strategy/john

    Returns the account's current investment strategy and approach.
    """
    account = Account.get(name.lower())
    return account.get_strategy()

# ===================================================================
# SERVER ENTRY POINT
# ===================================================================
# When run directly, this starts the MCP server using STDIO transport.
# The server will communicate with MCP clients using JSON-RPC over standard input/output.
if __name__ == "__main__":
    mcp.run(transport='stdio')
    # alternatively, use sse
    # mcp.run(transport='sse')