import gradio as gr
import os
from pathlib import Path
from gtts import gTTS
import tempfile
import speech_recognition as sr
from pydub import AudioSegment
import requests

# --- Utility Functions ---

luke_10 = {
    }

def get_verse_dropdown():
    """Create verse dropdown with verse numbers and preview text."""
    return [f"Verse {num}: {text[:30]}..." for num, text in luke_10.items()]

def get_verse_text(dropdown_selection):
    """Extract verse text from dropdown selection."""
    if not dropdown_selection:
        return ""
    verse_num = int(dropdown_selection.split(":")[0].split()[-1])
    return luke_10.get(verse_num, "Verse not found")

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

    # Verse selection
    with gr.Row():
        verse_dropdown = gr.Dropdown(
            choices=get_verse_dropdown(),
            label="Select a Verse",
            value=None
        )
        refresh_btn = gr.Button("🔄", variant="secondary")
    
    verse_text = gr.Textbox(label="Verse Text", lines=4, interactive=False)
    
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
            analyze_btn.click(fn=analyze, inputs=[user_audio, verse_text], outputs=result_box)
    
    def refresh_verse_list():
        return gr.Dropdown(choices=get_verse_dropdown())
    
    refresh_btn.click(fn=refresh_verse_list, outputs=verse_dropdown)

    verse_dropdown.change(fn=get_verse_text, inputs=verse_dropdown, outputs=verse_text)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", ssl_certfile="cert.pem", ssl_keyfile="key.pem", ssl_verify=False, debug = True)
    requests.get(f"{demo.local_url}startup-events")