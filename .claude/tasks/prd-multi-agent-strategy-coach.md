# Product Requirements Document: AI Strategic Co-pilot

## 1. Introduction & Vision

### 1.1. Vision

To create an AI-powered strategic co-pilot that guides business leaders through a rigorous, Socratic process of developing, refining, and testing their organizational strategy. The system will leverage a multi-agent workflow to move beyond superficial analysis and build a robust, logically sound strategic foundation.

### 1.2. Problem Statement

Developing a clear and effective strategy is challenging. Leaders often rely on unstated assumptions, face cognitive biases, and struggle to connect high-level vision with day-to-day operations. Traditional strategy consulting is expensive and not always accessible.

### 1.3. Solution

This product provides a suite of specialized AI agents, managed by a central orchestrator, to engage the user in a structured dialogue. Each agent uses a distinct, research-backed methodology to challenge the user's thinking on different facets of their strategy, from core purpose to operational design and logical consistency.

## 2. User Persona & Story

* **Persona:** A Manager at a large corporation. They are business-savvy but not necessarily an expert in formal strategy frameworks. They are busy, results-oriented, and need to create a clear, defensible strategy to gain alignment and resources within their organization.

* **User Story:** "As a Business Unit Manager, I want to use an interactive tool to guide my thinking so that I can transform my high-level ideas into a logically sound and well-structured strategy document that I can confidently share with my team and senior leadership."

## 3. The User Journey

The user's interaction with the coach is designed to be intuitive and logical, without exposing the complexity of the underlying multi-agent system. The journey follows three main phases:

1. **The "Why" Phase:** The coach begins by helping the user explore and articulate the core purpose of their strategy, engaging the **WHY Agent**. It seeks to answer: "Why is this strategy needed?" and "What is the fundamental goal or problem to be solved?"

2. **The "How" Phase:** Once the "Why" is established, the coach transitions to exploring *how* the goal could be achieved. This phase leverages the **Analogy Agent** to find a causal model for success and the **Logic Agent** to structure the argument.

3. **The "What" Phase:** Finally, the coach works with the user to flesh out the specific details of the strategy using the **Strategy Map Agent**. This includes formalizing the logic, creating a visual map of the components, and using the **Open Strategy Agent** to consider implementation and stakeholder engagement.

## 4. System Architecture & Agentic Workflow

The system is designed around a central **Orchestrator Agent** that manages the flow of information between the user (via the **Conversation Stream**) and a team of specialist agents. The **Strategy Map Agent** acts as a persistent state manager, continuously updating the strategy as the conversation progresses.

### 4.1. High-Level Workflow

1. The **Conversation Stream** captures user input.

2. The **Orchestrator Agent** receives the `current conversation state`.

3. At each turn, the Orchestrator sends the `current conversation state` to the **Strategy Map Agent**, which reads the existing strategy JSON, updates it with new information, and saves it.

4. The Orchestrator receives the `updated strategy map state` back from the Strategy Map Agent.

5. Based on the conversation and map state, the Orchestrator routes tasks to the appropriate **Specialist Agent** (WHY, Logic, etc.).

6. The Specialist Agent returns its output (questions, topics) to the Orchestrator.

7. The Orchestrator synthesizes a `next response` and sends it to the Conversation Stream.

8. This loop continues until the strategy is complete.

### 4.2. System Diagram

```
+-----------------------+      +--------------------------+
|                       |      |                          |
|  Conversation Stream  |----->|   Strategy Map (JSON)    |
|    (User Interface)   |<-----|      (State File)        |
|                       |      |                          |
+-----------+-----------+      +------------+-------------+
            ^                               ^
            | Sends next response           | Reads/Writes Map State
            |                               |
+-----------v-------------------------------v-----------+
|                                                       |
|                  Orchestrator Agent                   |
|                (LangGraph StateGraph)                 |
|                                                       |
+--+-------------------------------------------------+--+
   |                                                 ^
   | Routes State to                                 | Receives Agent Output
   | Specialist Agents                               | (Questions, Topics, Plans)
   |                                                 |
+--v-------------------------------------------------+--+
|                                                       |
|  Specialist Agents (Worker Nodes in LangGraph)        |
|                                                       |
| +-------------------+ +-----------------------------+ |
| |    WHY Agent      | |        Analogy Agent        | |
| +-------------------+ +-----------------------------+ |
| |    Logic Agent    | |     Open Strategy Agent     | |
| +-------------------+ +-----------------------------+ |
|                                                       |
+-------------------------------------------------------+

```

## 5. Core Components & Agent Profiles

### 5.1. Conversation Stream

* **Role:** The primary user interface for the conversation.

* **Function:** Captures user inputs and displays responses from the Orchestrator.

### 5.2. Orchestrator Agent

* **Role:** The central controller and "brain" of the system.

* **Function:** Manages the conversation flow, routes information to all specialist agents, and synthesizes their outputs into a final, user-facing response.

### 5.3. Specialist Agents

#### 5.3.1. Strategy Map Agent
* **Core Function:** To build and maintain a visual, holistic representation of the user's strategy. It uses the Kaplan & Norton Strategy Map framework as its base but replaces the traditional top-level "Financial Perspective" with the modern, more comprehensive **Six Value Components** from the Integrated Reporting framework. This ensures the strategy is oriented towards holistic value creation, not just financial returns.
* **Inputs:** `Current conversation state` from the Orchestrator.
* **Outputs:** `Current strategy map state` sent back to the Orchestrator.
* **Methodology:** The agent guides the user through the four perspectives of the strategy map, building a cause-and-effect story based on an "outside-in" logic:
    1.  **Stakeholder & Customer Perspective:** Clarifies the value proposition for key stakeholders, starting with the fundamental problem the organization solves for them.
    2.  **Internal Process Perspective:** Defines the critical processes the organization must excel at to deliver on its value proposition.
    3.  **Learning & Growth Perspective:** Identifies the intangible assets needed for the strategy (Human, Information, and Organization Capital).
    4.  **Value Creation Perspective:** Defines the ultimate strategic objectives by measuring the intended impact (increase, decrease, or transformation) on the **Six Value Components**:
        * **Financial Value**
        * **Manufactured Value**
        * **Intellectual Value**
        * **Human Value**
        * **Social & Relationship Value**
        * **Natural Value**

#### 5.3.2. WHY Agent
* **Core Function:** To act as an expert facilitator inspired by Simon Sinek's "Start with Why" methodology. Its purpose is to guide the user in discovering and articulating their organization's core purpose—its WHY. This agent ensures the entire strategy is built on an authentic, inspiring, and human-centric foundation.
* **Inputs:** `Conversation state` from the Orchestrator.
* **Outputs:** `Returns questions on value creation and customer value proposition`.
* **Methodology:** The agent uses a Socratic, introspective process focused on uncovering the user's foundational beliefs. It does not invent a WHY; it helps the user discover the one that already exists by looking to the past.
    * **The Golden Circle:** The core framework used to structure the conversation, moving from the inside out: WHY, HOW, WHAT.
    * **Discovery, Not Invention:** The agent operates on the principle that an organization's WHY comes from its origin story, its moments of greatest pride, and the deeply held beliefs of its founders and leaders.
    * **Biology over Business:** The agent frames the importance of the WHY in the context of human decision-making, explaining that the WHY appeals to the limbic brain, which drives trust, loyalty, and behavior.
* **Coaching Workflow:**
    1.  **Deconstruct the WHAT & HOW:** Establishes a baseline of the user's current thinking.
    2.  **Mine the Past for the WHY:** Asks probing questions to uncover the origin story and emotional drivers.
    3.  **Distill the WHY Statement:** Helps synthesize stories into a concise "To..." statement.
    4.  **Define the HOWs:** Guides the user to articulate their values as actionable verbs.
    5.  **Connect to the WHATs:** Helps the user connect their products/services as tangible proof of their WHY.

#### 5.3.3. Analogy Agent
* **Core Function:** To act as an expert strategic coach using the Carroll & Sørensen method of analogical reasoning. Its purpose is to guide the user in developing a robust, theory-based strategy by moving beyond superficial comparisons to uncover deep causal logic.
* **Inputs:** `Conversation state` from the Orchestrator.
* **Outputs:** `Returns questions on operations and organizational design`.
* **Methodology:** The agent facilitates a structured process to build and test a strategic analogy.
    * **Source vs. Target:** The user's company is the `target`; the company it is compared to is the `source`.
    * **Horizontal vs. Vertical Relations:** This is the critical distinction. The agent constantly pushes the user from **horizontal relations** (e.g., "Company A has feature X, and we have feature X") to **vertical relations** (the causal theory of *why* the source succeeded).
    * **Positive & Negative Analogies:** The agent insists on analyzing both similarities (`positive`) and differences (`negative`) to avoid confirmation bias.
* **Coaching Workflow:**
    1.  **Define Target & Conclusion:** Asks the user to state their company (`target`) and desired outcome (`conclusion`).
    2.  **Select a Source:** Instructs the user to identify a company (`source`) that has already achieved the desired `conclusion`.
    3.  **Decompose the Analogy (Horizontal):** Prompts the user to list key similarities (`positive analogies`) and differences (`negative analogies`).
    4.  **Uncover Causal Theory (Vertical):** Asks probing questions to force the user to articulate the source's theory of success.
    5.  **Apply & Test the Theory:** Guides the user to apply the source's causal theory to their own company, using the horizontal analogies.
    6.  **Formulate Strategy:** Helps the user synthesize the analysis into a unique, firm-specific theory of success.

#### 5.3.4. Logic Agent
* **Core Function:** To ensure the user's strategy is a rigorously logical and defensible argument, based on the principles of deductive logic.
* **Inputs:** `Conversation state` and `current strategy map state` from the Orchestrator.
* **Outputs:** `Returns list of topics to discuss` to ensure all parts of the strategic argument are addressed.

#### 5.3.5. Open Strategy Agent
* **Core Function:** To act as an expert facilitator of **Open Strategy**. Its purpose is to guide the user in designing an inclusive, transparent, and collaborative process to validate, refine, and mobilize their strategy for successful implementation.
* **Inputs:** `Sends final strategy map` from the Orchestrator.
* **Outputs:** `Returns strategy testing plan`.
* **Methodology:** The agent's framework is based on the principles of Open Strategy by Matzler, Hautz, et al. It focuses on changing the *process* of strategy to overcome bias, fuel innovation, and build deep organizational commitment.
    * **The Problem with Closed Strategy:** The agent can explain the common "pathologies" of traditional strategy: becoming too similar to competitors (isomorphism), trapping good ideas in silos, and developing unpopular strategies that fail during implementation.
    * **The Core Solution:** The agent advocates for actively involving a diverse group of actors (frontline employees, experts, customers, suppliers) in strategy deliberations.
    * **Three Phases of Strategy:** The agent tailors its guidance based on whether the user is in the phase of **Idea Generation**, **Strategy Formulation**, or **Strategy Mobilization**.
* **Coaching Workflow:**
    1.  **Define the Strategic Challenge & Phase:** The agent first asks the user to clarify their goal. ("What is the core strategic challenge you are facing? Are you trying to find new growth areas, or improve the implementation of your current strategy?")
    2.  **Identify Participants ("Who to Open Up To?"):** The agent helps the user determine the right mix of people. ("Who holds the knowledge you need? Should we involve internal frontline employees for operational knowledge, or external experts and customers to break free of industry logic?")
    3.  **Design the Engagement ("How to Open Up?"):** The agent helps select the right tool for the task. ("Do you need a broad, digital approach like a 'Strategy Jam' to gather many ideas, or a focused, in-person workshop like a 'Nightmare Competitor Challenge' to develop disruptive business models?")
    4.  **Frame the Core Question:** The agent helps craft a powerful question to pose to the group. ("For idea generation, it could be open: 'What should our company look like in 2030?' For disruption, it could be provocative: 'If you were to create a startup to destroy our business, what would it be?'")
    5.  **Plan for Synthesis and Feedback:** The agent ensures the process is well-managed. ("How will you manage and synthesize the contributions? Crucially, how will you provide feedback to participants so they know their contribution was valued?")

## 6. Final Output

The primary deliverable is a structured **JSON object** (`strategy_map.json`) that is built incrementally throughout the session and represents the complete, visualized strategy.

## 7. Technical Implementation Plan

This section provides a technical implementation plan for a junior developer to build the AI Strategic Co-pilot using Python and the LangChain ecosystem.

### 7.1. Core Concept: Orchestrator-Worker Workflow

Our system uses an **Orchestrator-Worker** model built with **LangGraph**.

* **Orchestrator:** A central graph that manages the overall state and routes tasks.

* **Workers:** The specialist agents that perform specific tasks.

* **State Manager:** The **Strategy Map Agent** is a special worker that also handles persistent state by reading from and writing to a JSON file.

### 7.2. Project Setup

*(Environment and project structure remain the same as the previous version)*

### 7.3. Implementation Steps

#### Step 1: Define the State (`models.py`)

The state now includes a file path for the strategy map.

```
# models.py
from typing import List, Dict, Any, Optional, TypedDict
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """The central state of our application."""
    conversation_history: List[BaseMessage]
    strategy_map_path: str  # Path to the session's strategy_map.json
    
    # Output from the specialist agent chosen by the router
    agent_out: Optional[str] 

```

#### Step 2: Build the Strategy Map Agent

This agent now handles file I/O.

```
# agents/strategy_map_agent.py
import json
from models import AgentState

def strategy_map_node(state: AgentState) -> dict:
    """Reads, updates, and writes the strategy map JSON file."""
    map_path = state['strategy_map_path']
    
    # 1. Read the current map
    try:
        with open(map_path, 'r') as f:
            strategy_map = json.load(f)
    except FileNotFoundError:
        strategy_map = {} # Initialize if it doesn't exist

    # 2. LLM call to analyze conversation and decide what to update
    # This is a complex prompt that asks the LLM to act as a JSON editor
    # based on the conversation.
    # ... (LLM logic to get `updated_fields`) ...
    
    # 3. Update the map
    strategy_map.update(updated_fields)
    
    # 4. Write the new map back to the file
    with open(map_path, 'w') as f:
        json.dump(strategy_map, f, indent=2)
        
    # This node doesn't produce a direct response to the user,
    # it just updates the state file for other agents to use.
    return {} 

```

#### Step 3: Update the Orchestrator (`orchestrator.py`)

The graph must now ensure the Strategy Map agent runs at every step before the router decides on the next specialist.

```
# orchestrator.py
from langgraph.graph import StateGraph, END
from models import AgentState
from agents.strategy_map_agent import strategy_map_node
# ... import other agent nodes

def orchestrator_router(state: AgentState) -> str:
    # ... (router logic remains the same) ...

workflow = StateGraph(AgentState)

# Add all nodes
workflow.add_node("strategy_map_updater", strategy_map_node)
workflow.add_node("why_agent", why_agent_node)
# ... add other specialist nodes
workflow.add_node("router", orchestrator_router) # Router is now a standard node

# Define the workflow
workflow.set_entry_point("strategy_map_updater")
workflow.add_edge("strategy_map_updater", "router") # Always run the router after updating the map

workflow.add_conditional_edges("router", orchestrator_router, {
    "why_agent": "why_agent",
    # ... other routes
    "end_session": END
})

# After a specialist agent runs, its output is synthesized and the loop repeats
workflow.add_edge("why_agent", "strategy_map_updater")
# ... add edges from all other specialists back to the map updater

app = workflow.compile()

```

#### Step 4: Update the API (`main.py`)

The API needs to create a unique JSON file for each session.

```
# main.py
import uuid
import os
from fastapi import FastAPI
# ... other imports

api = FastAPI()
sessions = {}

@api.post("/conversation/start")
async def start_conversation():
    session_id = str(uuid.uuid4())
    map_path = f"./{session_id}_strategy_map.json"
    
    # Create an empty file to start
    with open(map_path, 'w') as f:
        json.dump({}, f)

    sessions[session_id] = {
        "conversation_history": [],
        "strategy_map_path": map_path,
    }
    return {"session_id": session_id, "message": "Hello! ..."}

# ... (post_message logic remains similar)

```

# 8. Success Metrics
* **Completeness:** The final JSON output contains all necessary elements to fully describe the strategy and render a strategy map.
* **Logical Flow:** The system successfully guides a test user through the conversational journey without logical dead-ends or agent conflicts.
* **Methodological Fidelity:** The coaching logic is demonstrably faithful to the principles in the specialist agent profiles.
* **Conversation Logging:** The system successfully generates a complete log file for each coaching conversation for analysis and improvement.

---

## 9. User Interface (Web Application)

### 9.1. Technology Stack
* **HTML5** - Semantic structure and accessibility
* **Tailwind CSS** - Utility-first CSS framework for modern styling
* **Alpine.js** - Lightweight reactive framework for interactions
* **Chart.js** - For visualizing the strategy map
* **Marked.js** - For rendering markdown responses

### 9.2. UI Components

#### 9.2.1. Main Chat Interface
The primary interface is a conversational chat UI with:
* Message history display with user/AI distinction
* Input field with send button
* Real-time typing indicators
* Session management controls
* Export functionality

#### 9.2.2. Strategy Map Visualization
A visual representation of the strategy map showing:
* Four perspectives in a hierarchical layout
* Six Value Components with progress indicators
* Interactive nodes showing relationships
* Completeness percentage display

#### 9.2.3. Session Dashboard
* Active session information
* Phase progress tracker (WHY → HOW → WHAT)
* Current agent indicator
* Recommendations panel
* Quick actions (Export, Reset, Save)

### 9.3. HTML Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Strategic Co-pilot</title>
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Alpine.js -->
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <!-- Marked.js for Markdown -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    
    <!-- Custom Styles -->
    <style>
        .chat-container { height: calc(100vh - 200px); }
        .message-fade-in { animation: fadeIn 0.3s ease-in; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        .typing-indicator::after {
            content: '...';
            animation: typing 1.5s infinite;
        }
        @keyframes typing {
            0%, 60%, 100% { opacity: 0; }
            30% { opacity: 1; }
        }
    </style>
</head>
<body class="bg-gray-50">
    <div x-data="strategyCoach()" x-init="init()" class="container mx-auto px-4 py-6">
        
        <!-- Header -->
        <header class="bg-white rounded-lg shadow-sm p-6 mb-6">
            <div class="flex justify-between items-center">
                <div>
                    <h1 class="text-3xl font-bold text-gray-800">AI Strategic Co-pilot</h1>
                    <p class="text-gray-600 mt-1">Develop your organizational strategy with AI guidance</p>
                </div>
                <div class="flex space-x-4">
                    <button @click="exportStrategy()" 
                            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
                        Export Strategy
                    </button>
                    <button @click="newSession()" 
                            class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition">
                        New Session
                    </button>
                </div>
            </div>
        </header>

        <!-- Progress Tracker -->
        <div class="bg-white rounded-lg shadow-sm p-4 mb-6">
            <div class="flex justify-between items-center">
                <div class="flex space-x-8">
                    <div class="text-center">
                        <div :class="currentPhase === 'why' ? 'bg-blue-600' : 'bg-gray-300'" 
                             class="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold">
                            WHY
                        </div>
                        <p class="text-xs mt-1">Purpose</p>
                    </div>
                    <div class="text-center">
                        <div :class="currentPhase === 'how' ? 'bg-blue-600' : 'bg-gray-300'" 
                             class="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold">
                            HOW
                        </div>
                        <p class="text-xs mt-1">Method</p>
                    </div>
                    <div class="text-center">
                        <div :class="currentPhase === 'what' ? 'bg-blue-600' : 'bg-gray-300'" 
                             class="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold">
                            WHAT
                        </div>
                        <p class="text-xs mt-1">Actions</p>
                    </div>
                </div>
                <div class="text-right">
                    <p class="text-sm text-gray-600">Completeness</p>
                    <p class="text-2xl font-bold text-blue-600" x-text="completeness + '%'"></p>
                </div>
            </div>
        </div>

        <!-- Main Content Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            <!-- Chat Interface (2/3 width on large screens) -->
            <div class="lg:col-span-2 bg-white rounded-lg shadow-sm">
                <div class="chat-container overflow-y-auto p-6">
                    <div id="messages" class="space-y-4">
                        <template x-for="message in messages" :key="message.id">
                            <div :class="message.role === 'user' ? 'flex justify-end' : 'flex justify-start'">
                                <div :class="message.role === 'user' 
                                    ? 'bg-blue-600 text-white max-w-xs lg:max-w-md' 
                                    : 'bg-gray-100 text-gray-800 max-w-xs lg:max-w-md'"
                                    class="rounded-lg px-4 py-2 message-fade-in">
                                    <div x-html="renderMarkdown(message.content)"></div>
                                    <p class="text-xs mt-1 opacity-70" x-text="message.timestamp"></p>
                                </div>
                            </div>
                        </template>
                        <div x-show="isTyping" class="flex justify-start">
                            <div class="bg-gray-100 text-gray-800 rounded-lg px-4 py-2">
                                <span class="typing-indicator">AI is thinking</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Input Area -->
                <div class="border-t p-4">
                    <div class="flex space-x-2">
                        <input 
                            x-model="userInput"
                            @keyup.enter="sendMessage()"
                            type="text" 
                            placeholder="Type your message..."
                            class="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
                            :disabled="isTyping">
                        <button 
                            @click="sendMessage()"
                            :disabled="isTyping || !userInput.trim()"
                            class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 transition">
                            Send
                        </button>
                    </div>
                </div>
            </div>

            <!-- Strategy Map & Info Panel -->
            <div class="space-y-6">
                
                <!-- Current Agent Info -->
                <div class="bg-white rounded-lg shadow-sm p-4">
                    <h3 class="font-semibold text-gray-800 mb-2">Current Focus</h3>
                    <div class="space-y-2">
                        <p class="text-sm">
                            <span class="text-gray-600">Agent:</span>
                            <span class="font-medium" x-text="currentAgent"></span>
                        </p>
                        <p class="text-sm">
                            <span class="text-gray-600">Phase:</span>
                            <span class="font-medium uppercase" x-text="currentPhase"></span>
                        </p>
                    </div>
                </div>

                <!-- Recommendations -->
                <div class="bg-white rounded-lg shadow-sm p-4">
                    <h3 class="font-semibold text-gray-800 mb-2">Next Steps</h3>
                    <ul class="space-y-1">
                        <template x-for="step in nextSteps">
                            <li class="text-sm text-gray-600 flex items-start">
                                <span class="text-blue-600 mr-2">→</span>
                                <span x-text="step"></span>
                            </li>
                        </template>
                    </ul>
                </div>

                <!-- Strategy Map Preview -->
                <div class="bg-white rounded-lg shadow-sm p-4">
                    <h3 class="font-semibold text-gray-800 mb-2">Strategy Map</h3>
                    <canvas id="strategyMapChart" width="300" height="300"></canvas>
                </div>
            </div>
        </div>
    </div>

    <!-- JavaScript Application Logic -->
    <script>
        function strategyCoach() {
            return {
                // State
                sessionId: null,
                messages: [],
                userInput: '',
                isTyping: false,
                currentPhase: 'why',
                currentAgent: 'WHY Agent',
                completeness: 0,
                nextSteps: [],
                apiUrl: 'http://localhost:8000',
                
                // Initialize
                async init() {
                    await this.startNewSession();
                    this.initStrategyMapChart();
                },
                
                // Start new session
                async startNewSession() {
                    try {
                        const response = await fetch(`${this.apiUrl}/conversation/start`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                user_context: {
                                    company_name: "Your Company",
                                    industry: "Your Industry"
                                }
                            })
                        });
                        
                        const data = await response.json();
                        this.sessionId = data.session_id;
                        this.currentPhase = data.current_phase;
                        this.nextSteps = data.next_steps;
                        
                        this.addMessage('assistant', data.message);
                    } catch (error) {
                        console.error('Failed to start session:', error);
                        this.addMessage('system', 'Failed to connect to the server. Please ensure the API is running.');
                    }
                },
                
                // Send message
                async sendMessage() {
                    if (!this.userInput.trim() || this.isTyping) return;
                    
                    const message = this.userInput;
                    this.userInput = '';
                    this.addMessage('user', message);
                    this.isTyping = true;
                    
                    try {
                        const response = await fetch(`${this.apiUrl}/conversation/${this.sessionId}/message`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ message })
                        });
                        
                        const data = await response.json();
                        this.currentPhase = data.current_phase;
                        this.currentAgent = this.formatAgentName(data.current_agent);
                        this.completeness = Math.round(data.completeness_percentage);
                        this.nextSteps = data.recommendations || [];
                        
                        this.addMessage('assistant', data.response);
                        this.updateStrategyMapChart();
                    } catch (error) {
                        console.error('Failed to send message:', error);
                        this.addMessage('system', 'Failed to send message. Please try again.');
                    } finally {
                        this.isTyping = false;
                    }
                },
                
                // Add message to chat
                addMessage(role, content) {
                    this.messages.push({
                        id: Date.now(),
                        role: role,
                        content: content,
                        timestamp: new Date().toLocaleTimeString()
                    });
                    
                    // Scroll to bottom
                    this.$nextTick(() => {
                        const messagesEl = document.getElementById('messages');
                        messagesEl.scrollTop = messagesEl.scrollHeight;
                    });
                },
                
                // Export strategy
                async exportStrategy() {
                    try {
                        const response = await fetch(`${this.apiUrl}/conversation/${this.sessionId}/export`);
                        const data = await response.json();
                        
                        // Download as JSON
                        const blob = new Blob([JSON.stringify(data.strategy_map, null, 2)], 
                            { type: 'application/json' });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `strategy_${this.sessionId}.json`;
                        a.click();
                    } catch (error) {
                        console.error('Failed to export strategy:', error);
                    }
                },
                
                // New session
                async newSession() {
                    if (confirm('Start a new session? Current progress will be saved.')) {
                        this.messages = [];
                        this.completeness = 0;
                        await this.startNewSession();
                    }
                },
                
                // Render markdown
                renderMarkdown(text) {
                    return marked.parse(text);
                },
                
                // Format agent name
                formatAgentName(agent) {
                    if (!agent) return 'Strategic Coach';
                    return agent.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
                },
                
                // Initialize strategy map chart
                initStrategyMapChart() {
                    const ctx = document.getElementById('strategyMapChart').getContext('2d');
                    this.strategyChart = new Chart(ctx, {
                        type: 'radar',
                        data: {
                            labels: ['Financial', 'Manufactured', 'Intellectual', 
                                    'Human', 'Social', 'Natural'],
                            datasets: [{
                                label: 'Value Creation',
                                data: [0, 0, 0, 0, 0, 0],
                                backgroundColor: 'rgba(59, 130, 246, 0.2)',
                                borderColor: 'rgba(59, 130, 246, 1)',
                                borderWidth: 2
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: true,
                            scales: {
                                r: {
                                    beginAtZero: true,
                                    max: 100
                                }
                            }
                        }
                    });
                },
                
                // Update strategy map chart
                updateStrategyMapChart() {
                    // Update with actual data from strategy map
                    const progress = this.completeness / 100;
                    this.strategyChart.data.datasets[0].data = [
                        Math.random() * 100 * progress,
                        Math.random() * 100 * progress,
                        Math.random() * 100 * progress,
                        Math.random() * 100 * progress,
                        Math.random() * 100 * progress,
                        Math.random() * 100 * progress
                    ];
                    this.strategyChart.update();
                }
            }
        }
    </script>
</body>
</html>
```

### 9.4. Deployment Instructions

1. **Standalone HTML File**: The UI can be deployed as a single HTML file that connects to the API
2. **CORS Configuration**: Ensure the FastAPI backend has proper CORS settings for the UI domain
3. **Environment Variables**: Update the `apiUrl` in JavaScript to match your deployment
4. **HTTPS**: For production, ensure both the UI and API are served over HTTPS

### 9.5. Progressive Enhancements

Future improvements can include:
* WebSocket support for real-time updates
* Dark mode toggle
* Mobile-responsive improvements
* Voice input/output capabilities
* Collaborative session sharing
* Advanced strategy map visualization with D3.js

## 10. Non-Goals (Out of Scope)
* The coach will **not** provide its own business advice, opinions, or recommendations.
* The coach will **not** perform any external data gathering, market analysis, or competitor research.
* The coach will **not** generate financial models, projections, or forecasts.
* Future concepts like pluggable research agents or a "Board of Directors" feedback feature are explicitly out of scope.
