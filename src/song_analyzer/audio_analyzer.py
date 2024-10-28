import docker
import os
import librosa
import soundfile as sf

def convert_to_wav(audio_path):
    if not os.path.exists(audio_path):
        print(f"Error: File not found at {audio_path}")
        return None

    if audio_path.endswith(".wav"):
        return audio_path

    print(f"Converting {audio_path} to WAV format...")
    wav_path = audio_path.rsplit(".", 1)[0] + ".wav"

    try:
        y, sr = librosa.load(audio_path, sr=None)
        sf.write(wav_path, y, sr)
        return wav_path
    except Exception as e:
        print(f"Error during conversion: {e}")
        return None

def analyze_audio_with_essentia(audio_path):
    wav_path = convert_to_wav(audio_path)
    if wav_path is None:
        print("Audio conversion failed.")
        return

    client = docker.from_env()
    try:
        volume_mapping = {
            os.path.abspath(os.path.dirname(wav_path)): {"bind": "/workspace", "mode": "rw"}
        }

        # Run the Essentia Docker container and output JSON to console
        container = client.containers.run(
            "mtgupf/essentia",
            f"sh -c 'essentia_streaming_extractor_music /workspace/{os.path.basename(wav_path)} /workspace/analysis_output.json && cat /workspace/analysis_output.json'",
            detach=True,
            volumes=volume_mapping
        )

        # Wait for container to finish and capture logs
        container.wait()
        logs = container.logs()
        print("Essentia Analysis Results:")
        print(logs.decode("utf-8"))

        container.remove()

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Use absolute paths
    audio_file = r"C:\Python\MusicAI\musicAnalyzer\data\sample\01LaFemmeDargent.mp3"

    if not os.path.exists(audio_file):
        print(f"Error: Input file not found at {audio_file}")
    else:
        analyze_audio_with_essentia(audio_file)
