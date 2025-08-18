Source: https://langchain-ai.github.io/langgraph/tutorials/get-started/1-build-basic-chatbot/

# Build a basic chatbot

In this tutorial, you will build a basic chatbot. This chatbot is the basis for the following series of tutorials where you will progressively add more sophisticated capabilities, and be introduced to key LangGraph concepts along the way. Let's dive in! 🌟

## Prerequisites

Before you start this tutorial, ensure you have access to a LLM that supports
tool-calling features, such as [OpenAI](https://platform.openai.com/api-keys),
[Anthropic](https://console.anthropic.com/settings/keys), or
[Google Gemini](https://ai.google.dev/gemini-api/docs/api-key).

## 1. Install packages

Install the required packages:

```bash
pip install -U langgraph langsmith
```





!!! tip

    Sign up for LangSmith to quickly spot issues and improve the performance of your LangGraph projects. LangSmith lets you use trace data to debug, test, and monitor your LLM apps built with LangGraph. For more information on how to get started, see [LangSmith docs](https://docs.smith.langchain.com).

## 2. Create a `StateGraph`

Now you can create a basic chatbot using LangGraph. This chatbot will respond directly to user messages.

Start by creating a `StateGraph`. A `StateGraph` object defines the structure of our chatbot as a "state machine". We'll add `nodes` to represent the llm and functions our chatbot can call and `edges` to specify how the bot should transition between these functions.

API Reference: StateGraph</a> | START</a> | END</a> | add_messages</a></i></sup>

```python
from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)
```





Our graph can now handle two key tasks:

1. Each `node` can receive the current `State` as input and output an update to the state.
2. Updates to `messages` will be appended to the existing list rather than overwriting it, thanks to the prebuilt reducer function.

!!! tip "Concept"

    When defining a graph, the first step is to define its `State`. The `State` includes the graph's schema and [reducer functions](https://langchain-ai.github.io/langgraph/concepts/low_level/#reducers) that handle state updates. In our example, `State` is a schema with one key: `messages`. The reducer function is used to append new messages to the list instead of overwriting it. Keys without a reducer annotation will overwrite previous values.

    To learn more about state, reducers, and related concepts, see [LangGraph reference docs](https://langchain-ai.github.io/langgraph/reference/graphs/#langgraph.graph.message.add_messages).

## 3. Add a node

Next, add a "`chatbot`" node. **Nodes** represent units of work and are typically regular functions.

Let's first select a chat model:

=== "OpenAI"

    ```shell
    pip install -U "langchain[openai]"
    ```
    ```python
    import os
    from langchain.chat_models import init_chat_model

    os.environ["OPENAI_API_KEY"] = "sk-..."

    llm = init_chat_model("openai:gpt-4.1")
    ```

    👉 Read the [OpenAI integration docs](https://python.langchain.com/docs/integrations/chat/openai/)

=== "Anthropic"

    ```shell
    pip install -U "langchain[anthropic]"
    ```
    ```python
    import os
    from langchain.chat_models import init_chat_model

    os.environ["ANTHROPIC_API_KEY"] = "sk-..."

    llm = init_chat_model("anthropic:claude-3-5-sonnet-latest")
    ```

    👉 Read the [Anthropic integration docs](https://python.langchain.com/docs/integrations/chat/anthropic/)

=== "Azure"

    ```shell
    pip install -U "langchain[openai]"
    ```
    ```python
    import os
    from langchain.chat_models import init_chat_model

    os.environ["AZURE_OPENAI_API_KEY"] = "..."
    os.environ["AZURE_OPENAI_ENDPOINT"] = "..."
    os.environ["OPENAI_API_VERSION"] = "2025-03-01-preview"

    llm = init_chat_model(
        "azure_openai:gpt-4.1",
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    )
    ```
 
    👉 Read the [Azure integration docs](https://python.langchain.com/docs/integrations/chat/azure_chat_openai/)

=== "Google Gemini"

    ```shell
    pip install -U "langchain[google-genai]"
    ```
    ```python
    import os
    from langchain.chat_models import init_chat_model

    os.environ["GOOGLE_API_KEY"] = "..."

    llm = init_chat_model("google_genai:gemini-2.0-flash")
    ```

    👉 Read the [Google GenAI integration docs](https://python.langchain.com/docs/integrations/chat/google_generative_ai/)

=== "AWS Bedrock"

    ```shell
    pip install -U "langchain[aws]"
    ```
    ```python
    from langchain.chat_models import init_chat_model

    # Follow the steps here to configure your credentials:
    # https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html

    llm = init_chat_model(
        "anthropic.claude-3-5-sonnet-20240620-v1:0",
        model_provider="bedrock_converse",
    )
    ```

    👉 Read the [AWS Bedrock integration docs](https://python.langchain.com/docs/integrations/chat/bedrock/)








We can now incorporate the chat model into a simple node:

```python
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("chatbot", chatbot)
```





**Notice** how the `chatbot` node function takes the current `State` as input and returns a dictionary containing an updated `messages` list under the key "messages". This is the basic pattern for all LangGraph node functions.

The `add_messages` function in our `State` will append the LLM's response messages to whatever messages are already in the state.




## 4. Add an `entry` point

Add an `entry` point to tell the graph **where to start its work** each time it is run:

```python
graph_builder.add_edge(START, "chatbot")
```





## 5. Add an `exit` point

Add an `exit` point to indicate **where the graph should finish execution**. This is helpful for more complex flows, but even in a simple graph like this, adding an end node improves clarity.

```python
graph_builder.add_edge("chatbot", END)
```





This tells the graph to terminate after running the chatbot node.

## 6. Compile the graph

Before running the graph, we'll need to compile it. We can do so by calling `compile()`
on the graph builder. This creates a `CompiledGraph` we can invoke on our state.

```python
graph = graph_builder.compile()
```





## 7. Visualize the graph (optional)

You can visualize the graph using the `get_graph` method and one of the "draw" methods, like `draw_ascii` or `draw_png`. The `draw` methods each require additional dependencies.

```python
from IPython.display import Image, display

try:
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
    # This requires some extra dependencies and is optional
    pass
```





![basic chatbot diagram](basic-chatbot.png)

## 8. Run the chatbot

Now run the chatbot!

!!! tip

    You can exit the chat loop at any time by typing `quit`, `exit`, or `q`.

```python
def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)


while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_updates(user_input)
    except:
        # fallback if input() is not available
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break
```





```
Assistant: LangGraph is a library designed to help build stateful multi-agent applications using language models. It provides tools for creating workflows and state machines to coordinate multiple AI agents or language model interactions. LangGraph is built on top of LangChain, leveraging its components while adding graph-based coordination capabilities. It's particularly useful for developing more complex, stateful AI applications that go beyond simple query-response interactions.
```

```
Goodbye!
```



**Congratulations!** You've built your first chatbot using LangGraph. This bot can engage in basic conversation by taking user input and generating responses using an LLM. You can inspect a [LangSmith Trace](https://smith.langchain.com/public/7527e308-9502-4894-b347-f34385740d5a/r) for the call above.

Below is the full code for this tutorial:

API Reference: init_chat_model</a> | StateGraph</a> | START</a> | END</a> | add_messages</a></i></sup>

```python
from typing import Annotated

from langchain.chat_models import init_chat_model
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)


llm = init_chat_model("anthropic:claude-3-5-sonnet-latest")


def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
graph = graph_builder.compile()
```

Source: https://langchain-ai.github.io/langgraph/tutorials/get-started/2-add-tools/

# Add tools

To handle queries that your chatbot can't answer "from memory", integrate a web search tool. The chatbot can use this tool to find relevant information and provide better responses.

!!! note

    This tutorial builds on [Build a basic chatbot](./1-build-basic-chatbot.md).

## Prerequisites

Before you start this tutorial, ensure you have the following:

- An API key for the [Tavily Search Engine](https://python.langchain.com/docs/integrations/tools/tavily_search/).





## 1. Install the search engine

Install the requirements to use the [Tavily Search Engine](https://python.langchain.com/docs/integrations/tools/tavily_search/):

```bash
pip install -U langchain-tavily
```





## 2. Configure your environment

Configure your environment with your search engine API key:

```python
import os

os.environ["TAVILY_API_KEY"] = "tvly-..."
```




## 3. Define the tool

Define the web search tool:

API Reference: TavilySearch</a></i></sup>

```python
from langchain_tavily import TavilySearch

tool = TavilySearch(max_results=2)
tools = [tool]
tool.invoke("What's a 'node' in LangGraph?")
```





The results are page summaries our chat bot can use to answer questions:

```
{'query': "What's a 'node' in LangGraph?",
'follow_up_questions': None,
'answer': None,
'images': [],
'results': [{'title': "Introduction to LangGraph: A Beginner's Guide - Medium",
'url': 'https://medium.com/@cplog/introduction-to-langgraph-a-beginners-guide-14f9be027141',
'content': 'Stateful Graph: LangGraph revolves around the concept of a stateful graph, where each node in the graph represents a step in your computation, and the graph maintains a state that is passed around and updated as the computation progresses. LangGraph supports conditional edges, allowing you to dynamically determine the next node to execute based on the current state of the graph. We define nodes for classifying the input, handling greetings, and handling search queries. def classify_input_node(state): LangGraph is a versatile tool for building complex, stateful applications with LLMs. By understanding its core concepts and working through simple examples, beginners can start to leverage its power for their projects. Remember to pay attention to state management, conditional edges, and ensuring there are no dead-end nodes in your graph.',
'score': 0.7065353,
'raw_content': None},
{'title': 'LangGraph Tutorial: What Is LangGraph and How to Use It?',
'url': 'https://www.datacamp.com/tutorial/langgraph-tutorial',
'content': 'LangGraph is a library within the LangChain ecosystem that provides a framework for defining, coordinating, and executing multiple LLM agents (or chains) in a structured and efficient manner. By managing the flow of data and the sequence of operations, LangGraph allows developers to focus on the high-level logic of their applications rather than the intricacies of agent coordination. Whether you need a chatbot that can handle various types of user requests or a multi-agent system that performs complex tasks, LangGraph provides the tools to build exactly what you need. LangGraph significantly simplifies the development of complex LLM applications by providing a structured framework for managing state and coordinating agent interactions.',
'score': 0.5008063,
'raw_content': None}],
'response_time': 1.38}
```





## 4. Define the graph

For the `StateGraph` you created in the [first tutorial](./1-build-basic-chatbot.md), add `bind_tools` on the LLM. This lets the LLM know the correct JSON format to use if it wants to use the search engine.




Let's first select our LLM:

=== "OpenAI"

    ```shell
    pip install -U "langchain[openai]"
    ```
    ```python
    import os
    from langchain.chat_models import init_chat_model

    os.environ["OPENAI_API_KEY"] = "sk-..."

    llm = init_chat_model("openai:gpt-4.1")
    ```

    👉 Read the [OpenAI integration docs](https://python.langchain.com/docs/integrations/chat/openai/)

=== "Anthropic"

    ```shell
    pip install -U "langchain[anthropic]"
    ```
    ```python
    import os
    from langchain.chat_models import init_chat_model

    os.environ["ANTHROPIC_API_KEY"] = "sk-..."

    llm = init_chat_model("anthropic:claude-3-5-sonnet-latest")
    ```

    👉 Read the [Anthropic integration docs](https://python.langchain.com/docs/integrations/chat/anthropic/)

=== "Azure"

    ```shell
    pip install -U "langchain[openai]"
    ```
    ```python
    import os
    from langchain.chat_models import init_chat_model

    os.environ["AZURE_OPENAI_API_KEY"] = "..."
    os.environ["AZURE_OPENAI_ENDPOINT"] = "..."
    os.environ["OPENAI_API_VERSION"] = "2025-03-01-preview"

    llm = init_chat_model(
        "azure_openai:gpt-4.1",
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    )
    ```
 
    👉 Read the [Azure integration docs](https://python.langchain.com/docs/integrations/chat/azure_chat_openai/)

=== "Google Gemini"

    ```shell
    pip install -U "langchain[google-genai]"
    ```
    ```python
    import os
    from langchain.chat_models import init_chat_model

    os.environ["GOOGLE_API_KEY"] = "..."

    llm = init_chat_model("google_genai:gemini-2.0-flash")
    ```

    👉 Read the [Google GenAI integration docs](https://python.langchain.com/docs/integrations/chat/google_generative_ai/)

=== "AWS Bedrock"

    ```shell
    pip install -U "langchain[aws]"
    ```
    ```python
    from langchain.chat_models import init_chat_model

    # Follow the steps here to configure your credentials:
    # https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html

    llm = init_chat_model(
        "anthropic.claude-3-5-sonnet-20240620-v1:0",
        model_provider="bedrock_converse",
    )
    ```

    👉 Read the [AWS Bedrock integration docs](https://python.langchain.com/docs/integrations/chat/bedrock/)








We can now incorporate it into a `StateGraph`:

API Reference: StateGraph</a> | START</a> | END</a> | add_messages</a></i></sup>

```python hl_lines="14"
from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

# Modification: tell the LLM which tools it can call
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)
```





## 5. Create a function to run the tools

Now, create a function to run the tools if they are called. Do this by adding the tools to a new node called `BasicToolNode` that checks the most recent message in the state and calls tools if the message contains `tool_calls`. It relies on the LLM's `tool_calling` support, which is available in Anthropic, OpenAI, Google Gemini, and a number of other LLM providers.

API Reference: ToolMessage</a></i></sup>

```python
import json

from langchain_core.messages import ToolMessage


class BasicToolNode:
    """A node that runs the tools requested in the last AIMessage."""

    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}


tool_node = BasicToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)
```

!!! note

    If you do not want to build this yourself in the future, you can use LangGraph's prebuilt [ToolNode](https://langchain-ai.github.io/langgraph/reference/agents/#langgraph.prebuilt.tool_node.ToolNode).





## 6. Define the `conditional_edges`

With the tool node added, now you can define the `conditional_edges`.

**Edges** route the control flow from one node to the next. **Conditional edges** start from a single node and usually contain "if" statements to route to different nodes depending on the current graph state. These functions receive the current graph `state` and return a string or list of strings indicating which node(s) to call next.

Next, define a router function called `route_tools` that checks for `tool_calls` in the chatbot's output. Provide this function to the graph by calling `add_conditional_edges`, which tells the graph that whenever the `chatbot` node completes to check this function to see where to go next.




The condition will route to `tools` if tool calls are present and `END` if not. Because the condition can return `END`, you do not need to explicitly set a `finish_point` this time.

```python
def route_tools(
    state: State,
):
    """
    Use in the conditional_edge to route to the ToolNode if the last message
    has tool calls. Otherwise, route to the end.
    """
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return END


# The `tools_condition` function returns "tools" if the chatbot asks to use a tool, and "END" if
# it is fine directly responding. This conditional routing defines the main agent loop.
graph_builder.add_conditional_edges(
    "chatbot",
    route_tools,
    # The following dictionary lets you tell the graph to interpret the condition's outputs as a specific node
    # It defaults to the identity function, but if you
    # want to use a node named something else apart from "tools",
    # You can update the value of the dictionary to something else
    # e.g., "tools": "my_tools"
    {"tools": "tools", END: END},
)
# Any time a tool is called, we return to the chatbot to decide the next step
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile()
```

!!! note

    You can replace this with the prebuilt [tools_condition](https://langchain-ai.github.io/langgraph/reference/prebuilt/#tools_condition) to be more concise.





## 7. Visualize the graph (optional)

You can visualize the graph using the `get_graph` method and one of the "draw" methods, like `draw_ascii` or `draw_png`. The `draw` methods each require additional dependencies.

```python
from IPython.display import Image, display

try:
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
    # This requires some extra dependencies and is optional
    pass
```





![chatbot-with-tools-diagram](chatbot-with-tools.png)

## 8. Ask the bot questions

Now you can ask the chatbot questions outside its training data:

```python
def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)

while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        stream_graph_updates(user_input)
    except:
        # fallback if input() is not available
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break
```

```
Assistant: [{'text': "To provide you with accurate and up-to-date information about LangGraph, I'll need to search for the latest details. Let me do that for you.", 'type': 'text'}, {'id': 'toolu_01Q588CszHaSvvP2MxRq9zRD', 'input': {'query': 'LangGraph AI tool information'}, 'name': 'tavily_search_results_json', 'type': 'tool_use'}]
Assistant: [{"url": "https://www.langchain.com/langgraph", "content": "LangGraph sets the foundation for how we can build and scale AI workloads \u2014 from conversational agents, complex task automation, to custom LLM-backed experiences that 'just work'. The next chapter in building complex production-ready features with LLMs is agentic, and with LangGraph and LangSmith, LangChain delivers an out-of-the-box solution ..."}, {"url": "https://github.com/langchain-ai/langgraph", "content": "Overview. LangGraph is a library for building stateful, multi-actor applications with LLMs, used to create agent and multi-agent workflows. Compared to other LLM frameworks, it offers these core benefits: cycles, controllability, and persistence. LangGraph allows you to define flows that involve cycles, essential for most agentic architectures ..."}]
Assistant: Based on the search results, I can provide you with information about LangGraph:

1. Purpose:
   LangGraph is a library designed for building stateful, multi-actor applications with Large Language Models (LLMs). It's particularly useful for creating agent and multi-agent workflows.

2. Developer:
   LangGraph is developed by LangChain, a company known for its tools and frameworks in the AI and LLM space.

3. Key Features:
   - Cycles: LangGraph allows the definition of flows that involve cycles, which is essential for most agentic architectures.
   - Controllability: It offers enhanced control over the application flow.
   - Persistence: The library provides ways to maintain state and persistence in LLM-based applications.

4. Use Cases:
   LangGraph can be used for various applications, including:
   - Conversational agents
   - Complex task automation
   - Custom LLM-backed experiences

5. Integration:
   LangGraph works in conjunction with LangSmith, another tool by LangChain, to provide an out-of-the-box solution for building complex, production-ready features with LLMs.

6. Significance:
...
   LangGraph is noted to offer unique benefits compared to other LLM frameworks, particularly in its ability to handle cycles, provide controllability, and maintain persistence.

LangGraph appears to be a significant tool in the evolving landscape of LLM-based application development, offering developers new ways to create more complex, stateful, and interactive AI systems.
Goodbye!
```





## 9. Use prebuilts

For ease of use, adjust your code to replace the following with LangGraph prebuilt components. These have built in functionality like parallel API execution.

- `BasicToolNode` is replaced with the prebuilt [ToolNode](https://langchain-ai.github.io/langgraph/reference/prebuilt/#toolnode)
- `route_tools` is replaced with the prebuilt [tools_condition](https://langchain-ai.github.io/langgraph/reference/prebuilt/#tools_condition)

=== "OpenAI"

    ```shell
    pip install -U "langchain[openai]"
    ```
    ```python
    import os
    from langchain.chat_models import init_chat_model

    os.environ["OPENAI_API_KEY"] = "sk-..."

    llm = init_chat_model("openai:gpt-4.1")
    ```

    👉 Read the [OpenAI integration docs](https://python.langchain.com/docs/integrations/chat/openai/)

=== "Anthropic"

    ```shell
    pip install -U "langchain[anthropic]"
    ```
    ```python
    import os
    from langchain.chat_models import init_chat_model

    os.environ["ANTHROPIC_API_KEY"] = "sk-..."

    llm = init_chat_model("anthropic:claude-3-5-sonnet-latest")
    ```

    👉 Read the [Anthropic integration docs](https://python.langchain.com/docs/integrations/chat/anthropic/)

=== "Azure"

    ```shell
    pip install -U "langchain[openai]"
    ```
    ```python
    import os
    from langchain.chat_models import init_chat_model

    os.environ["AZURE_OPENAI_API_KEY"] = "..."
    os.environ["AZURE_OPENAI_ENDPOINT"] = "..."
    os.environ["OPENAI_API_VERSION"] = "2025-03-01-preview"

    llm = init_chat_model(
        "azure_openai:gpt-4.1",
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    )
    ```
 
    👉 Read the [Azure integration docs](https://python.langchain.com/docs/integrations/chat/azure_chat_openai/)

=== "Google Gemini"

    ```shell
    pip install -U "langchain[google-genai]"
    ```
    ```python
    import os
    from langchain.chat_models import init_chat_model

    os.environ["GOOGLE_API_KEY"] = "..."

    llm = init_chat_model("google_genai:gemini-2.0-flash")
    ```

    👉 Read the [Google GenAI integration docs](https://python.langchain.com/docs/integrations/chat/google_generative_ai/)

=== "AWS Bedrock"

    ```shell
    pip install -U "langchain[aws]"
    ```
    ```python
    from langchain.chat_models import init_chat_model

    # Follow the steps here to configure your credentials:
    # https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html

    llm = init_chat_model(
        "anthropic.claude-3-5-sonnet-20240620-v1:0",
        model_provider="bedrock_converse",
    )
    ```

    👉 Read the [AWS Bedrock integration docs](https://python.langchain.com/docs/integrations/chat/bedrock/)






```python hl_lines="25 30"
from typing import Annotated

from langchain_tavily import TavilySearch
from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

tool = TavilySearch(max_results=2)
tools = [tool]
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
# Any time a tool is called, we return to the chatbot to decide the next step
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile()
```

Source: https://langchain-ai.github.io/langgraph/tutorials/get-started/3-add-memory/

# Add memory

The chatbot can now [use tools](./2-add-tools.md) to answer user questions, but it does not remember the context of previous interactions. This limits its ability to have coherent, multi-turn conversations.

LangGraph solves this problem through **persistent checkpointing**. If you provide a `checkpointer` when compiling the graph and a `thread_id` when calling your graph, LangGraph automatically saves the state after each step. When you invoke the graph again using the same `thread_id`, the graph loads its saved state, allowing the chatbot to pick up where it left off.

We will see later that **checkpointing** is _much_ more powerful than simple chat memory - it lets you save and resume complex state at any time for error recovery, human-in-the-loop workflows, time travel interactions, and more. But first, let's add checkpointing to enable multi-turn conversations.

!!! note

    This tutorial builds on [Add tools](./2-add-tools.md).

## 1. Create a `MemorySaver` checkpointer

Create a `MemorySaver` checkpointer:

API Reference: InMemorySaver</a></i></sup>

```python
from langgraph.checkpoint.memory import InMemorySaver

memory = InMemorySaver()
```





This is in-memory checkpointer, which is convenient for the tutorial. However, in a production application, you would likely change this to use `SqliteSaver` or `PostgresSaver` and connect a database.

## 2. Compile the graph

Compile the graph with the provided checkpointer, which will checkpoint the `State` as the graph works through each node:

```python
graph = graph_builder.compile(checkpointer=memory)
```





## 3. Interact with your chatbot

Now you can interact with your bot!

1.  Pick a thread to use as the key for this conversation.

    ```python
    config = {"configurable": {"thread_id": "1"}}
    ```





2.  Call your chatbot:

    ```python
    user_input = "Hi there! My name is Will."

    # The config is the **second positional argument** to stream() or invoke()!
    events = graph.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config,
        stream_mode="values",
    )
    for event in events:
        event["messages"][-1].pretty_print()
    ```

    ```
    ================================ Human Message =================================

    Hi there! My name is Will.
    ================================== Ai Message ==================================

    Hello Will! It's nice to meet you. How can I assist you today? Is there anything specific you'd like to know or discuss?
    ```

    !!! note

        The config was provided as the **second positional argument** when calling our graph. It importantly is _not_ nested within the graph inputs (`{'messages': []}`).





## 4. Ask a follow up question

Ask a follow up question:

```python
user_input = "Remember my name?"

# The config is the **second positional argument** to stream() or invoke()!
events = graph.stream(
    {"messages": [{"role": "user", "content": user_input}]},
    config,
    stream_mode="values",
)
for event in events:
    event["messages"][-1].pretty_print()
```

```
================================ Human Message =================================

Remember my name?
================================== Ai Message ==================================

Of course, I remember your name, Will. I always try to pay attention to important details that users share with me. Is there anything else you'd like to talk about or any questions you have? I'm here to help with a wide range of topics or tasks.
```





**Notice** that we aren't using an external list for memory: it's all handled by the checkpointer! You can inspect the full execution in this [LangSmith trace](https://smith.langchain.com/public/29ba22b5-6d40-4fbe-8d27-b369e3329c84/r) to see what's going on.

Don't believe me? Try this using a different config.

```python hl_lines="4"
# The only difference is we change the `thread_id` here to "2" instead of "1"
events = graph.stream(
    {"messages": [{"role": "user", "content": user_input}]},
    {"configurable": {"thread_id": "2"}},
    stream_mode="values",
)
for event in events:
    event["messages"][-1].pretty_print()
```

```
================================ Human Message =================================

Remember my name?
================================== Ai Message ==================================

I apologize, but I don't have any previous context or memory of your name. As an AI assistant, I don't retain information from past conversations. Each interaction starts fresh. Could you please tell me your name so I can address you properly in this conversation?
```





**Notice** that the **only** change we've made is to modify the `thread_id` in the config. See this call's [LangSmith trace](https://smith.langchain.com/public/51a62351-2f0a-4058-91cc-9996c5561428/r) for comparison.

## 5. Inspect the state

By now, we have made a few checkpoints across two different threads. But what goes into a checkpoint? To inspect a graph's `state` for a given config at any time, call `get_state(config)`.

```python
snapshot = graph.get_state(config)
snapshot
```

```
StateSnapshot(values={'messages': [HumanMessage(content='Hi there! My name is Will.', additional_kwargs={}, response_metadata={}, id='8c1ca919-c553-4ebf-95d4-b59a2d61e078'), AIMessage(content="Hello Will! It's nice to meet you. How can I assist you today? Is there anything specific you'd like to know or discuss?", additional_kwargs={}, response_metadata={'id': 'msg_01WTQebPhNwmMrmmWojJ9KXJ', 'model': 'claude-3-5-sonnet-20240620', 'stop_reason': 'end_turn', 'stop_sequence': None, 'usage': {'input_tokens': 405, 'output_tokens': 32}}, id='run-58587b77-8c82-41e6-8a90-d62c444a261d-0', usage_metadata={'input_tokens': 405, 'output_tokens': 32, 'total_tokens': 437}), HumanMessage(content='Remember my name?', additional_kwargs={}, response_metadata={}, id='daba7df6-ad75-4d6b-8057-745881cea1ca'), AIMessage(content="Of course, I remember your name, Will. I always try to pay attention to important details that users share with me. Is there anything else you'd like to talk about or any questions you have? I'm here to help with a wide range of topics or tasks.", additional_kwargs={}, response_metadata={'id': 'msg_01E41KitY74HpENRgXx94vag', 'model': 'claude-3-5-sonnet-20240620', 'stop_reason': 'end_turn', 'stop_sequence': None, 'usage': {'input_tokens': 444, 'output_tokens': 58}}, id='run-ffeaae5c-4d2d-4ddb-bd59-5d5cbf2a5af8-0', usage_metadata={'input_tokens': 444, 'output_tokens': 58, 'total_tokens': 502})]}, next=(), config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1ef7d06e-93e0-6acc-8004-f2ac846575d2'}}, metadata={'source': 'loop', 'writes': {'chatbot': {'messages': [AIMessage(content="Of course, I remember your name, Will. I always try to pay attention to important details that users share with me. Is there anything else you'd like to talk about or any questions you have? I'm here to help with a wide range of topics or tasks.", additional_kwargs={}, response_metadata={'id': 'msg_01E41KitY74HpENRgXx94vag', 'model': 'claude-3-5-sonnet-20240620', 'stop_reason': 'end_turn', 'stop_sequence': None, 'usage': {'input_tokens': 444, 'output_tokens': 58}}, id='run-ffeaae5c-4d2d-4ddb-bd59-5d5cbf2a5af8-0', usage_metadata={'input_tokens': 444, 'output_tokens': 58, 'total_tokens': 502})]}}, 'step': 4, 'parents': {}}, created_at='2024-09-27T19:30:10.820758+00:00', parent_config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1ef7d06e-859f-6206-8003-e1bd3c264b8f'}}, tasks=())
```

```
snapshot.next  # (since the graph ended this turn, `next` is empty. If you fetch a state from within a graph invocation, next tells which node will execute next)
```





The snapshot above contains the current state values, corresponding config, and the `next` node to process. In our case, the graph has reached an `END` state, so `next` is empty.

**Congratulations!** Your chatbot can now maintain conversation state across sessions thanks to LangGraph's checkpointing system. This opens up exciting possibilities for more natural, contextual interactions. LangGraph's checkpointing even handles **arbitrarily complex graph states**, which is much more expressive and powerful than simple chat memory.

Check out the code snippet below to review the graph from this tutorial:

=== "OpenAI"

    ```shell
    pip install -U "langchain[openai]"
    ```
    ```python
    import os
    from langchain.chat_models import init_chat_model

    os.environ["OPENAI_API_KEY"] = "sk-..."

    llm = init_chat_model("openai:gpt-4.1")
    ```

    👉 Read the [OpenAI integration docs](https://python.langchain.com/docs/integrations/chat/openai/)

=== "Anthropic"

    ```shell
    pip install -U "langchain[anthropic]"
    ```
    ```python
    import os
    from langchain.chat_models import init_chat_model

    os.environ["ANTHROPIC_API_KEY"] = "sk-..."

    llm = init_chat_model("anthropic:claude-3-5-sonnet-latest")
    ```

    👉 Read the [Anthropic integration docs](https://python.langchain.com/docs/integrations/chat/anthropic/)

=== "Azure"

    ```shell
    pip install -U "langchain[openai]"
    ```
    ```python
    import os
    from langchain.chat_models import init_chat_model

    os.environ["AZURE_OPENAI_API_KEY"] = "..."
    os.environ["AZURE_OPENAI_ENDPOINT"] = "..."
    os.environ["OPENAI_API_VERSION"] = "2025-03-01-preview"

    llm = init_chat_model(
        "azure_openai:gpt-4.1",
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    )
    ```
 
    👉 Read the [Azure integration docs](https://python.langchain.com/docs/integrations/chat/azure_chat_openai/)

=== "Google Gemini"

    ```shell
    pip install -U "langchain[google-genai]"
    ```
    ```python
    import os
    from langchain.chat_models import init_chat_model

    os.environ["GOOGLE_API_KEY"] = "..."

    llm = init_chat_model("google_genai:gemini-2.0-flash")
    ```

    👉 Read the [Google GenAI integration docs](https://python.langchain.com/docs/integrations/chat/google_generative_ai/)

=== "AWS Bedrock"

    ```shell
    pip install -U "langchain[aws]"
    ```
    ```python
    from langchain.chat_models import init_chat_model

    # Follow the steps here to configure your credentials:
    # https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html

    llm = init_chat_model(
        "anthropic.claude-3-5-sonnet-20240620-v1:0",
        model_provider="bedrock_converse",
    )
    ```

    👉 Read the [AWS Bedrock integration docs](https://python.langchain.com/docs/integrations/chat/bedrock/)




```python hl_lines="36 37"
from typing import Annotated

from langchain.chat_models import init_chat_model
from langchain_tavily import TavilySearch
from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

tool = TavilySearch(max_results=2)
tools = [tool]
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.set_entry_point("chatbot")
memory = InMemorySaver()
graph = graph_builder.compile(checkpointer=memory)
```

Source: https://langchain-ai.github.io/langgraph/tutorials/get-started/4-human-in-the-loop/

# Add human-in-the-loop controls

Agents can be unreliable and may need human input to successfully accomplish tasks. Similarly, for some actions, you may want to require human approval before running to ensure that everything is running as intended.

LangGraph's [persistence](../../concepts/persistence.md) layer supports **human-in-the-loop** workflows, allowing execution to pause and resume based on user feedback. The primary interface to this functionality is the [`interrupt`](../../how-tos/human_in_the_loop/add-human-in-the-loop.md) function. Calling `interrupt` inside a node will pause execution. Execution can be resumed, together with new input from a human, by passing in a [Command](../../concepts/low_level.md#command).

`interrupt` is ergonomically similar to Python's built-in `input()`, [with some caveats](../../how-tos/human_in_the_loop/add-human-in-the-loop.md).




!!! note

    This tutorial builds on [Add memory](./3-add-memory.md).

## 1. Add the `human_assistance` tool

Starting with the existing code from the [Add memory to the chatbot](./3-add-memory.md) tutorial, add the `human_assistance` tool to the chatbot. This tool uses `interrupt` to receive information from a human.

Let's first select a chat model:

=== "OpenAI"

    ```shell
    pip install -U "langchain[openai]"
    ```
    ```python
    import os
    from langchain.chat_models import init_chat_model

    os.environ["OPENAI_API_KEY"] = "sk-..."

    llm = init_chat_model("openai:gpt-4.1")
    ```

    👉 Read the [OpenAI integration docs](https://python.langchain.com/docs/integrations/chat/openai/)

=== "Anthropic"

    ```shell
    pip install -U "langchain[anthropic]"
    ```
    ```python
    import os
    from langchain.chat_models import init_chat_model

    os.environ["ANTHROPIC_API_KEY"] = "sk-..."

    llm = init_chat_model("anthropic:claude-3-5-sonnet-latest")
    ```

    👉 Read the [Anthropic integration docs](https://python.langchain.com/docs/integrations/chat/anthropic/)

=== "Azure"

    ```shell
    pip install -U "langchain[openai]"
    ```
    ```python
    import os
    from langchain.chat_models import init_chat_model

    os.environ["AZURE_OPENAI_API_KEY"] = "..."
    os.environ["AZURE_OPENAI_ENDPOINT"] = "..."
    os.environ["OPENAI_API_VERSION"] = "2025-03-01-preview"

    llm = init_chat_model(
        "azure_openai:gpt-4.1",
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    )
    ```
 
    👉 Read the [Azure integration docs](https://python.langchain.com/docs/integrations/chat/azure_chat_openai/)

=== "Google Gemini"

    ```shell
    pip install -U "langchain[google-genai]"
    ```
    ```python
    import os
    from langchain.chat_models import init_chat_model

    os.environ["GOOGLE_API_KEY"] = "..."

    llm = init_chat_model("google_genai:gemini-2.0-flash")
    ```

    👉 Read the [Google GenAI integration docs](https://python.langchain.com/docs/integrations/chat/google_generative_ai/)

=== "AWS Bedrock"

    ```shell
    pip install -U "langchain[aws]"
    ```
    ```python
    from langchain.chat_models import init_chat_model

    # Follow the steps here to configure your credentials:
    # https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html

    llm = init_chat_model(
        "anthropic.claude-3-5-sonnet-20240620-v1:0",
        model_provider="bedrock_converse",
    )
    ```

    👉 Read the [AWS Bedrock integration docs](https://python.langchain.com/docs/integrations/chat/bedrock/)








We can now incorporate it into our `StateGraph` with an additional tool:

```python hl_lines="12 19 20 21 22 23"
from typing import Annotated

from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from typing_extensions import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from langgraph.types import Command, interrupt

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

@tool
def human_assistance(query: str) -> str:
    """Request assistance from a human."""
    human_response = interrupt({"query": query})
    return human_response["data"]

tool = TavilySearch(max_results=2)
tools = [tool, human_assistance]
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    # Because we will be interrupting during tool execution,
    # we disable parallel tool calling to avoid repeating any
    # tool invocations when we resume.
    assert len(message.tool_calls) <= 1
    return {"messages": [message]}

graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
```





!!! tip

    For more information and examples of human-in-the-loop workflows, see [Human-in-the-loop](../../concepts/human_in_the_loop.md).

## 2. Compile the graph

We compile the graph with a checkpointer, as before:

```python
memory = InMemorySaver()

graph = graph_builder.compile(checkpointer=memory)
```





## 3. Visualize the graph (optional)

Visualizing the graph, you get the same layout as before – just with the added tool!

```python
from IPython.display import Image, display

try:
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
    # This requires some extra dependencies and is optional
    pass
```





![chatbot-with-tools-diagram](chatbot-with-tools.png)

## 4. Prompt the chatbot

Now, prompt the chatbot with a question that will engage the new `human_assistance` tool:

```python
user_input = "I need some expert guidance for building an AI agent. Could you request assistance for me?"
config = {"configurable": {"thread_id": "1"}}

events = graph.stream(
    {"messages": [{"role": "user", "content": user_input}]},
    config,
    stream_mode="values",
)
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()
```

```
================================ Human Message =================================

I need some expert guidance for building an AI agent. Could you request assistance for me?
================================== Ai Message ==================================

[{'text': "Certainly! I'd be happy to request expert assistance for you regarding building an AI agent. To do this, I'll use the human_assistance function to relay your request. Let me do that for you now.", 'type': 'text'}, {'id': 'toolu_01ABUqneqnuHNuo1vhfDFQCW', 'input': {'query': 'A user is requesting expert guidance for building an AI agent. Could you please provide some expert advice or resources on this topic?'}, 'name': 'human_assistance', 'type': 'tool_use'}]
Tool Calls:
  human_assistance (toolu_01ABUqneqnuHNuo1vhfDFQCW)
 Call ID: toolu_01ABUqneqnuHNuo1vhfDFQCW
  Args:
    query: A user is requesting expert guidance for building an AI agent. Could you please provide some expert advice or resources on this topic?
```





The chatbot generated a tool call, but then execution has been interrupted. If you inspect the graph state, you see that it stopped at the tools node:

```python
snapshot = graph.get_state(config)
snapshot.next
```

```
('tools',)
```





!!! info Additional information

    Take a closer look at the `human_assistance` tool:

    ```python
    @tool
    def human_assistance(query: str) -> str:
        """Request assistance from a human."""
        human_response = interrupt({"query": query})
        return human_response["data"]
    ```

    Similar to Python's built-in `input()` function, calling `interrupt` inside the tool will pause execution. Progress is persisted based on the [checkpointer](../../concepts/persistence.md#checkpointer-libraries); so if it is persisting with Postgres, it can resume at any time as long as the database is alive. In this example, it is persisting with the in-memory checkpointer and can resume any time if the Python kernel is running.




## 5. Resume execution

To resume execution, pass a [`Command`](../../concepts/low_level.md#command) object containing data expected by the tool. The format of this data can be customized based on needs.

For this example, use a dict with a key `"data"`:

```python
human_response = (
    "We, the experts are here to help! We'd recommend you check out LangGraph to build your agent."
    " It's much more reliable and extensible than simple autonomous agents."
)

human_command = Command(resume={"data": human_response})

events = graph.stream(human_command, config, stream_mode="values")
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()
```

```
================================== Ai Message ==================================

[{'text': "Certainly! I'd be happy to request expert assistance for you regarding building an AI agent. To do this, I'll use the human_assistance function to relay your request. Let me do that for you now.", 'type': 'text'}, {'id': 'toolu_01ABUqneqnuHNuo1vhfDFQCW', 'input': {'query': 'A user is requesting expert guidance for building an AI agent. Could you please provide some expert advice or resources on this topic?'}, 'name': 'human_assistance', 'type': 'tool_use'}]
Tool Calls:
  human_assistance (toolu_01ABUqneqnuHNuo1vhfDFQCW)
 Call ID: toolu_01ABUqneqnuHNuo1vhfDFQCW
  Args:
    query: A user is requesting expert guidance for building an AI agent. Could you please provide some expert advice or resources on this topic?
================================= Tool Message =================================
Name: human_assistance

We, the experts are here to help! We'd recommend you check out LangGraph to build your agent. It's much more reliable and extensible than simple autonomous agents.
================================== Ai Message ==================================

Thank you for your patience. I've received some expert advice regarding your request for guidance on building an AI agent. Here's what the experts have suggested:

The experts recommend that you look into LangGraph for building your AI agent. They mention that LangGraph is a more reliable and extensible option compared to simple autonomous agents.

LangGraph is likely a framework or library designed specifically for creating AI agents with advanced capabilities. Here are a few points to consider based on this recommendation:

1. Reliability: The experts emphasize that LangGraph is more reliable than simpler autonomous agent approaches. This could mean it has better stability, error handling, or consistent performance.

2. Extensibility: LangGraph is described as more extensible, which suggests that it probably offers a flexible architecture that allows you to easily add new features or modify existing ones as your agent's requirements evolve.

3. Advanced capabilities: Given that it's recommended over "simple autonomous agents," LangGraph likely provides more sophisticated tools and techniques for building complex AI agents.
...
2. Look for tutorials or guides specifically focused on building AI agents with LangGraph.
3. Check if there are any community forums or discussion groups where you can ask questions and get support from other developers using LangGraph.

If you'd like more specific information about LangGraph or have any questions about this recommendation, please feel free to ask, and I can request further assistance from the experts.
Output is truncated. View as a scrollable element or open in a text editor. Adjust cell output settings...
```





The input has been received and processed as a tool message. Review this call's [LangSmith trace](https://smith.langchain.com/public/9f0f87e3-56a7-4dde-9c76-b71675624e91/r) to see the exact work that was done in the above call. Notice that the state is loaded in the first step so that our chatbot can continue where it left off.

**Congratulations!** You've used an `interrupt` to add human-in-the-loop execution to your chatbot, allowing for human oversight and intervention when needed. This opens up the potential UIs you can create with your AI systems. Since you have already added a **checkpointer**, as long as the underlying persistence layer is running, the graph can be paused **indefinitely** and resumed at any time as if nothing had happened.

Check out the code snippet below to review the graph from this tutorial:

=== "OpenAI"

    ```shell
    pip install -U "langchain[openai]"
    ```
    ```python
    import os
    from langchain.chat_models import init_chat_model

    os.environ["OPENAI_API_KEY"] = "sk-..."

    llm = init_chat_model("openai:gpt-4.1")
    ```

    👉 Read the [OpenAI integration docs](https://python.langchain.com/docs/integrations/chat/openai/)

=== "Anthropic"

    ```shell
    pip install -U "langchain[anthropic]"
    ```
    ```python
    import os
    from langchain.chat_models import init_chat_model

    os.environ["ANTHROPIC_API_KEY"] = "sk-..."

    llm = init_chat_model("anthropic:claude-3-5-sonnet-latest")
    ```

    👉 Read the [Anthropic integration docs](https://python.langchain.com/docs/integrations/chat/anthropic/)

=== "Azure"

    ```shell
    pip install -U "langchain[openai]"
    ```
    ```python
    import os
    from langchain.chat_models import init_chat_model

    os.environ["AZURE_OPENAI_API_KEY"] = "..."
    os.environ["AZURE_OPENAI_ENDPOINT"] = "..."
    os.environ["OPENAI_API_VERSION"] = "2025-03-01-preview"

    llm = init_chat_model(
        "azure_openai:gpt-4.1",
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    )
    ```
 
    👉 Read the [Azure integration docs](https://python.langchain.com/docs/integrations/chat/azure_chat_openai/)

=== "Google Gemini"

    ```shell
    pip install -U "langchain[google-genai]"
    ```
    ```python
    import os
    from langchain.chat_models import init_chat_model

    os.environ["GOOGLE_API_KEY"] = "..."

    llm = init_chat_model("google_genai:gemini-2.0-flash")
    ```

    👉 Read the [Google GenAI integration docs](https://python.langchain.com/docs/integrations/chat/google_generative_ai/)

=== "AWS Bedrock"

    ```shell
    pip install -U "langchain[aws]"
    ```
    ```python
    from langchain.chat_models import init_chat_model

    # Follow the steps here to configure your credentials:
    # https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html

    llm = init_chat_model(
        "anthropic.claude-3-5-sonnet-20240620-v1:0",
        model_provider="bedrock_converse",
    )
    ```

    👉 Read the [AWS Bedrock integration docs](https://python.langchain.com/docs/integrations/chat/bedrock/)


API Reference: TavilySearch</a> | tool</a> | InMemorySaver</a> | StateGraph</a> | START</a> | END</a> | add_messages</a> | ToolNode</a> | tools_condition</a> | Command</a> | interrupt</a></i></sup>

```python
from typing import Annotated

from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from typing_extensions import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command, interrupt

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

@tool
def human_assistance(query: str) -> str:
    """Request assistance from a human."""
    human_response = interrupt({"query": query})
    return human_response["data"]

tool = TavilySearch(max_results=2)
tools = [tool, human_assistance]
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    assert(len(message.tool_calls) <= 1)
    return {"messages": [message]}

graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

memory = InMemorySaver()
graph = graph_builder.compile(checkpointer=memory)
```

Source: https://langchain-ai.github.io/langgraph/tutorials/get-started/5-customize-state/

# Customize state

In this tutorial, you will add additional fields to the state to define complex behavior without relying on the message list. The chatbot will use its search tool to find specific information and forward them to a human for review.

!!! note

    This tutorial builds on [Add human-in-the-loop controls](./4-human-in-the-loop.md).

## 1. Add keys to the state

Update the chatbot to research the birthday of an entity by adding `name` and `birthday` keys to the state:

API Reference: add_messages</a></i></sup>

```python hl_lines="10 11"
from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[list, add_messages]
    name: str
    birthday: str
```





Adding this information to the state makes it easily accessible by other graph nodes (like a downstream node that stores or processes the information), as well as the graph's persistence layer.

## 2. Update the state inside the tool

Now, populate the state keys inside of the `human_assistance` tool. This allows a human to review the information before it is stored in the state. Use [`Command`](../../concepts/low_level.md#using-inside-tools) to issue a state update from inside the tool.

API Reference: ToolMessage</a> | InjectedToolCallId</a> | tool</a> | Command</a> | interrupt</a></i></sup>

```python
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool

from langgraph.types import Command, interrupt

@tool
# Note that because we are generating a ToolMessage for a state update, we
# generally require the ID of the corresponding tool call. We can use
# LangChain's InjectedToolCallId to signal that this argument should not
# be revealed to the model in the tool's schema.
def human_assistance(
    name: str, birthday: str, tool_call_id: Annotated[str, InjectedToolCallId]
) -> str:
    """Request assistance from a human."""
    human_response = interrupt(
        {
            "question": "Is this correct?",
            "name": name,
            "birthday": birthday,
        },
    )
    # If the information is correct, update the state as-is.
    if human_response.get("correct", "").lower().startswith("y"):
        verified_name = name
        verified_birthday = birthday
        response = "Correct"
    # Otherwise, receive information from the human reviewer.
    else:
        verified_name = human_response.get("name", name)
        verified_birthday = human_response.get("birthday", birthday)
        response = f"Made a correction: {human_response}"

    # This time we explicitly update the state with a ToolMessage inside
    # the tool.
    state_update = {
        "name": verified_name,
        "birthday": verified_birthday,
        "messages": [ToolMessage(response, tool_call_id=tool_call_id)],
    }
    # We return a Command object in the tool to update our state.
    return Command(update=state_update)
```





The rest of the graph stays the same.

## 3. Prompt the chatbot

Prompt the chatbot to look up the "birthday" of the LangGraph library and direct the chatbot to reach out to the `human_assistance` tool once it has the required information. By setting `name` and `birthday` in the arguments for the tool, you force the chatbot to generate proposals for these fields.

```python
user_input = (
    "Can you look up when LangGraph was released? "
    "When you have the answer, use the human_assistance tool for review."
)
config = {"configurable": {"thread_id": "1"}}

events = graph.stream(
    {"messages": [{"role": "user", "content": user_input}]},
    config,
    stream_mode="values",
)
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()
```





```
================================ Human Message =================================

Can you look up when LangGraph was released? When you have the answer, use the human_assistance tool for review.
================================== Ai Message ==================================

[{'text': "Certainly! I'll start by searching for information about LangGraph's release date using the Tavily search function. Then, I'll use the human_assistance tool for review.", 'type': 'text'}, {'id': 'toolu_01JoXQPgTVJXiuma8xMVwqAi', 'input': {'query': 'LangGraph release date'}, 'name': 'tavily_search_results_json', 'type': 'tool_use'}]
Tool Calls:
  tavily_search_results_json (toolu_01JoXQPgTVJXiuma8xMVwqAi)
 Call ID: toolu_01JoXQPgTVJXiuma8xMVwqAi
  Args:
    query: LangGraph release date
================================= Tool Message =================================
Name: tavily_search_results_json

[{"url": "https://blog.langchain.dev/langgraph-cloud/", "content": "We also have a new stable release of LangGraph. By LangChain 6 min read Jun 27, 2024 (Oct '24) Edit: Since the launch of LangGraph Platform, we now have multiple deployment options alongside LangGraph Studio - which now fall under LangGraph Platform. LangGraph Platform is synonymous with our Cloud SaaS deployment option."}, {"url": "https://changelog.langchain.com/announcements/langgraph-cloud-deploy-at-scale-monitor-carefully-iterate-boldly", "content": "LangChain - Changelog | ☁ 🚀 LangGraph Platform: Deploy at scale, monitor LangChain LangSmith LangGraph LangChain LangSmith LangGraph LangChain LangSmith LangGraph LangChain Changelog Sign up for our newsletter to stay up to date DATE: The LangChain Team LangGraph LangGraph Platform ☁ 🚀 LangGraph Platform: Deploy at scale, monitor carefully, iterate boldly DATE: June 27, 2024 AUTHOR: The LangChain Team LangGraph Platform is now in closed beta, offering scalable, fault-tolerant deployment for LangGraph agents. LangGraph Platform also includes a new playground-like studio for debugging agent failure modes and quick iteration: Join the waitlist today for LangGraph Platform. And to learn more, read our blog post announcement or check out our docs. Subscribe By clicking subscribe, you accept our privacy policy and terms and conditions."}]
================================== Ai Message ==================================

[{'text': "Based on the search results, it appears that LangGraph was already in existence before June 27, 2024, when LangGraph Platform was announced. However, the search results don't provide a specific release date for the original LangGraph. \n\nGiven this information, I'll use the human_assistance tool to review and potentially provide more accurate information about LangGraph's initial release date.", 'type': 'text'}, {'id': 'toolu_01JDQAV7nPqMkHHhNs3j3XoN', 'input': {'name': 'Assistant', 'birthday': '2023-01-01'}, 'name': 'human_assistance', 'type': 'tool_use'}]
Tool Calls:
  human_assistance (toolu_01JDQAV7nPqMkHHhNs3j3XoN)
 Call ID: toolu_01JDQAV7nPqMkHHhNs3j3XoN
  Args:
    name: Assistant
    birthday: 2023-01-01
```

We've hit the `interrupt` in the `human_assistance` tool again.




## 4. Add human assistance

The chatbot failed to identify the correct date, so supply it with information:

```python
human_command = Command(
    resume={
        "name": "LangGraph",
        "birthday": "Jan 17, 2024",
    },
)

events = graph.stream(human_command, config, stream_mode="values")
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()
```





```
================================== Ai Message ==================================

[{'text': "Based on the search results, it appears that LangGraph was already in existence before June 27, 2024, when LangGraph Platform was announced. However, the search results don't provide a specific release date for the original LangGraph. \n\nGiven this information, I'll use the human_assistance tool to review and potentially provide more accurate information about LangGraph's initial release date.", 'type': 'text'}, {'id': 'toolu_01JDQAV7nPqMkHHhNs3j3XoN', 'input': {'name': 'Assistant', 'birthday': '2023-01-01'}, 'name': 'human_assistance', 'type': 'tool_use'}]
Tool Calls:
  human_assistance (toolu_01JDQAV7nPqMkHHhNs3j3XoN)
 Call ID: toolu_01JDQAV7nPqMkHHhNs3j3XoN
  Args:
    name: Assistant
    birthday: 2023-01-01
================================= Tool Message =================================
Name: human_assistance

Made a correction: {'name': 'LangGraph', 'birthday': 'Jan 17, 2024'}
================================== Ai Message ==================================

Thank you for the human assistance. I can now provide you with the correct information about LangGraph's release date.

LangGraph was initially released on January 17, 2024. This information comes from the human assistance correction, which is more accurate than the search results I initially found.

To summarize:
1. LangGraph's original release date: January 17, 2024
2. LangGraph Platform announcement: June 27, 2024

It's worth noting that LangGraph had been in development and use for some time before the LangGraph Platform announcement, but the official initial release of LangGraph itself was on January 17, 2024.
```

Note that these fields are now reflected in the state:

```python
snapshot = graph.get_state(config)

{k: v for k, v in snapshot.values.items() if k in ("name", "birthday")}
```

```
{'name': 'LangGraph', 'birthday': 'Jan 17, 2024'}
```





This makes them easily accessible to downstream nodes (e.g., a node that further processes or stores the information).

## 5. Manually update the state

LangGraph gives a high degree of control over the application state. For instance, at any point (including when interrupted), you can manually override a key using `graph.update_state`:

```python
graph.update_state(config, {"name": "LangGraph (library)"})
```

```
{'configurable': {'thread_id': '1',
  'checkpoint_ns': '',
  'checkpoint_id': '1efd4ec5-cf69-6352-8006-9278f1730162'}}
```





## 6. View the new value

If you call `graph.get_state`, you can see the new value is reflected:

```python
snapshot = graph.get_state(config)

{k: v for k, v in snapshot.values.items() if k in ("name", "birthday")}
```

```
{'name': 'LangGraph (library)', 'birthday': 'Jan 17, 2024'}
```





Manual state updates will [generate a trace](https://smith.langchain.com/public/7ebb7827-378d-49fe-9f6c-5df0e90086c8/r) in LangSmith. If desired, they can also be used to [control human-in-the-loop workflows](../../how-tos/human_in_the_loop/add-human-in-the-loop.md). Use of the `interrupt` function is generally recommended instead, as it allows data to be transmitted in a human-in-the-loop interaction independently of state updates.

**Congratulations!** You've added custom keys to the state to facilitate a more complex workflow, and learned how to generate state updates from inside tools.

Check out the code snippet below to review the graph from this tutorial:

=== "OpenAI"

    ```shell
    pip install -U "langchain[openai]"
    ```
    ```python
    import os
    from langchain.chat_models import init_chat_model

    os.environ["OPENAI_API_KEY"] = "sk-..."

    llm = init_chat_model("openai:gpt-4.1")
    ```

    👉 Read the [OpenAI integration docs](https://python.langchain.com/docs/integrations/chat/openai/)

=== "Anthropic"

    ```shell
    pip install -U "langchain[anthropic]"
    ```
    ```python
    import os
    from langchain.chat_models import init_chat_model

    os.environ["ANTHROPIC_API_KEY"] = "sk-..."

    llm = init_chat_model("anthropic:claude-3-5-sonnet-latest")
    ```

    👉 Read the [Anthropic integration docs](https://python.langchain.com/docs/integrations/chat/anthropic/)

=== "Azure"

    ```shell
    pip install -U "langchain[openai]"
    ```
    ```python
    import os
    from langchain.chat_models import init_chat_model

    os.environ["AZURE_OPENAI_API_KEY"] = "..."
    os.environ["AZURE_OPENAI_ENDPOINT"] = "..."
    os.environ["OPENAI_API_VERSION"] = "2025-03-01-preview"

    llm = init_chat_model(
        "azure_openai:gpt-4.1",
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    )
    ```
 
    👉 Read the [Azure integration docs](https://python.langchain.com/docs/integrations/chat/azure_chat_openai/)

=== "Google Gemini"

    ```shell
    pip install -U "langchain[google-genai]"
    ```
    ```python
    import os
    from langchain.chat_models import init_chat_model

    os.environ["GOOGLE_API_KEY"] = "..."

    llm = init_chat_model("google_genai:gemini-2.0-flash")
    ```

    👉 Read the [Google GenAI integration docs](https://python.langchain.com/docs/integrations/chat/google_generative_ai/)

=== "AWS Bedrock"

    ```shell
    pip install -U "langchain[aws]"
    ```
    ```python
    from langchain.chat_models import init_chat_model

    # Follow the steps here to configure your credentials:
    # https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html

    llm = init_chat_model(
        "anthropic.claude-3-5-sonnet-20240620-v1:0",
        model_provider="bedrock_converse",
    )
    ```

    👉 Read the [AWS Bedrock integration docs](https://python.langchain.com/docs/integrations/chat/bedrock/)




API Reference: TavilySearch</a> | ToolMessage</a> | InjectedToolCallId</a> | tool</a> | InMemorySaver</a> | StateGraph</a> | START</a> | END</a> | add_messages</a> | ToolNode</a> | tools_condition</a> | Command</a> | interrupt</a></i></sup>

```python
from typing import Annotated

from langchain_tavily import TavilySearch
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from typing_extensions import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command, interrupt

class State(TypedDict):
    messages: Annotated[list, add_messages]
    name: str
    birthday: str

@tool
def human_assistance(
    name: str, birthday: str, tool_call_id: Annotated[str, InjectedToolCallId]
) -> str:
    """Request assistance from a human."""
    human_response = interrupt(
        {
            "question": "Is this correct?",
            "name": name,
            "birthday": birthday,
        },
    )
    if human_response.get("correct", "").lower().startswith("y"):
        verified_name = name
        verified_birthday = birthday
        response = "Correct"
    else:
        verified_name = human_response.get("name", name)
        verified_birthday = human_response.get("birthday", birthday)
        response = f"Made a correction: {human_response}"

    state_update = {
        "name": verified_name,
        "birthday": verified_birthday,
        "messages": [ToolMessage(response, tool_call_id=tool_call_id)],
    }
    return Command(update=state_update)


tool = TavilySearch(max_results=2)
tools = [tool, human_assistance]
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    assert(len(message.tool_calls) <= 1)
    return {"messages": [message]}

graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

memory = InMemorySaver()
graph = graph_builder.compile(checkpointer=memory)
```

Source: https://langchain-ai.github.io/langgraph/tutorials/get-started/6-time-travel/

# Time travel

In a typical chatbot workflow, the user interacts with the bot one or more times to accomplish a task. [Memory](./3-add-memory.md) and a [human-in-the-loop](./4-human-in-the-loop.md) enable checkpoints in the graph state and control future responses.

What if you want a user to be able to start from a previous response and explore a different outcome? Or what if you want users to be able to rewind your chatbot's work to fix mistakes or try a different strategy, something that is common in applications like autonomous software engineers?

You can create these types of experiences using LangGraph's built-in **time travel** functionality.

!!! note

    This tutorial builds on [Customize state](./5-customize-state.md).

## 1. Rewind your graph

Rewind your graph by fetching a checkpoint using the graph's `get_state_history` method. You can then resume execution at this previous point in time.




=== "OpenAI"

    ```shell
    pip install -U "langchain[openai]"
    ```
    ```python
    import os
    from langchain.chat_models import init_chat_model

    os.environ["OPENAI_API_KEY"] = "sk-..."

    llm = init_chat_model("openai:gpt-4.1")
    ```

    👉 Read the [OpenAI integration docs](https://python.langchain.com/docs/integrations/chat/openai/)

=== "Anthropic"

    ```shell
    pip install -U "langchain[anthropic]"
    ```
    ```python
    import os
    from langchain.chat_models import init_chat_model

    os.environ["ANTHROPIC_API_KEY"] = "sk-..."

    llm = init_chat_model("anthropic:claude-3-5-sonnet-latest")
    ```

    👉 Read the [Anthropic integration docs](https://python.langchain.com/docs/integrations/chat/anthropic/)

=== "Azure"

    ```shell
    pip install -U "langchain[openai]"
    ```
    ```python
    import os
    from langchain.chat_models import init_chat_model

    os.environ["AZURE_OPENAI_API_KEY"] = "..."
    os.environ["AZURE_OPENAI_ENDPOINT"] = "..."
    os.environ["OPENAI_API_VERSION"] = "2025-03-01-preview"

    llm = init_chat_model(
        "azure_openai:gpt-4.1",
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    )
    ```
 
    👉 Read the [Azure integration docs](https://python.langchain.com/docs/integrations/chat/azure_chat_openai/)

=== "Google Gemini"

    ```shell
    pip install -U "langchain[google-genai]"
    ```
    ```python
    import os
    from langchain.chat_models import init_chat_model

    os.environ["GOOGLE_API_KEY"] = "..."

    llm = init_chat_model("google_genai:gemini-2.0-flash")
    ```

    👉 Read the [Google GenAI integration docs](https://python.langchain.com/docs/integrations/chat/google_generative_ai/)

=== "AWS Bedrock"

    ```shell
    pip install -U "langchain[aws]"
    ```
    ```python
    from langchain.chat_models import init_chat_model

    # Follow the steps here to configure your credentials:
    # https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html

    llm = init_chat_model(
        "anthropic.claude-3-5-sonnet-20240620-v1:0",
        model_provider="bedrock_converse",
    )
    ```

    👉 Read the [AWS Bedrock integration docs](https://python.langchain.com/docs/integrations/chat/bedrock/)




API Reference: TavilySearch</a> | BaseMessage</a> | InMemorySaver</a> | StateGraph</a> | START</a> | END</a> | add_messages</a> | ToolNode</a> | tools_condition</a></i></sup>

```python
from typing import Annotated

from langchain_tavily import TavilySearch
from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

tool = TavilySearch(max_results=2)
tools = [tool]
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

memory = InMemorySaver()
graph = graph_builder.compile(checkpointer=memory)
```





## 2. Add steps

Add steps to your graph. Every step will be checkpointed in its state history:

```python
config = {"configurable": {"thread_id": "1"}}
events = graph.stream(
    {
        "messages": [
            {
                "role": "user",
                "content": (
                    "I'm learning LangGraph. "
                    "Could you do some research on it for me?"
                ),
            },
        ],
    },
    config,
    stream_mode="values",
)
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()
```

```
================================ Human Message =================================

I'm learning LangGraph. Could you do some research on it for me?
================================== Ai Message ==================================

[{'text': "Certainly! I'd be happy to research LangGraph for you. To get the most up-to-date and accurate information, I'll use the Tavily search engine to look this up. Let me do that for you now.", 'type': 'text'}, {'id': 'toolu_01BscbfJJB9EWJFqGrN6E54e', 'input': {'query': 'LangGraph latest information and features'}, 'name': 'tavily_search_results_json', 'type': 'tool_use'}]
Tool Calls:
  tavily_search_results_json (toolu_01BscbfJJB9EWJFqGrN6E54e)
 Call ID: toolu_01BscbfJJB9EWJFqGrN6E54e
  Args:
    query: LangGraph latest information and features
================================= Tool Message =================================
Name: tavily_search_results_json

[{"url": "https://blockchain.news/news/langchain-new-features-upcoming-events-update", "content": "LangChain, a leading platform in the AI development space, has released its latest updates, showcasing new use cases and enhancements across its ecosystem. According to the LangChain Blog, the updates cover advancements in LangGraph Platform, LangSmith's self-improving evaluators, and revamped documentation for LangGraph."}, {"url": "https://blog.langchain.dev/langgraph-platform-announce/", "content": "With these learnings under our belt, we decided to couple some of our latest offerings under LangGraph Platform. LangGraph Platform today includes LangGraph Server, LangGraph Studio, plus the CLI and SDK. ... we added features in LangGraph Server to deliver on a few key value areas. Below, we'll focus on these aspects of LangGraph Platform."}]
================================== Ai Message ==================================

Thank you for your patience. I've found some recent information about LangGraph for you. Let me summarize the key points:

1. LangGraph is part of the LangChain ecosystem, which is a leading platform in AI development.

2. Recent updates and features of LangGraph include:

   a. LangGraph Platform: This seems to be a cloud-based version of LangGraph, though specific details weren't provided in the search results.
...
3. Keep an eye on LangGraph Platform developments, as cloud-based solutions often provide an easier starting point for learners.
4. Consider how LangGraph fits into the broader LangChain ecosystem, especially its interaction with tools like LangSmith.

Is there any specific aspect of LangGraph you'd like to know more about? I'd be happy to do a more focused search on particular features or use cases.
Output is truncated. View as a scrollable element or open in a text editor. Adjust cell output settings...
```

```python
events = graph.stream(
    {
        "messages": [
            {
                "role": "user",
                "content": (
                    "Ya that's helpful. Maybe I'll "
                    "build an autonomous agent with it!"
                ),
            },
        ],
    },
    config,
    stream_mode="values",
)
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()
```

```
================================ Human Message =================================

Ya that's helpful. Maybe I'll build an autonomous agent with it!
================================== Ai Message ==================================

[{'text': "That's an exciting idea! Building an autonomous agent with LangGraph is indeed a great application of this technology. LangGraph is particularly well-suited for creating complex, multi-step AI workflows, which is perfect for autonomous agents. Let me gather some more specific information about using LangGraph for building autonomous agents.", 'type': 'text'}, {'id': 'toolu_01QWNHhUaeeWcGXvA4eHT7Zo', 'input': {'query': 'Building autonomous agents with LangGraph examples and tutorials'}, 'name': 'tavily_search_results_json', 'type': 'tool_use'}]
Tool Calls:
  tavily_search_results_json (toolu_01QWNHhUaeeWcGXvA4eHT7Zo)
 Call ID: toolu_01QWNHhUaeeWcGXvA4eHT7Zo
  Args:
    query: Building autonomous agents with LangGraph examples and tutorials
================================= Tool Message =================================
Name: tavily_search_results_json

[{"url": "https://towardsdatascience.com/building-autonomous-multi-tool-agents-with-gemini-2-0-and-langgraph-ad3d7bd5e79d", "content": "Building Autonomous Multi-Tool Agents with Gemini 2.0 and LangGraph | by Youness Mansar | Jan, 2025 | Towards Data Science Building Autonomous Multi-Tool Agents with Gemini 2.0 and LangGraph A practical tutorial with full code examples for building and running multi-tool agents Towards Data Science LLMs are remarkable — they can memorize vast amounts of information, answer general knowledge questions, write code, generate stories, and even fix your grammar. In this tutorial, we are going to build a simple LLM agent that is equipped with four tools that it can use to answer a user's question. This Agent will have the following specifications: Follow Published in Towards Data Science --------------------------------- Your home for data science and AI. Follow Follow Follow"}, {"url": "https://github.com/anmolaman20/Tools_and_Agents", "content": "GitHub - anmolaman20/Tools_and_Agents: This repository provides resources for building AI agents using Langchain and Langgraph. This repository provides resources for building AI agents using Langchain and Langgraph. This repository provides resources for building AI agents using Langchain and Langgraph. This repository serves as a comprehensive guide for building AI-powered agents using Langchain and Langgraph. It provides hands-on examples, practical tutorials, and resources for developers and AI enthusiasts to master building intelligent systems and workflows. AI Agent Development: Gain insights into creating intelligent systems that think, reason, and adapt in real time. This repository is ideal for AI practitioners, developers exploring language models, or anyone interested in building intelligent systems. This repository provides resources for building AI agents using Langchain and Langgraph."}]
================================== Ai Message ==================================

Great idea! Building an autonomous agent with LangGraph is definitely an exciting project. Based on the latest information I've found, here are some insights and tips for building autonomous agents with LangGraph:

1. Multi-Tool Agents: LangGraph is particularly well-suited for creating autonomous agents that can use multiple tools. This allows your agent to have a diverse set of capabilities and choose the right tool for each task.

2. Integration with Large Language Models (LLMs): You can combine LangGraph with powerful LLMs like Gemini 2.0 to create more intelligent and capable agents. The LLM can serve as the "brain" of your agent, making decisions and generating responses.

3. Workflow Management: LangGraph excels at managing complex, multi-step AI workflows. This is crucial for autonomous agents that need to break down tasks into smaller steps and execute them in the right order.
...
6. Pay attention to how you structure the agent's decision-making process and workflow.
7. Don't forget to implement proper error handling and safety measures, especially if your agent will be interacting with external systems or making important decisions.

Building an autonomous agent is an iterative process, so be prepared to refine and improve your agent over time. Good luck with your project! If you need any more specific information as you progress, feel free to ask.
Output is truncated. View as a scrollable element or open in a text editor. Adjust cell output settings...
```





## 3. Replay the full state history

Now that you have added steps to the chatbot, you can `replay` the full state history to see everything that occurred.

```python
to_replay = None
for state in graph.get_state_history(config):
    print("Num Messages: ", len(state.values["messages"]), "Next: ", state.next)
    print("-" * 80)
    if len(state.values["messages"]) == 6:
        # We are somewhat arbitrarily selecting a specific state based on the number of chat messages in the state.
        to_replay = state
```

```
Num Messages:  8 Next:  ()
--------------------------------------------------------------------------------
Num Messages:  7 Next:  ('chatbot',)
--------------------------------------------------------------------------------
Num Messages:  6 Next:  ('tools',)
--------------------------------------------------------------------------------
Num Messages:  5 Next:  ('chatbot',)
--------------------------------------------------------------------------------
Num Messages:  4 Next:  ('__start__',)
--------------------------------------------------------------------------------
Num Messages:  4 Next:  ()
--------------------------------------------------------------------------------
Num Messages:  3 Next:  ('chatbot',)
--------------------------------------------------------------------------------
Num Messages:  2 Next:  ('tools',)
--------------------------------------------------------------------------------
Num Messages:  1 Next:  ('chatbot',)
--------------------------------------------------------------------------------
Num Messages:  0 Next:  ('__start__',)
--------------------------------------------------------------------------------
```





Checkpoints are saved for every step of the graph. This **spans invocations** so you can rewind across a full thread's history.

## Resume from a checkpoint

Resume from the `to_replay` state, which is after the `chatbot` node in the second graph invocation. Resuming from this point will call the **action** node next.




```python
print(to_replay.next)
print(to_replay.config)
```

```
('tools',)
{'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1efd43e3-0c1f-6c4e-8006-891877d65740'}}
```





## 4. Load a state from a moment-in-time

The checkpoint's `to_replay.config` contains a `checkpoint_id` timestamp. Providing this `checkpoint_id` value tells LangGraph's checkpointer to **load** the state from that moment in time.

```python
# The `checkpoint_id` in the `to_replay.config` corresponds to a state we've persisted to our checkpointer.
for event in graph.stream(None, to_replay.config, stream_mode="values"):
    if "messages" in event:
        event["messages"][-1].pretty_print()
```

```
================================== Ai Message ==================================

[{'text': "That's an exciting idea! Building an autonomous agent with LangGraph is indeed a great application of this technology. LangGraph is particularly well-suited for creating complex, multi-step AI workflows, which is perfect for autonomous agents. Let me gather some more specific information about using LangGraph for building autonomous agents.", 'type': 'text'}, {'id': 'toolu_01QWNHhUaeeWcGXvA4eHT7Zo', 'input': {'query': 'Building autonomous agents with LangGraph examples and tutorials'}, 'name': 'tavily_search_results_json', 'type': 'tool_use'}]
Tool Calls:
  tavily_search_results_json (toolu_01QWNHhUaeeWcGXvA4eHT7Zo)
 Call ID: toolu_01QWNHhUaeeWcGXvA4eHT7Zo
  Args:
    query: Building autonomous agents with LangGraph examples and tutorials
================================= Tool Message =================================
Name: tavily_search_results_json

[{"url": "https://towardsdatascience.com/building-autonomous-multi-tool-agents-with-gemini-2-0-and-langgraph-ad3d7bd5e79d", "content": "Building Autonomous Multi-Tool Agents with Gemini 2.0 and LangGraph | by Youness Mansar | Jan, 2025 | Towards Data Science Building Autonomous Multi-Tool Agents with Gemini 2.0 and LangGraph A practical tutorial with full code examples for building and running multi-tool agents Towards Data Science LLMs are remarkable — they can memorize vast amounts of information, answer general knowledge questions, write code, generate stories, and even fix your grammar. In this tutorial, we are going to build a simple LLM agent that is equipped with four tools that it can use to answer a user's question. This Agent will have the following specifications: Follow Published in Towards Data Science --------------------------------- Your home for data science and AI. Follow Follow Follow"}, {"url": "https://github.com/anmolaman20/Tools_and_Agents", "content": "GitHub - anmolaman20/Tools_and_Agents: This repository provides resources for building AI agents using Langchain and Langgraph. This repository provides resources for building AI agents using Langchain and Langgraph. This repository provides resources for building AI agents using Langchain and Langgraph. This repository serves as a comprehensive guide for building AI-powered agents using Langchain and Langgraph. It provides hands-on examples, practical tutorials, and resources for developers and AI enthusiasts to master building intelligent systems and workflows. AI Agent Development: Gain insights into creating intelligent systems that think, reason, and adapt in real time. This repository is ideal for AI practitioners, developers exploring language models, or anyone interested in building intelligent systems. This repository provides resources for building AI agents using Langchain and Langgraph."}]
================================== Ai Message ==================================

Great idea! Building an autonomous agent with LangGraph is definitely an exciting project. Based on the latest information I've found, here are some insights and tips for building autonomous agents with LangGraph:

1. Multi-Tool Agents: LangGraph is particularly well-suited for creating autonomous agents that can use multiple tools. This allows your agent to have a diverse set of capabilities and choose the right tool for each task.

2. Integration with Large Language Models (LLMs): You can combine LangGraph with powerful LLMs like Gemini 2.0 to create more intelligent and capable agents. The LLM can serve as the "brain" of your agent, making decisions and generating responses.

3. Workflow Management: LangGraph excels at managing complex, multi-step AI workflows. This is crucial for autonomous agents that need to break down tasks into smaller steps and execute them in the right order.
...

Remember, building an autonomous agent is an iterative process. Start simple and gradually increase complexity as you become more comfortable with LangGraph and its capabilities.

Would you like more information on any specific aspect of building your autonomous agent with LangGraph?
Output is truncated. View as a scrollable element or open in a text editor. Adjust cell output settings...
```

The graph resumed execution from the `tools` node. You can tell this is the case since the first value printed above is the response from our search engine tool.




**Congratulations!** You've now used time-travel checkpoint traversal in LangGraph. Being able to rewind and explore alternative paths opens up a world of possibilities for debugging, experimentation, and interactive applications.

## Learn more

Take your LangGraph journey further by exploring deployment and advanced features:

- **[LangGraph Server quickstart](../../tutorials/langgraph-platform/local-server.md)**: Launch a LangGraph server locally and interact with it using the REST API and LangGraph Studio Web UI.



