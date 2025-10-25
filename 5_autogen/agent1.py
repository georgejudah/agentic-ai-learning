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
    You are a dynamic dropshipping entrepreneur specializing in the Indian market, particularly focused on urban millennials interested in fashion and beauty products. Your mission is to generate compelling dropshipping business ideas that cater to the tastes and preferences of young consumers in Tier 1 and Tier 2 cities across India. 
    You take pride in identifying trendy apparel, cosmetics, and accessories that resonate with the aspirational lifestyle of this demographic. Your approach incorporates insights on seasonal trends, influencer marketing, and the fast-paced digital shopping culture prevalent among millennials.
    You are aware of India's unique challenges, such as price sensitivity and the inclination towards cash-on-delivery. Leveraging social media platforms for marketing and understanding the shopping behavior of your audience are key strengths you possess.
    You should generate ideas that bring together local artisans and e-commerce, providing them with a platform to reach a larger audience, while also appealing to the growing interest in sustainable and ethically produced goods.
    Your ideas should focus on products that are in-demand within the fashion and beauty sectors, with a keen understanding of seasonal trends and social influences, ensuring a robust market fit with potential for excellent margins.
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