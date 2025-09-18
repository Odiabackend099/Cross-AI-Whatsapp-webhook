#!/usr/bin/env python3
"""
Benchmarking script for NaijaTTS performance and quality testing.
Measures latency, throughput, and audio quality metrics.
"""

import argparse
import csv
import json
import time
import statistics
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
import soundfile as sf
import requests
from datetime import datetime

# Test sentences for benchmarking
SAMPLE_SENTENCES = [
    "How you dey?",
    "Wetin dey happen?",
    "Abi you dey hear me?",
    "Today go sweet well-well.",
    "Na so e be, sha o.",
    "Thank you abeg, I appreciate am.",
]


def _post_tts(base, text, timeout=30):
    return requests.post(f"{base}/speak", json={"text": text}, timeout=timeout)


class NaijaTTSBenchmark:
    """Benchmarking class for NaijaTTS performance testing."""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.results = []
        
    def test_health(self) -> Dict[str, Any]:
        """Test API health endpoint."""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def test_single_synthesis(self, text: str, language: str = "en") -> Dict[str, Any]:
        """Test single text synthesis."""
        start_time = time.time()
        
        try:
            payload = {
                "text": text,
                "language": language
            }
            
            response = requests.post(
                f"{self.api_url}/speak",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            # Save audio to temporary file for analysis
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_file.write(response.content)
                tmp_path = tmp_file.name
            
            # Analyze audio
            audio, sample_rate = sf.read(tmp_path)
            duration = len(audio) / sample_rate
            peak_amplitude = np.max(np.abs(audio))
            rms_amplitude = np.sqrt(np.mean(audio**2))
            
            # Clean up temp file
            os.unlink(tmp_path)
            
            synthesis_time = time.time() - start_time
            
            return {
                "success": True,
                "synthesis_time": synthesis_time,
                "duration": duration,
                "sample_rate": sample_rate,
                "peak_amplitude": peak_amplitude,
                "rms_amplitude": rms_amplitude,
                "text_length": len(text),
                "chars_per_second": len(text) / synthesis_time if synthesis_time > 0 else 0,
                "request_id": response.headers.get("X-Request-ID", "unknown"),
                "device": response.headers.get("X-Device", "unknown"),
                "synthesis_time_header": response.headers.get("X-Synthesis-Time", "unknown")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "synthesis_time": time.time() - start_time
            }
    
    def test_batch_synthesis(self, texts: List[str], language: str = "en") -> Dict[str, Any]:
        """Test batch synthesis."""
        start_time = time.time()
        
        try:
            items = [
                {"id": f"item_{i}", "text": text, "language": language}
                for i, text in enumerate(texts)
            ]
            
            payload = {
                "items": items,
                "return_format": "json"
            }
            
            response = requests.post(
                f"{self.api_url}/batch_speak",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            batch_time = time.time() - start_time
            
            return {
                "success": True,
                "batch_time": batch_time,
                "total_items": result.get("total_items", 0),
                "successful": result.get("successful", 0),
                "failed": result.get("total_items", 0) - result.get("successful", 0),
                "items_per_second": result.get("total_items", 0) / batch_time if batch_time > 0 else 0,
                "request_id": result.get("request_id", "unknown")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "batch_time": time.time() - start_time
            }
    
    def run_latency_benchmark(self, num_tests: int = 50) -> Dict[str, Any]:
        """Run latency benchmark with random sentences."""
        print(f"Running latency benchmark with {num_tests} tests...")
        
        # Select random sentences
        import random
        test_sentences = random.sample(SAMPLE_SENTENCES, min(num_tests, len(SAMPLE_SENTENCES)))
        
        results = []
        for i, sentence in enumerate(test_sentences):
            print(f"Test {i+1}/{len(test_sentences)}: {sentence[:50]}...")
            result = self.test_single_synthesis(sentence)
            results.append(result)
            
            if not result["success"]:
                print(f"  Failed: {result.get('error', 'Unknown error')}")
            else:
                print(f"  Success: {result['synthesis_time']:.3f}s, {result['chars_per_second']:.1f} chars/s")
        
        # Calculate statistics
        successful_results = [r for r in results if r["success"]]
        
        if not successful_results:
            return {"error": "No successful tests"}
        
        synthesis_times = [r["synthesis_time"] for r in successful_results]
        chars_per_second = [r["chars_per_second"] for r in successful_results]
        
        return {
            "total_tests": len(results),
            "successful_tests": len(successful_results),
            "failed_tests": len(results) - len(successful_results),
            "synthesis_time": {
                "mean": statistics.mean(synthesis_times),
                "median": statistics.median(synthesis_times),
                "p95": np.percentile(synthesis_times, 95),
                "p99": np.percentile(synthesis_times, 99),
                "min": min(synthesis_times),
                "max": max(synthesis_times),
                "std": statistics.stdev(synthesis_times) if len(synthesis_times) > 1 else 0
            },
            "chars_per_second": {
                "mean": statistics.mean(chars_per_second),
                "median": statistics.median(chars_per_second),
                "min": min(chars_per_second),
                "max": max(chars_per_second)
            },
            "results": results
        }
    
    def run_quality_benchmark(self) -> Dict[str, Any]:
        """Run audio quality benchmark."""
        print("Running quality benchmark...")
        
        # Test with different sentence lengths
        test_cases = [
            ("Short", "How you dey?"),
            ("Medium", "How you dey? Today go sweet well-well, make we enjoy am."),
            ("Long", "How you dey? Today go sweet well-well, make we enjoy am together, sha o, and we go have fun."),
            ("Code-switch", "Hello, how are you doing today? I hope you dey fine, sha o."),
            ("Pidgin", "Na wa o, this thing dey confuse me well-well, abi na so?")
        ]
        
        results = []
        for category, text in test_cases:
            print(f"Testing {category}: {text}")
            result = self.test_single_synthesis(text)
            if result["success"]:
                result["category"] = category
                result["text"] = text
                results.append(result)
                print(f"  Peak: {result['peak_amplitude']:.3f}, RMS: {result['rms_amplitude']:.3f}")
            else:
                print(f"  Failed: {result.get('error', 'Unknown error')}")
        
        return {
            "test_cases": len(test_cases),
            "successful": len(results),
            "results": results
        }
    
    def save_results(self, results: Dict[str, Any], output_dir: str = "bench"):
        """Save benchmark results to CSV and JSON files."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results as JSON
        json_file = output_path / f"bench_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Save latency results as CSV
        if "latency" in results and "results" in results["latency"]:
            csv_file = output_path / f"bench_latency_{timestamp}.csv"
            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "test_id", "text", "success", "synthesis_time", "duration", 
                    "peak_amplitude", "rms_amplitude", "chars_per_second", 
                    "request_id", "device"
                ])
                
                for i, result in enumerate(results["latency"]["results"]):
                    writer.writerow([
                        i, result.get("text", ""), result.get("success", False),
                        result.get("synthesis_time", 0), result.get("duration", 0),
                        result.get("peak_amplitude", 0), result.get("rms_amplitude", 0),
                        result.get("chars_per_second", 0), result.get("request_id", ""),
                        result.get("device", "")
                    ])
        
        print(f"Results saved to {output_path}")
        return json_file, csv_file if "latency" in results else None


def main():
    parser = argparse.ArgumentParser(description="NaijaTTS Benchmarking Tool")
    parser.add_argument("--api-url", default="http://localhost:7860", help="API base URL")
    parser.add_argument("--num-tests", type=int, default=50, help="Number of latency tests")
    parser.add_argument("--output-dir", default="bench", help="Output directory for results")
    parser.add_argument("--health-only", action="store_true", help="Only test health endpoint")
    parser.add_argument("--quality-only", action="store_true", help="Only run quality benchmark")
    parser.add_argument("--latency-only", action="store_true", help="Only run latency benchmark")
    
    args = parser.parse_args()
    
    # Import required modules
    import os
    import tempfile
    
    benchmark = NaijaTTSBenchmark(args.api_url)
    
    print("NaijaTTS Benchmarking Tool")
    print("=" * 50)
    
    # Test health
    print("Testing health endpoint...")
    health = benchmark.test_health()
    if "error" in health:
        print(f"Health check failed: {health['error']}")
        return
    else:
        print(f"Health check passed: {health}")
    
    if args.health_only:
        return
    
    results = {"health": health}
    
    # Run latency benchmark
    if not args.quality_only:
        print("\nRunning latency benchmark...")
        latency_results = benchmark.run_latency_benchmark(args.num_tests)
        results["latency"] = latency_results
        
        if "error" not in latency_results:
            print(f"\nLatency Results:")
            print(f"  Total tests: {latency_results['total_tests']}")
            print(f"  Successful: {latency_results['successful_tests']}")
            print(f"  Failed: {latency_results['failed_tests']}")
            print(f"  Mean synthesis time: {latency_results['synthesis_time']['mean']:.3f}s")
            print(f"  Median synthesis time: {latency_results['synthesis_time']['median']:.3f}s")
            print(f"  P95 synthesis time: {latency_results['synthesis_time']['p95']:.3f}s")
            print(f"  Mean chars/sec: {latency_results['chars_per_second']['mean']:.1f}")
    
    # Run quality benchmark
    if not args.latency_only:
        print("\nRunning quality benchmark...")
        quality_results = benchmark.run_quality_benchmark()
        results["quality"] = quality_results
        
        print(f"\nQuality Results:")
        print(f"  Test cases: {quality_results['test_cases']}")
        print(f"  Successful: {quality_results['successful']}")
    
    # Save results
    print("\nSaving results...")
    json_file, csv_file = benchmark.save_results(results, args.output_dir)
    print(f"Results saved to {json_file}")
    if csv_file:
        print(f"Latency CSV saved to {csv_file}")


if __name__ == "__main__":
    main()
