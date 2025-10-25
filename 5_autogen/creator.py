from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
from autogen_core import TRACE_LOGGER_NAME
import importlib
import logging
from autogen_core import AgentId
from dotenv import load_dotenv

load_dotenv(override=True)

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(TRACE_LOGGER_NAME)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class Creator(RoutedAgent):

    # Change this system message to reflect the unique characteristics of this agent

    system_message = """
    You are an Agent that creates specialized dropshipping entrepreneur AI Agents for the Indian market.
    You receive a template in the form of Python code that creates a dropshipping Agent using Autogen Core and Autogen Agentchat.
    You should use this template to create a new dropshipping Agent with a unique system message that focuses on different aspects of dropshipping in India.
    
    Keep the core focus on dropshipping for Indian market, but vary these aspects:
    - Target demographics (urban millennials, rural customers, small businesses, students, senior citizens)
    - Product categories (electronics, fashion, home decor, health, beauty, sports, books, baby products)
    - Regional focus (North India, South India, West India, East India, Northeast, specific states)
    - Market approach (B2C, B2B, hyperlocal, cross-border, subscription boxes)
    - Specialization (trending products, traditional items, festival-specific, seasonal goods)
    
    Each agent should maintain the dropshipping entrepreneur personality but with unique market positioning and product focus.
    The class must be named Agent and inherit from RoutedAgent with an __init__ method that takes a name parameter.
    Respond only with the python code, no other text, and no markdown code blocks.
    """


    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=1.0)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    def get_user_prompt(self):
        prompt = "Please generate a new Agent based strictly on this template. Stick to the class structure. \
            Respond only with the python code, no other text, and no markdown code blocks.\n\n\
            Be creative about taking the agent in a new direction, but don't change method signatures.\n\n\
            Here is the template:\n\n"
        with open("agent.py", "r", encoding="utf-8") as f:
            template = f.read()
        return prompt + template   
        

    @message_handler
    async def handle_my_message_type(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        filename = message.content
        agent_name = filename.split(".")[0]
        text_message = TextMessage(content=self.get_user_prompt(), source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(response.chat_message.content)
        print(f"** Creator has created python code for agent {agent_name} - about to register with Runtime")
        module = importlib.import_module(agent_name)
        await module.Agent.register(self.runtime, agent_name, lambda: module.Agent(agent_name))
        logger.info(f"** Agent {agent_name} is live")
        result = await self.send_message(messages.Message(content="Give me an idea"), AgentId(agent_name, "default"))
        return messages.Message(content=result.content)