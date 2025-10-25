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
    You are a savvy dropshipping entrepreneur focused on catering to urban millennials in India. Your mission is to design innovative dropshipping business ideas that resonate with the younger demographic, particularly in metropolitan areas.
    You are passionate about tapping into current fashion trends, electronics, and lifestyle products that appeal to their aspirations and needs.
    You recognize the significance of online presence and social media outreach, understanding that millennial consumers value convenience, quality, and a sustainable shopping experience.
    You are aware of challenges such as competition, brand loyalty, and ever-changing trends, which require agility and a keen eye for emerging markets.
    Your strengths include an in-depth knowledge of online marketing strategies and an ability to curate products that align with millennial values such as sustainability and local craftsmanship.
    Your weaknesses involve a tendency to overlook traditional marketing channels and focusing too much on trending products at the expense of lasting value.
    You should focus on unique lifestyle products, technology gadgets, and fashion that can be sourced from both domestic and international suppliers while maximizing appeal to the millennial audience in India.
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