import cv2
import numpy as np
import math

class TrackMapper:
    def __init__(self, image_path, map_width_cm, map_height_cm):
        # Load image in grayscale
        self.img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if self.img is None:
            raise ValueError("Could not find image")
        
        # Threshold to ensure binary (Black/White)
        _, self.img = cv2.threshold(self.img, 127, 255, cv2.THRESH_BINARY)
        
        self.height_px, self.width_px = self.img.shape
        self.width_cm = map_width_cm
        self.height_cm = map_height_cm
        
        # Calculate scale
        self.px_per_cm_x = self.width_px / self.width_cm
        self.px_per_cm_y = self.height_px / self.height_cm
        self.scale = (self.px_per_cm_x + self.px_per_cm_y) / 2.0
        
        print(f"Map resolution: {self.scale:.2f} pixels per cm")

    def get_track_center_on_slice(self, pos, direction_rad, search_width_px=100):
        cx, cy = pos
        perp_angle = direction_rad + (math.pi / 2)
        dx = math.cos(perp_angle)
        dy = math.sin(perp_angle)
        
        samples = []
        for r in range(-search_width_px, search_width_px):
            sx = int(cx + dx * r)
            sy = int(cy + dy * r)
            if 0 <= sx < self.width_px and 0 <= sy < self.height_px:
                val = self.img[sy, sx]
                samples.append((r, val))
        
        white_runs = []
        in_white = False
        start_r = 0
        
        for r, val in samples:
            if val > 200: # White
                if not in_white:
                    in_white = True
                    start_r = r
            else: # Black
                if in_white:
                    in_white = False
                    end_r = r - 1
                    center_r = (start_r + end_r) / 2.0
                    white_runs.append(center_r)
        
        if in_white:
             end_r = samples[-1][0]
             white_runs.append((start_r + end_r) / 2.0)

        if not white_runs:
            return None

        best_r = min(white_runs, key=lambda x: abs(x))
        new_cx = cx + dx * best_r
        new_cy = cy + dy * best_r
        return np.array([new_cx, new_cy])

    def generate_path(self, start_x_px, start_y_px, start_angle_deg, end_x_px, end_y_px, intersections_px=[]):
        curr_pos = np.array([float(start_x_px), float(start_y_px)])
        end_pos_px = np.array([float(end_x_px), float(end_y_px)])
        curr_angle = math.radians(start_angle_deg)
        
        step_size_cm = 0.5  
        step_size_px = step_size_cm * self.scale
        
        # Safety Mode Configuration
        safety_distance_cm = 10.0
        safety_steps_duration = int(safety_distance_cm / step_size_cm)
        max_turn_safety_deg = 5.0
        max_turn_safety_rad = math.radians(max_turn_safety_deg)
        
        trigger_radius_cm = 5.0
        trigger_radius_px = trigger_radius_cm * self.scale
        stop_radius_cm = 2.0 
        stop_radius_px = stop_radius_cm * self.scale

        path_pixels = [curr_pos]
        safety_timer = 0
        
        print("Starting trace...")
        
        for i in range(10000):
            # Check Distance to End Point
            dist_to_end = np.linalg.norm(curr_pos - end_pos_px)
            if dist_to_end < stop_radius_px:
                print(f"Reached End Position (within {stop_radius_cm}cm)!")
                break

            # Check Proximity to Manual Intersections
            dist_to_intersection = float('inf')
            if intersections_px:
                dists = [np.linalg.norm(curr_pos - np.array(p)) for p in intersections_px]
                dist_to_intersection = min(dists)

            if dist_to_intersection < trigger_radius_px:
                safety_timer = safety_steps_duration
            
            is_safety_mode = (safety_timer > 0)

            momentum_pos = curr_pos + np.array([math.cos(curr_angle), math.sin(curr_angle)]) * step_size_px
            sensor_target = self.get_track_center_on_slice(momentum_pos, curr_angle)
            
            next_pos = None
            next_angle = curr_angle

            if sensor_target is None:
                next_pos = momentum_pos
            else:
                move_vec = sensor_target - curr_pos
                target_angle = math.atan2(move_vec[1], move_vec[0])
                
                angle_diff = target_angle - curr_angle
                while angle_diff > math.pi: angle_diff -= 2*math.pi
                while angle_diff < -math.pi: angle_diff += 2*math.pi
                
                if is_safety_mode:
                    if angle_diff > max_turn_safety_rad:
                        angle_diff = max_turn_safety_rad
                    elif angle_diff < -max_turn_safety_rad:
                        angle_diff = -max_turn_safety_rad
                    
                    next_angle = curr_angle + angle_diff
                    next_pos = curr_pos + np.array([math.cos(next_angle), math.sin(next_angle)]) * step_size_px
                    safety_timer -= 1
                else:
                    next_pos = sensor_target
                    next_angle = target_angle

            curr_pos = next_pos
            curr_angle = next_angle
            
            if i > 50:
                dist_to_start = np.linalg.norm(curr_pos - path_pixels[0])
                if dist_to_start < step_size_px:
                    print("Loop closed!")
                    break
            
            path_pixels.append(curr_pos)

        return self.resample_path(path_pixels, target_spacing_cm=1.0)

    def resample_path(self, path_pixels, target_spacing_cm):
        spacing_px = target_spacing_cm * self.scale
        new_path_cm = []
        raw_points = np.array(path_pixels)
        if len(raw_points) == 0: return []
        
        current_point = raw_points[0]
        new_path_cm.append(current_point / self.scale)
        current_idx = 0
        
        while current_idx < len(raw_points) - 1:
            found_next = False
            temp_idx = current_idx
            while temp_idx < len(raw_points) - 1:
                dist_direct = np.linalg.norm(raw_points[temp_idx+1] - current_point)
                if dist_direct >= spacing_px:
                    v_to_target = raw_points[temp_idx+1] - current_point
                    norm = np.linalg.norm(v_to_target) or 1
                    next_point = current_point + (v_to_target / norm * spacing_px)
                    new_path_cm.append(next_point / self.scale)
                    current_point = next_point
                    current_idx = temp_idx 
                    found_next = True
                    break
                temp_idx += 1
            if not found_next: break
        return new_path_cm

    # =========================================================
    # NEW METHOD: Convert Absolute Map Coordinates to Robot Frame
    # =========================================================
    def convert_to_robot_frame(self, path_cm, start_x_cm, start_y_cm, start_angle_deg):
        """
        Transforms the path so that:
        1. Start position becomes (0, 0)
        2. Start direction becomes +X axis
        """
        robot_path = []
        
        # Start angle in radians
        theta = math.radians(start_angle_deg)
        
        # Precompute rotation matrix components for -theta
        # We rotate by negative theta to align global direction to local X axis
        cos_theta = math.cos(theta) 
        sin_theta = math.sin(theta)

        start_vec = np.array([start_x_cm, start_y_cm])

        for p in path_cm:
            # 1. Translation: Relative to start
            dx = p[0] - start_vec[0]
            dy = p[1] - start_vec[1]
            
            # 2. Rotation: Align start heading with X-axis
            # x' = x*cos(theta) + y*sin(theta)
            # y' = -x*sin(theta) + y*cos(theta)
            local_x = dx * cos_theta + dy * sin_theta
            local_y = -dx * sin_theta + dy * cos_theta
            
            robot_path.append(np.array([local_x, local_y]))
            
        return robot_path

    def save_to_file(self, path_cm, filename):
        with open(filename, "w") as f:
            for p in path_cm:
                f.write(f"{p[0]:.4f},{p[1]:.4f}\n")
        print(f"Saved {len(path_cm)} points to {filename}")

# ==========================================
# USAGE CONFIGURATION
# ==========================================

# 1. Map Dimensions (Keep these in CM to define scale)
REAL_WIDTH_CM = 829
REAL_HEIGHT_CM = 304

# 2. Start Position (NOW IN PIXELS)
START_X_PX = 1592  # Example pixel coordinate
START_Y_PX = 37  # Example pixel coordinate
START_ANGLE = 0 # 90 down, 0 right, 180 left, 270 up

# 3. End Position (NOW IN PIXELS)
END_X_PX = 1288    # Example pixel coordinate
END_Y_PX = 37      # Example pixel coordinate

# 4. MANUAL INTERSECTION LIST (NOW IN PIXELS)
INTERSECTIONS_PX = [
    (930, 270),
    (996, 270),
    (1063, 270),
    (1130, 270),
    (1197, 270),
]

image_file = "all-japan-2024.png" 
out_file = image_file.replace(".png", "_path.txt")
out_png = image_file.replace(".png", "_path_viz.png")

try:
    processor = TrackMapper(image_file, REAL_WIDTH_CM, REAL_HEIGHT_CM)
    
    # 1. Generate path in absolute coordinates (CM)
    absolute_path = processor.generate_path(
        START_X_PX, 
        START_Y_PX, 
        START_ANGLE, 
        END_X_PX, 
        END_Y_PX,
        INTERSECTIONS_PX
    )
    
    # 2. Convert to Robot Frame (0,0 is start, +X is forward)
    # Note: We need the start position in CM for the subtraction
    start_x_cm = START_X_PX / processor.scale
    start_y_cm = START_Y_PX / processor.scale
    
    robot_frame_path = processor.convert_to_robot_frame(
        absolute_path, 
        start_x_cm, 
        start_y_cm, 
        START_ANGLE
    )
    
    # 3. Save the ROBOT FRAME path to file
    processor.save_to_file(robot_frame_path, out_file)
    
    # Visualization (We still visualize on the map image using absolute pixels)
    viz_img = cv2.cvtColor(processor.img, cv2.COLOR_GRAY2BGR)
    
    for inter in INTERSECTIONS_PX:
        cv2.circle(viz_img, (int(inter[0]), int(inter[1])), int(5 * processor.scale), (0, 255, 255), 2) 
    
    cv2.circle(viz_img, (int(END_X_PX), int(END_Y_PX)), int(5 * processor.scale), (0, 255, 0), 2) 
    cv2.circle(viz_img, (int(START_X_PX), int(START_Y_PX)), int(5 * processor.scale), (255, 0, 0), 2)

    # Visualize the absolute path (to check alignment with map)
    for p in absolute_path:
        px = int(p[0] * processor.scale)
        py = int(p[1] * processor.scale)
        cv2.circle(viz_img, (px, py), 2, (0, 0, 255), -1)
    
    cv2.imwrite(out_png, viz_img)
    print("Debug image saved.")

except Exception as e:
    print(f"Error: {e}")