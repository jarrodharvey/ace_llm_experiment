#!/usr/bin/env python3
"""
ChatGPT Consultant Script
Simplifies ChatGPT API calls for case creation by handling all JSON/curl complexity.
"""

import json
import requests
import argparse
import sys
import os
from pathlib import Path

class ChatGPTConsultant:
    def __init__(self, api_key_file="openai_key.txt"):
        """Initialize with API key from file"""
        try:
            with open(api_key_file, 'r') as f:
                self.api_key = f.read().strip()
        except FileNotFoundError:
            print(f"Error: API key file '{api_key_file}' not found")
            sys.exit(1)
        
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def consult(self, prompt, model="gpt-4", temperature=0.7, max_tokens=2000):
        """Send prompt to ChatGPT and return response"""
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            print("Consulting ChatGPT...")
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            if 'choices' in data and len(data['choices']) > 0:
                content = data['choices'][0]['message']['content']
                return {
                    "success": True,
                    "content": content,
                    "usage": data.get('usage', {}),
                    "model": data.get('model', model)
                }
            else:
                return {
                    "success": False,
                    "error": "No response content received",
                    "raw_response": data
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"API request failed: {str(e)}"
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"JSON decode error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def save_response(self, response, output_file, content_only=False):
        """Save response to file - JSON format or content only"""
        try:
            # Ensure output directory exists
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w') as f:
                if content_only and response['success']:
                    # Save only the content field as plain text
                    f.write(response['content'])
                else:
                    # Save full JSON response (default behavior)
                    json.dump(response, f, indent=2)
            
            if response['success']:
                mode = "content" if content_only else "JSON"
                print(f"✅ ChatGPT consultation saved as {mode} to: {output_file}")
                print(f"📊 Tokens used: {response.get('usage', {}).get('total_tokens', 'unknown')}")
            else:
                print(f"❌ Error response saved to: {output_file}")
                print(f"🚨 Error: {response['error']}")
                
        except Exception as e:
            print(f"❌ Failed to save response: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Consult ChatGPT for case creation')
    parser.add_argument('prompt', help='Prompt to send to ChatGPT')
    parser.add_argument('-o', '--output', required=True, help='Output file path')
    parser.add_argument('--content-only', action='store_true', help='Save only content field as plain text (not full JSON response)')
    parser.add_argument('--case-dir', help='Case directory to prepend to relative output paths')
    parser.add_argument('-m', '--model', default='gpt-4', help='OpenAI model to use (default: gpt-4)')
    parser.add_argument('-t', '--temperature', type=float, default=0.7, help='Temperature setting (default: 0.7)')
    parser.add_argument('--max-tokens', type=int, default=2000, help='Maximum tokens (default: 2000)')
    parser.add_argument('--api-key-file', default='openai_key.txt', help='API key file path (default: openai_key.txt)')
    
    args = parser.parse_args()
    
    # Process output path with case directory if provided
    output_path = args.output
    if args.case_dir and not Path(output_path).is_absolute():
        # Prepend case directory to relative paths
        output_path = str(Path(args.case_dir) / output_path)
        print(f"📁 Using case directory: {args.case_dir}")
        print(f"📄 Output will be saved to: {output_path}")
    
    # Initialize consultant
    consultant = ChatGPTConsultant(args.api_key_file)
    
    # Get response from ChatGPT
    response = consultant.consult(
        prompt=args.prompt,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens
    )
    
    # Save response
    consultant.save_response(response, output_path, content_only=args.content_only)
    
    # Exit with appropriate code
    sys.exit(0 if response['success'] else 1)

if __name__ == "__main__":
    main()