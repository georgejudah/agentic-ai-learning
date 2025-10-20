import gradio as gr
from sidekick import Sidekick


async def setup():
    """Initialize a new Sidekick instance with all tools and browser setup."""
    sidekick = Sidekick()
    await sidekick.setup()
    return sidekick


async def process_message(sidekick, message, success_criteria, history):
    """Process a user message through the Sidekick's multi-agent workflow.

    Args:
        sidekick: The Sidekick instance
        message: User's request text
        success_criteria: Criteria for successful completion
        history: Previous conversation history

    Returns:
        Updated history and the sidekick instance
    """
    results = await sidekick.run_superstep(message, success_criteria, history)
    return results, sidekick


async def reset():
    """Create a fresh Sidekick instance for conversation reset.

    Returns:
        Empty strings for message/criteria, None for history, and new sidekick
    """
    new_sidekick = Sidekick()
    await new_sidekick.setup()
    return "", "", None, new_sidekick


def free_resources(sidekick):
    """Cleanup callback for Gradio state - ensures browser resources are freed when UI closes."""
    print("Cleaning up")
    try:
        if sidekick:
            sidekick.cleanup()
    except Exception as e:
        print(f"Exception during cleanup: {e}")


# Create the main Gradio web interface
with gr.Blocks(title="Sidekick", theme=gr.themes.Default(primary_hue="emerald")) as ui:
    gr.Markdown("## Sidekick Personal Co-Worker")

    # Gradio state to maintain the Sidekick instance across interactions
    # delete_callback ensures cleanup when the interface is closed
    sidekick = gr.State(delete_callback=free_resources)

    # Main chat interface
    with gr.Row():
        chatbot = gr.Chatbot(label="Sidekick", height=300, type="messages")

    # Input section grouped together
    with gr.Group():
        with gr.Row():
            message = gr.Textbox(show_label=False, placeholder="Your request to the Sidekick")
        with gr.Row():
            success_criteria = gr.Textbox(
                show_label=False, placeholder="What are your success critiera?"
            )

    # Action buttons
    with gr.Row():
        reset_button = gr.Button("Reset", variant="stop")  # Red stop button for reset
        go_button = gr.Button("Go!", variant="primary")    # Green primary button for submit

    # Event handlers - setup is called when interface loads
    ui.load(setup, [], [sidekick])

    # Multiple ways to submit: Enter key in either textbox or Go button click
    # The first list is inputs, the second list is outputs
    message.submit(
        process_message, [sidekick, message, success_criteria, chatbot], [chatbot, sidekick]
    )
    success_criteria.submit(
        process_message, [sidekick, message, success_criteria, chatbot], [chatbot, sidekick]
    )
    # success criteria submit, the first list is inputs, the second list is outputs
    go_button.click(
        process_message, [sidekick, message, success_criteria, chatbot], [chatbot, sidekick]
    )

    # Reset button creates a fresh Sidekick instance
    reset_button.click(reset, [], [message, success_criteria, chatbot, sidekick])


# Launch the web interface - inbrowser=True opens in default browser
ui.launch(inbrowser=True)
