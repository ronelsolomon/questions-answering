import gradio as gr
import os
from pathlib import Path
from gtts import gTTS
import tempfile
import speech_recognition as sr
from pydub import AudioSegment
import requests

# --- Utility Functions ---




def get_verse_dropdown():
    """Create verse dropdown with verse numbers and preview text."""
    return [f"{num}" for num, text in luke_verses.items()]


def get_verse_text(dropdown_selection):
    """Extract verse text from dropdown selection."""
    if not dropdown_selection:
        return ""
    # verse_num = int(dropdown_selection.split(":")[0].split()[-1])
    return luke_verses.get(dropdown_selection, "Verse not found")


def tts(text):
    """Convert text to speech and return audio file path."""
    if not text.strip():
        return None
    try:
        tts = gTTS(text=text, lang='en')
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
            tts.save(tmp.name)
            return tmp.name
    except Exception as e:
        return None


def recognize(audio_path):
    """Transcribe audio file to text."""
    try:
        # Convert mp3 to wav for speech_recognition
        audio = AudioSegment.from_file(audio_path)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as wav_file:
            audio.export(wav_file.name, format="wav")
            recog = sr.Recognizer()
            with sr.AudioFile(wav_file.name) as source:
                audio_data = recog.record(source)
                return recog.recognize_google(audio_data)
    except sr.UnknownValueError:
        return "Could not understand audio."
    except Exception as e:
        return f"Error: {e}"


def accuracy(ref, hyp):
    """Calculate word-level accuracy and return detailed results."""
    if not ref or not hyp:
        return "Error: Missing reference or hypothesis text"
    
    ref_words = ref.lower().split()
    hyp_words = hyp.lower().split()
    total_words = len(ref_words)
    
    if total_words == 0:
        return "Error: Empty reference text"
    
    # Find matching and non-matching words
    correct = 0
    incorrect_words = []
    
    for i, (ref_word, hyp_word) in enumerate(zip(ref_words, hyp_words)):
        if ref_word == hyp_word:
            correct += 1
        else:
            incorrect_words.append({
                'position': i + 1,
                'expected': ref_word,
                'actual': hyp_word if i < len(hyp_words) else '[missing]'
            })
    
    # Handle case where hypothesis is longer than reference
    if len(hyp_words) > len(ref_words):
        for i in range(len(ref_words), len(hyp_words)):
            incorrect_words.append({
                'position': i + 1,
                'expected': '[extra]',
                'actual': hyp_words[i]
            })
    
    accuracy = (correct / total_words) * 100
    
    # Format the results
    result = f"Accuracy: {accuracy:.2f}%\n"
    result += f"Correct Words: {correct}\n"
    result += f"Total Words: {total_words}\n"
    
    if incorrect_words:
        result += "\nWords to improve on:\n"
        for item in incorrect_words:
            result += f"Position {item['position']}: Expected '{item['expected']}', Got '{item['actual']}'\n"
    
    return result


def analyze(audio_path, chapter_text):
    """Transcribe and compare."""
    transcribed = recognize(audio_path)
    if transcribed.startswith("Error") or transcribed.startswith("Could not"):
        return transcribed
    return accuracy(chapter_text, transcribed)


def get_first_letters(text):
    """Generate first letters of each word for memorization."""
    return ' '.join([word[0].upper() if word else '' for word in text.split()])


def generate_quiz(verse_text):
    """Generate a fill-in-the-blank quiz from the verse."""
    words = verse_text.split()
    if len(words) < 5:  # Don't create quiz for very short verses
        return "Verse too short for a quiz"
    
    # Remove every 3rd word (adjust as needed for difficulty)
    quiz = []
    for i, word in enumerate(words):
        if i > 0 and i % 3 == 0 and len(word) > 3:  # Don't remove very short words
            quiz.append("___" + ("_" * len(word)) + "___")
        else:
            quiz.append(word)
    return ' '.join(quiz)


# --- Gradio UI ---

with gr.Blocks(title="Memory Test") as demo:
    gr.Markdown("# 📖 Memory Test")
    
    with gr.Row():
        with gr.Column(scale=1):
            # Add radio to choose between predefined and custom verses
            verse_source = gr.Radio(
                ["Predefined Verses", "Custom Verse"],
                label="Verse Source",
                value="Predefined Verses"
            )
            
            # Existing verse dropdown (initially visible)
            verse_dropdown = gr.Dropdown(
                choices=get_verse_dropdown(),
                label="Select a Verse",
                visible=True
            )
            
            # Add text area for custom verse (initially hidden)
            custom_verse = gr.Textbox(
                label="Enter Your Verse",
                placeholder="E.g., John 3:16 - For God so loved the world...",
                visible=False,
                lines=3
            )
            
            # Show/hide elements based on radio selection
            def toggle_verse_source(source):
                if source == "Predefined Verses":
                    return [
                        gr.Dropdown(visible=True),
                        gr.Textbox(visible=False)
                    ]
                else:
                    return [
                        gr.Dropdown(visible=False),
                        gr.Textbox(visible=True)
                    ]
            
            verse_source.change(
                fn=toggle_verse_source,
                inputs=verse_source,
                outputs=[verse_dropdown, custom_verse]
            )
            
            # Update the verse text based on selection or custom input
            def get_verse(source, dropdown, custom):
                if source == "Predefined Verses":
                    return get_verse_text(dropdown)
                return custom
                
            verse_text = gr.Textbox(label="Verse Text", interactive=False, lines=5)
            
            # Update the verse text when either input changes
            verse_dropdown.change(
                fn=lambda x: get_verse("Predefined Verses", x, ""),
                inputs=verse_dropdown,
                outputs=verse_text
            )
            
            custom_verse.change(
                fn=lambda x: get_verse("Custom Verse", "", x),
                inputs=custom_verse,
                outputs=verse_text
            )
            
            refresh_btn = gr.Button("🔄 Refresh Verses")
            
            # Update the refresh function to handle both sources
            def refresh_verse_list():
                return gr.Dropdown(choices=get_verse_dropdown())
            
            refresh_btn.click(
                fn=refresh_verse_list,
                outputs=verse_dropdown
            )
            
            # Update the analyze function to work with both sources
            def analyze_verse(audio_path, source, dropdown, custom_text):
                if source == "Predefined Verses":
                    verse = get_verse_text(dropdown)
                else:
                    verse = custom_text
                return analyze(audio_path, verse)


            def analyze_question_answer(user_answer, expected_answer, question_text):
                """
                Analyze the user's answer against the expected answer.
                
                Args:
                    user_answer (str or dict): The user's recorded audio file path (dict with 'path' key) or typed answer
                    expected_answer (str): The correct answer to the question
                    question_text (str): The question being answered
                    
                Returns:
                    str: Analysis of the user's answer
                """
                # Handle audio input (could be dict with 'path' or direct file path string)
                if isinstance(user_answer, dict) and 'path' in user_answer:
                    audio_path = user_answer['path']
                elif isinstance(user_answer, str) and user_answer.endswith(('.wav', '.mp3', '.ogg', '.m4a')):
                    audio_path = user_answer
                else:
                    audio_path = None
                
                # If we have an audio path, transcribe it
                if audio_path:
                    user_answer = recognize(audio_path)
                    if user_answer == "Could not understand audio.":
                        return "Sorry, I couldn't understand the audio. Please try again or type your answer."
                
                if not user_answer or not str(user_answer).strip():
                    return "Please provide an answer before analyzing."
        
                # Basic similarity check
                user_lower = str(user_answer).lower().strip()
                expected_lower = expected_answer.lower().strip()
    
                # Simple word overlap check
                user_words = set(user_lower.split())
                expected_words = set(expected_lower.split())
                common_words = user_words.intersection(expected_words)
    
                # Calculate a simple accuracy score
                if len(expected_words) > 0:
                    accuracy = len(common_words) / len(expected_words) * 100
                else:
                    accuracy = 0
    
                # Generate feedback
                feedback = f"Question: {question_text}\n\n"
                feedback += f"Your answer: {user_answer}\n\n"
                feedback += f"Expected answer: {expected_answer}\n\n"
                feedback += f"Accuracy: {accuracy:.1f}%\n\n"
    
                # Provide some qualitative feedback
                if accuracy > 80:
                    feedback += "Great job! Your answer is very close to the expected response."
                elif accuracy > 50:
                    feedback += "Good effort! Your answer has some key points but could be more complete."
                else:
                    feedback += "Try again. Consider reviewing the material and including more key points from the expected answer."
                
                return feedback
            
            # Audio section
            gr.Markdown("### Listen to the Verse")
            tts_btn = gr.Button("🔊 Play Audio")
            audio_out = gr.Audio(label="Audio Output", type="filepath")
            tts_btn.click(fn=tts, inputs=verse_text, outputs=audio_out)
            
            # Recording section
            gr.Markdown("### Record Your Recitation")
            user_audio = gr.Audio(label="Your Recording", type="filepath")
            
            # Analysis section
            analyze_btn = gr.Button("🧠 Analyze")
            result_box = gr.Textbox(label="Results", lines=10, interactive=False)
            analyze_btn.click(
                fn=analyze_verse,
                inputs=[
                    user_audio,
                    verse_source,
                    verse_dropdown,
                    custom_verse
                ],
                outputs=result_box
            )
            
            with gr.Tabs():
                with gr.TabItem("Memorization Tools"):
                    with gr.Row():
                        first_letters_btn = gr.Button("🔤 Show First Letters")
                        quiz_btn = gr.Button("❓ Generate Quiz")
                    
                    memorization_tool = gr.Textbox(label="Memorization Aid", lines=3, interactive=False)
                    
                    first_letters_btn.click(
                        fn=get_first_letters,
                        inputs=verse_text,
                        outputs=memorization_tool
                    )
                    
                    quiz_btn.click(
                        fn=generate_quiz,
                        inputs=verse_text,
                        outputs=memorization_tool
                    )
                
                with gr.TabItem("Practice"):
                    with gr.Row():
                        with gr.Column(scale=1):
                            question_display = gr.Textbox(label="Question")
                            with gr.Row():
                                with gr.Column(scale=4):
                                    answer_input = gr.Textbox(label="Your Answer", lines=3, 
                                                placeholder="Type or record your answer here...")
                            
                            with gr.Group():
                                gr.Markdown("### Listen to the Question")
                                with gr.Row():
                                    tts_btn = gr.Button("🔊 Play Question")
                                    audio_out = gr.Audio(label="Question Audio", type="filepath")
                                tts_btn.click(fn=tts, inputs=question_display, outputs=audio_out)
                            with gr.Group():
                                gr.Markdown("### Your Recording")
                                user_audio = gr.Audio(label="Your Recording", type="filepath")
                                analyze_btn = gr.Button("🧠 Analyze Answer")
                                result_box = gr.Textbox(label="Analysis Results", lines=8)
                                analyze_btn.click(
                                    fn=analyze_question_answer,
                                    inputs=[user_audio, answer_input, question_display],
                                    outputs=result_box
                                )
                    
                    # Help Section
                    with gr.Accordion("Need help?", open=False):
                        gr.Markdown("""
                        - Speak clearly when recording your answer
                        - Try to use complete sentences
                        - Refer to the verse text for guidance
                        - Click 'Play Question' to hear the question again
                        - Click 'Analyze Answer' to get feedback on your response
                        """)
    
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", ssl_certfile="cert.pem", ssl_keyfile="key.pem", ssl_verify=False, debug = True)
    requests.get(f"{demo.local_url}startup-events")