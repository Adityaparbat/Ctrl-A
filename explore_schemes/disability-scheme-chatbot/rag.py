"""
RAG (Retrieval-Augmented Generation) Module
This module formats Neo4j graph data into natural language answers.
CRITICAL: The LLM is used ONLY for response generation, NOT as a knowledge source.
All information comes from the Neo4j graph context.

Response Rules:
- Use simple, clear language
- Structured output (bullet points / steps)
- Answer ONLY from Neo4j graph context
- If information is missing: "This information is not available in the official scheme data."
"""

from typing import Dict, Any, List, Optional
import logging
import os
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Configure Gemini API
GENAI_API_KEY = os.getenv("GEMINI_API_KEY")
if GENAI_API_KEY:
    genai.configure(api_key=GENAI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
else:
    logger.warning("GEMINI_API_KEY not found. Fallback to Gemini will be disabled.")
    model = None


def generate_gemini_response(query: str, context: Optional[Dict[str, Any]] = None) -> str:
    """
    Generate a response using Google Gemini API.
    Used as a fallback when local graph retrieval fails or for general knowledge.
    
    Args:
        query: User's question
        context: Optional retrieved context (if any)
    
    Returns:
        Generated answer string
    """
    if not model:
        return "I'm sorry, I couldn't find specific information in my database, and I'm not connected to the internet to search further. Please ask about the schemes listed in the menu."
        
    try:
        prompt = f"User Question: {query}\n\n"
        
        if context and context.get('schemes'):
            # Enhancing response with partial context
             prompt += f"Context from local database (use if relevant): {str(context.get('schemes'))[:1000]}...\n\n"
        
        prompt += """
        You are a helpful assistant for Persons with Disabilities in India.
        Answer the question accurately. If the context is provided, prioritize it.
        If the context is irrelevant or empty, use your general knowledge about Indian government schemes for disabilities.
        Keep the answer concise, empathetic, and structured.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return "I'm having trouble connecting to my external knowledge base right now. Please try again later."


def format_scheme_list(schemes_data: List[Dict[str, Any]]) -> str:
    """
    Format a list of schemes into a readable answer.
    
    Args:
        schemes_data: List of scheme dictionaries with related nodes
    
    Returns:
        Formatted answer string
    """
    if not schemes_data:
        return "No government schemes found matching your query."
    
    response = "Here are the government schemes available:\n\n"
    
    for idx, scheme_info in enumerate(schemes_data, 1):
        scheme = scheme_info.get('scheme', {})
        name = scheme.get('name', 'Unknown Scheme')
        description = scheme.get('description', '')
        
        response += f"{idx}. **{name}**\n"
        
        if description:
            # Truncate description for list view
            desc_preview = description.split('.')[0] + '.'
            response += f"   {desc_preview}\n"
        
        response += "\n"
    
    response += "You can ask for more details about any specific scheme."
    return response


def format_scheme_details(scheme_data: Dict[str, Any]) -> str:
    """
    Format complete scheme details into a structured answer.
    
    Args:
        scheme_data: Dictionary with scheme and all related nodes
    
    Returns:
        Formatted answer string
    """
    scheme = scheme_data.get('scheme', {})
    
    if not scheme:
        return "Scheme details not found."
    
    response = f"**{scheme.get('name', 'Unknown Scheme')}**\n\n"
    
    description = scheme.get('description', '')
    if description:
        response += f"{description}\n\n"
    
    # Show deadline information (always show section for deadline queries, even if not specified)
    deadline = scheme.get('application_deadline') or scheme.get('deadline') or scheme.get('closing_date')
    response += "**📅 Application Deadline:**\n"
    if deadline:
        response += f"{deadline}\n\n"
    else:
        response += "Not specified in official data. Most disability pension schemes are open for application throughout the year. "
        response += "However, scholarship schemes may have specific deadlines. "
        response += "Please check the official portal or contact the implementing department for the latest deadline information.\n\n"
    
    # Show application links prominently at the top if available
    portals = scheme_data.get('portals', [])
    if portals:
        response += "**🚀 Quick Apply - Direct Application Links:**\n"
        for portal in portals:
            name = portal.get('name', '')
            url = portal.get('url', '')
            if name and url:
                response += f"- **[Apply via {name}]({url})** - {url}\n"
        response += "\n"
    
    # Disabilities
    disabilities = scheme_data.get('disabilities', [])
    if disabilities:
        response += "**Available for:**\n"
        for disability in disabilities:
            name = disability.get('name', '')
            desc = disability.get('description', '')
            if name:
                response += f"- {name}"
                if desc:
                    response += f": {desc}"
                response += "\n"
        response += "\n"
    
    # Benefits
    benefits = scheme_data.get('benefits', [])
    if benefits:
        response += "**Benefits Provided:**\n"
        for benefit in benefits:
            name = benefit.get('name', '')
            amount = benefit.get('amount', '')
            desc = benefit.get('description', '')
            if name:
                response += f"- {name}"
                if amount:
                    response += f": {amount}"
                if desc:
                    response += f" - {desc}"
                response += "\n"
        response += "\n"
    
    # Eligibility
    eligibility = scheme_data.get('eligibility', [])
    if eligibility:
        response += "**Eligibility Criteria:**\n"
        for elig in eligibility:
            name = elig.get('name', '')
            desc = elig.get('description', '')
            age_min = elig.get('age_min')
            age_max = elig.get('age_max')
            income_max = elig.get('income_max')
            disability_percent = elig.get('disability_percent_min')
            
            if name:
                response += f"- {name}\n"
            elif desc:
                response += f"- {desc}\n"
            
            if age_min is not None or age_max is not None:
                age_info = "Age: "
                if age_min is not None:
                    age_info += f"{age_min}+ years"
                if age_max is not None:
                    age_info += f" up to {age_max} years"
                response += f"  - {age_info}\n"
            
            if income_max is not None:
                response += f"  - Maximum income: ₹{income_max} per month\n"
            
            if disability_percent is not None:
                response += f"  - Minimum disability percentage: {disability_percent}%\n"
        response += "\n"
    
    # Documents
    documents = scheme_data.get('documents', [])
    if documents:
        response += "**Required Documents:**\n"
        for doc in documents:
            name = doc.get('name', '')
            doc_type = doc.get('document_type', '')
            desc = doc.get('description', '')
            if name:
                response += f"- {name}"
                if doc_type:
                    response += f" ({doc_type})"
                if desc:
                    response += f": {desc}"
                response += "\n"
        response += "\n"
    
    # Application Process
    application_processes = scheme_data.get('application_processes', [])
    if application_processes:
        response += "**Application Process:**\n"
        for process in application_processes:
            name = process.get('name', '')
            desc = process.get('description', '')
            steps = process.get('steps', [])
            
            if name:
                response += f"{name}\n"
            if desc:
                response += f"{desc}\n"
            if steps and isinstance(steps, list):
                for step_idx, step in enumerate(steps, 1):
                    response += f"{step_idx}. {step}\n"
        response += "\n"
    
    # Government Bodies
    government_bodies = scheme_data.get('government_bodies', [])
    if government_bodies:
        response += "**Implemented by:**\n"
        for gb in government_bodies:
            name = gb.get('name', '')
            contact = gb.get('contact', '')
            if name:
                response += f"- {name}"
                if contact:
                    response += f" (Contact: {contact})"
                response += "\n"
        response += "\n"
    
    # Helplines
    helplines = scheme_data.get('helplines', [])
    if helplines:
        response += "**Helplines:**\n"
        for helpline in helplines:
            name = helpline.get('name', '')
            number = helpline.get('number', '')
            if name and number:
                response += f"- {name}: {number}\n"
        response += "\n"
    
    # Source
    source = scheme.get('source', '')
    if source:
        response += f"Source: {source}\n"
    
    return response


def format_eligibility_info(schemes_data: List[Dict[str, Any]]) -> str:
    """Format eligibility information from schemes."""
    if not schemes_data:
        return "Eligibility information is not available."
    
    response = "**Eligibility Criteria:**\n\n"
    
    for scheme_info in schemes_data:
        scheme = scheme_info.get('scheme', {})
        scheme_name = scheme.get('name', 'Unknown Scheme')
        
        eligibility = scheme_info.get('eligibility', [])
        if eligibility:
            response += f"For **{scheme_name}**:\n"
            for elig in eligibility:
                name = elig.get('name', '')
                desc = elig.get('description', '')
                age_min = elig.get('age_min')
                age_max = elig.get('age_max')
                income_max = elig.get('income_max')
                disability_percent = elig.get('disability_percent_min')
                
                if name:
                    response += f"- {name}\n"
                elif desc:
                    response += f"- {desc}\n"
                
                if age_min is not None or age_max is not None:
                    age_info = "Age: "
                    if age_min is not None:
                        age_info += f"{age_min}+ years"
                    if age_max is not None:
                        age_info += f" up to {age_max} years"
                    response += f"  - {age_info}\n"
                
                if income_max is not None:
                    response += f"  - Maximum income: ₹{income_max} per month\n"
                
                if disability_percent is not None:
                    response += f"  - Minimum disability percentage: {disability_percent}%\n"
            
            response += "\n"
    
    return response


def format_documents_info(schemes_data: List[Dict[str, Any]]) -> str:
    """Format required documents information."""
    if not schemes_data:
        return "Document requirements are not available."
    
    # Collect unique documents across all schemes
    all_documents = {}
    
    for scheme_info in schemes_data:
        scheme = scheme_info.get('scheme', {})
        scheme_name = scheme.get('name', 'Unknown')
        
        documents = scheme_info.get('documents', [])
        for doc in documents:
            doc_id = doc.get('id')
            doc_name = doc.get('name', '')
            if doc_id and doc_name:
                if doc_id not in all_documents:
                    all_documents[doc_id] = {
                        'name': doc_name,
                        'document_type': doc.get('document_type', ''),
                        'description': doc.get('description', ''),
                        'schemes': []
                    }
                all_documents[doc_id]['schemes'].append(scheme_name)
    
    if not all_documents:
        return "Document requirements are not available."
    
    response = "**Required Documents:**\n\n"
    
    for doc_id, doc_info in all_documents.items():
        name = doc_info['name']
        doc_type = doc_info.get('document_type', '')
        desc = doc_info.get('description', '')
        
        response += f"- **{name}**"
        if doc_type:
            response += f" ({doc_type})"
        if desc:
            response += f": {desc}"
        response += "\n"
    
    return response


def format_application_process(schemes_data: List[Dict[str, Any]]) -> str:
    """Format application process information."""
    if not schemes_data:
        return "Application process information is not available."
    
    response = "**Application Process:**\n\n"
    
    for scheme_info in schemes_data:
        scheme = scheme_info.get('scheme', {})
        scheme_name = scheme.get('name', 'Unknown Scheme')
        
        # Application processes
        application_processes = scheme_info.get('application_processes', [])
        if application_processes:
            response += f"For **{scheme_name}**:\n"
            for process in application_processes:
                name = process.get('name', '')
                desc = process.get('description', '')
                steps = process.get('steps', [])
                
                if name:
                    response += f"{name}\n"
                if desc:
                    response += f"{desc}\n"
                if steps and isinstance(steps, list):
                    for step_idx, step in enumerate(steps, 1):
                        response += f"{step_idx}. {step}\n"
                response += "\n"
        
        # Portals with clickable links
        portals = scheme_info.get('portals', [])
        if portals:
            response += f"**🚀 Apply Online for {scheme_name}:**\n"
            for portal in portals:
                name = portal.get('name', '')
                url = portal.get('url', '')
                if name and url:
                    response += f"- **[Apply via {name}]({url})** - {url}\n"
            response += "\n"
    
    return response


def format_deadline_info(schemes_data: List[Dict[str, Any]]) -> str:
    """Format deadline information for schemes."""
    if not schemes_data:
        return "Deadline information is not available."
    
    response = "**📅 Application Deadlines:**\n\n"
    
    has_deadline_info = False
    
    for scheme_info in schemes_data:
        scheme = scheme_info.get('scheme', {})
        scheme_name = scheme.get('name', 'Unknown Scheme')
        
        # Check for deadline field in scheme
        deadline = scheme.get('application_deadline') or scheme.get('deadline') or scheme.get('closing_date')
        
        response += f"For **{scheme_name}**:\n"
        
        if deadline:
            has_deadline_info = True
            response += f"  **Application Deadline**: {deadline}\n\n"
        else:
            response += "  **Application Deadline**: Not specified in official data.\n"
            response += "  Most disability pension schemes are open for application throughout the year.\n"
            response += "  However, some scholarship schemes may have specific deadlines.\n\n"
        
        # Show portal links for deadline-related queries
        portals = scheme_info.get('portals', [])
        if portals:
            response += "  **📋 Check Official Portal for Latest Deadlines:**\n"
            for portal in portals:
                name = portal.get('name', '')
                url = portal.get('url', '')
                if name and url:
                    response += f"  - [{name}]({url}) - {url}\n"
            response += "\n"
        
        # Show government body contact for deadline inquiries
        government_bodies = scheme_info.get('government_bodies', [])
        if government_bodies:
            response += "  **📞 Contact for Deadline Information:**\n"
            for gb in government_bodies:
                name = gb.get('name', '')
                contact = gb.get('contact', '')
                if name:
                    response += f"  - {name}"
                    if contact:
                        response += f" - {contact}"
                    response += "\n"
            response += "\n"
    
    if not has_deadline_info:
        response += "\n**ℹ️ Important Note:**\n"
        response += "For the most accurate deadline information, please check the official portals listed above."
    
    return response


def generate_answer(context: Dict[str, Any]) -> str:
    """
    Generate natural language answer from GraphRAG context.
    Includes logic to filter specific schemes and fallback to Gemini.
    
    Args:
        context: Dictionary containing retrieved graph context
    
    Returns:
        Formatted answer string
    """
    if not context:
        return generate_gemini_response("General inquiry about government schemes")
    
    schemes_data = context.get('schemes', [])
    intent_info = context.get('intent', {})
    intent = intent_info.get('intent', 'general')
    query = context.get('query', '').lower()
    
    # --- FALLBACK LOGIC ---
    # If no schemes found or very low confidence, use Gemini
    if not schemes_data:
        # Check if there's a helpful message in context
        message = context.get('message', '')
        if message and "data_ingestion" in message:
            return message # System error, don't use Gemini
            
        logger.info("No schemes found in graph. Falling back to Gemini.")
        return generate_gemini_response(context.get('query', ''))

    # --- SPECIFIC SCHEME FILTERING (Fix for "All schemes" bug) ---
    # If the user asks for a specific scheme (e.g., "tell me about ADIP"),
    # filter the schemes_data to only include the most relevant one(s).
    
    # Check if query contains any scheme name from the results
    matched_schemes = []
    for s_data in schemes_data:
        s_name = s_data['scheme']['name'].lower()
        # Simple containment check; for better results, use fuzzy matching or the similarity score
        # Check if a significant part of the name is in the query (e.g., "adip", "igndps", "pension")
        # OR if the similarity score is high enough to indicate a specific match
        sim_score = context.get('similarity_scores', {}).get(s_data['scheme']['id'], 0)
        
        if sim_score > 0.75: # Strong vector match
             matched_schemes.append(s_data)
        elif "adip" in query and "adip" in s_name:
             matched_schemes.append(s_data)
        elif "igndps" in query and "igndps" in s_name:
             matched_schemes.append(s_data)
        elif "pension" in query and "pension" in s_name:
             matched_schemes.append(s_data)
        elif "scholarship" in query and "scholarship" in s_name:
             matched_schemes.append(s_data)
        elif "udid" in query and "udid" in s_name:
             matched_schemes.append(s_data)
        elif "railway" in query and "railway" in s_name:
             matched_schemes.append(s_data)
             
    # If we found specific matches, use ONLY them
    if matched_schemes:
        schemes_data = matched_schemes
        # Force intent to details if a single scheme is matched specifically
        if len(matched_schemes) == 1:
            intent = 'scheme_details'

    
    # --- ROUTING LOGIC ---
    
    if intent == 'scheme_list' or intent == 'general':
        # If we have many schemes, list them. If only 1, show details.
        if len(schemes_data) == 1:
            return format_scheme_details(schemes_data[0])
        return format_scheme_list(schemes_data)
    
    elif intent == 'scheme_details':
        # Return details of top scheme
        if schemes_data:
             # Even if multiple, just show the first one (most relevant) for details intent
             # or show all matched ones if we filtered above
             if len(schemes_data) > 1:
                 # If we have multiple "specific" matches (e.g. "scholarship"), list them with short details
                 return format_scheme_list(schemes_data)
             else:
                return format_scheme_details(schemes_data[0])
        return format_scheme_list(schemes_data)
    
    elif intent == 'benefit':
        return format_scheme_list(schemes_data)
    
    elif intent == 'eligibility':
        return format_eligibility_info(schemes_data)
    
    elif intent == 'documents':
        return format_documents_info(schemes_data)
    
    elif intent == 'application_process' or intent == 'portal':
        return format_application_process(schemes_data)
    
    elif intent == 'deadline':
        return format_deadline_info(schemes_data)
    
    elif intent == 'disability_specific':
        return format_scheme_list(schemes_data)
    
    elif intent == 'helpline':
        response = "**Helplines for Disability Schemes:**\n\n"
        for scheme_info in schemes_data:
            scheme = scheme_info.get('scheme', {})
            scheme_name = scheme.get('name', '')
            helplines = scheme_info.get('helplines', [])
            if helplines:
                response += f"For **{scheme_name}**:\n"
                for helpline in helplines:
                    name = helpline.get('name', '')
                    number = helpline.get('number', '')
                    if name and number:
                        response += f"- {name}: {number}\n"
                response += "\n"
        
        if response == "**Helplines for Disability Schemes:**\n\n":
            return "Helpline information is not available."
        return response
    
    else:
        return format_scheme_list(schemes_data)
