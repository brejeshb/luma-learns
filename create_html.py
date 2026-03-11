# create_index_html.py
import os
import json
from pathlib import Path

def scan_audio_files():
    """Scan both output folders and collect audio files"""
    output_dirs = {
        'Original (Mixed)': 'output',
        'Tâi-lô': 'output2'
    }
    
    all_files = []
    
    for version_name, folder in output_dirs.items():
        folder_path = Path(folder)
        if folder_path.exists():
            for wav_file in folder_path.glob("*.wav"):
                # Try to extract English phrase from filename
                filename = wav_file.stem
                
                # Clean up filename for display
                display_name = filename.replace('tailo_', '').replace('bonus_', '').replace('_', ' ').title()
                
                all_files.append({
                    'version': version_name,
                    'filename': wav_file.name,
                    'path': f"{folder}/{wav_file.name}",
                    'display_name': display_name,
                    'sort_key': display_name
                })
    
    # Sort by display name
    all_files.sort(key=lambda x: x['sort_key'])
    return all_files

def generate_html(audio_files):
    """Generate HTML page with audio players"""
    
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hokkien Audio Samples</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            color: white;
            padding: 40px 20px;
        }
        
        h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .subtitle {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .version-tabs {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-bottom: 30px;
        }
        
        .tab-button {
            padding: 12px 30px;
            font-size: 1.1em;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            transition: all 0.3s;
        }
        
        .tab-button:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        
        .tab-button.active {
            background: white;
            color: #667eea;
            font-weight: bold;
        }
        
        .audio-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            padding: 20px;
        }
        
        .audio-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s;
        }
        
        .audio-card:hover {
            transform: translateY(-5px);
        }
        
        .version-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .badge-original {
            background: #ffd700;
            color: #333;
        }
        
        .badge-tailo {
            background: #4caf50;
            color: white;
        }
        
        .phrase-english {
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        
        .filename {
            font-size: 0.8em;
            color: #666;
            margin-bottom: 10px;
            word-break: break-all;
        }
        
        audio {
            width: 100%;
            margin-top: 10px;
        }
        
        .stats {
            text-align: center;
            color: white;
            margin: 20px 0;
            font-size: 1.1em;
        }
        
        .footer {
            text-align: center;
            color: rgba(255,255,255,0.8);
            margin-top: 40px;
            padding: 20px;
        }
        
        .footer a {
            color: white;
            text-decoration: none;
            border-bottom: 1px dotted white;
        }
        
        .footer a:hover {
            border-bottom: 1px solid white;
        }
        
        @media (max-width: 768px) {
            h1 { font-size: 2em; }
            .audio-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎤 Hokkien Audio Samples</h1>
            <div class="subtitle">Compare Original vs Tâi-lô Romanization</div>
        </header>
        
        <div class="version-tabs">
            <button class="tab-button active" onclick="filterVersion('all')">All</button>
            <button class="tab-button" onclick="filterVersion('Original')">Original</button>
            <button class="tab-button" onclick="filterVersion('Tâi-lô')">Tâi-lô</button>
        </div>
        
        <div class="stats" id="stats"></div>
        
        <div class="audio-grid" id="audioGrid">
"""
    
    # Add audio cards
    for file in audio_files:
        badge_class = "badge-original" if "Original" in file['version'] else "badge-tailo"
        
        html += f"""
            <div class="audio-card" data-version="{file['version']}">
                <span class="version-badge {badge_class}">{file['version']}</span>
                <div class="phrase-english">{file['display_name']}</div>
                <div class="filename">{file['filename']}</div>
                <audio controls>
                    <source src="{file['path']}" type="audio/wav">
                    Your browser does not support audio
                </audio>
            </div>
"""
    
    # Close HTML
    html += """
        </div>
        
        <div class="footer">
            <p>Generated with Meta's MMS-TTS-NAN model</p>
            <p><a href="#" onclick="playAll()">🔊 Play all samples</a> (may autoplay be blocked)</p>
            <p><a href="#" onclick="downloadAll()">📥 Download all as ZIP</a></p>
        </div>
    </div>
    
    <script>
        function filterVersion(version) {
            const cards = document.querySelectorAll('.audio-card');
            const buttons = document.querySelectorAll('.tab-button');
            let count = 0;
            
            // Update button states
            buttons.forEach(btn => {
                if (btn.textContent.includes(version) || (version === 'all' && btn.textContent === 'All')) {
                    btn.classList.add('active');
                } else {
                    btn.classList.remove('active');
                }
            });
            
            // Filter cards
            cards.forEach(card => {
                if (version === 'all' || card.dataset.version === version) {
                    card.style.display = 'block';
                    count++;
                } else {
                    card.style.display = 'none';
                }
            });
            
            // Update stats
            document.getElementById('stats').textContent = `Showing ${count} audio samples`;
        }
        
        function playAll() {
            const audioElements = document.querySelectorAll('audio');
            audioElements.forEach(audio => {
                audio.play().catch(e => console.log('Autoplay prevented:', e));
            });
        }
        
        function downloadAll() {
            alert('To download all files, please zip the output and output2 folders manually, or use your browser\'s download manager.');
        }
        
        // Show initial count
        filterVersion('all');
    </script>
</body>
</html>
"""
    
    return html

def main():
    """Main function to generate HTML"""
    print("🌐 Generating Hokkien Audio Player HTML...")
    
    # Scan for audio files
    audio_files = scan_audio_files()
    
    if not audio_files:
        print("⚠️  No audio files found in output/ or output2/ folders")
        print("   Please run generate_audio.py and generate_audio_tailo.py first")
        return
    
    # Generate HTML
    html_content = generate_html(audio_files)
    
    # Save HTML file
    output_path = Path("index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"✅ Generated index.html with {len(audio_files)} audio files")
    print(f"   Original: {sum(1 for f in audio_files if 'Original' in f['version'])} files")
    print(f"   Tâi-lô: {sum(1 for f in audio_files if 'Tâi-lô' in f['version'])} files")
    print("\n📱 Open index.html in your browser to play the audio!")
    print("   Or upload to GitHub and enable GitHub Pages")

if __name__ == "__main__":
    main()