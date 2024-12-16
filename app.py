import os

import gradio as gr
import openai

# Set your OpenAI API key
openai.api_key = "your-api-key-here"  # Replace with your actual API key

# Initialize conversation history
conversation_history = []


def chat_with_bot(message, history):
    # Add user message to conversation history
    conversation_history.append({"role": "user", "content": message})

    try:
        # TODO: 调用llama-api-server

        # # Get response from OpenAI
        # response = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo", messages=conversation_history
        # )

        # # Extract assistant's response
        # assistant_response = response.choices[0].message["content"]

        # # Add assistant's response to conversation history
        # conversation_history.append(
        #     {"role": "assistant", "content": assistant_response}
        # )

        assistant_response = "dummy response"
        conversation_history.append(
            {"role": "assistant", "content": assistant_response}
        )

        return assistant_response

    except Exception as e:
        return f"An error occurred: {str(e)}"


def transcribe_audio(audio):
    if audio is None:
        return ""
    return audio


with gr.Blocks(theme="soft") as demo:
    gr.Markdown("# ChatGPT-like Assistant")
    gr.Markdown("Ask me anything using text or voice!")

    with gr.Row():
        with gr.Column():
            # Chat history display
            chatbot = gr.Chatbot()

            # Input type selector
            input_type = gr.Radio(
                ["Keyboard", "Voice"], label="Input Type", value="Keyboard"
            )

            # Text input
            with gr.Column(visible=True) as text_input_group:
                text_input = gr.Textbox(
                    placeholder="Type your message here...", label="Text Input"
                )

            # Voice input
            with gr.Column(visible=False) as voice_input_group:
                audio_input = gr.Audio(
                    sources=["microphone"], type="numpy", label="Voice Input"
                )

            # Submit button
            submit_btn = gr.Button("Submit")

    # Handle visibility of input methods
    def update_input_type(choice):
        return (
            gr.Column(visible=(choice == "Keyboard")),
            gr.Column(visible=(choice == "Voice")),
        )

    input_type.change(
        fn=update_input_type,
        inputs=input_type,
        outputs=[text_input_group, voice_input_group],
    )

    # Handle submissions
    def process_input(text_msg, audio_msg, input_mode):
        if input_mode == "Keyboard":
            return chat_with_bot(text_msg, None)
        else:
            return chat_with_bot(audio_msg, None)

    submit_btn.click(
        fn=process_input,
        inputs=[text_input, audio_input, input_type],
        outputs=chatbot,
    )

if __name__ == "__main__":
    demo.launch(share=True)
