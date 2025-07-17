#!/usr/bin/env python3
"""
Random Word Inspiration Generator
Uses random words as A-to-C creative forcing functions for game master improvisation.
"""

import json
import random
from case_config import get_config_manager

class RandomWordInspiration:
    def __init__(self):
        self.config_manager = get_config_manager()
        
        # Categories from shared configuration
        self.categories = self.config_manager.get_inspiration_categories()
        
        # Fallback word list if external library not available
        self.fallback_words = [
            "ancient", "bridge", "cascade", "distant", "ethereal", "fragile", "glowing", "hidden",
            "infinite", "jagged", "kindred", "luminous", "mysterious", "nested", "obscure", "pristine",
            "quaint", "radiant", "silent", "twisted", "uniform", "vivid", "weathered", "xenial",
            "yearning", "zealous", "abandoned", "bitter", "curious", "delicate", "elaborate", "forgotten",
            "graceful", "hollow", "intricate", "joyful", "knotted", "lonely", "melancholy", "nostalgic",
            "ornate", "peculiar", "quiet", "restless", "serene", "tangled", "uncertain", "vibrant",
            "wistful", "xenophobic", "youthful", "zestful", "crystalline", "ephemeral", "labyrinthine",
            "temporal", "resonant", "liminal", "volatile", "immutable", "paradoxical", "symbiotic"
        ]
    
    def generate_inspiration_set(self, words_per_category=None):
        """Generate random words for each category"""
        if words_per_category is None:
            words_per_category = self.config_manager.get_words_per_category()
        
        inspiration_pool = {}
        
        for category in self.categories:
            words = []
            attempts = 0
            
            # Generate unique words for this category using fallback
            while len(words) < words_per_category and attempts < 100:
                word = random.choice(self.fallback_words)
                if word and word not in words:
                    words.append(word)
                attempts += 1
            
            inspiration_pool[category] = words
        
        return inspiration_pool
    
    def get_random_inspiration(self, category=None):
        """Get a single random word for immediate inspiration"""
        if category:
            return random.choice(self.fallback_words)
        else:
            return {
                "word": random.choice(self.fallback_words),
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
        
        # Show configuration info
        settings = self.config_manager.get_inspiration_settings()
        print(f"\nConfiguration:")
        print(f"Words per category: {settings.get('words_per_category', 'default')}")
        print(f"Categories from config: {len(self.categories)}")

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
    parser.add_argument('--words-per-category', type=int,
                       help='Override words per category from config')
    parser.add_argument('--show-config', action='store_true',
                       help='Show configuration information')
    
    args = parser.parse_args()
    
    generator = RandomWordInspiration()
    
    # Show configuration if requested
    if args.show_config:
        print("=== Configuration Info ===")
        print(f"Categories: {generator.categories}")
        print(f"Words per category: {generator.config_manager.get_words_per_category()}")
        print(f"Inspiration settings: {generator.config_manager.get_inspiration_settings()}")
        print()
    
    # Generate inspiration pool
    pool = generator.generate_inspiration_set(args.words_per_category)
    generator.save_inspiration_pool(pool, args.target_dir, args.filename)
    
    # Test individual inspiration if requested
    if args.test:
        print("\n--- Individual Inspiration Test ---")
        for i in range(5):
            word = generator.get_random_inspiration()
            print(f"Random inspiration: {word}")

if __name__ == "__main__":
    main()