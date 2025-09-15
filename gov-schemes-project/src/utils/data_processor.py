"""
Data processing utilities for the disability schemes system.

This module provides functions for processing, cleaning, and validating
scheme data before it's stored in the vector database.
"""

import re
import logging
from typing import List, Dict, Any, Optional
import pandas as pd
from src.models.scheme_models import DisabilityType, SupportType

logger = logging.getLogger(__name__)


class DataProcessor:
    """Data processor for scheme data cleaning and validation."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text data.
        
        Args:
            text (str): Input text to clean
            
        Returns:
            str: Cleaned text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\-.,!?()]', '', text)
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        return text
    
    @staticmethod
    def validate_scheme_data(scheme: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean scheme data.
        
        Args:
            scheme (Dict[str, Any]): Raw scheme data
            
        Returns:
            Dict[str, Any]: Cleaned and validated scheme data
        """
        cleaned_scheme = {}
        
        # Required fields
        required_fields = ["name", "description", "state", "disability_type", "support_type", "apply_link"]
        
        for field in required_fields:
            if field not in scheme or not scheme[field]:
                raise ValueError(f"Missing required field: {field}")
            
            cleaned_scheme[field] = DataProcessor.clean_text(str(scheme[field]))
        
        # Validate disability type
        disability_type = cleaned_scheme["disability_type"].lower().replace(" ", "_")
        if disability_type not in [dt.value for dt in DisabilityType]:
            # Try to map common variations
            mapping = {
                "visual": "visual_impairment",
                "hearing": "hearing_impairment",
                "mobility": "mobility_impairment",
                "intellectual": "intellectual_disability",
                "mental": "intellectual_disability",
                "physical": "mobility_impairment"
            }
            
            for key, value in mapping.items():
                if key in disability_type:
                    disability_type = value
                    break
            else:
                disability_type = "other"
        
        cleaned_scheme["disability_type"] = disability_type
        
        # Validate support type
        support_type = cleaned_scheme["support_type"].lower().replace(" ", "_")
        if support_type not in [st.value for st in SupportType]:
            # Try to map common variations
            mapping = {
                "financial": "financial",
                "education": "educational",
                "medical": "medical",
                "employment": "employment",
                "job": "employment",
                "device": "assistive_devices",
                "transport": "transportation",
                "housing": "housing",
                "home": "housing"
            }
            
            for key, value in mapping.items():
                if key in support_type:
                    support_type = value
                    break
            else:
                support_type = "other"
        
        cleaned_scheme["support_type"] = support_type
        
        # Optional fields
        optional_fields = ["eligibility", "benefits", "contact_info", "validity_period"]
        for field in optional_fields:
            if field in scheme and scheme[field]:
                cleaned_scheme[field] = DataProcessor.clean_text(str(scheme[field]))
            else:
                cleaned_scheme[field] = None
        
        return cleaned_scheme
    
    @staticmethod
    def process_schemes_batch(schemes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process a batch of schemes.
        
        Args:
            schemes (List[Dict[str, Any]]): List of raw scheme data
            
        Returns:
            List[Dict[str, Any]]: List of cleaned and validated schemes
        """
        processed_schemes = []
        errors = []
        
        for i, scheme in enumerate(schemes):
            try:
                cleaned_scheme = DataProcessor.validate_scheme_data(scheme)
                processed_schemes.append(cleaned_scheme)
            except Exception as e:
                error_msg = f"Error processing scheme {i}: {str(e)}"
                logger.warning(error_msg)
                errors.append(error_msg)
        
        if errors:
            logger.warning(f"Processed {len(processed_schemes)} schemes with {len(errors)} errors")
        
        return processed_schemes
    
    @staticmethod
    def create_document_text(scheme: Dict[str, Any]) -> str:
        """
        Create searchable document text from scheme data.
        
        Args:
            scheme (Dict[str, Any]): Scheme data
            
        Returns:
            str: Combined searchable text
        """
        parts = [
            scheme.get("name", ""),
            scheme.get("description", ""),
            scheme.get("state", ""),
            scheme.get("disability_type", ""),
            scheme.get("support_type", ""),
            scheme.get("eligibility", ""),
            scheme.get("benefits", "")
        ]
        
        # Filter out None values and join
        text_parts = [part for part in parts if part]
        return " - ".join(text_parts)
    
    @staticmethod
    def extract_keywords(text: str) -> List[str]:
        """
        Extract keywords from text for better search.
        
        Args:
            text (str): Input text
            
        Returns:
            List[str]: List of keywords
        """
        if not text:
            return []
        
        # Convert to lowercase and split
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Remove common stop words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "must", "can", "this", "that", "these", "those"
        }
        
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(keywords))
    
    @staticmethod
    def generate_suggestions(schemes: List[Dict[str, Any]]) -> List[str]:
        """
        Generate search suggestions from scheme data.
        
        Args:
            schemes (List[Dict[str, Any]]): List of schemes
            
        Returns:
            List[str]: List of search suggestions
        """
        suggestions = set()
        
        for scheme in schemes:
            # Create suggestions based on disability type and support type
            disability = scheme.get("disability_type", "").replace("_", " ")
            support = scheme.get("support_type", "").replace("_", " ")
            state = scheme.get("state", "")
            
            if disability and support:
                suggestions.add(f"{support} for {disability}")
                suggestions.add(f"{disability} {support}")
            
            if state and disability:
                suggestions.add(f"{disability} in {state}")
            
            if state and support:
                suggestions.add(f"{support} in {state}")
        
        return sorted(list(suggestions))[:20]  # Return top 20 suggestions
