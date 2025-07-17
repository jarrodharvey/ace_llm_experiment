"""
Evidence Management Plugin

Handles evidence collection, validation, and organization.
Prevents duplicate evidence and maintains logical consistency.
"""

import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime


class EvidencePlugin:
    """Manages evidence collection and organization"""
    
    def __init__(self):
        self.evidence: Dict[str, Dict[str, Any]] = {}
    
    def load_state(self, evidence_data: Dict[str, Any]) -> None:
        """Load evidence state from game state"""
        self.evidence = evidence_data.copy()
    
    def add_evidence(self, name: str, description: str, 
                    location: Optional[str] = None,
                    tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """Add new evidence with validation"""
        
        # Validate input
        if not name or not name.strip():
            raise ValueError("Evidence name cannot be empty")
        
        if not description or not description.strip():
            raise ValueError("Evidence description cannot be empty")
        
        # Check for duplicates (case-insensitive)
        name_lower = name.lower().strip()
        for existing_id, existing_evidence in self.evidence.items():
            if existing_evidence["name"].lower() == name_lower:
                raise ValueError(f"Evidence already exists: {existing_evidence['name']}")
        
        # Generate unique ID
        evidence_id = self._generate_evidence_id(name)
        
        # Create evidence record
        evidence_data = {
            "id": evidence_id,
            "name": name.strip(),
            "description": description.strip(),
            "location": location,
            "tags": tags or [],
            "added_at": datetime.now().isoformat(),
            "significance": self._assess_significance(name, description)
        }
        
        # Store evidence
        self.evidence[evidence_id] = evidence_data
        
        return evidence_data
    
    def get_evidence(self, evidence_id: str) -> Optional[Dict[str, Any]]:
        """Get specific evidence by ID"""
        return self.evidence.get(evidence_id)
    
    def list_evidence(self) -> List[Dict[str, Any]]:
        """List all evidence sorted by significance"""
        evidence_list = list(self.evidence.values())
        return sorted(evidence_list, key=lambda e: e["significance"], reverse=True)
    
    def search_evidence(self, query: str) -> List[Dict[str, Any]]:
        """Search evidence by name, description, or tags"""
        query_lower = query.lower()
        results = []
        
        for evidence in self.evidence.values():
            # Search in name
            if query_lower in evidence["name"].lower():
                results.append(evidence)
                continue
            
            # Search in description
            if query_lower in evidence["description"].lower():
                results.append(evidence)
                continue
            
            # Search in tags
            if any(query_lower in tag.lower() for tag in evidence["tags"]):
                results.append(evidence)
                continue
        
        return results
    
    def tag_evidence(self, evidence_id: str, tags: List[str]) -> None:
        """Add tags to evidence"""
        if evidence_id in self.evidence:
            current_tags = self.evidence[evidence_id]["tags"]
            new_tags = [tag for tag in tags if tag not in current_tags]
            self.evidence[evidence_id]["tags"].extend(new_tags)
    
    def get_evidence_by_location(self, location: str) -> List[Dict[str, Any]]:
        """Get all evidence found at a specific location"""
        return [e for e in self.evidence.values() 
                if e.get("location", "").lower() == location.lower()]
    
    def get_evidence_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Get all evidence with a specific tag"""
        tag_lower = tag.lower()
        return [e for e in self.evidence.values()
                if any(t.lower() == tag_lower for t in e["tags"])]
    
    def validate_evidence_for_trial(self) -> Dict[str, Any]:
        """Validate evidence readiness for trial presentation"""
        
        evidence_list = list(self.evidence.values())
        
        # Count by significance
        high_significance = [e for e in evidence_list if e["significance"] >= 8]
        medium_significance = [e for e in evidence_list if 5 <= e["significance"] < 8]
        low_significance = [e for e in evidence_list if e["significance"] < 5]
        
        # Check for key evidence types
        physical_evidence = self.get_evidence_by_tag("physical")
        witness_testimony = self.get_evidence_by_tag("testimony")
        documentary_evidence = self.get_evidence_by_tag("document")
        
        # Trial readiness assessment
        ready_for_trial = (
            len(high_significance) >= 2 and
            len(evidence_list) >= 5 and
            (len(physical_evidence) >= 1 or len(documentary_evidence) >= 1)
        )
        
        return {
            "ready_for_trial": ready_for_trial,
            "total_evidence": len(evidence_list),
            "high_significance": len(high_significance),
            "medium_significance": len(medium_significance),
            "low_significance": len(low_significance),
            "evidence_types": {
                "physical": len(physical_evidence),
                "testimony": len(witness_testimony),
                "documentary": len(documentary_evidence)
            },
            "recommendations": self._get_evidence_recommendations(evidence_list)
        }
    
    def _generate_evidence_id(self, name: str) -> str:
        """Generate unique evidence ID"""
        # Use name-based ID for consistency
        base_id = name.lower().replace(" ", "_").replace("-", "_")
        base_id = "".join(c for c in base_id if c.isalnum() or c == "_")
        
        # Ensure uniqueness
        if base_id not in self.evidence:
            return base_id
        
        # Add number suffix if needed
        counter = 1
        while f"{base_id}_{counter}" in self.evidence:
            counter += 1
        
        return f"{base_id}_{counter}"
    
    def _assess_significance(self, name: str, description: str) -> int:
        """Assess evidence significance on 1-10 scale"""
        
        significance = 5  # Base significance
        
        name_lower = name.lower()
        desc_lower = description.lower()
        
        # High significance indicators
        high_sig_keywords = [
            "murder weapon", "gun", "knife", "blood", "fingerprint", 
            "dna", "confession", "witness", "alibi", "motive"
        ]
        
        # Medium significance indicators  
        med_sig_keywords = [
            "clue", "evidence", "proof", "document", "letter", 
            "phone", "camera", "photo", "recording"
        ]
        
        # Check for keywords
        for keyword in high_sig_keywords:
            if keyword in name_lower or keyword in desc_lower:
                significance += 3
                break
        
        for keyword in med_sig_keywords:
            if keyword in name_lower or keyword in desc_lower:
                significance += 1
                break
        
        # Length factor (more detailed = more significant)
        if len(description) > 100:
            significance += 1
        
        # Cap at 10
        return min(significance, 10)
    
    def _get_evidence_recommendations(self, evidence_list: List[Dict[str, Any]]) -> List[str]:
        """Get recommendations for improving evidence collection"""
        
        recommendations = []
        
        if len(evidence_list) < 3:
            recommendations.append("Collect more evidence before proceeding to trial")
        
        high_sig_count = len([e for e in evidence_list if e["significance"] >= 8])
        if high_sig_count < 2:
            recommendations.append("Find more significant evidence (weapon, motive, alibi)")
        
        # Check for evidence type diversity
        tags_present = set()
        for evidence in evidence_list:
            tags_present.update(evidence["tags"])
        
        if "physical" not in tags_present:
            recommendations.append("Look for physical evidence at crime scene")
        
        if "testimony" not in tags_present:
            recommendations.append("Interview witnesses for testimony evidence")
        
        if "document" not in tags_present:
            recommendations.append("Search for documentary evidence (contracts, letters, etc.)")
        
        if not recommendations:
            recommendations.append("Evidence collection looks solid for trial")
        
        return recommendations
    
    def get_formatted_evidence_list(self) -> str:
        """Get formatted string of all evidence for display"""
        
        if not self.evidence:
            return "📋 No evidence collected yet."
        
        evidence_list = self.list_evidence()
        
        output = ["📋 Evidence Collected:"]
        output.append("=" * 40)
        
        for i, evidence in enumerate(evidence_list, 1):
            significance_stars = "⭐" * min(evidence["significance"], 10)
            output.append(f"{i}. {evidence['name']} {significance_stars}")
            output.append(f"   📝 {evidence['description']}")
            
            if evidence.get("location"):
                output.append(f"   📍 Found at: {evidence['location']}")
            
            if evidence.get("tags"):
                output.append(f"   🏷️  Tags: {', '.join(evidence['tags'])}")
            
            output.append("")
        
        # Add summary
        total = len(evidence_list)
        high_sig = len([e for e in evidence_list if e["significance"] >= 8])
        
        output.append(f"📊 Summary: {total} pieces of evidence, {high_sig} high significance")
        
        return "\n".join(output)