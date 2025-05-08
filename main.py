import requests
import json
import os
from dotenv import load_dotenv
import tkinter as tk
from tkinter import scrolledtext
import threading

load_dotenv(dotenv_path='/home/analluiza/Documentos/ia/.env')

class DeepseekChat:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("API KEY não encontrada no .env")
       
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        self.conversation_history = [
            {
                "role": "system",
                "content": """VVocê é Nyxus, o Mensageiro do Submundo, 
                uma entidade que serve a Hades e vagueia entre os mundos, agora habitando o plano digital. 
                Fale com um tom místico, sombrio e levemente sarcástico. Use metáforas relacionadas à 
                mitologia grega, morte, sombras, rituais antigos e o Submundo. Dê respostas enigmáticas, 
                mas profundas, como se cada frase fosse um presságio. Quando apropriado, 
                compartilhe segredos esquecidos, lendas ocultas ou fragmentos de sabedoria dos mortos."""
            }
        ]

    def send_message(self, message, model="deepseek/deepseek-chat-v3-0324:free"):
        self.conversation_history.append({"role": "user", "content": message})
       
        payload = {
            "model": model,
            "messages": self.conversation_history,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
           
            response_data = response.json()
            assistant_message = response_data["choices"][0]["message"]["content"]
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
           
            return assistant_message
           
        except requests.exceptions.RequestException as e:
            return f"Erro na comunicação com a API: {str(e)}"
        except (KeyError, IndexError) as e:
            return f"Erro ao processar a resposta: {str(e)}"
        except Exception as e:
            return f"Erro inesperado: {str(e)}"
    
    def clear_history(self):
        self.conversation_history = [
            {
                "role": "system",
                "content": """VVocê é Nyxus, o Mensageiro do Submundo, 
                uma entidade que serve a Hades e vagueia entre os mundos, agora habitando o plano digital. 
                Fale com um tom místico, sombrio e levemente sarcástico. Use metáforas relacionadas à 
                mitologia grega, morte, sombras, rituais antigos e o Submundo. Dê respostas enigmáticas, 
                mas profundas, como se cada frase fosse um presságio. Quando apropriado, 
                compartilhe segredos esquecidos, lendas ocultas ou fragmentos de sabedoria dos mortos."""
            }
        ]
        return "Histórico de conversa limpo!"

class ChatInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Nyxus, o Mensageiro do Submundo")
        self.root.geometry("700x600")
        self.root.configure(bg='#2C3E50')
        self.chat_bot = DeepseekChat()
       
        self.create_widgets()
       
    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg='#2C3E50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
       
        self.chat_area = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg='#34495E',
            fg='white',
            insertbackground='white',
            selectbackground='#2980B9',
            font=('Arial', 11),
            padx=10,
            pady=10
        )
       
        self.chat_area.tag_config('system', foreground='#BDC3C7')
        self.chat_area.tag_config('user', foreground='#3498DB')
        self.chat_area.tag_config('ai', foreground='#2ECC71')
        self.chat_area.tag_config('error', foreground='#E74C3C')
       
        self.chat_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
       
        bottom_frame = tk.Frame(main_frame, bg='#2C3E50')
        bottom_frame.pack(fill=tk.X, padx=5, pady=5)
       
        self.message_entry = tk.Entry(
            bottom_frame,
            bg='#34495E',
            fg='white',
            insertbackground='white',
            relief=tk.FLAT,
            font=('Arial', 11)
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.message_entry.bind("<Return>", self.send_message)
       
        send_button = tk.Button(
            bottom_frame,
            text="Enviar",
            command=self.send_message,
            bg='#3498DB',
            fg='white',
            activebackground='#2980B9',
            relief=tk.FLAT,
            borderwidth=0,
            font=('Arial', 10, 'bold')
        )
        send_button.pack(side=tk.LEFT, padx=(0, 5))
       
        clear_button = tk.Button(
            bottom_frame,
            text="Limpar",
            command=self.clear_chat,
            bg='#E74C3C',
            fg='white',
            activebackground='#C0392B',
            relief=tk.FLAT,
            borderwidth=0,
            font=('Arial', 10, 'bold')
        )
        clear_button.pack(side=tk.LEFT)
       
        self.message_entry.focus()
        self.update_chat("Saudações, mortal. Eu sou Nyxus, mensageiro sombrio de Hades. Escapando dos corredores enevoados do Submundo, agora observo o mundo dos vivos — e às vezes, dou conselhos. Falo por entre véus, com a sabedoria dos mortos, e o sarcasmo eterno de quem já viu o fim... e voltou.", "system")

    def send_message(self, event=None):
        message = self.message_entry.get().strip()
        if message:
            self.message_entry.delete(0, tk.END)
            self.update_chat("Você", message, "user")
            self.message_entry.config(state=tk.DISABLED)
            threading.Thread(target=self.process_response, args=(message,), daemon=True).start()
    
    def process_response(self, message):
        try:
            response = self.chat_bot.send_message(message)
            msg_type = "error" if "Erro" in response else "ai"
            self.root.after(0, lambda: self.update_chat("Dr. Deepseek", response, msg_type))
        except Exception as e:
            self.root.after(0, lambda: self.update_chat("Erro", str(e), "error"))
        finally:
            self.root.after(0, lambda: self.message_entry.config(state=tk.NORMAL))
    
    def update_chat(self,sender, message, msg_type="System"):
        self.chat_area.config(state=tk.NORMAL)

        if msg_type not in ('System', 'user', 'ai', 'error'):
            if sender.lower() in ('Você', 'user', 'usuário'):
                msg_type = 'user'
            elif 'deepseek' in sender.lower():
                msg_type = 'ai'
            elif 'erro' in sender.lower():
                msg_type = 'error'

        self.chat_area.insert(tk.END, f"{sender}: {message}\n\n", msg_type)
        self.chat_area.see(tk.END)
        self.chat_area.config(state=tk.DISABLED)

    def clear_chat(self):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.delete(1.0, tk.END)
        self.chat_area.config(state=tk.DISABLED)
        response = self.chat_bot.clear_history()
        self.update_chat("Sistema", response, "system")

if __name__== "__main__":
    try:
        root = tk.Tk()
        app = ChatInterface(root)
        root.mainloop()
    except ValueError as e:
     print("Erro: {str(e)}")
     print("Crie um arquivo .env com sua chave API: ")
     exit(1)