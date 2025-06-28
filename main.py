import asyncio
import json

import openai
from fastmcp import Client
from openai.types.chat import ChatCompletionMessageParam

config = {
    "mcpServers": {
        "garmin": {
            "command": "uv",
            "args": ["run", "server.py"],
        },
        "time": {
            "command": "uvx",
            "args": ["mcp-server-time", "--local-timezone=Europe/London"],
        },
    }
}

client = Client(config)


async def main():
    async with client as mcp_client:
        mcp_tools = await mcp_client.list_tools()

        openai_tools = []
        for tool in mcp_tools:
            openai_tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema,
                    },
                }
            )

        openai_client = openai.AsyncOpenAI()

        messages: list[ChatCompletionMessageParam] = [
            {
                "role": "user",
                "content": """
                What has been my average sleep duration in the last week? Ensure you use the time tool to get the current time and date and the garmin tool to get the sleep data.
                """,
            }
        ]

        response = await openai_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=openai_tools,
            tool_choice="auto",
        )

        messages.append(response.choices[0].message.model_dump())  # type: ignore

        while response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                arguments = json.loads(tool_call.function.arguments)
                result = await mcp_client.call_tool(tool_call.function.name, arguments)
                messages.append(
                    {
                        "role": "tool",
                        "content": str(result),
                        "tool_call_id": tool_call.id,
                    }
                )

            response = await openai_client.chat.completions.create(
                model="gpt-4.1",
                messages=messages,
                tools=openai_tools,
                tool_choice="auto",
            )
            messages.append(response.choices[0].message.model_dump())  # type: ignore
        print(f"Final response: {response.choices[0].message.content}")


if __name__ == "__main__":
    asyncio.run(main())
