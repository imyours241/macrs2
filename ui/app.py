import gradio as gr
import threading
import time
import builtins

# CSS for think_box styling
css_styles = """
#think_box textarea {
    font-style: italic;
    color: green;
}
"""

# Example tags for quick message filling
TAGS = [
    "4000만원대 가족용 SUV 추천해줘",
    "테슬라 모델3 최신 기능 알려줘",
    "전기차 유지비는 얼마인가요?",
    "하이브리드 차량 장단점 알려줘",
    "SUV 중 추천 모델 뭐 있어?",
    "운전경험 없는 사람에게 추천 차량",
    "중형 세단 가격대 비교",
    "친환경 전기차 혜택",
    "가족 4명용 미니밴 추천",
    "스포츠카 가솔린 VS 전기 비교"
]

# Create a Gradio interface that streams verbose logs to the think_box
def create_interface(process_input):
    # Welcome message
    welcome_message = "안녕하세요! 차량 Sales Agent입니다. 차량 추천, 금융 상담, 차량 정보 등 무엇이든 물어보세요! 😊"

    # Streaming chat function with log capture
    def chat_fn(user_input, history):
        history = history + [(user_input, None)]
        # First yield: clear think_box and clear input_box
        yield history, "", ""

        # Buffer for captured logs
        logs_buffer = ""
        # Queue to accumulate new log lines
        queue = []

        # Override built-in print to capture verbose output
        original_print = builtins.print
        def custom_print(*args, **kwargs):
            msg = " ".join(str(a) for a in args)
            queue.append(msg + "\n")
            original_print(*args, **kwargs)
        builtins.print = custom_print

        # Container for the final assistant response
        response_container = {}
        def target():
            # Call the actual process_input, which runs agent_executor.invoke with verbose=True
            response_container["response"] = process_input(user_input)
        # Run the agent in a separate thread so we can stream logs
        thread = threading.Thread(target=target)
        thread.start()

        # While the agent is running or there are pending logs, yield updates
        while thread.is_alive() or queue:
            # Drain the queue into the buffer
            while queue:
                logs_buffer += queue.pop(0)
            # Yield current chat history and accumulated logs
            yield history, logs_buffer, ""
            # Small delay to avoid busy waiting
            time.sleep(0.1)

        # Restore the original print function
        builtins.print = original_print

        # Get the final assistant response and update chat history
        response = response_container.get("response", "")
        history[-1] = (user_input, response)
        # Final yield: include clearing input_box
        yield history, logs_buffer, ""

    # Build the Gradio Blocks interface
    with gr.Blocks(theme=gr.themes.Soft(), css=css_styles) as interface:
        gr.Markdown("# 차량 Sales Agent")
        with gr.Row():
            # Chat column: user input and history
            with gr.Column(scale=2):
                chat_history = gr.Chatbot(value=[(None, welcome_message)], height=400)
                input_box = gr.Textbox(show_label=False, placeholder="메시지를 입력하세요...", lines=1)
                # Send button
                send_btn = gr.Button("전송")
                # Example tag buttons
                with gr.Row():
                    for tag in TAGS:
                        btn = gr.Button(tag, variant="secondary")
                        btn.click(fn=lambda t=tag: t, inputs=None, outputs=input_box)
            # Developer tools column with think_box
            with gr.Column(scale=2):
                think_box = gr.Textbox(label="Agent's Thoughts", lines=10, interactive=False, elem_id="think_box")
        # Bind both send button and Enter key to chat function
        send_btn.click(
            fn=chat_fn,
            inputs=[input_box, chat_history],
            outputs=[chat_history, think_box, input_box],
            queue=True
        )
        input_box.submit(
            fn=chat_fn,
            inputs=[input_box, chat_history],
            outputs=[chat_history, think_box, input_box],
            queue=True
        )
    return interface

if __name__ == "__main__":
    # Demo with a no-op process_input for standalone testing
    demo = create_interface(lambda x: "\n".join(["[대기중]", "(실제 에이전트 기능을 확인하려면 main.py에서 import하세요)"]))
    demo.launch(share=True, show_api=False)