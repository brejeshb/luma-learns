# generate_audio_tailo.py
import torch
from transformers import VitsModel, AutoTokenizer
import scipy
import os
from pathlib import Path
import re
from lessons_data2 import lessons_data_tailo, additional_phrases_tailo

# Import from original file for any shared functions
from joi_speaks import HokkienAudioGenerator as BaseGenerator

class HokkienTailoGenerator(BaseGenerator):
    """
    Specialized generator for Tâi-lô romanization
    Outputs to 'output2' folder
    """
    def __init__(self, output_dir="output2"):
        # Initialize with output2 directory
        super().__init__(output_dir)
        print("📍 Using Tâi-lô romanization")
        print("📁 Output folder: output2/")
    
    def extract_hokkien_text(self, word_data):
        """
        Extract Tâi-lô text specifically for TTS
        Uses hk_tts field if available, falls back to extracting from hk_display
        """
        # If word_data is a dict with hk_tts field, use it directly
        if isinstance(word_data, dict) and 'hk_tts' in word_data:
            return word_data['hk_tts']
        
        # If it's a string (old format), try to extract
        if isinstance(word_data, str):
            return super().extract_hokkien_text(word_data)
        
        # Fallback to hk_display if available
        if isinstance(word_data, dict) and 'hk_display' in word_data:
            return super().extract_hokkien_text(word_data['hk_display'])
        
        return ""
    
    def get_display_text(self, word_data):
        """Get the display text (for HTML)"""
        if isinstance(word_data, dict) and 'hk_display' in word_data:
            return word_data['hk_display']
        elif isinstance(word_data, dict) and 'hk' in word_data:
            return word_data['hk']
        return str(word_data)
    
    def generate_all_phrases(self):
        """Generate all Tâi-lô phrases"""
        print("\n" + "=" * 50)
        print("📋 Generating All Tâi-lô Phrases")
        print("=" * 50)
        
        generated_files = []
        
        # Generate from lessons
        for lesson in lessons_data_tailo:
            print(f"\n📚 Lesson: {lesson['title']}")
            for word in lesson['words']:
                # Extract Tâi-lô text for TTS
                tts_text = self.extract_hokkien_text(word)
                display_text = self.get_display_text(word)
                
                # Generate audio
                audio_path = self.generate_audio(
                    text=tts_text,
                    description=f"tailo_{word['en']}"
                )
                
                if audio_path:
                    generated_files.append({
                        'english': word['en'],
                        'hokkien_display': display_text,
                        'hokkien_tts': tts_text,
                        'audio_file': audio_path,
                        'version': 'Tâi-lô'
                    })
        
        # Generate additional phrases
        if additional_phrases_tailo:
            print("\n📚 Additional Phrases")
            for phrase in additional_phrases_tailo:
                tts_text = self.extract_hokkien_text(phrase)
                display_text = self.get_display_text(phrase)
                
                audio_path = self.generate_audio(
                    text=tts_text,
                    description=f"tailo_bonus_{phrase['en']}"
                )
                
                if audio_path:
                    generated_files.append({
                        'english': phrase['en'],
                        'hokkien_display': display_text,
                        'hokkien_tts': tts_text,
                        'audio_file': audio_path,
                        'version': 'Tâi-lô'
                    })
        
        return generated_files

def main():
    """Main function for Tâi-lô generator"""
    print("\n🎵 Hokkien Audio Generator - Tâi-lô Version")
    print("   Optimized for Meta MMS TTS model")
    print("=" * 50)
    
    # Create generator
    generator = HokkienTailoGenerator()
    
    # Test with single phrase
    print("\n🔧 Running test...")
    test_file = generator.generate_audio("tsia̍h-pá--bē", "tailo_test_have_you_eaten")
    
    if test_file:
        print(f"\n✅ Test successful! File saved to: {test_file}")
        
        # Generate all phrases
        print("\n" + "=" * 50)
        response = input("Generate all Tâi-lô phrases? (y/n): ").strip().lower()
        
        if response == 'y':
            print("\n🎯 Generating all Tâi-lô phrases...")
            files = generator.generate_all_phrases()
            
            print("\n" + "=" * 50)
            print("📊 Tâi-lô Summary")
            print("=" * 50)
            print(f"✅ Generated {len(files)} audio files")
            print(f"📁 Location: {generator.output_dir.absolute()}")
            
            print("\n📋 Files created:")
            for f in files:
                print(f"   • {f['english']}: {os.path.basename(f['audio_file'])}")
                print(f"     TTS: {f['hokkien_tts']}")
    else:
        print("❌ Test failed. Please check the error messages above.")

if __name__ == "__main__":
    main()