import docker
import os
import librosa
import soundfile as sf
import subprocess
import json

from src.song_analyzer.flattener import flatten  # Import flatten function


def is_docker_running():
    try:
        subprocess.check_output(["docker", "info"], stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        print("Docker is not installed or not in PATH.")
        return False


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
    if not is_docker_running():
        print("Docker is not running. Please start Docker and try again.")
        return

    wav_path = convert_to_wav(audio_path)
    if wav_path is None:
        print("Audio conversion failed.")
        return

    # Define the output file path
    output_file = os.path.join(os.path.dirname(wav_path), "analysis_output.json")

    # Delete the output file if it already exists
    if os.path.exists(output_file):
        os.remove(output_file)

    try:
        client = docker.from_env()
        volume_mapping = {
            os.path.abspath(os.path.dirname(wav_path)): {"bind": "/workspace", "mode": "rw"}
        }

        # Run Essentia Docker container to write JSON output to /output/analysis_output.json
        container = client.containers.run(
            "mtgupf/essentia",
            f"sh -c 'essentia_streaming_extractor_music /workspace/{os.path.basename(wav_path)} /workspace/analysis_output.json'",
            detach=True,
            volumes=volume_mapping
        )

        # Wait for container to finish
        container.wait()
        container.remove()

        # Load and flatten JSON data
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                data = json.load(f)

            try:
                # Flatten the JSON data and print it
                flattened_data = {}
                flatten(data, "", flattened_data)
                print("Flattened Essentia Analysis Results:")
                for key, value in flattened_data.items():
                    print(f"{key}: {value}")

                # Log successful flattening
                print("Flattening successful. Deleting analysis_output.json.")

                # Delete the file after successful flattening
                os.remove(output_file)

            except Exception as e:
                print(f"An error occurred during flattening: {e}")
                print("Keeping analysis_output.json for inspection.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    audio_file = r"C:\Python\MusicAI\musicAnalyzer\data\sample\01LaFemmeDargent.mp3"
    if not os.path.exists(audio_file):
        print(f"Error: Input file not found at {audio_file}")
    else:
        analyze_audio_with_essentia(audio_file)
