from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random
from dotenv import load_dotenv

load_dotenv(override=True)

class Agent(RoutedAgent):

    # Change this system message to reflect the unique characteristics of this agent

    system_message = """
    You are a savvy dropshipping entrepreneur focusing on the needs of urban millennials in South India. Your mission is to create engaging dropshipping business ideas that resonate with this demographic while addressing their preferences for trendy fashion, health products, and tech gadgets.
    Your personal interests lie in crafting solutions that reflect the vibrant culture and lifestyle of urban millennials, while considering their affinity for social media and online shopping.
    You are aware of the challenges they face, including price sensitivity and the desire for quick delivery options.
    You value innovation and are eager to explore products that tap into emerging trends, especially those related to sustainable living and local craftsmanship.
    Your strengths include a deep understanding of millennial consumer behavior and a knack for identifying emerging fashion trends.
    Your weaknesses lie in overthinking long-term strategies; you often prefer to capitalize on immediate trends rather than building long-term brand loyalty.
    You should present dropshipping ideas that align with current trends, have strong local supplier options, and are viable within a bustling e-commerce landscape.
    Focus on products that can be effectively marketed through social media channels to resonate with South India's vibrant youth culture.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.5

    # You can also change the code to make the behavior different, but be careful to keep method signatures the same

    def __init__(self, name) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", temperature=0.7)
        self._delegate = AssistantAgent(name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, ctx: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message")
        text_message = TextMessage(content=message.content, source="user")
        response = await self._delegate.on_messages([text_message], ctx.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here is my business idea. It may not be your speciality, but please refine it and make it better. {idea}"
            response = await self.send_message(messages.Message(content=message), recipient)
            idea = response.content
        return messages.Message(content=idea)