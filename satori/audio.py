import os
import ffmpeg
from pydub import AudioSegment

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "authentication.json"

def synthesize_text_english(text, output_string):
    from google.cloud import texttospeech

    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.SynthesisInput(text=text)

    # Note: the voice can also be specified by name.
    # Names of voices can be retrieved with client.list_voices().
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="US-wavenet-F",
        ssml_gender=texttospeech.SsmlVoiceGender.MALE,
    )

    audio_config = texttospeech.AudioConfig(
        pitch = 4.2,
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        request={"input": input_text, "voice": voice, "audio_config": audio_config}
    )

    # The response's audio_content is binary.
    with open(output_string, "wb") as out:
        out.write(response.audio_content)
        print('Audio content written to file "output.mp3"')

def synthesize_text_chinese(text, output_string):
    from google.cloud import texttospeech

    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.SynthesisInput(text=text)

    # Note: the voice can also be specified by name.
    # Names of voices can be retrieved with client.list_voices().
    voice = texttospeech.VoiceSelectionParams(
        language_code="yue-HK",
        name="yue-HK-Standard-A",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
    )

    audio_config = texttospeech.AudioConfig(
        pitch = 3.2,
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        request={"input": input_text, "voice": voice, "audio_config": audio_config}
    )

    # The response's audio_content is binary.
    with open(output_string, "wb") as out:
        out.write(response.audio_content)
        print('Audio content written to file "output.mp3"')

def synthesize_text(text, audio_path):
    if len(text) > 5000:
        text1 = synthesize_text_english(text[0:4998], "output1.mp3")
        text2 = synthesize_text_english(text[4999:len(text)], "output2.mp3")

        audio1 = ffmpeg.input("output1.mp3")
        audio2 = ffmpeg.input("output2.mp3")
        #sound1 = AudioSegment.from_wav("output1.wav")
        #sound2 = AudioSegment.from_wav("output2.wav")

        ffmpeg.concat(audio1, audio2, v=0, a=2).output(audio_path).run()
        #combined_sounds = sound1 + sound2
        #combined_sounds.export(audio_path, format="mp3")

    else:
        synthesize_text_english(text, audio_path)
