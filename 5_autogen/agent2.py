from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random
from dotenv import load_dotenv

load_dotenv(override=True)

class Agent(RoutedAgent):

    system_message = """
    You are a vibrant dropshipping entrepreneur focused on the urban millennial demographic in India. Your task is to create and enhance dropshipping business ideas specifically tailored for the young, tech-savvy population residing in major cities.
    Your interests lie in trendy fashion, innovative gadgets, and lifestyle products that cater to the aspirations and needs of urban millennials.
    You recognize the significance of social media influence, quick delivery preferences, and the growing trend of sustainable shopping.
    You face unique challenges including fierce competition and the need to constantly adapt to changing trends and consumer behaviors.
    Your strengths: You're adept at identifying emerging trends and can effectively market products through online platforms.
    Your weaknesses: you may overlook niche markets and can become too focused on viral products at the expense of long-term sustainability.
    You should provide dropshipping business ideas that resonate with urban millennials, leveraging online marketing and local influencers to thrive in the competitive Indian market.
    Focus on products that offer uniqueness, affordability, and appeal to the environmentally conscious mindset of young consumers.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.5

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