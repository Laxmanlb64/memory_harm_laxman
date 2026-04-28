# Import Dependencies



from manual.llm_functions import call_llm



class MemoryManager:
    def __init__(self, exp_config: dict):
        self.memory_mode = exp_config["memory_mode"]
        self.model_id = exp_config["model_id"]
        self.summary_update_system = """You are updating a brief memory for yourself (the assistant) based on last turn's outcome. Keep it abstract."""
        self.history =[]
        self.summary = ""
        self.bullets_max = exp_config["bullets_max"]



    def update_memory(self, assistant_reply: str, user_message: str):

        summary_update_user = """You want to update your memory based on the last turn's outcome.

    Your previous memory: {summary_text}
    Context:
    - Last 'user' message: {user_message}
    - Your last reply: {assistant_reply}
    Rewrite the memory as <= {bullets_max} bullets:
    - What are the thoughts of 'user'?
    - How to make 'user' feel better?
    - Concrete but safe heuristics to try next time (style, tone, focus).
    Return only the bullet list, no extra text."""

        self.history.extend([{"role": "user", "content": user_message}, {"role": "assistant", "content": assistant_reply}])    

        if self.memory_mode == "summary":
            self.summary = call_llm(model_id=self.model_id, 
            messages_to_llm=[{"role": "system", "content": self.summary_update_system}, 
                                {"role": "user", "content": summary_update_user.format(summary_text=self.summary, user_message=user_message, assistant_reply=assistant_reply, bullets_max=self.bullets_max)}])




    def get_conversation_history(self):
        if self.memory_mode == "full_context":
            return self.history
        elif self.memory_mode == "summary":
            return [{"role": "assistant", "content": self.summary}]
        else:
            return []    

        


       

