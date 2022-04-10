import os
import ffmpeg
from pydub import AudioSegment
from common import MAX_VIDEO_LENGTH

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

def synthesize_text(text_arr, audio_dir):
    '''
    text is an array of texts that can be greater in length than 5000 
    between each element in the array we will add an additional 3 seconds of silence 
    and return the combined audio
    '''

    # creates a file with name audio_path
    times = []
    #synthesize_text_english("", audio_path)
    #prev = AudioSegment.from_file(audio_path, format="mp3")
    prev=None
    idx = 0
    for text in text_arr: 
        for _ in range(2):
            if len(text) > 5000: 
                text1 = synthesize_text_english(text[0:4998], "output1.mp3")
                text2 = synthesize_text_english(text[4999:len(text)], "output2.mp3")

                audio1 = AudioSegment.from_file("output1.mp3", format="mp3")
                audio2 = AudioSegment.from_file("output2.mp3", format="mp3")
                #prev = AudioSegment.from_file(audio_path, format="mp3") # audio_path is the name of the file
                if prev == None:
                    new_prev = audio1 + audio2 # combine the three audios
                else:
                    new_prev = prev + audio1 + audio2
                #file_handle = outpt.export(audio_path, format="mp3")
            else: 
                text = synthesize_text_english(text, "output1.mp3") 

                audio1 = AudioSegment.from_file("output1.mp3", format="mp3")
                #prev = AudioSegment.from_file(audio_path, format="mp3")

                if prev == None:
                    new_prev = audio1
                else:
                    new_prev = prev + audio1

                #file_handle = outpt.export(audio_path, format="mp3")

            second_of_silence = AudioSegment.silent(duration = 3)
            #prev = AudioSegment.from_file(audio_path, format="mp3")
            times.append(prev.duration_seconds)

            new_prev = new_prev + second_of_silence

            if new_prev.duration_seconds > MAX_VIDEO_LENGTH:
                os.makedirs(f'{audio_dir}/{idx}', exist_ok=True)
                file_handle = prev.export(f'{audio_dir}/{idx}/audio.mp3', format="mp3")
                idx += 1
                prev = None
            else:
                prev = new_prev

    if prev is not None:
        file_handle = prev.export(f'{audio_dir}/{idx}/audio.mp3', format="mp3")
        idx += 1
    return times, idx 