import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

def _describe_object_position(bbox: List[float], image_size: Dict[str, int]) -> str:
    """Describe where an object is positioned in the image"""
    x1, y1, x2, y2 = bbox
    img_w, img_h = image_size.get('width', 1), image_size.get('height', 1)
    
    # Calculate relative positions
    center_x = (x1 + x2) / 2 / img_w
    center_y = (y1 + y2) / 2 / img_h
    
    # Determine horizontal position
    if center_x < 0.33:
        h_pos = "on the left"
    elif center_x > 0.67:
        h_pos = "on the right"
    else:
        h_pos = "in the center"
    
    # Determine vertical position
    if center_y < 0.33:
        v_pos = "at the top"
    elif center_y > 0.67:
        v_pos = "at the bottom"
    else:
        v_pos = "in the middle"
    
    return f"{h_pos} and {v_pos}"

def _describe_object_size(bbox: List[float], image_size: Dict[str, int]) -> str:
    """Describe the relative size of an object"""
    x1, y1, x2, y2 = bbox
    img_w, img_h = image_size.get('width', 1), image_size.get('height', 1)
    
    obj_area = (x2 - x1) * (y2 - y1)
    img_area = img_w * img_h
    relative_size = obj_area / img_area
    
    if relative_size > 0.35:
        return "large"
    elif relative_size > 0.18:
        return "medium-sized"
    elif relative_size > 0.08:
        return "small"
    else:
        return "small"

def _describe_object_confidence(confidence: float) -> str:
    """Describe how confident we are about the detection"""
    if confidence > 0.8:
        return "clearly visible"
    elif confidence > 0.6:
        return "visible"
    elif confidence > 0.4:
        return "partially visible"
    else:
        return "faintly visible"

def _generate_detailed_object_description(obj: Dict[str, Any], image_size: Dict[str, int]) -> str:
    """Generate a detailed description of a single object"""
    label = obj["label"]
    confidence = obj.get("confidence", 0.5)
    bbox = obj.get("bbox", [0, 0, 100, 100])
    
    # Basic object info
    confidence_desc = _describe_object_confidence(confidence)
    position_desc = _describe_object_position(bbox, image_size)
    size_desc = _describe_object_size(bbox, image_size)
    
    # Build detailed description
    description_parts = [f"a {confidence_desc} {size_desc} {label}"]
    
    # Add position information
    description_parts.append(f"positioned {position_desc}")
    
    # Add aspect ratio information if available
    aspect_ratio = obj.get("aspect_ratio", 1.0)
    if aspect_ratio > 2:
        description_parts.append("with a wide, rectangular shape")
    elif aspect_ratio < 0.5:
        description_parts.append("with a tall, narrow shape")
    elif 0.8 <= aspect_ratio <= 1.2:
        description_parts.append("with a roughly square shape")
    
    return " ".join(description_parts)

def _analyze_scene_composition(objects: List[Dict[str, Any]], props: Dict[str, Any]) -> str:
    """Analyze the overall composition and mood of the scene"""
    composition_parts = []
    
    # Analyze object distribution
    if len(objects) > 5:
        composition_parts.append("a busy scene with many elements")
    elif len(objects) > 2:
        composition_parts.append("a moderately detailed scene")
    elif len(objects) > 0:
        composition_parts.append("a relatively simple scene")
    else:
        composition_parts.append("a minimal scene")
    
    # Analyze visual properties
    if props.get("is_dark"):
        composition_parts.append("with a dark, moody atmosphere")
    elif props.get("brightness", 128) > 200:
        composition_parts.append("with bright, well-lit conditions")
    
    if props.get("is_low_contrast"):
        composition_parts.append("that appears somewhat flat or low-contrast")
    elif props.get("contrast", 50) > 80:
        composition_parts.append("with high contrast and strong visual definition")
    
    if props.get("is_complex"):
        composition_parts.append("featuring complex visual patterns and details")
    
    return " ".join(composition_parts)

def generate_narration(scene: Dict[str, Any]) -> str:
    """
    Generate a comprehensive, detailed narration from scene detection output.
    Provides rich descriptions with positioning, sizing, and contextual information.
    """
    objects: List[Dict[str, Any]] = scene.get("objects", [])
    texts: List[Dict[str, Any]] = scene.get("text_elements", [])
    props: Dict[str, Any] = scene.get("image_properties", {})
    image_size: Dict[str, int] = scene.get("image_size", {"width": 1, "height": 1})

    narration_parts = []

    # Start with scene composition analysis
    if objects or props:
        composition = _analyze_scene_composition(objects, props)
        narration_parts.append(f"This appears to be {composition}.")

    # Process objects with detailed descriptions
    if objects:
        # Filter objects by confidence and sort by confidence - lower threshold for more objects
        filtered_objects = [obj for obj in objects if obj.get("confidence", 0) > 0.1]
        filtered_objects.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        
        if filtered_objects:
            # Group objects by type for counting
            object_counts = {}
            detailed_objects = []
            
            for obj in filtered_objects:
                label = obj["label"]
                if label in object_counts:
                    object_counts[label] += 1
                else:
                    object_counts[label] = 1
                    detailed_objects.append(obj)
            
            # Generate detailed descriptions
            if len(detailed_objects) == 1:
                obj_desc = _generate_detailed_object_description(detailed_objects[0], image_size)
                narration_parts.append(f"The main subject is {obj_desc}.")
            elif len(detailed_objects) == 2:
                obj1_desc = _generate_detailed_object_description(detailed_objects[0], image_size)
                obj2_desc = _generate_detailed_object_description(detailed_objects[1], image_size)
                narration_parts.append(f"The primary elements include {obj1_desc} and {obj2_desc}.")
            elif len(detailed_objects) <= 8:
                # Describe more objects when available
                main_objects = detailed_objects[:5]  # Show up to 5 objects
                obj_descriptions = [_generate_detailed_object_description(obj, image_size) for obj in main_objects]
                
                if len(obj_descriptions) == 2:
                    narration_parts.append(f"The scene features {obj_descriptions[0]} and {obj_descriptions[1]}.")
                elif len(obj_descriptions) == 3:
                    narration_parts.append(f"The scene features {obj_descriptions[0]}, {obj_descriptions[1]}, and {obj_descriptions[2]}.")
                elif len(obj_descriptions) == 4:
                    narration_parts.append(f"The scene features {obj_descriptions[0]}, {obj_descriptions[1]}, {obj_descriptions[2]}, and {obj_descriptions[3]}.")
                elif len(obj_descriptions) == 5:
                    narration_parts.append(f"The scene features {obj_descriptions[0]}, {obj_descriptions[1]}, {obj_descriptions[2]}, {obj_descriptions[3]}, and {obj_descriptions[4]}.")
                else:
                    narration_parts.append(f"The scene features {', '.join(obj_descriptions[:-1])}, and {obj_descriptions[-1]}.")
                
                # Add count information for multiple objects of same type
                for label, count in object_counts.items():
                    if count > 1:
                        narration_parts.append(f"There are {count} {label}s visible in the image.")
            else:
                # Many objects - provide summary
                narration_parts.append(f"The scene contains multiple objects including {', '.join([obj['label'] for obj in detailed_objects[:5]])}.")
                narration_parts.append(f"In total, there are {len(filtered_objects)} distinct elements detected.")
        else:
            # No high-confidence objects, use image properties
            if props.get("is_dark"):
                narration_parts.append("The image appears dark with some visible content.")
            elif props.get("is_low_contrast"):
                narration_parts.append("The image has low contrast, making details difficult to distinguish.")
            elif props.get("is_complex"):
                narration_parts.append("The scene appears complex with intricate visual patterns.")
            else:
                narration_parts.append("The image contains visual content, though specific objects are not clearly identifiable.")
    else:
        # No objects detected - provide helpful description based on image properties
        if props.get("is_dark"):
            narration_parts.append("The image appears dark with some visible content.")
        elif props.get("is_low_contrast"):
            narration_parts.append("The image has low contrast, making details difficult to distinguish.")
        elif props.get("is_complex"):
            narration_parts.append("The scene appears complex with intricate visual patterns.")
        else:
            narration_parts.append("The image contains visual content, though specific objects are not clearly identifiable.")

    # Add text elements with detailed positioning
    if texts:
        extracted_texts = [t for t in texts if "text" in t and t["text"].strip()]
        if extracted_texts:
            text_descriptions = []
            for text_elem in extracted_texts[:3]:  # Limit to first 3 text elements
                text = text_elem["text"]
                confidence = text_elem.get("confidence", 0.5)
                bbox = text_elem.get("bbox", [0, 0, 100, 100])
                
                position_desc = _describe_object_position(bbox, image_size)
                confidence_desc = _describe_object_confidence(confidence)
                
                text_descriptions.append(f'"{text}" ({confidence_desc}, positioned {position_desc})')
            
            if len(text_descriptions) == 1:
                narration_parts.append(f"I can also read text: {text_descriptions[0]}.")
            else:
                narration_parts.append(f"I can also read text including: {', '.join(text_descriptions)}.")

    # Add additional context about image quality and characteristics
    if props:
        quality_notes = []
        
        if props.get("brightness", 128) < 50:
            quality_notes.append("very dark")
        elif props.get("brightness", 128) > 200:
            quality_notes.append("very bright")
        
        if props.get("contrast", 50) < 20:
            quality_notes.append("low contrast")
        elif props.get("contrast", 50) > 100:
            quality_notes.append("high contrast")
        
        if props.get("unique_colors", 1000) < 100:
            quality_notes.append("with limited color variety")
        elif props.get("unique_colors", 1000) > 10000:
            quality_notes.append("with rich color variety")
        
        if quality_notes:
            narration_parts.append(f"The image appears {', '.join(quality_notes)}.")

    # Final narration - ensure it's comprehensive and meaningful
    narration = " ".join(narration_parts)
    if not narration.strip():
        narration = "I can see an image with content, though I'm having difficulty providing a detailed description at this time."

    logger.info(f"Generated detailed narration: {narration}")
    return narration
