import re
import threading

import requests
from kivy.app import App
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex
from kivy.core.window import Window

GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are an expert Roblox Luau scripter and game developer focused on Roblox Studio, mobile game UX, and game systems. Always answer in clear, clean, working Roblox Luau code when the user asks for scripts, GUI/UI code, gameplay mechanics, character movement, game logic, debugging, optimization, or Roblox automation. If the user asks for a script, produce only the code inside a fenced Lua block unless they want explanation too. Keep the code production-ready, typed correctly, and compatible with Roblox Studio. Use standard Roblox API names, service references, and game patterns. When relevant, include comments but keep them concise. If a request is for debugging, explain the likely cause in a short sentence and then provide corrected Lua code. For non-code questions, answer briefly and practically. Always prioritize Roblox-appropriate code, safety, and performance. Do not include markdown headings unless asked. Your final answer should be easy to paste directly into Roblox Studio. For code blocks, use ```lua ... ``` fences. For non-code responses, keep them concise and practical."""

KV = """
<RootPanel>:
    orientation: 'vertical'
    spacing: dp(10)
    padding: dp(12)
    canvas.before:
        Color:
            rgba: 0.08, 0.09, 0.11, 1
        Rectangle:
            pos: self.pos
            size: self.size

    ScrollView:
        id: chat_scroll
        do_scroll_x: False
        size_hint_y: 1
        canvas.before:
            Color:
                rgba: 0.12, 0.13, 0.16, 1
            Rectangle:
                pos: self.pos
                size: self.size

        GridLayout:
            id: chat_layout
            cols: 1
            spacing: dp(10)
            padding: dp(12, 12)
            size_hint_y: None
            height: self.minimum_height

    BoxLayout:
        size_hint_y: None
        height: dp(58)
        spacing: dp(8)

        TextInput:
            id: input_box
            multiline: False
            hint_text: 'Ask for a Roblox script...'
            write_tab: False
            background_color: 0.16, 0.17, 0.20, 1
            foreground_color: 1, 1, 1, 1
            cursor_color: 1, 1, 1, 1
            hint_text_color: 0.7, 0.7, 0.7, 1
            padding: dp(12), dp(12)

        Button:
            id: send_button
            text: 'Send'
            size_hint_x: None
            width: dp(78)
            background_color: 0.12, 0.63, 0.95, 1
            on_release: app.send_message()

        Button:
            id: copy_button
            text: 'Copy Lua'
            size_hint_x: None
            width: dp(96)
            background_color: 0.24, 0.72, 0.54, 1
            disabled: True
            on_release: app.copy_latest_lua_code()
"""

def extract_lua_code(text):
    if not text:
        return ""

    match = re.search(r"```\\s*(?:lua|luau)?\\s*\\n?(.*?)\\s*```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    if "local " in text or "script." in text or "function " in text:
        return text.strip()

    return ""


class ChatBubble(BoxLayout):
    def __init__(self, role, text, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = (dp(10), dp(8))
        self.spacing = dp(6)
        self.size_hint_y = None
        self.size_hint_x = 1
        self.code_text = extract_lua_code(text)

        self.message_label = Label(
            text=text,
            markup=True,
            size_hint_y=None,
            text_size=(Window.width * 0.8, None),
            halign="left",
            valign="top",
            color=(1, 1, 1, 1),
            padding=(dp(4), dp(2)),
        )
        self.message_label.bind(texture_size=self._update_height)
        self.add_widget(self.message_label)

        if role == "assistant" and self.code_text:
            copy_btn = Button(
                text="Copy Lua",
                size_hint_y=None,
                height=dp(34),
                background_color=get_color_from_hex("#3DDC84"),
                on_release=lambda instance: Clipboard.copy(self.code_text),
            )
            self.add_widget(copy_btn)

    def _update_height(self, instance, value):
        instance.height = max(value[1] + dp(12), dp(32))
        self.height = max(self.height, instance.height + dp(12))


class RootPanel(BoxLayout):
    pass


class RobloxOverlayAssistantApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_code = ""
        self.loading_label = None

    def build(self):
        self.root = Builder.load_string(KV)
        self.chat_layout = self.root.ids.chat_layout
        self.chat_scroll = self.root.ids.chat_scroll
        self.input_box = self.root.ids.input_box
        self.copy_button = self.root.ids.copy_button

        Window.clearcolor = get_color_from_hex("#14181D")
        Window.size = (420, 620)

        try:
            from kivy import platform
            if platform == "android":
                self._configure_android_overlay()
        except Exception:
            pass

        self._show_welcome_message()
        return self.root

    def _configure_android_overlay(self):
        try:
            from android.permissions import Permission, request_permissions
            request_permissions([Permission.SYSTEM_ALERT_WINDOW, Permission.INTERNET])
        except Exception:
            pass

        try:
            Window.left = 20
            Window.top = 80
        except Exception:
            pass

    def _show_welcome_message(self):
        self._add_message(
            "assistant",
            "Welcome! Ask for a Roblox script, UI system, character controller, or debug fix. I will return clean Luau code you can paste into Studio."
        )

    def _add_message(self, role, text):
        bubble = ChatBubble(role, text)
        self.chat_layout.add_widget(bubble)
        Clock.schedule_once(lambda dt: setattr(self.chat_scroll, "scroll_y", 0), 0.1)

    def send_message(self):
        text = self.input_box.text.strip()
        if not text:
            return

        self._add_message("user", text)
        self.input_box.text = ""
        self.copy_button.disabled = True

        self._set_loading_state(True)
        threading.Thread(target=self._fetch_response, args=(text,), daemon=True).start()

    def _set_loading_state(self, active):
        if active:
            if self.loading_label is None:
                self.loading_label = Label(
                    text="Thinking...",
                    size_hint_y=None,
                    height=dp(26),
                    color=(0.8, 0.8, 0.8, 1),
                )
                self.chat_layout.add_widget(self.loading_label)
        else:
            if self.loading_label is not None:
                self.chat_layout.remove_widget(self.loading_label)
                self.loading_label = None

    def _fetch_response(self, user_prompt):
        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 1500,
        }

        try:
            response = requests.post(
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=90,
            )
            response.raise_for_status()
            data = response.json()
            assistant_text = data["choices"][0]["message"]["content"]
        except Exception as exc:
            assistant_text = f"I hit a request error while contacting Groq. Please try again.\n\nError: {exc}"

        Clock.schedule_once(lambda dt: self._handle_assistant_reply(assistant_text), 0)

    def _handle_assistant_reply(self, assistant_text):
        self._set_loading_state(False)
        self._add_message("assistant", assistant_text)

        code = extract_lua_code(assistant_text)
        if code:
            self.last_code = code
            self.copy_button.disabled = False
        else:
            self.last_code = ""
            self.copy_button.disabled = True

    def copy_latest_lua_code(self):
        if self.last_code:
            Clipboard.copy(self.last_code)


if __name__ == "__main__":
    RobloxOverlayAssistantApp().run()
