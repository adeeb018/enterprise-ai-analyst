import asyncio

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client


SERVER_PARAMS = StdioServerParameters(
    command="uv",
    args=[
        "run",
        "mcp",
        "run",
        "server.py",
    ],
)


async def call_analyst(
    session: ClientSession,
    question: str,
) -> None:

    result = await session.call_tool(
        "ask_analyst",
        {
            "question": question,
        },
    )

    if result.isError:
        print("\nMCP tool failed:\n")

        for content in result.content:
            if isinstance(content, types.TextContent):
                print(content.text)

        return

    print("\nAnalyst:\n")

    for content in result.content:
        if isinstance(content, types.TextContent):
            print(content.text)

    print()


async def run_client() -> None:

    async with stdio_client(
        SERVER_PARAMS
    ) as (read, write):

        async with ClientSession(
            read,
            write,
        ) as session:

            # Initialize MCP session
            await session.initialize()

            # Discover tools once
            tools = await session.list_tools()

            print("\nConnected to MCP server.")
            print("\nAvailable tools:")

            for tool in tools.tools:
                print(
                    f"- {tool.name}: "
                    f"{tool.description or ''}"
                )

            print(
                "\nType 'exit' or 'quit' to stop."
            )

            # Keep the same MCP session alive
            while True:

                try:
                    question = input(
                        "\nYou: "
                    ).strip()

                except (EOFError, KeyboardInterrupt):
                    print("\nExiting.")
                    break

                if not question:
                    continue

                if question.lower() in {
                    "exit",
                    "quit",
                }:
                    print("Exiting.")
                    break

                try:
                    await call_analyst(
                        session,
                        question,
                    )

                except Exception as e:
                    print(
                        f"\nMCP request failed: {e}"
                    )


def main() -> None:

    asyncio.run(
        run_client()
    )


if __name__ == "__main__":
    main()