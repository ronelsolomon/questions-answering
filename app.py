import gradio as gr
import os
from pathlib import Path
from gtts import gTTS
import tempfile
import speech_recognition as sr
from pydub import AudioSegment
import requests

# --- Utility Functions ---

luke_verses = {
    "Luke 1:1-2": "Many have undertaken to draw up an account of the things that have been fulfilled among us, just as they were handed down to us by those who from the first were eyewitnesses and servants of the word.",
    "Luke 1:3-4": "With this in mind, since I myself have carefully investigated everything from the beginning, I too decided to write an orderly account for you, most excellent Theophilus, so that you may know the certainty of the things you have been taught.",
    "Luke 1:16-17": "He will bring back many of the people of Israel to the Lord their God. And he will go on before the Lord, in the spirit and power of Elijah, to turn the hearts of the parents to their children and the disobedient to the wisdom of the righteous - to make ready a people prepared for the Lord.",
    "Luke 1:31": "You will conceive and give birth to a son, and you are to call him Jesus.",
    "Luke 1:32-33": "He will be great and will be called the Son of the Most High. The Lord God will give him the throne of his father David, and he will reign over Jacob's descendants forever; his kingdom will never end.",
    "Luke 1:46-48": "And Mary said: 'My soul glorifies the Lord and my spirit rejoices in God my Savior, for he has been mindful of the humble state of his servant. From now on all generations will call me blessed,'",
    "Luke 2:6-7": "While they were there, the time came for the baby to be born, and she gave birth to her firstborn, a son. She wrapped him in cloths and placed him in a manger, because there was no guest room available for them.",
    "Luke 2:10": "But the angel said to them, 'Do not be afraid. I bring you good news that will cause great joy for all the people.'",
    "Luke 2:11-12": "Today in the town of David a Savior has been born to you; he is the Messiah, the Lord. This will be a sign to you: You will find a baby wrapped in cloths and lying in a manger.",
    "Luke 2:13-14": "Suddenly a great company of the heavenly host appeared with the angel, praising God and saying, 'Glory to God in the highest heaven, and on earth peace to those on whom his favor rests.'",
    "Luke 2:49": "'Why were you searching for me?' he asked. 'Didn't you know I had to be in my Father's house?'",
    "Luke 2:52": "And Jesus grew in wisdom and stature, and in favor with God and man.",
    "Luke 3:4": "As it is written in the book of the words of Isaiah the prophet: 'A voice of one calling in the wilderness, 'Prepare the way for the Lord, make straight paths for him.'",
    "Luke 3:8": "Produce fruit in keeping with repentance. And do not begin to say to yourselves, 'We have Abraham as our father.' For I tell you that out of these stones God can raise up children for Abraham.",
    "Luke 3:16": "John answered them all, 'I baptize you with water. But one who is more powerful than I will come, the straps of whose sandals I am not worthy to untie. He will baptize you with the Holy Spirit and fire.'",
    "Luke 3:21-22": "When all the people were being baptized, Jesus was baptized too. And as he was praying, heaven was opened and the Holy Spirit descended on him in bodily form like a dove. And a voice came from heaven: 'You are my Son, whom I love; with you I am well pleased.'",
    "Luke 4:4": "Jesus answered, 'It is written: Man shall not live on bread alone.'",
    "Luke 4:7-8": "'If you worship me, it will all be yours.' Jesus answered, 'It is written: Worship the Lord your God and serve him only.'",
    "Luke 4:12-13": "Jesus answered, 'It is said: Do not put the Lord your God to the test.' When the devil had finished all this tempting, he left him until an opportune time.",
    "Luke 4:18-19": "'The Spirit of the Lord is on me, because he has anointed me to proclaim good news to the poor. He has sent me to proclaim freedom for the prisoners and recovery of sight for the blind, to set the oppressed free, to proclaim the year of the Lord's favor.'",
    "Luke 5:24-25": "But I want you to know that the Son of Man has authority on earth to forgive sins. So he said to the paralyzed man, 'I tell you, get up, take your mat and go home.' Immediately he stood up in front of them, took what he had been lying on and went home praising God.",
    "Luke 5:31-32": "Jesus answered them, 'It is not the healthy who need a doctor, but the sick. I have not come to call the righteous, but sinners to repentance.'",
    "Luke 6:5": "Then Jesus said to them, 'The Son of Man is Lord of the Sabbath.'",
    "Luke 6:20": "Looking at his disciples, he said: 'Blessed are you who are poor, for yours is the kingdom of God.'",
    "Luke 6:21": "Blessed are you who hunger now, for you will be satisfied. Blessed are you who weep now, for you will laugh.",
    "Luke 6:22-23": "Blessed are you when people hate you, when they exclude you and insult you and reject your name as evil, because of the Son of Man. Rejoice in that day and leap for joy, because great is your reward in heaven. For that is how their ancestors treated the prophets.",
    "Luke 6:27-28": "But to you who are listening I say: Love your enemies, do good to those who hate you, bless those who curse you, pray for those who mistreat you.",
    "Luke 6:31": "Do to others as you would have them do to you.",
    "Luke 6:36": "Be merciful, just as your Father is merciful.",
    "Luke 6:37": "Do not judge, and you will not be judged. Do not condemn, and you will not be condemned. Forgive, and you will be forgiven.",
    "Luke 6:38": "Give, and it will be given to you. A good measure, pressed down, shaken together and running over, will be poured into your lap. For with the measure you use, it will be measured to you.",
    "Luke 6:45": "A good man brings good things out of the good stored up in his heart, and an evil man brings evil things out of the evil stored up in his heart. For the mouth speaks what the heart is full of.",
    "Luke 7:9": "When Jesus heard this, he was amazed at him, and turning to the crowd following him, he said, 'I tell you, I have not found such great faith even in Israel.'",
    "Luke 7:22-23": "So he replied to the messengers, 'Go back and report to John what you have seen and heard: The blind receive sight, the lame walk, those who have leprosy are cleansed, the deaf hear, the dead are raised, and the good news is proclaimed to the poor. Blessed is anyone who does not stumble on account of me.'",
    "Luke 8:16-17": "No one lights a lamp and hides it in a clay jar or puts it under a bed. Instead, they put it on a stand, so that those who come in can see the light. For there is nothing hidden that will not be disclosed, and nothing concealed that will not be known or brought out into the open.",
    "Luke 9:20": "But what about you? he asked. Who do you say I am? Peter answered, God's Messiah.",
    "Luke 9:25": "What good is it for someone to gain the whole world, and yet lose or forfeit their very self?",
    "Luke 9:29": "As he was praying, the appearance of his face changed, and his clothes became as bright as a flash of lightning.",
    "Luke 9:48": "Then he said to them, 'Whoever welcomes this little child in my name welcomes me; and whoever welcomes me welcomes the one who sent me. For it is the one who is least among you all who is the greatest.'",
    "Luke 9:62": "Jesus replied, 'No one who puts a hand to the plow and looks back is fit for service in the kingdom of God.'",
    "Luke 10:2": "He told them, 'The harvest is plentiful, but the workers are few. Ask the Lord of the harvest, therefore, to send out workers into his harvest field.'",
    "Luke 10:20": "However, do not rejoice that the spirits submit to you, but rejoice that your names are written in heaven.",
    "Luke 10:21": "At that time Jesus, full of joy through the Holy Spirit, said, 'I praise you, Father, Lord of heaven and earth, because you have hidden these things from the wise and learned, and revealed them to little children. Yes, Father, for this is what you were pleased to do.'",
    "Luke 10:22": "All things have been committed to me by my Father. No one knows who the Son is except the Father, and no one knows who the Father is except the Son and those to whom the Son chooses to reveal him.",
    "Luke 10:27": "He answered, 'Love the Lord your God with all your heart and with all your soul and with all your strength and with all your mind'; and, 'Love your neighbor as yourself.'",
    "Luke 11:2-4": "He said to them, 'When you pray, say: Father, hallowed be your name, your kingdom come. Give us each day our daily bread. Forgive us our sins, for we also forgive everyone who sins against us. And lead us not into temptation.'",
    "Luke 11:9-10": "So I say to you: Ask and it will be given to you; seek and you will find; knock and the door will be opened to you. For everyone who asks receives; the one who seeks finds; and to the one who knocks, the door will be opened.",
    "Luke 11:13": "If you then, though you are evil, know how to give good gifts to your children, how much more will your Father in heaven give the Holy Spirit to those who ask him!",
    "Luke 11:17": "Jesus knew their thoughts and said to them: 'Any kingdom divided against itself will be ruined, and a house divided against itself will fall.'",
    "Luke 12:8-9": "I tell you, whoever publicly acknowledges me before others, the Son of Man will also acknowledge before the angels of God. But whoever disowns me before others will be disowned before the angels of God.",
    "Luke 12:22-23": "Then Jesus said to his disciples: 'Therefore I tell you, do not worry about your life, what you will eat; or about your body, what you will wear. For life is more than food, and the body more than clothes.'",
    "Luke 12:31": "But seek his kingdom, and these things will be given to you as well.",
    "Luke 12:34": "For where your treasure is, there your heart will be also.",
    "Luke 13:16": "Then should not this woman, a daughter of Abraham, whom Satan has kept bound for eighteen long years, be set free on the Sabbath day from what bound her?",
    "Luke 13:24": "Make every effort to enter through the narrow door, because many, I tell you, will try to enter and will not be able to.",
    "Luke 13:30": "Indeed there are those who are last who will be first, and first who will be last.",
    "Luke 14:11": "For all those who exalt themselves will be humbled, and those who humble themselves will be exalted.",
    "Luke 14:27": "And whoever does not carry their cross and follow me cannot be my disciple.",
    "Luke 15:4": "Suppose one of you has a hundred sheep and loses one of them. Doesn't he leave the ninety-nine in the open country and go after the lost sheep until he finds it?",
    "Luke 15:7": "I tell you that in the same way there will be more rejoicing in heaven over one sinner who repents than over ninety-nine righteous persons who do not need to repent.",
    "Luke 15:24": "For this son of mine was dead and is alive again; he was lost and is found.' So they began to celebrate.",
    "Luke 16:13": "No one can serve two masters. Either you will hate the one and love the other, or you will be devoted to the one and despise the other. You cannot serve both God and money.",
    "Luke 16:31": "He said to him, 'If they do not listen to Moses and the Prophets, they will not be convinced even if someone rises from the dead.'",
    "Luke 17:1-2": "Jesus said to his disciples: 'Things that cause people to stumble are bound to come, but woe to anyone through whom they come. It would be better for them to be thrown into the sea with a millstone tied around their neck than to cause one of these little ones to stumble.'",
    "Luke 17:20-21": "Once, on being asked by the Pharisees when the kingdom of God would come, Jesus replied, 'The coming of the kingdom of God is not something that can be observed, nor will people say, 'Here it is,' or 'There it is,' because the kingdom of God is in your midst.'",
    "Luke 17:33": "Whoever tries to keep their life will lose it, and whoever loses their life will preserve it.",
    "Luke 18:16-17": "But Jesus called the children to him and said, 'Let the little children come to me, and do not hinder them, for the kingdom of God belongs to such as these. Truly I tell you, anyone who will not receive the kingdom of God like a little child will never enter it.'",
    "Luke 18:27": "Jesus replied, 'What is impossible with man is possible with God.'",
    "Luke 19:10": "For the Son of Man came to seek and to save the lost.",
    "Luke 19:38": "Blessed is the king who comes in the name of the Lord! Peace in heaven and glory in the highest!",
    "Luke 19:47-48": "Every day he was teaching at the temple. But the chief priests, the teachers of the law and the leaders among the people were trying to kill him. Yet they could not find any way to do it, because all the people hung on his words.",
    "Luke 20:26": "They were unable to trap him in what he had said there in public. And astonished by his answer, they became silent.",
    "Luke 20:38": "He is not the God of the dead, but of the living, for to him all are alive.",
    "Luke 21:14-15": "But make up your mind not to worry beforehand how you will defend yourselves. For I will give you words and wisdom that none of your adversaries will be able to resist or contradict.",
    "Luke 21:28": "When these things begin to take place, stand up and lift up your heads, because your redemption is drawing near.",
    "Luke 21:33": "Heaven and earth will pass away, but my words will never pass away.",
    "Luke 22:19": "And he took bread, gave thanks and broke it, and gave it to them, saying, 'This is my body given for you; do this in remembrance of me.'",
    "Luke 22:20": "In the same way, after the supper he took the cup, saying, 'This cup is the new covenant in my blood, which is poured out for you.'",
    "Luke 22:42": "Father, if you are willing, take this cup from me; yet not my will, but yours be done.",
    "Luke 22:43-44": "An angel from heaven appeared to him and strengthened him. And being in anguish, he prayed more earnestly, and his sweat was like drops of blood falling to the ground.",
    "Luke 23:34": "Jesus said, 'Father, forgive them, for they do not know what they are doing.' And they divided up his clothes by casting lots.",
    "Luke 23:42-43": "Then he said, 'Jesus, remember me when you come into your kingdom.' Jesus answered him, 'Truly I tell you, today you will be with me in paradise.'",
    "Luke 23:46": "Jesus called out with a loud voice, 'Father, into your hands I commit my spirit.' When he had said this, he breathed his last.",
    "Luke 24:6-7": "He is not here; he has risen! Remember how he told you, while he was still with you in Galilee: The Son of Man must be delivered over to the hands of sinners, be crucified and on the third day be raised again.",
    "Luke 24:44": "He said to them, 'This is what I told you while I was still with you: Everything must be fulfilled that is written about me in the Law of Moses, the Prophets and the Psalms.'",
    "Luke 24:45-47": "Then he opened their minds so they could understand the Scriptures. He told them, 'This is what is written: The Messiah will suffer and rise from the dead on the third day, and repentance for the forgiveness of sins will be preached in his name to all nations, beginning at Jerusalem.'",
    "Luke 24:49": "I am going to send you what my Father has promised; but stay in the city until you have been clothed with power from on high."
}


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