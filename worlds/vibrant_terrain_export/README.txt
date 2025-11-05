VIBRANT TERRAIN - COLOR ZONES WITH PHYSICS PROPERTIES
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
gazebo /home/vampiro/Desktop/vibrant_terrain_export/vibrant_terrain.world