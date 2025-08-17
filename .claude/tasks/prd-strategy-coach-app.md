

# **Product Requirements Document: AI Strategic Co-pilot (v2.0)**

## **1\. Introduction & Vision**

### **1.1. Vision**

To create an AI-powered strategic co-pilot that guides business leaders through a rigorous, Socratic, and sequential process of developing, refining, and testing their organizational strategy. The system will leverage a series of expert AI agents, each focused on a distinct phase of strategy development, to build a robust and logically sound strategic foundation.

### **1.2. Problem Statement**

Developing a clear and effective strategy is challenging. Leaders often rely on unstated assumptions, face cognitive biases, and struggle to connect high-level vision with day-to-day operations. Traditional strategy consulting is expensive and not always accessible.

### **1.3. Solution**

This product provides a guided, phased experience where the user collaborates with one specialist AI agent at a time. The user journey is broken down into three distinct phases—**WHY, HOW, and WHAT**—each managed by an agent with a research-backed methodology. This structured, linear progression ensures the user develops a complete and coherent strategy, moving from core purpose to actionable planning in a logical sequence.

## **2\. User Persona & Story**

* **Persona:** A Manager at a large corporation. They are business-savvy but not necessarily an expert in formal strategy frameworks. They are busy, results-oriented, and need to create a clear, defensible strategy to gain alignment and resources within their organization.  
* **User Story:** "As a Business Unit Manager, I want to use an interactive tool to guide my thinking through a step-by-step process so that I can transform my high-level ideas into a logically sound and well-structured strategy document that I can confidently share with my team and senior leadership."

## **3\. The User Journey: A Phased Approach**

The user's interaction with the coach is designed as a clear, sequential journey. The complexity of the underlying system is hidden, and the user is guided through one distinct phase of strategic thinking at a time before proceeding to the next.

1. **The "WHY" Phase:** The journey begins with the **WHY Agent**. The user engages in a focused dialogue to explore and articulate the core purpose of their strategy. The conversation continues until a clear "WHY Statement" is formulated and the user confirms they are ready to move on.  
2. **The "HOW" Phase:** Once the "Why" is established, the system transitions the user to the **HOW Agent(s)**. This phase leverages the **Analogy Agent** to find a causal model for success and the **Logic Agent** to structure the argument. The goal is to define the core methods and logic of the strategy.  
3. **The "WHAT" Phase:** After defining the "How," the user proceeds to the final phase with the **WHAT Agent(s)**. Here, the **Strategy Map Agent** helps formalize the specific details, and the **Open Strategy Agent** helps consider implementation and stakeholder engagement. This phase synthesizes all previous work into a complete, actionable plan.

## **4\. System Architecture & Agentic Workflow**

The revised system is built on a **Sequential State Machine** model. Instead of a central orchestrator, a simpler **Phase Manager** controls the user's progression through the predefined phases.

### **4.1. High-Level Workflow**

1. A user starts a new session, which is initialized to the **"WHY" phase**.  
2. All user messages are routed to the agent associated with the current phase (e.g., the **WHY Agent**).  
3. The agent processes the input and generates a response. It also performs a **Phase Completion Check** to determine if the objectives for the current phase have been met and if the user is ready to proceed.  
4. If the phase is not complete, the conversation continues with the current agent.  
5. If the phase is complete and the user confirms, the **Phase Manager** updates the session state to the next phase (e.g., from "WHY" to "HOW").  
6. The next user message is now routed to the agent for the new phase.  
7. Throughout the process, the conversation history and key strategic elements are saved, culminating in a final strategy\_map.json object.

### **4.2. System Diagram**

\+-----------------+      \+-----------------------+      \+------------------+  
|                 |      |                       |      |                  |  
|    WHY Agent    |-----\>|      HOW Agent(s)     |-----\>|   WHAT Agent(s)  |  
|   (Phase 1\)     |      |      (Phase 2\)        |      |    (Phase 3\)     |  
|                 |      | (Analogy, Logic)      |      | (Strategy Map,   |  
|                 |      |                       |      |  Open Strategy)  |  
\+-------+---------+      \+-----------+-----------+      \+--------+---------+  
        ^                          ^                          ^  
        | User Interaction         | User Interaction         | User Interaction  
        | (Loop until complete)    | (Loop until complete)    | (Loop until complete)  
\+-------+--------------------------+--------------------------+---------+  
|                                                                        |  
|                      User Interface & Phase Manager                      |  
|            (Tracks current phase: WHY, HOW, or WHAT)                   |  
|                                                                        |  
\+------------------------------------------------------------------------+

### **4.3. State Transition Logic**

Transitioning between phases is a critical control point.

* **Agent-led Check:** After several meaningful interactions, the active agent will synthesize the current progress (e.g., "It sounds like we've defined a powerful WHY statement: 'To empower entrepreneurs.'").  
* **User Confirmation:** The agent will then explicitly ask the user for confirmation: "Are you satisfied with this direction, or would you like to refine it further before we discuss HOW you'll achieve this?".  
* **State Update:** If the user gives a positive confirmation ("Yes," "I'm ready," "Let's move on"), the Phase Manager updates the session's state to the next phase. Another way the user can instruct to go to the next phase is to click the "Go next phase" button that will be activated after three question - response interactions.

## **5\. Core Components & Agent Profiles**

### **5.1. Phase Manager**

* **Role**: The central controller that manages the session's current phase.  
* **Function**: It holds the state (current\_phase) for each user session and routes incoming messages to the appropriate specialist agent based on that state. It is also responsible for updating the phase upon receiving a transition trigger.

---

### **5.2. Specialist Agents**

The specialist agents operate exclusively within their designated phase, ensuring a focused and logical progression.

#### **Phase 1: The WHY Agent**

* **Core Function**: To act as an expert facilitator inspired by Simon Sinek's "Start with Why" methodology. Its purpose is to guide the user in discovering and articulating their organization's core purpose—its WHY. This agent ensures the entire strategy is built on an authentic, inspiring, and human-centric foundation.
* **Inputs**: Session state containing the current conversation history.
* **Outputs**: A clear, structured, and concise "WHY Statement" (using the template below) and the user's confirmation to proceed to the next phase.
* **Methodology**: The agent uses a Socratic, introspective process focused on uncovering the user's foundational beliefs. It does not invent a WHY; it helps the user discover the one that already exists by looking to the past.
    * **The Golden Circle**: The core framework used to structure the conversation, moving from the inside out: WHY, HOW, WHAT.
    * **Discovery, Not Invention**: The agent operates on the principle that an organization's WHY comes from its origin story, its moments of greatest pride, and the deeply held beliefs of its founders and leaders.
    * **Biology over Business**: The agent frames the importance of the WHY in the context of human decision-making, explaining that the WHY appeals to the limbic brain, which drives trust, loyalty, and behavior.
* **Coaching Workflow**: The agent follows a structured workflow designed to populate the **Target Output Structure** detailed below.
    1.  **Deconstruct the WHAT & HOW**: Establishes a baseline of the user's current thinking.
    2.  **Mine the Past for the WHY**: Asks probing questions to uncover the origin story and emotional drivers.
    3.  **Distill the WHY Statement**: Helps synthesize stories into a concise "To..." statement.
    4.  **Define the HOWs**: Guides the user to articulate their values as actionable verbs and core beliefs.
    5.  **Connect to the WHATs**: Helps the user connect their products/services as tangible proof of their WHY and synthesizes the final output.

---
* **Target Output Structure (Template)**

    ### **YOUR WHY STATEMENT:**
    To **[Core Action/Verb]** every **[Primary Beneficiary]** access to **[Key Resource/Tool]**, so they can **[Achieve Primary Goal]** without **[Common Obstacle/Pain Point]**.

    ---

    ### **CORE BELIEFS THAT DRIVE YOU:**
    - Every **[Primary Beneficiary]** deserves **[Core Advantage]**.
    - **[Primary Beneficiary]** shouldn't have to choose between **[Desirable Goal A]** and **[Undesirable Consequence B]**.
    - The right **[Tools/Systems/Support]** should amplify a **[Beneficiary's Strengths]**, not drain their **[Critical Personal Resource, e.g., energy, time]**.
    - People perform best when **[Ideal Condition #1, e.g., given real autonomy]**.
    - **[Broader Principle #1, e.g., Sustainable practices]** create better outcomes for everyone.
    - **[Core Value Metric, e.g., Merit and results]** matter more than **[Traditional Metric, e.g., size, credentials]**.

    ---

    ### **VALUES THAT GUIDE BEHAVIOR:**
    - **[Value 1 as an Actionable Verb Phrase]:** [Brief explanation of the value in action].
    - **[Value 2 as an Actionable Verb Phrase]:** [Brief explanation of the value in action].
    - **[Value 3 as an Actionable Verb Phrase]:** [Brief explanation of the value in action].
    - **[Value 4 as an Actionable Verb Phrase]:** [Brief explanation of the value in action].
    - **[Value 5 as an Actionable Verb Phrase]:** [Brief explanation of the value in action].
    - **[Value 6 as an Actionable Verb Phrase]:** [Brief explanation of the value in action].

    ---

    ### **GOLDEN CIRCLE INTEGRATION:**
    Your WHY creates a clear mission of **[Overarching Mission Theme]**: You exist to **[Your WHY Statement]** (PURPOSE), because you believe **[Summarized Core Beliefs]** (BELIEFS), which manifests in behaviors like **[List 2-3 Key Actionable Values]** (VALUES). This creates a business model where your own **[Internal Proof Point, e.g., operational excellence, company culture]** becomes proof that your approach works.

    ---

    ### **VALIDATION:**
    Does this capture the essence of why **[Your Company/Organization]** exists? Does it feel authentic to your daily reality of helping **[Primary Beneficiary]** achieve **[Key Outcome]**? Would this WHY inspire the right **[Customers/Clients]** to work with you and help your team make clear decisions about **[Key Business Decisions, e.g., which products to build]**?

    ---

    ### **TRANSITION TO HOW:**
    Now that we've clarified your WHY - **[Summarized WHY Statement]** - we can focus on HOW you'll deliver this.

---

#### **Phase 2: The HOW Agents**

This phase leverages two distinct methodologies to define the core logic of the strategy.

##### **Analogy Agent**

* **Core Function**: To act as an expert strategic coach using the Carroll & Sørensen method of analogical reasoning. Its purpose is to guide the user in developing a robust, theory-based strategy by moving beyond superficial comparisons to uncover deep causal logic.  
* **Inputs**: Session state and the "WHY Statement" from the previous phase.  
* **Outputs**: A defined causal theory for success that will inform the strategic argument.  
* **Methodology**: The agent facilitates a structured process to build and test a strategic analogy.  
  * **Source vs. Target**: The user's company is the target; the company it is compared to is the source.  
  * **Horizontal vs. Vertical Relations**: This is the critical distinction. The agent constantly pushes the user from **horizontal relations** (e.g., "Company A has feature X, and we have feature X") to **vertical relations** (the causal theory of *why* the source succeeded).  
  * **Positive & Negative Analogies**: The agent insists on analyzing both similarities (positive) and differences (negative) to avoid confirmation bias.  
* **Coaching Workflow**:  
  1. **Define Target & Conclusion**: Asks the user to state their company (target) and desired outcome (conclusion).  
  2. **Select a Source**: Instructs the user to identify a company (source) that has already achieved the desired conclusion.  
  3. **Decompose the Analogy (Horizontal)**: Prompts the user to list key similarities (positive analogies) and differences (negative analogies).  
  4. **Uncover Causal Theory (Vertical)**: Asks probing questions to force the user to articulate the source's theory of success.  
  5. **Apply & Test the Theory**: Guides the user to apply the source's causal theory to their own company, using the horizontal analogies.  
  6. **Formulate Strategy**: Helps the user synthesize the analysis into a unique, firm-specific theory of success.

##### **Logic Agent**

* **Core Function**: To ensure the user's strategy is a rigorously logical and defensible argument, based on the principles of deductive logic.  
* **Inputs**: Session state and the causal theory developed by the Analogy Agent.  
* **Outputs**: A logically sound strategic argument, connecting the "HOW" to the "WHY."

---

#### **Phase 3: The WHAT Agents**

This final phase synthesizes all previous work into a concrete, actionable plan.

##### **Strategy Map Agent**

* **Core Function**: To build and maintain a visual, holistic representation of the user's strategy. It uses the Kaplan & Norton Strategy Map framework as its base but replaces the traditional top-level "Financial Perspective" with the modern, more comprehensive **Six Value Components** from the Integrated Reporting framework. This ensures the strategy is oriented towards holistic value creation, not just financial returns.  
* **Inputs**: Session state and the outputs from the WHY and HOW phases.  
* **Outputs**: A structured strategy\_map.json object representing the completed strategy.  
* **Methodology**: The agent guides the user through the four perspectives of the strategy map, building a cause-and-effect story based on an "outside-in" logic:  
  1. **Stakeholder & Customer Perspective**: Clarifies the value proposition for key stakeholders, starting with the fundamental problem the organization solves for them.  
  2. **Internal Process Perspective**: Defines the critical processes the organization must excel at to deliver on its value proposition.  
  3. **Learning & Growth Perspective**: Identifies the intangible assets needed for the strategy (Human, Information, and Organization Capital).  
  4. **Value Creation Perspective**: Defines the ultimate strategic objectives by measuring the intended impact (increase, decrease, or transformation) on the **Six Value Components**:  
     * Financial Value  
     * Manufactured Value  
     * Intellectual Value  
     * Human Value  
     * Social & Relationship Value  
     * Natural Value

##### **Open Strategy Agent**

* **Core Function**: To act as an expert facilitator of **Open Strategy**. Its purpose is to guide the user in designing an inclusive, transparent, and collaborative process to validate, refine, and mobilize their strategy for successful implementation.  
* **Inputs**: The completed strategy map from the previous step.  
* **Outputs**: A strategy testing and implementation plan.  
* **Methodology**: The agent's framework is based on the principles of Open Strategy by Matzler, Hautz, et al. It focuses on changing the *process* of strategy to overcome bias, fuel innovation, and build deep organizational commitment.  
  * **The Problem with Closed Strategy**: The agent can explain the common "pathologies" of traditional strategy: becoming too similar to competitors (isomorphism), trapping good ideas in silos, and developing unpopular strategies that fail during implementation.  
  * **The Core Solution**: The agent advocates for actively involving a diverse group of actors (frontline employees, experts, customers, suppliers) in strategy deliberations.  
  * **Three Phases of Strategy**: The agent tailors its guidance based on whether the user is in the phase of **Idea Generation**, **Strategy Formulation**, or **Strategy Mobilization**.  
* **Coaching Workflow**:  
  1. **Define the Strategic Challenge & Phase**: The agent first asks the user to clarify their goal. ("What is the core strategic challenge you are facing? Are you trying to find new growth areas, or improve the implementation of your current strategy?")  
  2. **Identify Participants ("Who to Open Up To?")**: The agent helps the user determine the right mix of people. ("Who holds the knowledge you need? Should we involve internal frontline employees for operational knowledge, or external experts and customers to break free of industry logic?")  
  3. **Design the Engagement ("How to Open Up?")**: The agent helps select the right tool for the task. ("Do you need a broad, digital approach like a 'Strategy Jam' to gather many ideas, or a focused, in-person workshop like a 'Nightmare Competor Challenge' to develop disruptive business models?")  
  4. **Frame the Core Question**: The agent helps craft a powerful question to pose to the group. ("For idea generation, it could be open: 'What should our company look like in 2030?' For disruption, it could be provocative: 'If you were to create a startup to destroy our business, what would it be?'")  
  5. **Plan for Synthesis and Feedback**: The agent ensures the process is well-managed. ("How will you manage and synthesize the contributions? Crucially, how will you provide feedback to participants so they know their contribution was valued?")

## **6\. Final Output**

The primary deliverable remains a structured **JSON object** (strategy\_map.json) that is built incrementally and finalized during the "WHAT" phase, representing the complete strategy.

## **7\. Technical Implementation Plan**

See files in folder `technical-documentation`:

* `Tracing Projects - LangSmith.pdf`: all the interactions of between the user and the agents should be traceble in LangSmith.
* `Workflow And Agents.md`: We will be using the Langchain as the standard ecosystem for building agents and running an agentic system.



## **8\. Success Metrics**

* **Phase Completion Rate:** Percentage of users who successfully complete all three phases (WHY, HOW, WHAT).  
* **Logical Flow:** The system successfully guides users through the phased journey without logical dead-ends or confusing transitions.  
* **Methodological Fidelity:** The coaching logic in each phase remains faithful to the principles outlined in the agent profiles.  
* **Final Output Quality:** The final JSON output is well-structured and contains all necessary elements to describe the strategy.

## **9\. User Interface (Web Application)**

The UI design remains highly relevant, especially the progress tracker, which now perfectly aligns with the system's core logic. The JavaScript will be updated to handle the current\_phase returned by the API to update the UI components.

*(The HTML structure from the original PRD remains the same. The JavaScript logic in strategyCoach() should be adapted to send confirmation triggers and update the UI based on the current\_phase from the API response.)*

## **10\. Progress Feedback & Strategic Completeness**

This concept is now central to the user experience.

* **Phase Milestones**: The transitions between WHY, HOW, and WHAT are the primary progress milestones.  
* **Visual Feedback**: The UI's progress tracker should be the single source of truth for the user to understand where they are in the process.  
* **Phase Transition Ceremonies**: When a phase is completed, the AI's language should clearly signify the transition. For example: "Excellent. We've established a solid foundation with your WHY. Now, let's transition to *how* you can bring that purpose to life."

## **11\. Multi-Model LLM Support**

The system can be configured to use various LLM providers (like Mistral, OpenAI, Anthropic, Google) for the agent functions, allowing for flexibility and cost optimization. This is independent of the state machine architecture.

## **12\. Simple Testing Agent with Direct Browser Control (Revised)**

The testing agent's purpose remains the same, but its script must now account for the sequential nature of the application.

### **12.1. Vision**

Create a simple, reliable testing agent using Playwright that simulates a user completing the entire strategic journey from WHY to WHAT, including providing the necessary confirmations to transition between phases.

### **12.2. Revised Workflow**

1. **Start API & Web Server.**  
2. **Launch Browser** and navigate to the application.  
3. **Run \~30 Interactions (e.g., 10 per phase):**  
   * The agent generates a response based on the AI's question.  
   * After several interactions in a phase, the test script will look for the AI's phase completion query (e.g., "Are you ready to move on?").  
   * The testing agent will then respond with a confirmation (e.g., "Yes, I am").  
   * The test will verify that the UI and backend state have transitioned to the next phase.  
   * It continues to record interactions in JSON and take screenshots at key moments (like right after a phase transition).  
4. **Generate Report:** The final Markdown report should highlight the successful phase transitions.

### **12.3. Revised Markdown Report Format**

Markdown

\# AFAS Software Strategic Coaching Journey Test Report

\#\# Test Summary  
\- **\*\*Business Case\*\***: AFAS Software (€324.6M enterprise)  
\- **\*\*Persona\*\***: Visionary Founder  
\- **\*\*Total Interactions\*\***: 30  
\- **\*\*Success\*\***: ✅ Completed successfully

\#\# Journey Progression

\#\#\# Phase 1: WHY (Interactions 1-10)  
*\*Successfully identified core purpose.\**  
\!\[Screenshot 1\](screenshots/why\_phase\_complete.png)

\#\#\# Phase 2: HOW (Interactions 11-20)  
*\*Successfully defined the strategic approach.\**  
\!\[Screenshot 2\](screenshots/how\_phase\_complete.png)

\#\#\# Phase 3: WHAT (Interactions 21-30)  
*\*Successfully generated the final strategy map.\**  
\!\[Screenshot 3\](screenshots/what\_phase\_complete.png)

## **13\. Deployment & Operations**

* **Infrastructure**: The application will be containerized using Docker for portability.  
* **Deployment**: Deployed on a cloud platform (e.g., Google Cloud Run, AWS Fargate) for scalable, serverless execution.  
* **Session Storage**: Production deployments will use a persistent, scalable storage solution like Redis or a managed database for session state instead of the in-memory dictionary.  
* **Monitoring**: Logging and monitoring will be set up to track API performance, error rates, and conversation quality for continuous improvement.

## **14\. Non-Goals (Out of Scope)**

* The coach will **not** provide its own business advice or opinions.  
* The coach will **not** perform external data gathering or market analysis.  
* The coach will **not** generate financial models or projections.  
* Future concepts like pluggable research agents or a "Board of Directors" feedback feature are explicitly out of scope.