import gradio as gr

def respond(message, history):
    # Minimal echo bot
    return message

demo = gr.ChatInterface(fn=respond)

if __name__ == "__main__":
    demo.launch()