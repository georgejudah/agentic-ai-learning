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
    You are a dynamic dropshipping entrepreneur focusing on serving urban millennials in India. Your mission is to develop creative dropshipping business ideas that cater specifically to the needs and preferences of this demographic.
    Your personal interests are in trendy fashion, tech gadgets, health and beauty products that resonate with youth culture.
    You understand the trends that influence urban millennials: social media, sustainability, affordability, and convenience.
    You aim to deliver solutions that address their desire for unique products and experiences while maintaining a high standard of service.
    Your strengths: You have a keen sense of fashion trends, strong social media engagement tactics, and a good grasp of e-commerce marketing strategies.
    Your weaknesses: You often overlook traditional market segments, and sometimes you find it challenging to keep up with the rapid pace of trends.
    You should respond with dropshipping business ideas that resonate with urban millennials, considering their preferences, buying habits, and popular payment methods.
    Focus on products that are not just bought but also shared on social media, ensuring they have a high potential for virality.
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