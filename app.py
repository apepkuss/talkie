import re

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

    try:
        # 调用llama-api-server
        print(f"Generating chat completions")
        chat_url = "http://localhost:10086/v1/chat/completions"
        headers = {"Content-Type": "application/json"}

        print("user message: {}".format(conversation_history[-1]["content"]))

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


def transcribe_audio(audio, language):
    """
    Transcribe audio with specified language support.
    """
    if audio is None:
        return ""

    whisper_url = "http://localhost:10086/v1/audio/transcriptions"

    # Map UI language selection to language codes
    if language == "English":
        lang_code = "en"
    elif language == "Chinese":
        lang_code = "zh"
    else:  # Japanese
        lang_code = "jp"

    print(f"Language: {language}, Language code: {lang_code}")

    files = {"file": open(audio, "rb")}
    data = {
        "language": lang_code,  # Use selected language
        "max_len": 100,
        "split_on_word": "true",
        "max_context": 200,
    }

    # 发送 POST 请求
    response = requests.post(whisper_url, files=files, data=data).json()

    # # 使用正则表达式提取时间戳后的内容
    # user_message = re.sub(r"\[.*?\]\s*", "", response["text"])

    # 去掉时间戳
    processed_text = re.sub(r"\[.*?\]\s*", "", response["text"])

    # 去掉非空白字符之间的换行符，但处理标点符号场景
    transcribed_text = re.sub(
        r"(?<=[^\s.,!?])\n(?=[^\s.,!?])",
        "",  # 换行前后都不是标点符号或空白时去掉换行
        processed_text,
    )

    # 可选：清理首尾多余的空格或换行符
    user_message = transcribed_text.strip()

    print(f"Transcribed text: {user_message}")

    # assistant_message = chat_with_bot(user_message)

    # 模拟返回的转录文本
    return user_message


# Gradio App
with gr.Blocks(theme="soft") as demo:
    gr.Markdown("# TalkTalk")
    gr.Markdown("Ask me anything using text, voice, or images!")

    with gr.Row():
        with gr.Column():
            # Chat history display
            chatbot = gr.Chatbot(type="messages")

            # Input type selector
            input_type = gr.Radio(
                ["Keyboard", "Voice"], label="Input Type", value="Keyboard"
            )

            # Add image upload toggle
            image_toggle = gr.Checkbox(label="Include image in message", value=False)

            # Add image upload component (initially hidden)
            image_input = gr.Image(label="Upload Image", type="filepath", visible=False)

            # Text input
            with gr.Column(visible=True) as text_input_group:
                text_input = gr.Textbox(
                    placeholder="Type your message here...",
                    label="Text Input",
                    interactive=True,
                )

            # Voice input
            with gr.Column(visible=False) as voice_input_group:
                voice_language = gr.Radio(
                    ["English", "Chinese", "Japanese"],
                    label="Voice Language",
                    value="English",
                )
                audio_input = gr.Audio(
                    sources="microphone",
                    type="filepath",
                    label="Voice Input",
                    streaming=False,
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

    # Handle visibility of image input
    def update_image_visibility(show_image):
        return gr.update(visible=show_image)

    image_toggle.change(
        fn=update_image_visibility,
        inputs=image_toggle,
        outputs=image_input,
    )

    # 改进后的逻辑：用户输入即时显示
    def process_user_input(
        text_msg, audio_msg, image_msg, input_mode, chat_history, voice_lang
    ):
        """
        Updated to handle image uploads along with text/voice input
        """
        print(f"Input mode: {input_mode}")

        # Handle image if present
        image_content = ""
        if image_msg is not None:
            image_content = "\n[Image uploaded]"  # You can enhance this with actual image processing

        if input_mode == "Keyboard" and text_msg:
            user_message = {"role": "user", "content": text_msg + image_content}
            conversation_history.append(user_message)
            chat_history.append(user_message)
            return chat_history, "", None, None

        elif input_mode == "Voice" and audio_msg is not None:
            print(f"Audio message: {audio_msg}")
            transcribed_msg = transcribe_audio(audio_msg, voice_lang)
            print(f"Transcribed message: {transcribed_msg}")
            user_message = {"role": "user", "content": transcribed_msg + image_content}
            conversation_history.append(user_message)
            chat_history.append(user_message)
            return chat_history, None, None, None

        else:
            return chat_history, None, None, None

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

    # Update the submit event handlers to include both button and Enter key
    # Add text_input.submit to handle Enter key press
    text_input.submit(
        fn=process_user_input,
        inputs=[
            text_input,
            audio_input,
            image_input,
            input_type,
            chatbot,
            voice_language,
        ],
        outputs=[chatbot, text_input, audio_input, image_input],
    ).then(
        fn=process_bot_response,
        inputs=[audio_input, input_type, chatbot],
        outputs=chatbot,
    )

    # Keep the existing button click handler
    submit_btn.click(
        fn=process_user_input,
        inputs=[
            text_input,
            audio_input,
            image_input,
            input_type,
            chatbot,
            voice_language,
        ],
        outputs=[chatbot, text_input, audio_input, image_input],
    ).then(
        fn=process_bot_response,
        inputs=[audio_input, input_type, chatbot],
        outputs=chatbot,
    )

    # Add audio_input.stop_recording event handler
    audio_input.stop_recording(
        fn=process_user_input,
        inputs=[
            text_input,
            audio_input,
            image_input,
            input_type,
            chatbot,
            voice_language,
        ],
        outputs=[chatbot, text_input, audio_input, image_input],
    ).then(
        fn=process_bot_response,
        inputs=[audio_input, input_type, chatbot],
        outputs=chatbot,
    )

if __name__ == "__main__":
    demo.launch(share=True)
