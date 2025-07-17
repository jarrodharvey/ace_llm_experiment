#!/usr/bin/env python3
"""
Documentation Consistency Checker

Validates that all references in CLAUDE.md point to existing files and 
checks for potential documentation drift issues.
"""

import os
import re
import sys
from pathlib import Path

class DocumentationChecker:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.errors = []
        self.warnings = []
        
    def check_file_references(self, claude_md_path):
        """Check that all file references in CLAUDE.md exist"""
        print("Checking file references in CLAUDE.md...")
        
        with open(claude_md_path, 'r') as f:
            content = f.read()
            
        # Find all markdown links to docs/
        doc_links = re.findall(r'\[([^\]]+)\]\((docs/[^)]+)\)', content)
        
        for link_text, file_path in doc_links:
            full_path = self.base_dir / file_path
            if not full_path.exists():
                self.errors.append(f"Missing referenced file: {file_path}")
            else:
                print(f"✓ Found: {file_path}")
                
        return len(self.errors) == 0
        
    def check_content_consistency(self):
        """Check for potential content drift between main doc and extracted files"""
        print("\\nChecking for potential content drift...")
        
        # Check if extracted files have been modified more recently than expected
        docs_dir = self.base_dir / "docs"
        if not docs_dir.exists():
            self.errors.append("docs/ directory not found")
            return False
            
        # Check for last updated timestamps
        for doc_file in docs_dir.rglob("*.md"):
            with open(doc_file, 'r') as f:
                content = f.read()
                
            # Check if file has "Last updated" timestamp
            if "Last updated:" not in content:
                self.warnings.append(f"Missing 'Last updated' timestamp in {doc_file.relative_to(self.base_dir)}")
                
        return True
        
    def check_critical_sections(self, claude_md_path):
        """Verify that critical operational sections are still in CLAUDE.md"""
        print("\\nChecking critical sections remain in CLAUDE.md...")
        
        with open(claude_md_path, 'r') as f:
            content = f.read()
            
        # Critical sections that must remain in main doc
        critical_sections = [
            "MASTER RULES",
            "FORCING FUNCTION REQUIREMENTS", 
            "MANDATORY STATE MANAGEMENT",
            "GAME STATE MANAGEMENT",
            "COMMANDS - GLOBAL",
            "Core Architecture"
        ]
        
        for section in critical_sections:
            if section not in content:
                self.errors.append(f"Critical section missing from CLAUDE.md: {section}")
            else:
                print(f"✓ Found critical section: {section}")
                
        return len(self.errors) == 0
        
    def generate_reference_update_reminder(self):
        """Generate reminder about which docs need updates when rules change"""
        print("\\nGenerating update reminder...")
        
        update_map = {
            "MASTER RULES": ["All extracted documentation"],
            "State Management Commands": ["docs/examples/game-state-management.md"],
            "Recovery Commands": ["docs/examples/recovery-workflow.md"],
            "ChatGPT Consultation": ["docs/examples/chatgpt-consultation.md"],
            "Admin Mode Guidelines": ["docs/reference/admin-mode-guidelines.md"],
            "Success/Failure Indicators": ["docs/troubleshooting/success-failure-indicators.md"]
        }
        
        print("\\n" + "="*50)
        print("DOCUMENTATION UPDATE REMINDER")
        print("="*50)
        print("When changing the following sections in CLAUDE.md:")
        print("")
        
        for section, files in update_map.items():
            print(f"• {section}:")
            for file in files:
                print(f"  - Check: {file}")
            print("")
            
        return True
        
    def run_full_check(self):
        """Run all consistency checks"""
        print("Running documentation consistency check...")
        print("="*50)
        
        claude_md = self.base_dir / "CLAUDE.md"
        
        if not claude_md.exists():
            self.errors.append("CLAUDE.md not found")
            return False
            
        # Run all checks
        self.check_file_references(claude_md)
        self.check_content_consistency()
        self.check_critical_sections(claude_md)
        self.generate_reference_update_reminder()
        
        # Report results
        print("\\n" + "="*50)
        print("CONSISTENCY CHECK RESULTS")
        print("="*50)
        
        if self.errors:
            print("❌ ERRORS FOUND:")
            for error in self.errors:
                print(f"  • {error}")
                
        if self.warnings:
            print("\\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  • {warning}")
                
        if not self.errors and not self.warnings:
            print("✅ All checks passed!")
            
        if not self.errors:
            print("\\n✅ Documentation structure is consistent")
            return True
        else:
            print("\\n❌ Documentation consistency issues found")
            return False

def main():
    """Main function"""
    if len(sys.argv) > 1:
        base_dir = sys.argv[1]
    else:
        base_dir = os.getcwd()
        
    checker = DocumentationChecker(base_dir)
    success = checker.run_full_check()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()