import gradio as gr
import requests

# Initialize conversation history
conversation_history = [
    {
        "role": "system",
        "content": "You are a helpful AI assistant. You should answer questions as precisely and concisely as possible.",
    }
]


def chat_with_bot(message):
    """
    Sends the user's message to the API and returns the assistant's response.
    """
    print(f"User message: {message}")

    # Add user message to conversation history
    conversation_history.append({"role": "user", "content": message})

    try:
        # 调用llama-api-server
        print(f"Generating chat completions")
        chat_url = "http://localhost:10086/v1/chat/completions"
        headers = {"Content-Type": "application/json"}

        # 构造请求的 JSON 数据
        data = {
            "messages": conversation_history,
            "model": "llama",
            "stream": False,
        }

        # 发送 POST 请求
        chat_completion_response = requests.post(
            chat_url, headers=headers, json=data
        ).json()
        assistant_message = chat_completion_response["choices"][0]["message"]["content"]

        # 打印响应内容
        print(f"AI Response: {assistant_message}")

        conversation_history.append({"role": "assistant", "content": assistant_message})

        return assistant_message

    except Exception as e:
        return f"An error occurred: {str(e)}"


def transcribe_audio(audio):
    """
    Mock transcribe audio function. In real use, integrate a transcription API or library.
    """
    if audio is None:
        return ""
    # 模拟返回的转录文本
    return "This is a transcribed text from the audio."


# Gradio App
with gr.Blocks(theme="soft") as demo:
    gr.Markdown("# ChatGPT-like Assistant")
    gr.Markdown("Ask me anything using text or voice!")

    with gr.Row():
        with gr.Column():
            # Chat history display
            chatbot = gr.Chatbot(type="messages")

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
                    sources="microphone", type="numpy", label="Voice Input"
                )

            # Submit button
            submit_btn = gr.Button("Submit")

    # Handle visibility of input methods
    def update_input_type(choice):
        """
        Dynamically show/hide text or voice input based on user's choice.
        """
        return (
            gr.update(visible=(choice == "Keyboard")),
            gr.update(visible=(choice == "Voice")),
        )

    input_type.change(
        fn=update_input_type,
        inputs=input_type,
        outputs=[text_input_group, voice_input_group],
    )

    # 改进后的逻辑：用户输入即时显示
    def process_user_input(text_msg, audio_msg, input_mode, chat_history):
        """
        Handles user input (text or voice) and updates the chat history.
        - Shows user input immediately in the chatbox.
        """
        if input_mode == "Keyboard" and text_msg:
            user_message = {"role": "user", "content": text_msg}
            conversation_history.append(user_message)
            chat_history.append(user_message)  # 添加用户文本输入
            return chat_history, "", None  # 返回更新后的聊天记录，清空文本框

        elif input_mode == "Voice" and audio_msg is not None:
            transcribed_msg = transcribe_audio(audio_msg)  # 模拟语音转文本
            user_message = {"role": "user", "content": transcribed_msg}
            chat_history.append(user_message)  # 添加用户语音输入的转文本
            return chat_history, None, None  # 清空音频输入框

        else:
            return chat_history, None, None

    def process_bot_response(audio_msg, input_mode, chat_history):
        """
        Processes the assistant's response and appends it to the chat history.
        """
        # user_input = (
        #     text_msg if input_mode == "Keyboard" else transcribe_audio(audio_msg)
        # )
        # if user_input:
        #     bot_response = chat_with_bot(user_input)  # 获取 AI 响应
        #     ai_message = {"role": "assistant", "content": bot_response}
        #     chat_history.append(ai_message)  # 显示 AI 响应
        bot_response = chat_with_bot("none")  # 获取 AI 响应
        ai_message = {"role": "assistant", "content": bot_response}
        chat_history.append(ai_message)  # 显示 AI 响应
        return chat_history

    # 按钮点击事件处理
    submit_btn.click(
        fn=process_user_input,
        inputs=[text_input, audio_input, input_type, chatbot],
        outputs=[chatbot, text_input, audio_input],
    ).then(
        fn=process_bot_response,
        # inputs=[text_input, audio_input, input_type, chatbot],
        inputs=[audio_input, input_type, chatbot],
        outputs=chatbot,
    )

if __name__ == "__main__":
    demo.launch(share=True)
