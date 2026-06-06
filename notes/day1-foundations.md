## Day 1 Foundations

- What is agent:
Agent is: an AI model capable of reasoning, planning, and interacting with its environment.
We call it Agent because it has agency, aka it has the ability to interact with the environment.
An Agent is a system that leverages an AI model to interact with its environment in order to achieve a user-defined objective. It combines reasoning, planning, and the execution of actions (often via external tools) to fulfill tasks.

- Think of the Agent as having two main parts:

The Brain (AI Model)
This is where all the thinking happens. The AI model handles reasoning and planning. It decides which Actions to take based on the situation.

The Body (Capabilities and Tools)
This part represents everything the Agent is equipped to do.

The scope of possible actions depends on what the agent has been equipped with. For example, because humans lack wings, they can’t perform the “fly” Action, but they can execute Actions like “walk”, “run”, “jump”, “grab”, and so on.






## 1. What is an LLM?
- An LLM (Large Language Model) is an AI model trained on large amounts of text data to understand and generate human-like language. It can answer questions, summarize information, generate code, and help with reasoning tasks based on the input it receives.
- LLM can interpret user instructions, maintain context in conversations, define a plan and decide which tools to use.
- LLM is the brain of the Agent

## 2. What is a Workflow?
A workflow is a fixed sequence of steps designed to complete a task. In automation, each step is predefined, and the system follows the same path every time unless explicitly changed.

Example:
- Check disk space
- If disk space is low, show cleanup suggestion
- Generate report

## 3. What is an AI Agent?
An AI agent is a system that can reason about a task, decide what action to take, use tools if needed, and then produce an output. Unlike a fixed workflow, an agent can choose between multiple possible actions depending on the situation.

## 4. What is RAG?
RAG stands for Retrieval-Augmented Generation. It means the AI first retrieves relevant information from documents, data, or knowledge sources, and then uses that information to generate a better answer.

This helps:
- reduce hallucination
- improve accuracy
- answer based on real data instead of memory only

## 5. Workflow vs Agent
- An AI model that can reason, plan, and use tools to interact with its environment to achieve a specific goal
A workflow follows fixed predefined steps.
An agent can decide which step or tool to use based on the situation.

Workflow is better when:
- rules are fixed
- task is predictable
- safety is very important

Agent is better when:
- task needs reasoning
- multiple tools may be needed
- user input can vary a lot

## 6. How Agentic AI connects to my background
My background is in automation engineering, scripting, packaging, diagnostics, self-healing systems, and enterprise support workflows.

This connects well to Agentic AI because:
- I already understand automation logic
- I already build tools and scripts
- I already work with diagnostics and remediation
- Agentic AI can add reasoning, tool selection, summarization, and guided decision-making on top of my existing automation skills

## 7. My understanding in simple words
LLM is the brain for language.
Workflow is fixed automation.
Agent is a smarter system that can decide what to do.
RAG helps the model answer using real information.
My current automation experience can be extended with Agentic AI to build smarter enterprise support and diagnostic systems.

## 8. Questions I still have
- When should I choose workflow instead of agent?
- How much freedom should an agent get in enterprise automation?
- How do I make agent output safe and reliable?

## 9. Today’s Progress
- Installed Python
- Installed VS Code
- Verified Git
- Verified Docker
- Created learning workspace
- Read Day 1 materials

## 10. End of Day Summary
Today I understood the basic difference between LLM, workflow, agent, and RAG. I also confirmed that my automation background is highly relevant for learning Agentic AI.


## What are AI Tools?
- A Tool is a function given to the LLM. This function should fulfill a clear objective (Web Search, Image Generation, API Interface etc.)
- if your agent needs up-to-date data you must provide it through some tool.

## Q2: What is the Role of Planning in an Agent?
To decide on the sequence of actions and select appropriate tools needed to fulfill the user’s request.
- Planning helps the Agent determine the best steps and tools to complete a task.

## Q3: How Do Tools Enhance an Agent’s Capabilities?
Tools provide the Agent with the ability to execute actions a text-generation model cannot perform natively, such as making coffee or generating images.
- Tools enable Agents to interact with the real world and complete tasks.

## Q4: How Do Actions Differ from Tools?
Actions are the steps the Agent takes, while Tools are external resources the Agent can use to perform those actions.
- Actions are higher-level objectives, while Tools are specific functions the Agent can call upon.

## Q5: What Role Do Large Language Models (LLMs) Play in Agents?
LLMs serve as the reasoning 'brain' of the Agent, processing text inputs to understand instructions and plan actions.
- LLMs enable the Agent to interpret, plan, and decide on the next steps.