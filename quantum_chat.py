# quantum_chat.py - ChatGPT chat interface
import os
import threading
from datetime import datetime

import requests
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk


class QuantumChat:
    """ChatGPT chat interface for Quantum Studio."""

    API_URL = "https://api.openai.com/v1/chat/completions"
    DEFAULT_MODEL = "gpt-4o-mini"

    def __init__(self, parent, context_provider=None):
        self.parent = parent
        self.context_provider = context_provider
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip() or None
        self.messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful quantum computing assistant inside a desktop "
                    "simulation studio. Give concise, practical answers."
                ),
            }
        ]
        self.is_waiting = False

        self.frame = ttk.LabelFrame(parent, text="ChatGPT Assistant", padding=8)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)

        api_frame = ttk.Frame(self.frame)
        api_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        api_frame.columnconfigure(1, weight=1)

        ttk.Label(api_frame, text="API Key").grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.api_key_entry = ttk.Entry(api_frame, show="*")
        self.api_key_entry.grid(row=0, column=1, sticky="ew", padx=(0, 6))
        if self.api_key:
            self.api_key_entry.insert(0, self.api_key)
        self.set_key_button = ttk.Button(api_frame, text="Set", command=self.set_api_key)
        self.set_key_button.grid(row=0, column=2, sticky="e")

        self.include_context_var = tk.BooleanVar(value=False)
        self.context_check = ttk.Checkbutton(
            api_frame,
            text="Add context",
            variable=self.include_context_var,
        )
        self.context_check.grid(row=1, column=0, columnspan=3, sticky="w", pady=(6, 0))

        self.chat_display = scrolledtext.ScrolledText(
            self.frame,
            wrap=tk.WORD,
            bg="#0f172a",
            fg="#e2e8f0",
            insertbackground="#e2e8f0",
            font=("Consolas", 10),
            relief=tk.FLAT,
            borderwidth=0,
            state=tk.DISABLED,
        )
        self.chat_display.grid(row=1, column=0, sticky="nsew")
        self.chat_display.tag_config("user", foreground="#60a5fa", font=("Consolas", 10, "bold"))
        self.chat_display.tag_config("assistant", foreground="#86efac", font=("Consolas", 10))
        self.chat_display.tag_config("system", foreground="#fbbf24", font=("Consolas", 10, "italic"))

        input_frame = ttk.Frame(self.frame)
        input_frame.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        input_frame.columnconfigure(0, weight=1)

        self.input_entry = tk.Text(
            input_frame,
            height=4,
            wrap=tk.WORD,
            bg="#111827",
            fg="#f8fafc",
            insertbackground="#f8fafc",
            font=("Consolas", 10),
            relief=tk.FLAT,
            padx=8,
            pady=8,
        )
        self.input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.input_entry.bind("<Return>", self.on_return_pressed)
        self.input_entry.bind("<Shift-Return>", self.insert_newline)

        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=0, column=1, sticky="ns")

        self.send_button = ttk.Button(button_frame, text="Send", command=self.send_message)
        self.send_button.pack(fill=tk.X, pady=(0, 4))
        ttk.Button(button_frame, text="Clear", command=self.clear_chat).pack(fill=tk.X)

        self.status_label = ttk.Label(self.frame, text="Ready", foreground="#15803d")
        self.status_label.grid(row=3, column=0, sticky="w", pady=(8, 0))

        self.add_system_message("Welcome to ChatGPT chat.")
        if self.api_key:
            self.add_system_message("API key loaded. Type a message and press Enter to send.")
        else:
            self.add_system_message("Paste your OpenAI API key above, click Set, then start chatting.")

    def set_busy(self, busy, status_text=None, color=None):
        self.is_waiting = busy
        self.send_button.config(state=tk.DISABLED if busy else tk.NORMAL)
        self.set_key_button.config(state=tk.DISABLED if busy else tk.NORMAL)
        self.input_entry.config(state=tk.DISABLED if busy else tk.NORMAL)
        if status_text:
            self.status_label.config(text=status_text, foreground=color or "#15803d")
        if not busy:
            self.input_entry.focus_set()

    def add_message(self, sender, message, tag):
        self.chat_display.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_display.insert(tk.END, f"[{timestamp}] ", "system")
        self.chat_display.insert(tk.END, f"{sender}\n", tag)
        self.chat_display.insert(tk.END, f"{message.strip()}\n\n", tag)
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def add_user_message(self, message):
        self.add_message("You", message, "user")

    def add_assistant_message(self, message):
        self.add_message("ChatGPT", message, "assistant")

    def add_system_message(self, message):
        self.add_message("System", message, "system")

    def set_api_key(self):
        key = self.api_key_entry.get().strip()
        if not key:
            messagebox.showwarning("API Key", "Please enter your OpenAI API key.")
            return
        self.api_key = key
        self.add_system_message("API key saved for this session.")
        self.input_entry.focus_set()

    def on_return_pressed(self, event):
        self.send_message()
        return "break"

    def insert_newline(self, event):
        self.input_entry.insert(tk.INSERT, "\n")
        return "break"

    def send_message(self, event=None):
        if self.is_waiting:
            return "break"
        if not self.api_key:
            messagebox.showwarning("API Key", "Please set your OpenAI API key first.")
            return "break"

        message = self.input_entry.get("1.0", tk.END).strip()
        if not message:
            return "break"

        outgoing_message = message
        if self.include_context_var.get() and self.context_provider is not None:
            context_text = self.context_provider()
            if context_text:
                outgoing_message = (
                    "Current simulator context:\n"
                    f"{context_text}\n\n"
                    f"User question:\n{message}"
                )
                self.add_system_message("Included current simulator context with this message.")

        self.add_user_message(message)
        self.messages.append({"role": "user", "content": outgoing_message})
        self.input_entry.delete("1.0", tk.END)
        self.set_busy(True, "ChatGPT is thinking...", "#d97706")

        threading.Thread(target=self.get_chatgpt_response, daemon=True).start()
        return "break"

    def get_chatgpt_response(self):
        try:
            response = requests.post(
                self.API_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.DEFAULT_MODEL,
                    "messages": self.messages,
                    "temperature": 0.7,
                    "max_tokens": 700,
                },
                timeout=45,
            )

            data = response.json()
            if response.status_code != 200:
                error_message = data.get("error", {}).get("message", response.text)
                self.parent.after(0, lambda: self.handle_error(f"API Error {response.status_code}: {error_message}"))
                return

            reply = data["choices"][0]["message"]["content"].strip()
            self.messages.append({"role": "assistant", "content": reply})
            self.parent.after(0, lambda: self.handle_success(reply))
        except requests.exceptions.Timeout:
            self.parent.after(0, lambda: self.handle_error("Request timed out. Please try again."))
        except Exception as exc:
            self.parent.after(0, lambda: self.handle_error(f"Error: {exc}"))

    def handle_success(self, reply):
        self.add_assistant_message(reply)
        self.set_busy(False, "Ready", "#15803d")

    def handle_error(self, error_message):
        self.add_system_message(error_message)
        if self.messages and self.messages[-1]["role"] == "user":
            self.messages.pop()
        self.set_busy(False, "Error", "#dc2626")

    def clear_chat(self):
        self.messages = [self.messages[0]]
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self.add_system_message("Chat cleared. Conversation history reset.")
