"""
Test script for the NPC Personality Decoder

This script demonstrates how to use the NPCPersonalityDecoder class to interpret
personality DNA strings and generate rich character descriptions.
"""

import os
import sys
import logging
from pathlib import Path

# Add the parent directory to the sys.path
sys.path.append(str(Path(__file__).parent.parent))

from core.npc_decoder import NPCPersonalityDecoder

def test_basic_decoding():
    """Test basic decoding of NPC personality DNA."""
    print("\n=== Testing Basic NPC Personality Decoding ===\n")
    
    # Example DNA string
    dna_string = "(7/3) 5B4,2R1,8L3,4F5,7S2,3P1,7D4,2G3,9Y5,1E2,6N3,4K2,6Z4,8O3,7C2,9R4,2A5,6D3,8A1,5I4 - H7,C3,K8,G2,L9,J4,M5,F6,E7,B3,U8,S2,I6,R7,T3,A9,D4,V5,Y2,X6"
    print(f"Example Personality DNA: {dna_string}\n")
    
    # Create decoder
    decoder = NPCPersonalityDecoder()
    
    # Format the DNA
    formatted_dna = decoder.format_personality_dna(dna_string)
    
    print("=== Formatted Personality DNA ===")
    print(f"LNC Average: {formatted_dna['lnc_average']} - {decoder.lnc_alignment.get(formatted_dna['lnc_average'], 'Unknown')}")
    print(f"GNE Average: {formatted_dna['gne_average']} - {decoder.gne_alignment.get(formatted_dna['gne_average'], 'Unknown')}\n")
    
    print("Core Character Traits:")
    for trait in formatted_dna["lnc_traits"]:
        print(f"  {trait['code']} - {trait['description']} (Score: {trait['lnc_score']}, Intensity: {trait['intensity']})")
    
    print("\nMoral/Ethical Values:")
    for trait in formatted_dna["gne_traits"]:
        print(f"  {trait['code']} - {trait['description']} (Score: {trait['gne_score']})")
    
    # Get the prompt
    prompt = decoder.decode_personality(dna_string)
    
    # Save the prompt
    file_path = decoder.save_npc_description("test_npc_prompt", prompt)
    print(f"\nDecoder prompt saved to: {file_path}")
    print("(This prompt would be sent to an LLM in a production environment)")

def test_decoding_with_context():
    """Test decoding of NPC personality DNA with additional context."""
    print("\n=== Testing NPC Personality Decoding with Context ===\n")
    
    # Example DNA string
    dna_string = "(8/2) 7B5,3R2,9L4,8F2,6S3,4P5,8D2,3G4,8Y1,2E3,5N4,3K5,7Z1,9O2,8C3,7R5,3A2,7D4,9A5,4I1 - H2,C8,K3,G7,L2,J3,M2,F1,E3,B9,U7,S2,I3,R8,T1,A9,D2,V7,Y3,X8"
    print(f"Example Personality DNA with context: {dna_string}\n")
    
    # Additional context
    additional_context = """
    This character is a master inventor in a steampunk world. They grew up in a poor district 
    but showed remarkable talent for mechanical engineering from a young age. They're known for 
    creating unusual devices that blend practical function with artistic design. Recently, they've 
    discovered a way to infuse their creations with magical energy, drawing the attention of 
    both government officials and criminal organizations.
    """
    print(f"Additional context: {additional_context}\n")
    
    # Create decoder
    decoder = NPCPersonalityDecoder()
    
    # Get the prompt with context
    prompt = decoder.decode_personality(dna_string, additional_context)
    
    # Save the prompt
    file_path = decoder.save_npc_description("inventor_npc_prompt", prompt)
    print(f"\nDecoder prompt with context saved to: {file_path}")
    print("(This prompt would be sent to an LLM in a production environment)")

def test_llm_integration():
    """Test the integration with an LLM using a mock response."""
    print("\n=== Testing LLM Integration with Mock Response ===\n")
    
    # Example DNA string
    dna_string = "(6/7) 5B3,7R2,4L4,6F3,5S2,7P1,4D5,6G3,3Y4,7E2,5N3,6K1,4Z5,7O2,5C4,4R3,7A1,5D4,6A2,4I3 - H8,C7,K9,G6,L8,J7,M9,F6,E8,B7,U6,S8,I7,R6,T9,A7,D8,V6,E7,X6"
    print(f"Example Personality DNA for LLM test: {dna_string}\n")
    
    # Additional context
    additional_context = """
    This character is a respected healer in a small steampunk city. They combine traditional
    herbal remedies with magical techniques and mechanical devices to cure ailments that
    others can't treat. They have a small clinic in the artisan district where they see
    patients from all walks of life, regardless of their ability to pay.
    """
    print(f"Additional context: {additional_context}\n")
    
    # Create decoder
    decoder = NPCPersonalityDecoder()
    
    # Get the prompt with context
    prompt = decoder.decode_personality(dna_string, additional_context)
    
    # Save the prompt
    file_path = decoder.save_npc_description("healer_npc_prompt", prompt)
    print(f"Decoder prompt saved to: {file_path}")
    
    # In a real implementation, this would be sent to an LLM
    # For testing purposes, we'll use a mock LLM response
    mock_llm_response = """
    # NPC CHARACTER PROFILE: DR. ELIAS THORNWOOD
    
    ## Personality Overview
    Dr. Elias Thornwood is a compassionate and methodical healer who balances scientific precision with genuine care for others. His calm demeanor masks an unwavering determination to help those in need, regardless of their status or wealth, though he struggles with setting personal boundaries and often works himself to exhaustion.
    
    ## Defining Traits
    - **Compassionate Healer (K9)**: Elias's defining characteristic is his deep compassion for the suffering of others. He will often waive fees for those who cannot afford his services and works tirelessly to find solutions for even the most challenging medical cases. When faced with a patient in pain, he becomes fully focused and will not rest until he has alleviated their suffering.
    
    - **Methodical Practitioner (D5)**: In his clinic, every tool has its place, and every procedure follows a carefully documented protocol. This methodical approach extends to his diagnostic process, where he systematically rules out possibilities before determining treatment. Patients often comment on his meticulous note-taking and carefully organized clinic.
    
    - **Ethical Innovator (I7/R6)**: Elias constantly pushes the boundaries of healing by combining traditional medicine with magical techniques and mechanical innovations, but he never experiments on patients without their explicit consent and clear explanation of risks. His ethical framework is uncompromising when it comes to patient welfare.
    
    - **Balanced Perspective (LNC 6)**: Elias respects traditions and established medical protocols, but isn't afraid to bend rules when a patient's wellbeing depends on it. He maintains detailed records of his experimental treatments, hoping to formalize them into accepted practices over time.
    
    ## Contradictions & Complexity
    Despite his giving nature and selfless approach to healing, Elias struggles with accepting help from others (U6 vs S8). He'll work himself to exhaustion rather than delegate or ask for assistance, creating a paradoxical situation where the healer himself often needs healing. Additionally, while generally outspoken about medical matters (O2), he becomes reserved (R2) when conversation shifts to personal topics, creating a fascinating duality where patients often know little about the man who knows everything about their health.
    
    ## Behavioral Patterns
    - **Under Pressure**: When faced with a medical emergency, Elias becomes hyperfocused and exceptionally calm (E2). His movements become more precise, his speech more concise, and he radiates a confidence that reassures those around him. However, when the crisis passes, he often experiences delayed emotional reactions, sometimes retreating to his private workshop to decompress.
    
    - **With Authority**: Elias shows appropriate respect to city officials and guild masters, but won't hesitate to advocate firmly for patient needs or necessary resources (T9). He's particularly assertive when bureaucracy threatens patient care, revealing the stubborn determination beneath his gentle exterior.
    
    - **With Subordinates**: He treats apprentices and assistants with patience and kindness (P1), offering thorough explanations for his techniques and valuing their input. However, he holds them to the same exacting standards he applies to himself, which some find inspiring and others find overwhelming.
    
    - **Core Values**: Above all, Elias values the alleviation of suffering and the dignity of each patient. He sees healing as a sacred trust rather than merely a profession, and believes that everyone deserves quality care regardless of their background or circumstances.
    
    ## Voice & Expression
    Elias speaks in measured, precise tones with a warm timbre that naturally soothes anxious patients. His vocabulary is technical when discussing medicine but shifts to simple explanations when communicating with patients. Common phrases include "Let's examine this systematically," "The body tells us what it needs, if we listen carefully," and "Healing is as much art as science."
    
    When emotionally moved, his speech becomes slightly more formal, as if the structure helps him manage his feelings. He unconsciously taps his fingers in a specific pattern when thinking deeply, and tends to make direct eye contact when speaking about important matters.
    
    ## Background Implications
    Elias's balanced moral approach and compassionate nature suggest he was raised with strong ethical principles, possibly by parents or mentors who emphasized service to others. His methodical tendencies and innovative spirit indicate formal medical training, perhaps at a prestigious academy, but his unconventional approaches hint at disappointment with traditional methods alone.
    
    The intensity of his commitment to helping the poor suggests he may have experienced or witnessed untreated suffering in his youth. His reluctance to speak about himself might indicate past trauma or loss, possibly a patient he couldn't save or a personal failure that drives his relentless pursuit of better healing techniques.
    
    ## Development Potential
    As Elias continues his practice, he may learn to better balance self-care with patient care, perhaps through a significant health scare of his own or through the influence of a supportive colleague or apprentice who helps him recognize his limits.
    
    His innovative combinations of magic and mechanics could lead to greater recognition in the medical community, forcing him to navigate fame and increased demand for his services. This could challenge his egalitarian approach as he decides how to scale his practice without compromising his values.
    
    If the tensions between government officials and criminal elements interested in his magical healing techniques escalate, Elias may be forced to take political sides, potentially developing his leadership abilities as he advocates for equitable access to medical care in the steampunk city.
    """
    
    print("\n=== Mock LLM Response ===\n")
    print(mock_llm_response)
    
    # In a real implementation, we would save this response
    file_path = decoder.save_npc_description("healer_npc_description", mock_llm_response)
    print(f"\nMock LLM response saved to: {file_path}")

if __name__ == "__main__":
    print("=== NPC Personality Decoder Test ===\n")
    
    test_basic_decoding()
    test_decoding_with_context()
    test_llm_integration()
    
    print("\n=== All tests completed ===")
