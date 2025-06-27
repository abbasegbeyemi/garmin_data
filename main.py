import asyncio
import json

import openai
from fastmcp import Client


async def main():
    async with Client("server.py") as mcp_client:
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

        response = await openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "user",
                    "content": "Give me a review of my sleep in the last week. What was good? What could be improved?",
                }
            ],
            tools=openai_tools,
            tool_choice="auto",
        )

        messages = [
            {
                "role": "user",
                "content": "Give me a review of my sleep in the last week. What was good? What could be improved?",
            },
            response.choices[0].message.model_dump(),
        ]

        if response.choices[0].message.tool_calls:
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

        # Final response with tool calls
        final_response = await openai_client.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
        )
        print(f"Final response: {final_response.choices[0].message.content}")


if __name__ == "__main__":
    asyncio.run(main())
