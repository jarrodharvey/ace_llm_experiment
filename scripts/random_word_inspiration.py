#!/usr/bin/env python3
"""
Random Word Inspiration Generator
Uses random words as A-to-C creative forcing functions for game master improvisation.
"""

import json
from random_word import RandomWords

class RandomWordInspiration:
    def __init__(self):
        self.r = RandomWords()
        
        # Categories for different improvisation needs
        self.categories = [
            "character_motivations",
            "relationship_dynamics", 
            "conflict_situations",
            "evidence_obstacles",
            "witness_behaviors",
            "plot_twists"
        ]
    
    def generate_inspiration_set(self, words_per_category=10):
        """Generate random words for each category"""
        inspiration_pool = {}
        
        for category in self.categories:
            words = []
            attempts = 0
            
            # Generate unique words for this category
            while len(words) < words_per_category and attempts < 50:
                word = self.r.get_random_word()
                if word and word not in words:
                    words.append(word)
                attempts += 1
            
            inspiration_pool[category] = words
        
        return inspiration_pool
    
    def get_random_inspiration(self, category=None):
        """Get a single random word for immediate inspiration"""
        if category:
            return self.r.get_random_word()
        else:
            return {
                "word": self.r.get_random_word(),
                "category": "general"
            }
    
    def save_inspiration_pool(self, pool, target_dir=".", filename="inspiration_pool.json"):
        """Save inspiration pool to file"""
        import os
        
        # Ensure target directory exists
        os.makedirs(target_dir, exist_ok=True)
        
        # Create full path
        filepath = os.path.join(target_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(pool, f, indent=2)
        
        total_words = sum(len(words) for words in pool.values())
        print(f"Random word inspiration pool saved to {filepath}")
        print(f"Categories: {list(pool.keys())}")
        print(f"Total words: {total_words}")
        
        # Show a sample
        print("\nSample words:")
        for category, words in pool.items():
            print(f"{category}: {words[:3]}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate random word inspiration pool for case creation')
    parser.add_argument('--target-dir', '-t', 
                       help='Target directory for inspiration pool (default: current directory)',
                       default='.')
    parser.add_argument('--filename', '-f',
                       help='Filename for inspiration pool (default: inspiration_pool.json)',
                       default='inspiration_pool.json')
    parser.add_argument('--test', action='store_true',
                       help='Run individual inspiration test after generation')
    
    args = parser.parse_args()
    
    generator = RandomWordInspiration()
    
    # Generate inspiration pool
    pool = generator.generate_inspiration_set()
    generator.save_inspiration_pool(pool, args.target_dir, args.filename)
    
    # Test individual inspiration if requested
    if args.test:
        print("\n--- Individual Inspiration Test ---")
        for i in range(5):
            word = generator.get_random_inspiration()
            print(f"Random inspiration: {word}")

if __name__ == "__main__":
    main()