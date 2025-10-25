# ===================================================================
# AUTOGEN MULTI-AGENT IDEA GENERATION SYSTEM
# ===================================================================
# 
# PROJECT OVERVIEW:
# This system demonstrates AutoGen's distributed runtime capabilities by creating
# a dynamic ecosystem of AI agents that generate and refine business ideas.
# 
# ARCHITECTURE:
# 1. Creator Agent: Generates new agent variants with unique personalities
# 2. Multiple Agent Instances: Each with different business focuses and traits  
# 3. Distributed Runtime: Agents run across multiple workers for scalability
# 4. Collaborative Refinement: Agents can bounce ideas off each other
#
# WORKFLOW:
# world.py → Creator generates agent{i}.py files → Each agent creates idea{i}.md
# ===================================================================

from autogen_ext.runtimes.grpc import GrpcWorkerAgentRuntimeHost
from agent import Agent
from creator import Creator
from autogen_ext.runtimes.grpc import GrpcWorkerAgentRuntime
from autogen_core import AgentId
import messages
import asyncio

# Configuration: Number of unique agent variants to create and run
# Each agent will have different personality traits, business focuses, and risk appetites
HOW_MANY_AGENTS = 5

async def create_and_message(worker, creator_id, i: int):
    """
    Core function that orchestrates the creation of a new agent variant and idea generation.
    
    PROCESS FLOW:
    1. Send request to Creator agent to generate a new agent variant (agent{i}.py)
    2. Creator reads agent.py template and generates unique agent with different:
       - System message/personality
       - Business sector focus 
       - Risk appetite and traits
       - Collaborative tendencies
    3. The generated agent code creates business ideas
    4. Save the final business idea to idea{i}.md file
    
    Args:
        worker: GRPC runtime worker for message passing
        creator_id: AgentId of the Creator agent that generates new agents
        i: Index number for unique agent/idea file naming
    """
    try:
        # Request Creator to generate a new agent variant
        # Creator will read agent.py template and create agent{i}.py with unique traits
        result = await worker.send_message(messages.Message(content=f"agent{i}.py"), creator_id)
        
        # Save the generated business idea to a markdown file
        # Each idea reflects the unique personality and focus of its generating agent
        with open(f"idea{i}.md", "w") as f:
            f.write(result.content)
    except Exception as e:
        print(f"Failed to run worker {i} due to exception: {e}")

async def main():
    """
    Main orchestration function that sets up the distributed AutoGen ecosystem.
    
    DISTRIBUTED RUNTIME SETUP:
    - Creates GRPC host server for agent coordination
    - Establishes worker runtime for message passing
    - Registers Creator agent for dynamic agent generation
    
    PARALLEL EXECUTION:
    - Launches multiple concurrent agent creation/idea generation tasks
    - Uses asyncio.gather() for true parallel processing
    - Each task creates a unique agent variant and business idea
    
    SYSTEM ARCHITECTURE:
    Host (localhost:50051) ← Worker ← Creator Agent
                                   ↓
                          Generates agent1.py, agent2.py, etc.
                                   ↓
                          Creates idea1.md, idea2.md, etc.
    """
    # Step 1: Initialize GRPC Host Server
    # This serves as the central coordination point for all distributed agents
    host = GrpcWorkerAgentRuntimeHost(address="localhost:50051")
    host.start() 
    
    # Step 2: Create Worker Runtime
    # Worker connects to host and handles message routing between agents
    worker = GrpcWorkerAgentRuntime(host_address="localhost:50051")
    await worker.start()
    
    # Step 3: Register Creator Agent
    # Creator is the "meta-agent" that generates new agent variants dynamically
    # It reads agent.py template and creates personalized agents with unique traits
    result = await Creator.register(worker, "Creator", lambda: Creator("Creator"))
    creator_id = AgentId("Creator", "default")
    
    # Step 4: Launch Parallel Agent Creation Tasks
    # Create coroutines for concurrent agent generation and idea creation
    # Each coroutine will:
    # a) Ask Creator to generate a new agent variant (agent{i}.py)
    # b) That agent creates a business idea (idea{i}.md)
    coroutines = [create_and_message(worker, creator_id, i) for i in range(1, HOW_MANY_AGENTS+1)]
    
    # Execute all tasks concurrently using asyncio.gather()
    # This enables true parallel processing of multiple agent creation workflows
    await asyncio.gather(*coroutines)
    
    # Step 5: Graceful Shutdown
    # Clean up resources and close connections
    try:
        await worker.stop()
        await host.stop()
    except Exception as e:
        print(e)




if __name__ == "__main__":
    """
    ENTRY POINT - MULTI-AGENT ECOSYSTEM LAUNCH
    
    EXECUTION FLOW:
    1. world.py starts → Creates distributed AutoGen runtime
    2. Creator agent generates 20 unique agent variants (agent1.py to agent20.py)
    3. Each agent variant has different:
       - Personality traits (optimistic/cautious, patient/impulsive)
       - Business sector focus (healthcare, education, fintech, etc.)
       - Collaboration patterns (some bounce ideas off others)
    4. Each agent generates business ideas → saved as idea1.md to idea20.md
    5. System demonstrates distributed agent coordination and dynamic agent creation
    
    OUTPUT FILES GENERATED:
    - agent1.py to agent20.py: Unique agent variants with different personalities
    - idea1.md to idea20.md: Business ideas reflecting each agent's traits and focus
    
    KEY AUTOGEN CONCEPTS DEMONSTRATED:
    - Distributed runtime with GRPC coordination
    - Dynamic agent generation and registration  
    - Parallel async message processing
    - Agent collaboration and idea refinement
    - Template-based agent creation patterns
    """
    asyncio.run(main())


