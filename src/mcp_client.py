import asyncio
import json

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


def get_text(result) -> str:

    texts = []

    for content in result.content:

        if isinstance(
            content,
            types.TextContent,
        ):
            texts.append(content.text)

    return "\n".join(texts)


async def create_conversation(
    session: ClientSession,
) -> str | None:

    result = await session.call_tool(
        "create_conversation",
        {
            "title": "New Chat",
        },
    )

    if result.isError:
        print("\nFailed to create conversation.")
        print(get_text(result))
        return None

    conversation_id = get_text(result).strip()

    print(
        f"\nCreated conversation: {conversation_id}"
    )

    return conversation_id


async def get_conversations(
    session: ClientSession,
) -> list[dict]:

    result = await session.call_tool(
        "list_conversations",
        {},
    )

    if result.isError:
        print("\nFailed to load conversations.")
        print(get_text(result))
        return []

    raw_text = get_text(result).strip()

    try:
        if not raw_text.startswith("["):
            wrapped_text = "[" + raw_text.replace("}\n{", "},\n{") + "]"
            return json.loads(wrapped_text)
        
        return json.loads(raw_text)

    except json.JSONDecodeError:
        print("\nUnexpected conversation response:")
        print(raw_text)
        return []


async def get_conversation(
    session: ClientSession,
    conversation_id: str,
) -> dict | None:

    result = await session.call_tool(
        "get_conversation",
        {
            "conversation_id": conversation_id,
        },
    )

    if result.isError:
        print("\nFailed to load conversation.")
        print(get_text(result))
        return None

    raw_text = get_text(result)

    try:
        return json.loads(raw_text)

    except json.JSONDecodeError:
        print("\nUnexpected conversation response:")
        print(raw_text)
        return None


def print_conversation_history(
    conversation: dict,
) -> None:

    print(
        f"\n{'=' * 60}"
    )

    print(
        f"Chat: "
        f"{conversation.get('title', 'Untitled')}"
    )

    print(
        f"ID: "
        f"{conversation.get('conversation_id')}"
    )

    print(
        f"{'=' * 60}"
    )

    turns = conversation.get(
        "turns",
        [],
    )

    if not turns:
        print("\nNo messages yet.")
        return

    for turn in turns:

        print(
            f"\nUser:"
        )

        print(
            turn.get(
                "question",
                "",
            )
        )

        answer = turn.get(
            "answer"
        )

        if answer:
            print(
                "\nAnalyst:"
            )
            print(answer)

        print(
            f"\n{'-' * 60}"
        )


async def list_conversations(
    session: ClientSession,
) -> list[dict]:

    conversations = await get_conversations(
        session
    )

    if not conversations:
        print("\nNo saved conversations.")
        return []

    print("\nSaved conversations:\n")

    for index, conversation in enumerate(
        conversations,
        start=1,
    ):

        print(
            f"{index}. "
            f"{conversation.get('title', 'Untitled')}"
        )

        print(
            f"   ID: "
            f"{conversation.get('conversation_id')}"
        )

        print(
            f"   Updated: "
            f"{conversation.get('updated_at')}"
        )

        print()

    return conversations


async def switch_conversation(
    session: ClientSession,
) -> str | None:

    conversations = await get_conversations(
        session
    )

    if not conversations:
        print("\nNo saved conversations.")
        return None

    print("\nSelect a conversation:\n")

    for index, conversation in enumerate(
        conversations,
        start=1,
    ):

        print(
            f"{index}. "
            f"{conversation.get('title', 'Untitled')}"
        )

        print(
            f"   Updated: "
            f"{conversation.get('updated_at')}"
        )

        print()

    choice = input(
        "Enter conversation number: "
    ).strip()

    try:
        index = int(choice)

    except ValueError:
        print("\nInvalid number.")
        return None

    if index < 1 or index > len(
        conversations
    ):
        print("\nConversation does not exist.")
        return None

    selected = conversations[
        index - 1
    ]

    conversation_id = selected[
        "conversation_id"
    ]

    conversation = await get_conversation(
        session,
        conversation_id,
    )

    if conversation is None:
        return None

    print_conversation_history(
        conversation
    )

    print(
        f"\nSwitched to: "
        f"{selected.get('title', 'Untitled')}"
    )

    return conversation_id


async def show_current_history(
    session: ClientSession,
    conversation_id: str,
) -> None:

    conversation = await get_conversation(
        session,
        conversation_id,
    )

    if conversation is None:
        return

    print_conversation_history(
        conversation
    )


async def delete_conversation(
    session: ClientSession,
    conversation_id: str,
) -> bool:

    result = await session.call_tool(
        "delete_conversation",
        {
            "conversation_id": conversation_id,
        },
    )

    if result.isError:
        print("\nFailed to delete conversation.")
        print(get_text(result))
        return False

    print("\nConversation deleted.")
    return True


async def delete_selected_conversation(
    session: ClientSession,
    current_conversation_id: str,
) -> str:

    conversations = await get_conversations(
        session
    )

    if not conversations:
        print("\nNo conversations to delete.")
        return current_conversation_id

    print(
        "\nSelect conversation to delete:\n"
    )

    for index, conversation in enumerate(
        conversations,
        start=1,
    ):

        print(
            f"{index}. "
            f"{conversation.get('title', 'Untitled')}"
        )

    choice = input(
        "\nEnter conversation number: "
    ).strip()

    try:
        index = int(choice)

    except ValueError:
        print("\nInvalid number.")
        return current_conversation_id

    if index < 1 or index > len(
        conversations
    ):
        print("\nConversation does not exist.")
        return current_conversation_id

    selected = conversations[
        index - 1
    ]

    conversation_id = selected[
        "conversation_id"
    ]

    title = selected.get(
        "title",
        "Untitled",
    )

    confirmation = input(
        f'\nDelete "{title}" and all messages? '
        "[y/N]: "
    ).strip().lower()

    if confirmation != "y":
        print("\nDeletion cancelled.")
        return current_conversation_id

    deleted = await delete_conversation(
        session,
        conversation_id,
    )

    if not deleted:
        return current_conversation_id

    if (
        conversation_id
        == current_conversation_id
    ):

        remaining = await get_conversations(
            session
        )

        if remaining:

            new_current = remaining[0][
                "conversation_id"
            ]

            print(
                "\nSwitched to:"
            )

            print(
                remaining[0].get(
                    "title",
                    "Untitled",
                )
            )

            return new_current

        new_id = await create_conversation(
            session
        )

        if new_id is None:
            raise RuntimeError(
                "Unable to create replacement "
                "conversation."
            )

        return new_id

    return current_conversation_id


async def call_analyst(
    session: ClientSession,
    conversation_id: str,
    question: str,
) -> None:

    result = await session.call_tool(
        "ask_analyst",
        {
            "conversation_id": conversation_id,
            "question": question,
        },
    )

    if result.isError:
        print("\nMCP tool failed:\n")
        print(get_text(result))
        return

    print("\nAnalyst:\n")
    print(get_text(result))
    print()


async def run_client() -> None:

    async with stdio_client(
        SERVER_PARAMS
    ) as (read, write):

        async with ClientSession(
            read,
            write,
        ) as session:

            await session.initialize()

            tools = await session.list_tools()

            print(
                "\nConnected to MCP server."
            )

            print("\nAvailable tools:")

            for tool in tools.tools:

                print(
                    f"- {tool.name}: "
                    f"{tool.description or ''}"
                )

            conversation_id = (
                await create_conversation(
                    session
                )
            )

            if conversation_id is None:
                return

            print(
                "\nCommands:"
            )

            print(
                "   :new      Create a new chat"
            )

            print(
                "   :chats    List saved chats"
            )

            print(
                "   :switch   Switch chat and view history"
            )

            print(
                "   :history  View current chat history"
            )

            print(
                "   :delete   Delete a saved chat"
            )

            print(
                "   :current  Show current chat ID"
            )

            print(
                "   :exit     Exit"
            )

            while True:

                try:

                    question = input(
                        "\nYou: "
                    ).strip()

                except (
                    EOFError,
                    KeyboardInterrupt,
                ):

                    print("\nExiting.")

                    break

                if not question:
                    continue

                if question.lower() in {
                    "exit",
                    "quit",
                    ":exit",
                }:

                    print("Exiting.")

                    break

                if question == ":new":

                    new_id = (
                        await create_conversation(
                            session
                        )
                    )

                    if new_id is not None:
                        conversation_id = new_id

                    continue

                if question == ":chats":

                    await list_conversations(
                        session
                    )

                    continue

                if question == ":switch":

                    new_id = (
                        await switch_conversation(
                            session
                        )
                    )

                    if new_id is not None:
                        conversation_id = new_id

                    continue

                if question == ":history":

                    await show_current_history(
                        session,
                        conversation_id,
                    )

                    continue

                if question == ":delete":

                    conversation_id = (
                        await delete_selected_conversation(
                            session,
                            conversation_id,
                        )
                    )

                    continue

                if question == ":current":

                    print(
                        "\nCurrent conversation ID:"
                    )

                    print(conversation_id)

                    continue

                try:

                    await call_analyst(
                        session=session,
                        conversation_id=conversation_id,
                        question=question,
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