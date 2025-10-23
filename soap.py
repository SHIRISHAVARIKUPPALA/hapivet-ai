# ================================
# 🧠 AI-Based SOAP Segmentation from Audio
# Converts medical audio conversations into structured SOAP notes
# ================================

# --- Install required packages (in Colab environment) ---
# moviepy: For audio processing
# openai-whisper: For automatic speech recognition (ASR)
# pandas & openpyxl: For data handling and Excel export
# spacy: For natural language processing
!pip install moviepy openai-whisper pandas openpyxl spacy

# --- Download the English language model for spaCy ---
!python -m spacy download en_core_web_sm


# --- Import required libraries ---
import moviepy.editor as mp       # For handling audio files
import whisper                    # For speech-to-text transcription
import pandas as pd               # For data manipulation and storage
import os                         # For file path and OS operations
from google.colab import files    # For uploading/downloading files in Google Colab
import spacy                      # For natural language processing


# --- Load the English NLP model ---
nlp = spacy.load("en_core_web_sm")


# ======================================
# 1️⃣ UPLOAD MEDIA FILE
# ======================================
print("📤 Please upload your audio or video file...")

# Prompt user to upload a media file via Colab’s upload widget
uploaded = files.upload()

# Get the uploaded filename
media_filename = list(uploaded.keys())[0]
print(f"✅ Uploaded file: {media_filename}")


# ======================================
# 2️⃣ EXTRACT AUDIO FROM MEDIA
# ======================================
try:
    # Try loading as a audio file
    clip = mp.VideoFileClip(media_filename)

    # Extract the audio track and save it as a .wav file
    audio_path = "extracted_audio.wav"
    clip.audio.write_audiofile(audio_path)

    # Store video duration (for record-keeping)
    media_duration = clip.duration

except Exception as e:
    # If the uploaded file is audio-only (no video track), load it directly
    clip = mp.AudioFileClip(media_filename)
    audio_path = media_filename
    media_duration = clip.duration

print("✅ Audio extracted successfully!")


# ======================================
# 3️⃣ TRANSCRIBE AUDIO USING WHISPER
# ======================================
print("🧠 Transcribing audio...")

# Load the Whisper model (base variant – balanced accuracy and speed)
model = whisper.load_model("base")

# Perform transcription
result = model.transcribe(audio_path)

# Extract the transcribed text
transcribed_text = result["text"]

# Display the generated transcript
print("\n📝 Generated Text:")
print(transcribed_text)


# ======================================
# 4️⃣ GENERATE SOAP COMPONENTS USING NLP
# ======================================
def generate_soap_components(transcript):
    """
    Takes the transcribed text as input and splits it into
    four components of the SOAP medical documentation format:
    Subjective, Objective, Assessment, and Plan.
    """

    # Process text with spaCy to get sentence-level structure
    doc = nlp(transcript)
    sentences = [sent.text.strip() for sent in doc.sents]

    # Define keyword lists to detect each SOAP category
    subjective_kw = ["i feel", "pain", "complain", "issue", "problem", "symptom", "experience"]
    objective_kw = ["observed", "examined", "measured", "vital", "temperature", "blood pressure", "heart rate", "inspection", "test"]
    assessment_kw = ["diagnosis", "assess", "impression", "finding", "conclude", "likely"]
    plan_kw = ["recommend", "advise", "plan", "follow-up", "should", "next step", "treatment", "prescribe"]

    # Helper function to extract sentences that match keywords
    def extract_sentences(keywords):
        extracted = [s for s in sentences if any(k in s.lower() for k in keywords)]
        return " ".join(extracted) if extracted else "N/A"

    # Extract each component based on keyword detection
    subjective = extract_sentences(subjective_kw)
    objective = extract_sentences(objective_kw)
    assessment = extract_sentences(assessment_kw)
    plan = extract_sentences(plan_kw)

    # Return the four categorized sections
    return subjective, objective, assessment, plan


# Call the function on the transcribed text
subjective, objective, assessment, plan = generate_soap_components(transcribed_text)


# ======================================
# 5️⃣ DISPLAY GENERATED SOAP NOTES
# ======================================
print("\n📄 SOAP Notes:")
print(f"Subjective:\n{subjective}\n")
print(f"Objective:\n{objective}\n")
print(f"Assessment:\n{assessment}\n")
print(f"Plan:\n{plan}\n")


# ======================================
# 6️⃣ CREATE STRUCTURED RECORD
# ======================================
# Prepare a single structured dictionary record for this file
record = {
    "File Name": media_filename,                           # Input filename
    "Duration (sec)": int(media_duration),                 # File duration in seconds
    "Generated Text": transcribed_text.strip(),            # Full transcript
    "Summary": transcribed_text[:150] + "..." if len(transcribed_text) > 150 else transcribed_text,  # Short summary
    "Subjective": subjective,                              # Extracted subjective info
    "Objective": objective,                                # Extracted objective info
    "Assessment": assessment,                              # Extracted assessment info
    "Plan": plan                                           # Extracted plan info
}


# ======================================
# 7️⃣ SAVE OR UPDATE RECORDS IN EXCEL
# ======================================
excel_file = "media_records.xlsx"  # Output Excel filename

# Check if Excel file already exists
if os.path.exists(excel_file):
    # Read existing records
    df = pd.read_excel(excel_file)

    # If the same file name already exists, update that record
    if media_filename in df['File Name'].values:
        print("⚡ Existing record found. Updating it...")
        df.loc[df['File Name'] == media_filename, :] = pd.DataFrame([record])
    else:
        # Otherwise, append the new record
        df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
else:
    # If no Excel file exists, create a new one
    df = pd.DataFrame([record])

# Write the final DataFrame back to Excel
df.to_excel(excel_file, index=False)
print(f"\n✅ Record saved/updated successfully to {excel_file}")


# ======================================
# 8️⃣ DOWNLOAD OUTPUT EXCEL FILE
# ======================================
# Automatically trigger file download in Google Colab
files.download(excel_file)
print("📥 Excel file downloaded successfully!")

# ======================================
# ✅ END OF SCRIPT
# ======================================

