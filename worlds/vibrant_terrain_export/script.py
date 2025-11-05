import bpy
import math
import random
import bmesh
from mathutils import Vector, noise
import os

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a new collection for our terrain
terrain_collection = bpy.data.collections.new("VibrantTerrain")
bpy.context.scene.collection.children.link(terrain_collection)

def create_realistic_terrain(size=50, resolution=128):
    """Creates a simplified terrain using noise functions with size of 50x50"""
    # Create a plane with high resolution
    bpy.ops.mesh.primitive_grid_add(
        x_subdivisions=resolution,
        y_subdivisions=resolution,
        size=size,
        location=(0, 0, 0)
    )
    terrain = bpy.context.active_object
    terrain.name = "VibrantTerrain"
    
    # Add fewer noise layers for simplified terrain
    seed = random.randint(0, 1000)
    
    # Apply height displacement using noise with simpler features
    for v in terrain.data.vertices:
        # Normalize coordinates to 0-1 range
        nx = (v.co.x / size) + 0.5
        ny = (v.co.y / size) + 0.5
        
        # Layer 1: Large features (gentle hills) - reduced complexity
        large = noise.noise((nx * 1.5, ny * 1.5, seed * 0.1)) * 3.0
        
        # Layer 2: Medium features (small variations) - reduced complexity
        medium = noise.noise((nx * 3.0, ny * 3.0, seed * 0.2)) * 2.5
        
        # Combine just two layers for simpler terrain
        height = large + medium
        
        # Apply height
        v.co.z = height
    
    # Smooth terrain a bit
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.vertices_smooth(factor=0.12, repeat=1)  # Reduced smoothing for more dramatic terrain
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Add obstacle hills
    add_obstacle_hills(terrain, size, 5)  # Added fewer obstacles - 4 major hills
    
    # Apply subsurface modifier for more smoothness
    subsurface = terrain.modifiers.new(name="Subsurface", type='SUBSURF')
    subsurface.levels = 1
    subsurface.render_levels = 2
    bpy.ops.object.modifier_apply(modifier=subsurface.name)
    
    # Add to collection
    bpy.ops.object.select_all(action='DESELECT')
    terrain.select_set(True)
    bpy.ops.object.move_to_collection(collection_index=bpy.data.collections.find(terrain_collection.name))
    
    return terrain

def add_obstacle_hills(terrain, size, num_hills=4):
    """Adds fewer, simpler hills to serve as obstacles"""
    # Select the terrain
    bpy.context.view_layer.objects.active = terrain
    terrain.select_set(True)
    
    # Parameters for obstacle hills - simpler and fewer
    min_radius = size * 0.08
    max_radius = size * 0.15
    min_height = 1.0  # More consistent height
    max_height = 8.0  # Lower maximum height
    
    # Create hills at semi-random positions
    for i in range(num_hills):
        # Pick a position that's not too close to the center or edges
        distance_from_center = random.uniform(size * 0.2, size * 0.4)
        angle = random.uniform(0, 2 * math.pi)
        
        x = distance_from_center * math.cos(angle)
        y = distance_from_center * math.sin(angle)
        radius = random.uniform(min_radius, max_radius)
        height = random.uniform(min_height, max_height)
        
        # Apply a displacement at this position
        for v in terrain.data.vertices:
            # Calculate distance from hill center
            dist = math.sqrt((v.co.x - x)**2 + (v.co.y - y)**2)
            
            # If within radius, apply height modification with falloff
            if dist < radius:
                # Smoother falloff curve
                falloff = 1 - (dist / radius) ** 2
                # Add height
                v.co.z += height * falloff
    
    return terrain

def create_vibrant_zone_materials():
    """Creates more vibrant materials for each physics zone"""
    materials = {}
    
    # Base material (grass/soil) - more vibrant green
    base_mat = bpy.data.materials.new(name="Terrain_Base")
    base_mat.use_nodes = True
    principled_bsdf = base_mat.node_tree.nodes.get('Principled BSDF')
    if principled_bsdf:
        principled_bsdf.inputs[0].default_value = (0.1, 0.5, 0.15, 1.0)  # Vibrant green
        principled_bsdf.inputs[7].default_value = 0.7  # Roughness
    materials["base"] = base_mat
    
    # Red Zone (High Friction) - Vibrant red
    red_mat = bpy.data.materials.new(name="RedZone_Material")
    red_mat.use_nodes = True
    principled_bsdf = red_mat.node_tree.nodes.get('Principled BSDF')
    if principled_bsdf:
        principled_bsdf.inputs[0].default_value = (0.9, 0.1, 0.1, 1.0)  # Vibrant red
        principled_bsdf.inputs[7].default_value = 0.8  # High roughness
    materials["red"] = red_mat
    
    # Blue Zone (Low Friction) - Vibrant blue
    blue_mat = bpy.data.materials.new(name="BlueZone_Material")
    blue_mat.use_nodes = True
    principled_bsdf = blue_mat.node_tree.nodes.get('Principled BSDF')
    if principled_bsdf:
        principled_bsdf.inputs[0].default_value = (0.1, 0.3, 0.9, 1.0)  # Vibrant blue
        principled_bsdf.inputs[7].default_value = 0.2  # Low roughness
    materials["blue"] = blue_mat
    
    # Yellow Zone (Bouncy) - Vibrant yellow
    yellow_mat = bpy.data.materials.new(name="YellowZone_Material")
    yellow_mat.use_nodes = True
    principled_bsdf = yellow_mat.node_tree.nodes.get('Principled BSDF')
    if principled_bsdf:
        principled_bsdf.inputs[0].default_value = (0.95, 0.8, 0.1, 1.0)  # Vibrant yellow
        principled_bsdf.inputs[7].default_value = 0.6  # Medium roughness
    materials["yellow"] = yellow_mat
    
    # Green Zone (High Damping) - Vibrant green
    green_mat = bpy.data.materials.new(name="GreenZone_Material")
    green_mat.use_nodes = True
    principled_bsdf = green_mat.node_tree.nodes.get('Principled BSDF')
    if principled_bsdf:
        principled_bsdf.inputs[0].default_value = (0.1, 0.8, 0.1, 1.0)  # Vibrant green
        principled_bsdf.inputs[7].default_value = 0.5  # Medium roughness
    materials["green"] = green_mat
    
    return materials

def distribute_zones_organically(terrain, materials):
    """Distributes physics zones across the terrain in larger, more prominent patterns"""
    # Add all materials to the terrain
    for mat in materials.values():
        terrain.data.materials.append(mat)
    
    # Get terrain dimensions
    min_x = min(v.co.x for v in terrain.data.vertices)
    max_x = max(v.co.x for v in terrain.data.vertices)
    min_y = min(v.co.y for v in terrain.data.vertices)
    max_y = max(v.co.y for v in terrain.data.vertices)
    
    terrain_size = max(max_x - min_x, max_y - min_y)
    
    # Generate random "seed points" for each zone type - with larger zones and GUARANTEED placement
    # Increased number of seed points for all color zones to ensure they're created
    num_seeds = {
        "red": 6,   # Increased from 4 to 6
        "blue": 6,  # Increased from 4 to 6
        "yellow": 6,  # Increased from 4 to 6
        "green": 6   # Increased from 4 to 6
    }
    
    seed_points = {}
    
    # Define specific quadrants to ensure zones are distributed across the terrain
    quadrants = [
        (min_x, (min_x + max_x) / 2, min_y, (min_y + max_y) / 2),  # Bottom-left
        ((min_x + max_x) / 2, max_x, min_y, (min_y + max_y) / 2),  # Bottom-right
        (min_x, (min_x + max_x) / 2, (min_y + max_y) / 2, max_y),  # Top-left
        ((min_x + max_x) / 2, max_x, (min_y + max_y) / 2, max_y)   # Top-right
    ]
    
    # Ensure each type of zone gets at least one seed in each quadrant
    for zone_type, count in num_seeds.items():
        seed_points[zone_type] = []
        
        # First place one seed in each quadrant to ensure distribution
        for q_min_x, q_max_x, q_min_y, q_max_y in quadrants:
            if zone_type in ["blue", "yellow", "red", "green"]:  # Make all color zones larger and strategically placed
                x = (q_min_x + q_max_x) / 2
                y = (q_min_y + q_max_y) / 2
                
                # Position each zone in a different part of the quadrant to prevent overlap
                if zone_type == "blue":
                    x -= terrain_size * 0.1
                    y -= terrain_size * 0.1
                elif zone_type == "yellow":
                    x += terrain_size * 0.1
                    y -= terrain_size * 0.1
                elif zone_type == "red":
                    x -= terrain_size * 0.1
                    y += terrain_size * 0.1
                elif zone_type == "green":
                    x += terrain_size * 0.1
                    y += terrain_size * 0.1
                
                # Make zones notably larger to ensure they're visible
                size = terrain_size * 0.25
            else:
                x = random.uniform(q_min_x, q_max_x)
                y = random.uniform(q_min_y, q_max_y)
                size = random.uniform(terrain_size * 0.15, terrain_size * 0.25)
                
            seed_points[zone_type].append((x, y, size))
        
        # Add any additional seeds randomly (if num_seeds > 4)
        for _ in range(count - len(quadrants)):
            if count > len(quadrants):
                x = random.uniform(min_x, max_x)
                y = random.uniform(min_y, max_y)
                
                if zone_type in ["blue", "yellow", "red", "green"]:  # Make all color zones larger
                    size = terrain_size * 0.25
                    
                    # Position each zone type in different locations to prevent overlap
                    if zone_type == "blue":
                        x -= terrain_size * 0.1
                        y -= terrain_size * 0.1
                    elif zone_type == "yellow":
                        x += terrain_size * 0.1
                        y -= terrain_size * 0.1
                    elif zone_type == "red":
                        x -= terrain_size * 0.1
                        y += terrain_size * 0.1
                    elif zone_type == "green":
                        x += terrain_size * 0.1
                        y += terrain_size * 0.1
                else:
                    size = random.uniform(terrain_size * 0.15, terrain_size * 0.25)
                    
                seed_points[zone_type].append((x, y, size))
    
    # Debug print to check seed points
    print(f"Created {len(seed_points['blue'])} blue zone seed points")
    print(f"Created {len(seed_points['yellow'])} yellow zone seed points")
    print(f"Created {len(seed_points['red'])} red zone seed points")
    print(f"Created {len(seed_points['green'])} green zone seed points")
    
    # Define start and end points (without a path)
    start_pos = (min_x + terrain_size * 0.2, min_y + terrain_size * 0.2)
    end_pos = (max_x - terrain_size * 0.2, max_y - terrain_size * 0.2)
    
    # Counter to track assigned faces for each material
    material_counts = {zone_type: 0 for zone_type in seed_points.keys()}
    material_counts["base"] = 0
    
    # Assign materials based on organic distribution with sharper zone boundaries
    for poly in terrain.data.polygons:
        # Calculate polygon center
        center = Vector((0, 0, 0))
        for vert_idx in poly.vertices:
            center += terrain.data.vertices[vert_idx].co
        center /= len(poly.vertices)
        
        # Check distance to each zone's seed points
        min_distances = {zone_type: float('inf') for zone_type in seed_points.keys()}
        
        for zone_type, points in seed_points.items():
            for point in points:
                x, y, size = point
                dist = math.sqrt((center.x - x)**2 + (center.y - y)**2)
                # Use a falloff function: distance / size
                falloff_dist = dist / size
                min_distances[zone_type] = min(min_distances[zone_type], falloff_dist)
        
        # Determine material based on distances with less noise for more defined zones
        # Add less noise for sharper zone boundaries
        noise_val = noise.noise((center.x * 0.01, center.y * 0.01, 0)) * 0.3  # Reduced noise effect
        
        # Adjust distances with less noise
        for zone_type in min_distances:
            min_distances[zone_type] += noise_val
        
        # Bias toward all color zones to ensure they appear
        min_distances["blue"] *= 0.8  # Give blue a 20% advantage in distance calculation
        min_distances["yellow"] *= 0.8  # Give yellow a 20% advantage in distance calculation
        min_distances["red"] *= 0.8  # Give red a 20% advantage in distance calculation
        min_distances["green"] *= 0.8  # Give green a 20% advantage in distance calculation
        
        # Find the closest zone type
        closest_zone = min(min_distances, key=min_distances.get)
        
        # Only apply special material if within influence radius - larger radius for more prominent zones
        if min_distances[closest_zone] < 1.3:  # Increased radius for larger zones
            poly.material_index = list(materials.values()).index(materials[closest_zone])
            material_counts[closest_zone] += 1
        else:
            # Default to base material
            poly.material_index = list(materials.values()).index(materials["base"])
            material_counts["base"] += 1
    
    # Debug print material assignments
    for zone_type, count in material_counts.items():
        print(f"{zone_type} zone: {count} polygons assigned")
    
    # Create vertex groups for physics properties in simulation engines
    for zone_type in ["red", "blue", "yellow", "green"]:
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Select vertices of faces with this material
        for poly in terrain.data.polygons:
            if poly.material_index == list(materials.values()).index(materials[zone_type]):
                for vert_idx in poly.vertices:
                    terrain.data.vertices[vert_idx].select = True
        
        # Create vertex group
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.object.vertex_group_add()
        vertex_group = terrain.vertex_groups[-1]
        vertex_group.name = f"{zone_type.capitalize()}Zone"
        bpy.ops.object.vertex_group_assign()
        bpy.ops.object.mode_set(mode='OBJECT')
    
    # If no blue, yellow, red, or green zones were assigned, force create them
    for zone_type in ["blue", "yellow", "red", "green"]:
        if material_counts[zone_type] == 0:
            print(f"No {zone_type} zones were created automatically. Forcing {zone_type} zone creation...")
            
            # Force create a zone
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')
            
            # Position differently based on zone type
            quadrant_offset = terrain_size * 0.2
            if zone_type == "blue":
                center_x = (min_x + max_x) / 2 - quadrant_offset
                center_y = (min_y + max_y) / 2 - quadrant_offset
            elif zone_type == "yellow":  
                center_x = (min_x + max_x) / 2 + quadrant_offset
                center_y = (min_y + max_y) / 2 - quadrant_offset
            elif zone_type == "red":
                center_x = (min_x + max_x) / 2 - quadrant_offset
                center_y = (min_y + max_y) / 2 + quadrant_offset
            else:  # green
                center_x = (min_x + max_x) / 2 + quadrant_offset
                center_y = (min_y + max_y) / 2 + quadrant_offset
                
            radius = terrain_size * 0.2
            
            # Select faces near the specified location
            for poly in terrain.data.polygons:
                # Calculate polygon center
                poly_center = Vector((0, 0, 0))
                for vert_idx in poly.vertices:
                    poly_center += terrain.data.vertices[vert_idx].co
                poly_center /= len(poly.vertices)
                
                # If within radius, assign the material
                dist = math.sqrt((poly_center.x - center_x)**2 + (poly_center.y - center_y)**2)
                if dist < radius:
                    poly.material_index = list(materials.values()).index(materials[zone_type])
                    for vert_idx in poly.vertices:
                        terrain.data.vertices[vert_idx].select = True
            
            # Create vertex group
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.object.vertex_group_add()
            new_group = terrain.vertex_groups[-1]
            new_group.name = f"{zone_type.capitalize()}Zone"
            bpy.ops.object.vertex_group_assign()
            bpy.ops.object.mode_set(mode='OBJECT')
            
            print(f"Forced {zone_type} zone created at ({center_x}, {center_y})")
            
            # Reset selection for next zone if needed
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')
    
    return terrain, start_pos, end_pos

def separate_by_material():
    """Separates the terrain into different objects based on material using Blender's built-in selection tools"""
    # Make sure we're in object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Get the terrain object
    terrain = bpy.context.active_object
    
    # Create individual objects for each color zone
    color_zones = ["red", "blue", "yellow", "green"]
    material_names = {
        "red": "RedZone_Material", 
        "blue": "BlueZone_Material", 
        "yellow": "YellowZone_Material", 
        "green": "GreenZone_Material"
    }
    
    # Make a duplicate of terrain to work with
    bpy.ops.object.duplicate()
    working_terrain = bpy.context.active_object
    
    # Create a separate object for each material
    separated_objects = []
    
    for zone_type in color_zones:
        material_name = material_names[zone_type]
        print(f"Creating separate object for {zone_type} zone...")
        
        # Select the working terrain
        bpy.ops.object.select_all(action='DESELECT')
        working_terrain.select_set(True)
        bpy.context.view_layer.objects.active = working_terrain
        
        # Find the material index
        material_index = -1
        for i, mat in enumerate(working_terrain.data.materials):
            if mat and mat.name == material_name:
                material_index = i
                break
        
        # If the material exists, select all faces with that material
        if material_index >= 0:
            print(f"Found {material_name} at index {material_index}")
            
            # Enter edit mode
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            
            # Set selection mode to faces
            bpy.ops.mesh.select_mode(type="FACE")
            
            # Select by material - this uses Blender's built-in selection functionality
            bpy.context.object.active_material_index = material_index
            bpy.ops.object.material_slot_select()
            
            # Check if we have any selected faces
            # We need to enter object mode briefly to get an accurate count
            bpy.ops.object.mode_set(mode='OBJECT')
            selected_count = sum(1 for p in working_terrain.data.polygons if p.select)
            bpy.ops.object.mode_set(mode='EDIT')
            
            print(f"Selected {selected_count} faces with {material_name}")
            
            # If we have selected faces, separate them
            if selected_count > 0:
                # Separate the selected faces
                bpy.ops.mesh.separate(type='SELECTED')
                bpy.ops.object.mode_set(mode='OBJECT')
                
                # Find the newly created object
                new_obj = None
                for obj in bpy.context.selected_objects:
                    if obj != working_terrain:
                        new_obj = obj
                        break
                
                if new_obj:
                    new_obj.name = f"terrain_{zone_type}"
                    separated_objects.append(new_obj)
                    print(f"Created {new_obj.name} with {len(new_obj.data.polygons)} polygons")
                else:
                    print(f"Failed to create separate object for {zone_type}")
            else:
                print(f"No faces selected for {material_name}")
                bpy.ops.object.mode_set(mode='OBJECT')
                
                # Create a placeholder object instead
                bpy.ops.mesh.primitive_plane_add(
                    size=10, 
                    location=(-10 if zone_type == "red" or zone_type == "blue" else 10, 
                              10 if zone_type == "red" or zone_type == "green" else -10, 
                              0)
                )
                placeholder = bpy.context.active_object
                placeholder.name = f"terrain_{zone_type}"
                
                # Assign the material
                if material_name in bpy.data.materials:
                    placeholder.data.materials.append(bpy.data.materials[material_name])
                
                separated_objects.append(placeholder)
                print(f"Created placeholder for {zone_type}")
        else:
            print(f"Material {material_name} not found!")
            bpy.ops.object.mode_set(mode='OBJECT')
            
            # Create a placeholder
            bpy.ops.mesh.primitive_plane_add(
                size=10, 
                location=(-10 if zone_type == "red" or zone_type == "blue" else 10, 
                          10 if zone_type == "red" or zone_type == "green" else -10, 
                          0)
            )
            placeholder = bpy.context.active_object
            placeholder.name = f"terrain_{zone_type}"
            
            # Create and assign the material
            mat = bpy.data.materials.new(name=material_name)
            mat.use_nodes = True
            principled_bsdf = mat.node_tree.nodes.get('Principled BSDF')
            if principled_bsdf:
                if zone_type == "red":
                    color = (0.9, 0.1, 0.1, 1.0)
                elif zone_type == "blue":
                    color = (0.1, 0.3, 0.9, 1.0)
                elif zone_type == "yellow":
                    color = (0.95, 0.8, 0.1, 1.0)
                else:  # green
                    color = (0.1, 0.8, 0.1, 1.0)
                principled_bsdf.inputs[0].default_value = color
            
            placeholder.data.materials.append(mat)
            separated_objects.append(placeholder)
            print(f"Created placeholder with new material for {zone_type}")
    
    # Also create the base terrain if needed
    bpy.ops.object.select_all(action='DESELECT')
    working_terrain.select_set(True)
    bpy.context.view_layer.objects.active = working_terrain
    working_terrain.name = "terrain_base"
    separated_objects.append(working_terrain)
    
    # Print all created objects
    print("Created separated objects:")
    for obj in separated_objects:
        print(f"- {obj.name} with {len(obj.data.polygons)} polygons")
    
    return separated_objects

def export_separated_objects(objects):
    """Exports each separated object as a DAE file with physics properties"""
    # Create export directory
    export_dir = "/home/vampiro/Desktop/vibrant_terrain_export"
    os.makedirs(export_dir, exist_ok=True)
    
    # Export each object
    exported_files = {}
    for obj in objects:
        # Select only this object
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        
        # Export as DAE
        export_path = os.path.join(export_dir, f"{obj.name}.dae")
        try:
            bpy.ops.wm.collada_export(
                filepath=export_path,
                apply_modifiers=True,
                selected=True
            )
            exported_files[obj.name] = export_path
            print(f"Exported {obj.name} to {export_path}")
        except Exception as e:
            print(f"Error exporting {obj.name}: {e}")
            # Try exporting as STL if DAE fails
            stl_path = os.path.join(export_dir, f"{obj.name}.stl")
            try:
                bpy.ops.export_mesh.stl(
                    filepath=stl_path,
                    use_selection=True
                )
                exported_files[obj.name] = stl_path
                print(f"Exported {obj.name} to {stl_path} (STL fallback)")
            except Exception as e2:
                print(f"Error exporting STL: {e2}")
    
    # Physics properties for different zones based on the terrain properties (friction only)
    physics_properties = {
        "terrain_green": {  # Good traversability
            "friction": {
                "mu": 80.0,  # High friction based on mu=0.8
                "mu2": 70.0,  # High secondary friction based on mu2=0.7
                "fdir1": "1 0 0",
                "slip1": 0.05,  # Low slip as specified (0.05)
                "slip2": 0.05   # Low slip as specified (0.05)
            }
        },
        "terrain_blue": {  # Water/hazard - very poor traversability
            "friction": {
                "mu": 10.0,   # Very low friction based on mu=0.1
                "mu2": 10.0,  # Very low secondary friction based on mu2=0.1
                "fdir1": "1 0 0",
                "slip1": 0.9,  # High slip as specified (0.9)
                "slip2": 0.9   # High slip as specified (0.9)
            }
        },
        "terrain_red": {  # Rough terrain - moderate traversability
            "friction": {
                "mu": 120.0,  # Very high friction based on mu=1.2
                "mu2": 100.0, # High secondary friction based on mu2=1.0
                "fdir1": "1 0 0",
                "slip1": 0.01,  # Very low slip as specified (0.01)
                "slip2": 0.01   # Very low slip as specified (0.01)
            }
        },
        "terrain_yellow": {  # Sandy - moderate-good traversability
            "friction": {
                "mu": 50.0,  # Medium friction based on mu=0.5
                "mu2": 40.0, # Medium secondary friction based on mu2=0.4
                "fdir1": "1 0 0",
                "slip1": 0.3,  # Medium slip as specified (0.3)
                "slip2": 0.3   # Medium slip as specified (0.3)
            }
        },
        "terrain_base": {  # Unknown terrain - defaults to similar properties as green
            "friction": {
                "mu": 80.0,  # Good friction like the green terrain
                "mu2": 70.0, # Good secondary friction
                "fdir1": "1 0 0",
                "slip1": 0.05,  # Low slip like the green terrain
                "slip2": 0.05   # Low slip
            }
        }
    }
    
    # Create a Gazebo world file with physics properties for each zone
    world_content = """<?xml version="1.0" ?>
<sdf version="1.5">
  <world name="vibrant_terrain_world">
    <!-- Include the sun with default values -->
    <light type="directional" name="sun">
      <cast_shadows>true</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.8 0.8 0.8 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <direction>-0.5 0.1 -0.9</direction>
    </light>

    <!-- Ambient light -->
    <scene>
      <ambient>0.4 0.4 0.4 1</ambient>
      <background>0.7 0.7 0.7 1</background>
      <shadows>true</shadows>
    </scene>

    <!-- Sky appearance -->
    <sky>
      <clouds>
        <speed>12</speed>
      </clouds>
    </sky>
"""
    
    # Add each zone to the world with proper physics properties
    # IMPORTANT: Make sure all zones are included, especially terrain_red
    required_zones = ["terrain_red", "terrain_blue", "terrain_yellow", "terrain_green", "terrain_base"]
    
    # First add all exported files
    for obj_name, file_path in exported_files.items():
        file_extension = os.path.splitext(file_path)[1].lower()
        geometry_type = "mesh" if file_extension == ".dae" else "mesh"
        
        # Get physics properties for this terrain type
        physics = physics_properties.get(obj_name, physics_properties["terrain_base"])
        
        world_content += f"""
    <!-- {obj_name} -->
    <model name="{obj_name}">
      <static>true</static>
      <pose>0 0 0 0 0 0</pose>
      <link name="{obj_name}_link">
        <collision name="collision">
          <geometry>
            <{geometry_type}>
              <uri>file://{os.path.abspath(file_path)}</uri>
            </{geometry_type}>
          </geometry>
          <surface>
            <friction>
              <ode>
                <mu>{physics["friction"]["mu"]}</mu>
                <mu2>{physics["friction"]["mu2"]}</mu2>
                <fdir1>{physics["friction"]["fdir1"]}</fdir1>
                <slip1>{physics["friction"]["slip1"]}</slip1>
                <slip2>{physics["friction"]["slip2"]}</slip2>
              </ode>
            </friction>
          </surface>
        </collision>
        <visual name="visual">
          <geometry>
            <{geometry_type}>
              <uri>file://{os.path.abspath(file_path)}</uri>
            </{geometry_type}>
          </geometry>
          <material>
            <script>
              <uri>file://media/materials/scripts/gazebo.material</uri>
              <name>Gazebo/{obj_name.split('_')[-1].capitalize()}</name>
            </script>
          </material>
        </visual>
      </link>
    </model>
"""
    
    # Check for missing required zones and add them if they're not in exported_files
    for zone_name in required_zones:
        if zone_name not in exported_files:
            print(f"WARNING: {zone_name} not found in exported files! Creating placeholder in world file.")
            
            # Create a placeholder entry with a simple plane mesh
            physics = physics_properties.get(zone_name, physics_properties["terrain_base"])
            
            # Determine position based on zone type
            position = "0 0 0"
            if zone_name == "terrain_red":
                position = "-10 10 0"
            elif zone_name == "terrain_blue":
                position = "-10 -10 0"
            elif zone_name == "terrain_yellow":
                position = "10 -10 0"
            elif zone_name == "terrain_green":
                position = "10 10 0"
            
            world_content += f"""
    <!-- {zone_name} (PLACEHOLDER) -->
    <model name="{zone_name}">
      <static>true</static>
      <pose>{position} 0 0 0</pose>
      <link name="{zone_name}_link">
        <collision name="collision">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>10 10</size>
            </plane>
          </geometry>
          <surface>
            <friction>
              <ode>
                <mu>{physics["friction"]["mu"]}</mu>
                <mu2>{physics["friction"]["mu2"]}</mu2>
                <fdir1>{physics["friction"]["fdir1"]}</fdir1>
                <slip1>{physics["friction"]["slip1"]}</slip1>
                <slip2>{physics["friction"]["slip2"]}</slip2>
              </ode>
            </friction>
          </surface>
        </collision>
        <visual name="visual">
          <geometry>
            <plane>
              <normal>0 0 1</normal>
              <size>10 10</size>
            </plane>
          </geometry>
          <material>
            <script>
              <uri>file://media/materials/scripts/gazebo.material</uri>
              <name>Gazebo/{zone_name.split('_')[-1].capitalize()}</name>
            </script>
          </material>
        </visual>
      </link>
    </model>
"""
    
    world_content += """
  </world>
</sdf>"""
    
    # Write the world file
    world_file_path = os.path.join(export_dir, "vibrant_terrain.world")
    with open(world_file_path, 'w') as f:
        f.write(world_content)
    
    print(f"Created Gazebo world file with physics properties at {world_file_path}")
    
    # Create a README file with detailed physics properties
    readme_content = """VIBRANT TERRAIN - COLOR ZONES WITH PHYSICS PROPERTIES
================================================

This terrain is divided into different colored zones, each with unique physics properties:

- terrain_red: High friction zone
  * High friction (mu=120.0, mu2=100.0)
  * Very low slip (slip1=0.01, slip2=0.01)
  * Simulates rough terrain with good grip

- terrain_blue: Low friction zone (slippery)
  * Very low friction (mu=10.0, mu2=10.0)
  * High slip (slip1=0.9, slip2=0.9)
  * Simulates ice or slippery surface

- terrain_yellow: Medium friction
  * Moderate friction (mu=50.0, mu2=40.0)
  * Medium slip (slip1=0.3, slip2=0.3)
  * Simulates sandy or loose surface

- terrain_green: Good traversability
  * High friction (mu=80.0, mu2=70.0)
  * Low slip (slip1=0.05, slip2=0.05)
  * Simulates solid, vegetated ground with good traction

- terrain_base: Regular ground
  * Similar to green terrain (mu=80.0, mu2=70.0) 
  * Low slip (slip1=0.05, slip2=0.05)
  * Default terrain with good traversability

The world file includes a sun with default parameters and standard ambient lighting.

To use in Gazebo, run:
gazebo """ + os.path.join(export_dir, "vibrant_terrain.world")
    
    readme_path = os.path.join(export_dir, "README.txt")
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    print(f"Created detailed README at {readme_path}")
    
    return export_dir

# Main execution
print("Creating simplified terrain with vibrant color zones (50x50 size)...")
terrain = create_realistic_terrain(size=50, resolution=128)

print("Creating vibrant zone materials...")
materials = create_vibrant_zone_materials()

print("Distributing color zones using organic patterns...")
terrain, start_pos, end_pos = distribute_zones_organically(terrain, materials)

print("Separating terrain by material...")
separated_objects = separate_by_material()

print("Exporting separated objects and creating Gazebo world file with physics properties...")
export_dir = export_separated_objects(separated_objects)

print(f"\nAll files exported to: {export_dir}")
print("Terrain processing and export complete!")
