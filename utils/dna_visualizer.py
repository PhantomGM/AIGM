#!/usr/bin/env python
"""
DNA Visualizer Utility

This utility provides visualization tools for the Advanced DNA system,
allowing users to explore trait evolution over time and visualize
the relationships between different traits.
"""

import sys
import os
import json
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Any, Tuple, Optional

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.dna_generator import WorldDNA, WorldDNAGenerator


def parse_advanced_dna(dna_string: str) -> Dict[str, Any]:
    """Parse advanced DNA string into its components."""
    result = {
        "version": "1.0",
        "traits": {},
        "thresholds": [],
        "evolution": {}
    }
    
    # Extract version
    if dna_string.startswith("V"):
        version_part = dna_string.split(" ")[0]
        result["version"] = version_part[1:]
    
    # Extract traits
    if "TRAITS{" in dna_string:
        traits_section = dna_string.split("TRAITS{")[1].split("}")[0]
        for trait_part in traits_section.split(";"):
            if ":" in trait_part:
                name, value = trait_part.split(":")
                prevalence = int(value[0]) if len(value) >= 1 and value[0].isdigit() else 5
                intensity = int(value[1]) if len(value) >= 2 and value[1].isdigit() else 3
                result["traits"][name] = {
                    "prevalence": prevalence,
                    "intensity": intensity
                }
    
    # Extract thresholds
    if "THRESH{" in dna_string:
        thresh_section = dna_string.split("THRESH{")[1].split("}")[0]
        result["thresholds"] = thresh_section.split(";")
    
    # Extract evolution
    if "EVO{" in dna_string:
        evo_section = dna_string.split("EVO{")[1].split("}")[0]
        for evo_part in evo_section.split(";"):
            if ":" in evo_part and "[" in evo_part and "]" in evo_part:
                trait, pattern_values = evo_part.split(":", 1)
                pattern = pattern_values.split("[")[0]
                values = pattern_values.split("[")[1].split("]")[0]
                values_list = values.split(",")
                
                # Parse prevalence and intensity for each time period
                evolution_data = []
                for value in values_list:
                    prevalence = int(value[0]) if len(value) >= 1 and value[0].isdigit() else 5
                    intensity = int(value[1]) if len(value) >= 2 and value[1].isdigit() else 3
                    evolution_data.append({
                        "prevalence": prevalence,
                        "intensity": intensity
                    })
                
                result["evolution"][trait] = {
                    "pattern": pattern,
                    "values": evolution_data
                }
    
    return result


def visualize_trait_evolution(parsed_dna: Dict[str, Any], 
                             trait_filter: Optional[List[str]] = None):
    """
    Visualize the evolution of traits over time.
    
    Args:
        parsed_dna: Parsed DNA dictionary
        trait_filter: Optional list of traits to include, if None shows all evolving traits
    """
    # Get evolution data
    evolution_data = parsed_dna.get("evolution", {})
    
    if not evolution_data:
        print("No evolution data found in DNA.")
        return
    
    # Filter traits if specified
    traits_to_show = list(evolution_data.keys())
    if trait_filter:
        traits_to_show = [t for t in traits_to_show if t in trait_filter]
    
    # Define time periods
    time_periods = ["PAST", "PRESENT", "NEAR FUTURE", "FAR FUTURE"]
    
    # Create figure
    plt.figure(figsize=(12, 8))
    
    # Plot prevalence evolution
    plt.subplot(2, 1, 1)
    for trait in traits_to_show:
        trait_data = evolution_data[trait]
        pattern = trait_data["pattern"]
        values = trait_data["values"]
        
        # Extract prevalence values for each time period
        prevalence_values = [v["prevalence"] for v in values]
        
        # Plot with trait name and pattern
        plt.plot(range(len(prevalence_values)), prevalence_values, marker='o', linewidth=2, 
                label=f"{trait} ({pattern})")
    
    plt.title("Trait Prevalence Evolution Over Time")
    plt.ylabel("Prevalence (1-9)")
    plt.xticks(range(len(time_periods)), time_periods)
    plt.ylim(0, 10)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    
    # Plot intensity evolution
    plt.subplot(2, 1, 2)
    for trait in traits_to_show:
        trait_data = evolution_data[trait]
        pattern = trait_data["pattern"]
        values = trait_data["values"]
        
        # Extract intensity values for each time period
        intensity_values = [v["intensity"] for v in values]
        
        # Plot with trait name and pattern
        plt.plot(range(len(intensity_values)), intensity_values, marker='o', linewidth=2, 
                label=f"{trait} ({pattern})")
    
    plt.title("Trait Intensity Evolution Over Time")
    plt.ylabel("Intensity (1-5)")
    plt.xticks(range(len(time_periods)), time_periods)
    plt.ylim(0, 6)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    
    plt.tight_layout()
    plt.show()


def visualize_trait_relationships(parsed_dna: Dict[str, Any]):
    """
    Visualize the relationships between traits as a network diagram.
    
    Args:
        parsed_dna: Parsed DNA dictionary
    """
    try:
        import networkx as nx
        from matplotlib.colors import LinearSegmentedColormap
    except ImportError:
        print("This visualization requires networkx. Install with: pip install networkx")
        return
    
    # Get traits and thresholds
    traits = parsed_dna.get("traits", {})
    thresholds = parsed_dna.get("thresholds", [])
    
    if not traits:
        print("No traits found in DNA.")
        return
    
    # Create graph
    G = nx.Graph()
    
    # Add trait nodes
    for trait, values in traits.items():
        # Create node attributes
        attr = {
            "prevalence": values["prevalence"],
            "intensity": values["intensity"],
            # Derive category from trait name (e.g., "magical.intensity" -> "magical")
            "category": trait.split(".")[0] if "." in trait else "unknown"
        }
        G.add_node(trait, **attr)
    
    # Create relationships based on thresholds and categories
    categories = set(nx.get_node_attributes(G, "category").values())
    
    # Connect nodes within the same category
    for category in categories:
        category_nodes = [n for n, d in G.nodes(data=True) if d.get("category") == category]
        for i in range(len(category_nodes)):
            for j in range(i+1, len(category_nodes)):
                G.add_edge(category_nodes[i], category_nodes[j], weight=0.5, type="category")
    
    # Create a custom colormap for categories
    category_colors = {}
    colors = plt.cm.tab10(np.linspace(0, 1, len(categories)))
    for i, category in enumerate(categories):
        category_colors[category] = colors[i]
    
    # Create position layout
    pos = nx.spring_layout(G, seed=42)
    
    # Draw the network
    plt.figure(figsize=(12, 10))
    
    # Draw nodes with category colors
    for category in categories:
        category_nodes = [n for n, d in G.nodes(data=True) if d.get("category") == category]
        nx.draw_networkx_nodes(
            G, pos, 
            nodelist=category_nodes,
            node_size=[G.nodes[n]["prevalence"] * 100 for n in category_nodes],
            node_color=[category_colors[category] for _ in category_nodes],
            alpha=0.8,
            label=category
        )
    
    # Draw edges
    nx.draw_networkx_edges(
        G, pos, 
        width=[G[u][v].get("weight", 0.5) for u, v in G.edges()],
        alpha=0.5
    )
    
    # Draw labels
    nx.draw_networkx_labels(
        G, pos, 
        font_size=8,
        font_family="sans-serif"
    )
    
    plt.legend(scatterpoints=1)
    plt.title("Trait Relationships Visualization")
    plt.axis("off")
    plt.tight_layout()
    plt.show()


def generate_and_visualize():
    """Generate a new DNA and visualize it."""
    generator = WorldDNAGenerator()
    
    # Generate DNA with some bias for interesting patterns
    bias = {
        "magical.intensity": (2, 1),
        "political.conflict": (1, 2)
    }
    
    dna_string = generator.generate_dna(bias)
    print(f"Generated DNA:\n{dna_string}\n")
    
    # Parse and visualize
    parsed_dna = parse_advanced_dna(dna_string)
    
    print("DNA Components:")
    print(f"Version: {parsed_dna['version']}")
    
    print("\nTraits:")
    for trait, values in parsed_dna["traits"].items():
        print(f"  {trait}: Prevalence={values['prevalence']}, Intensity={values['intensity']}")
    
    print("\nThresholds Met:")
    for threshold in parsed_dna["thresholds"]:
        print(f"  {threshold}")
    
    print("\nEvolution Patterns:")
    for trait, data in parsed_dna["evolution"].items():
        print(f"  {trait}: Pattern={data['pattern']}")
        for i, period_data in enumerate(data["values"]):
            period_name = ["PAST", "PRESENT", "NEAR", "FAR"][i if i < 4 else 3]
            print(f"    {period_name}: Prevalence={period_data['prevalence']}, "
                  f"Intensity={period_data['intensity']}")
    
    # Visualize trait evolution
    visualize_trait_evolution(parsed_dna)
    
    # Visualize trait relationships
    visualize_trait_relationships(parsed_dna)


def main():
    """Main function for the DNA Visualizer."""
    parser = argparse.ArgumentParser(description="DNA Visualizer for World DNA")
    parser.add_argument("--generate", action="store_true", help="Generate and visualize a new DNA")
    parser.add_argument("--file", type=str, help="JSON file containing DNA data to visualize")
    parser.add_argument("--dna", type=str, help="DNA string to parse and visualize")
    parser.add_argument("--traits", type=str, nargs="+", help="Specific traits to visualize")
    
    args = parser.parse_args()
    
    if args.generate:
        generate_and_visualize()
    elif args.file:
        try:
            with open(args.file, 'r') as f:
                data = json.load(f)
            
            dna_string = data.get("dna_string", "")
            if not dna_string:
                print(f"No DNA string found in {args.file}")
                return
            
            parsed_dna = parse_advanced_dna(dna_string)
            visualize_trait_evolution(parsed_dna, args.traits)
            visualize_trait_relationships(parsed_dna)
        except Exception as e:
            print(f"Error processing file: {e}")
    elif args.dna:
        parsed_dna = parse_advanced_dna(args.dna)
        visualize_trait_evolution(parsed_dna, args.traits)
        visualize_trait_relationships(parsed_dna)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
