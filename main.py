import openai
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import configparser
import datetime

# Import the functions from the new module
from openai_chat import save_settings, load_settings, openai_frontend, timestamp

def save_settings(api_key, api_base, model):
    config = configparser.ConfigParser()
    config["settings"] = {
        "api_key": api_key,
        "api_base": api_base,
        "model": model
    }
    with open("settings.ini", "w") as configfile:
        config.write(configfile)

def load_settings():
    config = configparser.ConfigParser()
    config.read("settings.ini")
    if "settings" in config:
        return config["settings"].get("api_key", ""), config["settings"].get("api_base", ""), config["settings"].get("model", "")
    return "", "", ""

def openai_frontend(api_key, api_base, model, messages):
    openai.api_key = api_key
    openai.api_base = api_base
    response = openai.ChatCompletion.create(model=model, messages=messages, stream=True)
    response_text = "".join(chunk.choices[0].delta.get("content", "") for chunk in response)
    return response_text

def get_response(prompt_entry, chat_box, conversation):
    prompt = prompt_entry.get()
    api_key, api_base, model = load_settings()

    if not (api_key and api_base and model):
        messagebox.showerror("Error", "Please fill in all fields in the settings.")
        return

    try:
        user_message = {'role': 'user', 'content': prompt}
        conversation.append(user_message)
        response_text = openai_frontend(api_key, api_base, model, conversation)
        chat_box.configure(state="normal")
        chat_box.insert("end", f"{timestamp()} You: {prompt}\n", "user")
        chat_box.see("end")
        chat_box.configure(state="disabled")

        ai_message = {'role': 'ai', 'content': response_text}
        conversation.append(ai_message)
        chat_box.configure(state="normal")
        chat_box.insert("end", f"{timestamp()} AI: {response_text}\n", "ai")
        chat_box.see("end")
        chat_box.configure(state="disabled")

        prompt_entry.delete(0, tk.END)

    except Exception as e:
        messagebox.showerror("Error", str(e))
        return

def open_settings():
    settings = tk.Toplevel()
    settings.title("Settings")
    settings.geometry("400x200")

    api_key, api_base, model = load_settings()

    api_key_label = ttk.Label(settings, text="API Key:")
    api_key_label.pack(pady=(20, 0))
    api_key_input = ttk.Entry(settings, width=50)
    api_key_input.pack(pady=10)
    api_key_input.insert(0, api_key)

    api_base_label = ttk.Label(settings, text="API Base URL:")
    api_base_label.pack()
    api_base_input = ttk.Entry(settings, width=50)
    api_base_input.pack(pady=10)
    api_base_input.insert(0, api_base)

    model_label = ttk.Label(settings, text="Model:")
    model_label.pack()
    model_input = ttk.Entry(settings, width=50)
    model_input.pack(pady=10)
    model_input.insert(0, model)

    def save_and_close():
        api_key = api_key_input.get()
        api_base = api_base_input.get()
        model = model_input.get()
        save_settings(api_key, api_base, model)
        settings.destroy()

    save_button = ttk.Button(settings, text="Save", command=save_and_close)
    save_button.pack(pady=(10, 0))

def clear_chat(chat_box, conversation):
    chat_box.configure(state="normal")
    chat_box.delete(1.0, tk.END)
    chat_box.configure(state="disabled")

    # Clear the conversation history
    conversation.clear()

def change_font_size(chat_box, size):
    chat_box.configure(font=("TkDefaultFont", size))

def timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def save_chat(chat_box):
    filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if not filepath:
        return
    with open(filepath, "w") as output_file:
        text = chat_box.get(1.0, tk.END)
        output_file.write(text)

def open_chat(chat_box, conversation):
    filepath = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if not filepath:
        return
    with open(filepath, "r") as input_file:
        text = input_file.read()
    clear_chat(chat_box, conversation)
    chat_box.configure(state="normal")
    chat_box.insert(tk.END, text)
    chat_box.configure(state="disabled")

def toggle_theme(chat_box):
    global dark_theme
    dark_theme = not dark_theme
    if dark_theme:
        chat_box.configure(bg="#2b2b2b", fg="#FFFFFF")
        chat_box.tag_configure("user",foreground="#3f87a6")
        chat_box.tag_configure("ai", foreground="#b388ff")
    else:
        chat_box.configure(bg="#FFFFFF", fg="#2b2b2b")
        chat_box.tag_configure("user",foreground="blue")
        chat_box.tag_configure("ai", foreground="green")

root = tk.Tk()
root.title("OpenAI Chat Interface")
root.geometry("800x600")
root.configure(bg="#FFFFFF")

style = ttk.Style()
style.configure("TEntry", background="#FFFFFF")
style.configure("TLabel", background="#FFFFFF")
style.configure("TButton", background="#4CAF50", foreground="#000000")

chat_frame = ttk.Frame(root)
chat_frame.pack(padx=10, pady=10, fill="both", expand=True)

scrollbar = ttk.Scrollbar(chat_frame)
scrollbar.pack(side="right", fill="y")

chat_box = tk.Text(chat_frame, wrap="word", state="disabled", bg="#FFFFFF", fg="#2b2b2b", yscrollcommand=scrollbar.set)
chat_box.pack(fill="both", expand=True)

scrollbar.config(command=chat_box.yview)

chat_box.tag_configure("user",foreground="blue")
chat_box.tag_configure("ai", foreground="green")

menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open", command=lambda: open_chat(chat_box, conversation_history))
file_menu.add_command(label="Save", command=lambda: save_chat(chat_box))
file_menu.add_separator()
file_menu.add_command(label="Clear", command=lambda: clear_chat(chat_box, conversation_history))
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)

options_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Options", menu=options_menu)
options_menu.add_command(label="Settings", command=open_settings)

theme_menu = tk.Menu(options_menu, tearoff=0)
options_menu.add_cascade(label="Theme", menu=theme_menu)

dark_theme = False
theme_menu.add_command(label="Toggle Light/Dark", command=lambda: toggle_theme(chat_box))

prompt_label = ttk.Label(root, text="Your Prompt:")
prompt_label.pack(pady=(10, 0))
prompt_input = ttk.Entry(root, width=60)
prompt_input.pack(pady=10)

conversation_history = []

submit_button = ttk.Button(root, text="Send", command=lambda: get_response(prompt_input, chat_box, conversation_history))
submit_button.pack(pady=(10, 20))

# Send message on pressing Enter
root.bind('<Return>', lambda event: get_response(prompt_input, chat_box, conversation_history))

settings_button = ttk.Button(root, text="Settings", command=open_settings)
settings_button.pack(pady=(0, 10))

clear_button = ttk.Button(root, text="Clear chat", command=lambda: clear_chat(chat_box, conversation_history))
clear_button.pack(pady=(0, 10))

# Keyboard shortcuts
root.bind('<Control-s>', lambda event: open_settings())
root.bind('<Control-c>', lambda event: clear_chat(chat_box, conversation_history))

# Font size
chat_font_sizes = [8, 10, 12, 14, 16, 18, 20]
fontsize_variable = tk.StringVar(root)
fontsize_variable.set(chat_font_sizes[2])  # Default font size is 12

fontsize_label = ttk.Label(root, text="Font size:")
fontsize_label.pack(side="left", padx=(10, 5))
fontsize_dropdown = ttk.OptionMenu(root, fontsize_variable, *chat_font_sizes, command=lambda size: change_font_size(chat_box, int(size)))
fontsize_dropdown.pack(side="left", padx=(0, 10))

root.mainloop()