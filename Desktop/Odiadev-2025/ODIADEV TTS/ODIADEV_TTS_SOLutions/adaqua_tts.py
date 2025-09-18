"""
Adaqua NaijaTTS Python SDK
A simple client library for the NaijaTTS API.
"""

import requests
import base64
import tempfile
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import soundfile as sf
import numpy as np


class NaijaTTSClient:
    """Client for the NaijaTTS API."""
    
    def __init__(self, api_url: str = "http://localhost:7860", timeout: int = 30):
        """
        Initialize the NaijaTTS client.
        
        Args:
            api_url: Base URL of the NaijaTTS API
            timeout: Request timeout in seconds
        """
        self.api_url = api_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
    
    def health(self) -> Dict[str, Any]:
        """
        Check API health status.
        
        Returns:
            Health status information
        """
        try:
            response = self.session.get(f"{self.api_url}/health", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status": "unhealthy"}
    
    def speak(self, 
              text: str, 
              language: str = "en", 
              speaker_wav: Optional[str] = None,
              seed: Optional[int] = None,
              save: bool = False,
              output_path: Optional[str] = None) -> Union[bytes, str]:
        """
        Synthesize speech from text.
        
        Args:
            text: Text to synthesize
            language: Language code (default: "en")
            speaker_wav: Path to reference speaker audio (optional)
            seed: Random seed for reproducibility (optional)
            save: Whether to save audio to file
            output_path: Output file path (if save=True and not provided, uses temp file)
            
        Returns:
            Audio data as bytes, or file path if save=True
        """
        payload = {
            "text": text,
            "language": language,
            "speaker_wav": speaker_wav,
            "seed": seed,
            "save": save
        }
        
        try:
            response = self.session.post(
                f"{self.api_url}/speak",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            if save:
                if output_path is None:
                    # Create temporary file
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                        output_path = tmp.name
                
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                return output_path
            else:
                return response.content
                
        except requests.exceptions.RequestException as e:
            raise NaijaTTSError(f"Speech synthesis failed: {str(e)}")
    
    def speak_to_file(self, 
                     text: str, 
                     output_path: str,
                     language: str = "en", 
                     speaker_wav: Optional[str] = None,
                     seed: Optional[int] = None) -> str:
        """
        Synthesize speech and save directly to file.
        
        Args:
            text: Text to synthesize
            output_path: Output file path
            language: Language code (default: "en")
            speaker_wav: Path to reference speaker audio (optional)
            seed: Random seed for reproducibility (optional)
            
        Returns:
            Path to the saved audio file
        """
        return self.speak(
            text=text,
            language=language,
            speaker_wav=speaker_wav,
            seed=seed,
            save=True,
            output_path=output_path
        )
    
    def batch_speak(self, 
                   items: List[Dict[str, Any]], 
                   return_format: str = "zip",
                   save: bool = False) -> Union[bytes, Dict[str, Any]]:
        """
        Synthesize multiple texts in batch.
        
        Args:
            items: List of synthesis items, each with 'id', 'text', and optional 'language', 'speaker_wav', 'seed'
            return_format: Return format - "zip" or "json"
            save: Whether to save individual audio files
            
        Returns:
            ZIP file as bytes (if return_format="zip") or JSON response (if return_format="json")
        """
        payload = {
            "items": items,
            "return_format": return_format,
            "save": save
        }
        
        try:
            response = self.session.post(
                f"{self.api_url}/batch_speak",
                json=payload,
                timeout=self.timeout * 2  # Longer timeout for batch requests
            )
            response.raise_for_status()
            
            if return_format == "zip":
                return response.content
            else:
                return response.json()
                
        except requests.exceptions.RequestException as e:
            raise NaijaTTSError(f"Batch synthesis failed: {str(e)}")
    
    def batch_speak_to_files(self, 
                            items: List[Dict[str, Any]], 
                            output_dir: str = "outputs") -> List[str]:
        """
        Synthesize multiple texts and save to individual files.
        
        Args:
            items: List of synthesis items
            output_dir: Output directory for audio files
            
        Returns:
            List of output file paths
        """
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Use JSON format to get individual audio data
        result = self.batch_speak(items, return_format="json")
        
        if "error" in result:
            raise NaijaTTSError(f"Batch synthesis failed: {result['error']}")
        
        output_files = []
        for item_result in result.get("results", []):
            if item_result.get("status") == "success":
                # Decode base64 audio data
                audio_b64 = item_result.get("audio_base64", "")
                if audio_b64:
                    audio_data = base64.b64decode(audio_b64)
                    
                    # Save to file
                    file_path = output_path / f"{item_result['id']}.wav"
                    with open(file_path, 'wb') as f:
                        f.write(audio_data)
                    
                    output_files.append(str(file_path))
        
        return output_files
    
    def get_audio_info(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Get information about audio data.
        
        Args:
            audio_data: Audio data as bytes
            
        Returns:
            Audio information dictionary
        """
        try:
            # Write to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(audio_data)
                tmp_path = tmp.name
            
            # Read audio file
            audio, sample_rate = sf.read(tmp_path)
            
            # Clean up temp file
            os.unlink(tmp_path)
            
            return {
                "sample_rate": sample_rate,
                "duration": len(audio) / sample_rate,
                "channels": 1 if len(audio.shape) == 1 else audio.shape[1],
                "samples": len(audio),
                "peak_amplitude": float(np.max(np.abs(audio))),
                "rms_amplitude": float(np.sqrt(np.mean(audio**2)))
            }
        except Exception as e:
            return {"error": str(e)}


class NaijaTTSError(Exception):
    """Custom exception for NaijaTTS errors."""
    pass


# Convenience functions for quick usage
def quick_speak(text: str, 
                api_url: str = "http://localhost:7860",
                output_file: Optional[str] = None) -> Union[bytes, str]:
    """
    Quick speech synthesis function.
    
    Args:
        text: Text to synthesize
        api_url: API URL
        output_file: Optional output file path
        
    Returns:
        Audio data or file path
    """
    client = NaijaTTSClient(api_url)
    
    if output_file:
        return client.speak_to_file(text, output_file)
    else:
        return client.speak(text)


def quick_batch_speak(texts: List[str], 
                     api_url: str = "http://localhost:7860",
                     output_dir: str = "outputs") -> List[str]:
    """
    Quick batch speech synthesis function.
    
    Args:
        texts: List of texts to synthesize
        api_url: API URL
        output_dir: Output directory
        
    Returns:
        List of output file paths
    """
    client = NaijaTTSClient(api_url)
    
    items = [
        {"id": f"text_{i}", "text": text}
        for i, text in enumerate(texts)
    ]
    
    return client.batch_speak_to_files(items, output_dir)


# Example usage
if __name__ == "__main__":
    # Example 1: Basic usage
    print("Example 1: Basic speech synthesis")
    client = NaijaTTSClient()
    
    # Check health
    health = client.health()
    print(f"API Health: {health}")
    
    if "error" not in health:
        # Synthesize speech
        audio_data = client.speak("How you dey? Today go sweet well-well!")
        print(f"Generated audio: {len(audio_data)} bytes")
        
        # Get audio info
        info = client.get_audio_info(audio_data)
        print(f"Audio info: {info}")
        
        # Save to file
        output_file = client.speak_to_file(
            "Wetin dey happen? Na so e be, sha o!",
            "example_output.wav"
        )
        print(f"Saved to: {output_file}")
    
    # Example 2: Batch synthesis
    print("\nExample 2: Batch synthesis")
    texts = [
        "How you dey?",
        "Today go sweet well-well!",
        "Wetin dey happen?",
        "Na so e be, sha o!"
    ]
    
    try:
        output_files = quick_batch_speak(texts, output_dir="batch_outputs")
        print(f"Generated {len(output_files)} audio files:")
        for file_path in output_files:
            print(f"  - {file_path}")
    except Exception as e:
        print(f"Batch synthesis failed: {e}")

