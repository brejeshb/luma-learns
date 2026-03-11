# generate_audio.py
import torch
from transformers import VitsModel, AutoTokenizer
import scipy
import os
from pathlib import Path
import re
from lessons_data import lessons_data, additional_phrases

class HokkienAudioGenerator:
    def __init__(self, output_dir="output"):
        """
        Initialize the Hokkien TTS generator
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        print("=" * 50)
        print("🎤 Hokkien Audio Generator")
        print("=" * 50)
        
        print("\n📥 Loading Meta's MMS-TTS-NAN model...")
        print("   (This might take a minute on first run)")
        
        try:
            # Load the model and tokenizer
            self.model = VitsModel.from_pretrained("facebook/mms-tts-nan")
            self.tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-nan")
            
            # Set to evaluation mode
            self.model.eval()
            
            # Use CPU (more compatible, no GPU needed)
            self.device = "cpu"
            self.model = self.model.to(self.device)
            
            print("✅ Model loaded successfully!")
            print(f"   Sampling rate: {self.model.config.sampling_rate} Hz")
            print(f"   Device: {self.device}")
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            print("\nTroubleshooting tips:")
            print("1. Make sure you have internet connection (first download)")
            print("2. Try: pip install --upgrade transformers")
            print("3. Check your disk space (model is ~2GB)")
            raise
    
    def extract_hokkien_text(self, hk_field):
        """
        Extract just the Hokkien pronunciation part from fields like '食飽未？(Chia̍h-pá--bē?)'
        
        Args:
            hk_field: The hk field from your data (e.g., "食飽未？(Chia̍h-pá--bē?)")
        
        Returns:
            Clean Hokkien text for TTS
        """
        # Method 1: Extract content inside parentheses if present
        if '(' in hk_field and ')' in hk_field:
            # Find text between last '(' and last ')'
            start = hk_field.rfind('(') + 1
            end = hk_field.rfind(')')
            if start < end:
                return hk_field[start:end].strip()
        
        # Method 2: Remove Chinese characters, keep romanization
        # This regex removes Chinese characters but keeps Latin letters and punctuation
        cleaned = re.sub(r'[^\x00-\x7F]+', '', hk_field)  # Remove non-ASCII
        cleaned = re.sub(r'[()]', '', cleaned).strip()    # Remove parentheses
        
        if cleaned:
            return cleaned
        
        # Method 3: If all else fails, return the whole string
        print(f"⚠️  Couldn't parse '{hk_field}', using as-is")
        return hk_field
    
    def clean_filename(self, text):
        """
        Create a safe filename from text
        """
        # Convert to lowercase and replace spaces with underscores
        filename = text.lower()
        # Remove special characters, keep letters, numbers, underscores
        filename = re.sub(r'[^a-z0-9\s-]', '', filename)
        filename = re.sub(r'[-\s]+', '_', filename)
        # Limit length
        return filename[:50].strip('_')
    
    def generate_audio(self, text, description=""):
        """
        Generate Hokkien audio from text
        
        Args:
            text: Hokkien text (romanization)
            description: Description for filename
        
        Returns:
            Path to generated audio file
        """
        print(f"\n🔊 Generating: {description}")
        print(f"   Text: {text}")
        
        try:
            # Tokenize input
            inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
            
            # Generate audio
            with torch.no_grad():
                output = self.model(**inputs).waveform
            
            # Convert to numpy
            audio_array = output.squeeze().cpu().numpy()
            
            # Create filename
            if description:
                filename = self.clean_filename(description) + ".wav"
            else:
                filename = self.clean_filename(text[:30]) + ".wav"
            
            # Save file
            output_path = self.output_dir / filename
            scipy.io.wavfile.write(
                output_path,
                rate=self.model.config.sampling_rate,
                data=audio_array
            )
            
            # Get file size
            size_kb = os.path.getsize(output_path) / 1024
            
            print(f"   ✅ Saved: {filename} ({size_kb:.1f} KB)")
            return str(output_path)
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    def generate_all_phrases(self):
        """
        Generate audio for all phrases in the lessons
        """
        print("\n" + "=" * 50)
        print("📋 Generating All Phrases")
        print("=" * 50)
        
        generated_files = []
        
        # Generate from lessons
        for lesson in lessons_data:
            print(f"\n📚 Lesson: {lesson['title']}")
            for word in lesson['words']:
                # Extract clean Hokkien text
                hokkien_text = self.extract_hokkien_text(word['hk'])
                
                # Generate audio
                audio_path = self.generate_audio(
                    text=hokkien_text,
                    description=f"{word['en']}"
                )
                
                if audio_path:
                    generated_files.append({
                        'english': word['en'],
                        'hokkien': word['hk'],
                        'hokkien_clean': hokkien_text,
                        'audio_file': audio_path
                    })
        
        # Generate additional phrases
        if additional_phrases:
            print("\n📚 Additional Phrases")
            for phrase in additional_phrases:
                hokkien_text = self.extract_hokkien_text(phrase['hk'])
                audio_path = self.generate_audio(
                    text=hokkien_text,
                    description=f"bonus_{phrase['en']}"
                )
                
                if audio_path:
                    generated_files.append({
                        'english': phrase['en'],
                        'hokkien': phrase['hk'],
                        'hokkien_clean': hokkien_text,
                        'audio_file': audio_path
                    })
        
        return generated_files
    
    def test_single_phrase(self):
        """
        Test with a single phrase first
        """
        print("\n" + "=" * 50)
        print("🧪 Testing Single Phrase")
        print("=" * 50)
        
        # Test with a simple phrase
        test_phrase = "Lim tsúi"  # Drink water in romanization
        return self.generate_audio(test_phrase, "test_drink_water")

def main():
    """
    Main function to run the generator
    """
    print("\n🎵 Hokkien Audio Generator")
    print("   For your friend to listen 🎧")
    print("=" * 50)
    
    # Create generator
    generator = HokkienAudioGenerator()
    
    # Option 1: Test with single phrase first
    print("\n🔧 Running test...")
    test_file = generator.test_single_phrase()
    
    if test_file:
        print(f"\n✅ Test successful! File saved to: {test_file}")
        
        # Option 2: Generate all phrases
        print("\n" + "=" * 50)
        response = input("Generate all phrases? (y/n): ").strip().lower()
        
        if response == 'y':
            print("\n🎯 Generating all phrases...")
            files = generator.generate_all_phrases()
            
            print("\n" + "=" * 50)
            print("📊 Summary")
            print("=" * 50)
            print(f"✅ Generated {len(files)} audio files")
            print(f"📁 Location: {generator.output_dir.absolute()}")
            
            print("\n📋 Files created:")
            for f in files:
                print(f"   • {f['english']}: {os.path.basename(f['audio_file'])}")
                print(f"     Text: {f['hokkien_clean']}")
            
            print("\n🎧 You can now:")
            print("1. Open the 'output' folder")
            print("2. Play the WAV files")
            print("3. Send them to your friend!")
    else:
        print("❌ Test failed. Please check the error messages above.")

if __name__ == "__main__":
    main()