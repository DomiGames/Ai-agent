import speech_recognition as sr
import pyttsx3
import subprocess

ACTIVATION_NAME = "Jarvis"

class AI_Agent:
    def __init__(self, model="TinyLLaMa"):
        self.model = model
        self.feedback_log = []
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self._configure_voice()

    def _configure_voice(self):
        """Configure the voice settings for the text-to-speech engine."""
        voices = self.engine.getProperty("voices")
        for voice in voices:
            if "female" in voice.name.lower() or "zira" in voice.name.lower():
                self.engine.setProperty("voice", voice.id)
                break
        self.engine.setProperty("rate", 150)  # Adjust the speech rate (lower is slower)

    def listen(self):

        userInputOption = input(f"Use mic? (yes/no): ").strip().lower()

        if userInputOption == "yes":
            """Capture voice input and convert it to text."""
            with sr.Microphone() as source:
                print("Listening...")
                try:
                    audio = self.recognizer.listen(source)
                    text = self.recognizer.recognize_google(audio).lower()

                    if ACTIVATION_NAME.lower() in text:
                        return text.replace(ACTIVATION_NAME.lower(), "").strip()
                    else:
                        print("Activation name not detected.")
                        return None
                except sr.UnknownValueError:
                    print("Sorry, I didn't catch that.")
                    return "Sorry, I didn't catch that."
                except sr.RequestError:
                    print("Speech recognition service is unavailable.")
                    return "Speech recognition service is unavailable."
        else:
            keyboardInput = input(f"Type your chat i'm listening: ")
            return keyboardInput

    def speak(self, text):
        """Convert text to speech."""
        self.engine.say(text)
        self.engine.runAndWait()

    def chat(self, prompt):
        """Send the user prompt to the Ollama model and get a response."""
        try:
            # Use subprocess to run the ollama command
            result = subprocess.run(
                ["ollama", "run", self.model, prompt],
                capture_output=True, text=True
            )
            
            # Print raw output for debugging
            print("Raw output from Ollama:", result.stdout)
            print("Error output from Ollama:", result.stderr)  # Print any error output

            # If the output is not empty, return it directly
            if result.stdout.strip():
                return result.stdout.strip()
            else:
                return "I'm having trouble processing your request right now."
            
        except Exception as e:
            print(f"Error interacting with the model: {e}")
            return "I'm having trouble processing your request right now."

    def collect_feedback(self, prompt, response):
        """Log feedback from the user about the AI's response."""
        feedback = input(f"Was this response helpful? (yes/no): ").strip().lower()
        self.feedback_log.append({"prompt": prompt, "response": response, "feedback": feedback})
        print("Feedback saved.")

    def save_feedback(self, filename="feedback_log.txt"):
        """Save feedback to a file."""
        try:
            with open(filename, "w") as file:
                for entry in self.feedback_log:
                    file.write(f"Prompt: {entry['prompt']}\n")
                    file.write(f"Response: {entry['response']}\n")
                    file.write(f"Feedback: {entry['feedback']}\n")
                    file.write("-" * 50 + "\n")
            print(f"Feedback saved to {filename}.")
        except Exception as e:
            print(f"Error saving feedback: {e}")

    def run(self):
        """Main loop to handle interactions."""
        print("AI Agent is now running. Say 'exit' or 'quit' to stop.")
        while True:
            # Listen for user input
            user_input = self.listen()
            print(f"You: {user_input}")

            # Exit condition
            if user_input.lower() in ["exit", "quit"]:
                self.speak("Goodbye!")
                break

            # Get response from the model
            response = self.chat(user_input)
            print(f"AI: {response}")

            # Speak the response
            self.speak(response)

            # Collect feedback
            self.collect_feedback(user_input, response)

        # Save feedback on exit
        self.save_feedback()


# Initialize and run the agent
if __name__ == "__main__":
    agent = AI_Agent()
    agent.run()
