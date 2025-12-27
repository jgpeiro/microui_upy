"""
Demo 5: Home Assistant Interface
Comprehensive home automation control and monitoring interface
Features: Multi-screen navigation, device control, monitoring, logs, network map
Screen Size: 320x240 with two-level navigation bars
"""
from microui import *
import math

# UI state for Demo 5
ui_state = {
    # Navigation
    'current_screen': 'dashboard',  # dashboard, climate, lighting, security, energy, calendar, network, logs
    'previous_screen': 'dashboard',
    
    # Dashboard data
    'home_mode': 'Home',  # Home, Away, Night, Vacation
    'temperature': 22.5,
    'humidity': 45,
    'outdoor_temp': 18.0,
    'lights_on': 7,
    'total_lights': 15,
    'doors_locked': True,
    'windows_open': 2,
    'alarm_armed': False,
    'power_usage': 2.4,  # kW
    
    # Climate control
    'climate_zones': {
        'Living Room': {'temp': 22.5, 'target': 22.0, 'humidity': 45, 'mode': 'Auto'},
        'Bedroom': {'temp': 20.0, 'target': 19.0, 'humidity': 50, 'mode': 'Cool'},
        'Kitchen': {'temp': 23.0, 'target': 22.0, 'humidity': 55, 'mode': 'Off'},
        'Bathroom': {'temp': 21.5, 'target': 21.0, 'humidity': 60, 'mode': 'Heat'},
    },
    'hvac_power': True,
    
    # Lighting control
    'lights': {
        'Living Room': {'on': True, 'brightness': 80, 'color_temp': 3000},
        'Bedroom': {'on': False, 'brightness': 0, 'color_temp': 2700},
        'Kitchen': {'on': True, 'brightness': 100, 'color_temp': 4000},
        'Bathroom': {'on': True, 'brightness': 60, 'color_temp': 3500},
        'Hallway': {'on': True, 'brightness': 40, 'color_temp': 3000},
        'Garage': {'on': False, 'brightness': 0, 'color_temp': 5000},
        'Garden': {'on': True, 'brightness': 70, 'color_temp': 3000},
        'Office': {'on': True, 'brightness': 90, 'color_temp': 4500},
    },
    
    # Security
    'cameras': {
        'Front Door': {'status': 'Online', 'motion': False, 'recording': True},
        'Back Yard': {'status': 'Online', 'motion': True, 'recording': True},
        'Garage': {'status': 'Online', 'motion': False, 'recording': False},
        'Living Room': {'status': 'Offline', 'motion': False, 'recording': False},
    },
    'sensors': {
        'Front Door': {'type': 'Door', 'state': 'Closed', 'battery': 85},
        'Back Door': {'type': 'Door', 'state': 'Closed', 'battery': 92},
        'Window LR': {'type': 'Window', 'state': 'Open', 'battery': 78},
        'Window BR': {'type': 'Window', 'state': 'Open', 'battery': 88},
        'Motion Hall': {'type': 'Motion', 'state': 'Clear', 'battery': 95},
    },
    
    # Energy monitoring
    'energy_history': [2.1, 2.3, 2.2, 2.5, 2.4, 2.6, 2.4, 2.3, 2.5, 2.4],
    'device_power': {
        'HVAC': 1.2,
        'Refrigerator': 0.3,
        'Lights': 0.4,
        'Computer': 0.2,
        'TV': 0.15,
        'Other': 0.15,
    },
    'solar_production': 0.8,  # kW
    'grid_import': 1.6,  # kW
    
    # Calendar/Schedule
    'events': [
        {'time': '08:00', 'title': 'Wake Up Routine', 'type': 'automation'},
        {'time': '09:30', 'title': 'Cleaning Service', 'type': 'event'},
        {'time': '14:00', 'title': 'Package Delivery', 'type': 'event'},
        {'time': '18:30', 'title': 'Dinner Mode', 'type': 'automation'},
        {'time': '22:00', 'title': 'Night Mode', 'type': 'automation'},
    ],
    'automations_enabled': True,
    
    # Network devices
    'network_devices': {
        'Router': {'status': 'Online', 'ip': '192.168.1.1', 'signal': 100},
        'Hub Main': {'status': 'Online', 'ip': '192.168.1.10', 'signal': 95},
        'Hub Garage': {'status': 'Online', 'ip': '192.168.1.11', 'signal': 88},
        'Thermostat': {'status': 'Online', 'ip': '192.168.1.20', 'signal': 92},
        'Camera 1': {'status': 'Online', 'ip': '192.168.1.30', 'signal': 85},
        'Camera 2': {'status': 'Online', 'ip': '192.168.1.31', 'signal': 78},
        'Light Bridge': {'status': 'Online', 'ip': '192.168.1.40', 'signal': 90},
        'Smart Plug 1': {'status': 'Online', 'ip': '192.168.1.50', 'signal': 82},
    },
    
    # System logs
    'system_logs': [
        {'time': '14:35', 'type': 'INFO', 'msg': 'Motion detected: Back Yard'},
        {'time': '14:12', 'type': 'WARN', 'msg': 'Camera 4: Offline'},
        {'time': '13:45', 'type': 'INFO', 'msg': 'Light turned on: Garden'},
        {'time': '13:20', 'type': 'INFO', 'msg': 'Temperature adjusted: Living'},
        {'time': '12:58', 'type': 'INFO', 'msg': 'Door opened: Front Door'},
        {'time': '12:30', 'type': 'ERROR', 'msg': 'Hub Garage: Connection lost'},
        {'time': '12:29', 'type': 'INFO', 'msg': 'Hub Garage: Reconnected'},
        {'time': '11:15', 'type': 'INFO', 'msg': 'Automation executed: Morning'},
    ],
    
    # Animation/update counter
    'frame': 0,
}


def update_ui(ctx):
    """Demo 5: Home Assistant Main UI"""
    
    ui_state['frame'] += 1
    
    # Main window - full screen 320x240
    if begin_window_ex(ctx, "Home Assistant", Rect(0, 0, 320, 240), 
                       MU_OPT_NOCLOSE|MU_OPT_NORESIZE|MU_OPT_NOTITLE|MU_OPT_NOINTERACT):
        
        # Top navigation bar - screen selection
        layout_row(ctx, 4, [78, 78, 78, -1], 0)
        if button(ctx, "Home" if ui_state['current_screen'] == 'dashboard' else "Home"):
            ui_state['current_screen'] = 'dashboard'
        if button(ctx, "Climate" if ui_state['current_screen'] == 'climate' else "Climate"):
            ui_state['current_screen'] = 'climate'
        if button(ctx, "Lights" if ui_state['current_screen'] == 'lighting' else "Lights"):
            ui_state['current_screen'] = 'lighting'
        if button(ctx, "Security" if ui_state['current_screen'] == 'security' else "Security"):
            ui_state['current_screen'] = 'security'
        
        # Second navigation bar - more screens
        layout_row(ctx, 4, [78, 78, 78, -1], 0)
        if button(ctx, "Energy" if ui_state['current_screen'] == 'energy' else "Energy"):
            ui_state['current_screen'] = 'energy'
        if button(ctx, "Schedule" if ui_state['current_screen'] == 'calendar' else "Schedule"):
            ui_state['current_screen'] = 'calendar'
        if button(ctx, "Network" if ui_state['current_screen'] == 'network' else "Network"):
            ui_state['current_screen'] = 'network'
        if button(ctx, "Logs" if ui_state['current_screen'] == 'logs' else "Logs"):
            ui_state['current_screen'] = 'logs'
        
        # Render current screen
        if ui_state['current_screen'] == 'dashboard':
            render_dashboard(ctx)
        elif ui_state['current_screen'] == 'climate':
            render_climate(ctx)
        elif ui_state['current_screen'] == 'lighting':
            render_lighting(ctx)
        elif ui_state['current_screen'] == 'security':
            render_security(ctx)
        elif ui_state['current_screen'] == 'energy':
            render_energy(ctx)
        elif ui_state['current_screen'] == 'calendar':
            render_calendar(ctx)
        elif ui_state['current_screen'] == 'network':
            render_network(ctx)
        elif ui_state['current_screen'] == 'logs':
            render_logs(ctx)
        
        end_window(ctx)


def render_dashboard(ctx):
    """Main dashboard overview"""
    
    # Status header
    layout_row(ctx, 2, [160, -1], 0)
    label(ctx, f"Mode: {ui_state['home_mode']}")
    label(ctx, f"Time: {14 + (ui_state['frame'] // 60) % 10}:{35 + (ui_state['frame'] // 10) % 60:02d}")
    
    # Two column layout - left column
    layout_row(ctx, 2, [155, -1], 85)
    
    # Left panel - Climate summary
    begin_panel(ctx, "Climate")
    label(ctx, f"Indoor: {ui_state['temperature']:.1f}C")
    label(ctx, f"Outdoor: {ui_state['outdoor_temp']:.1f}C")
    label(ctx, f"Humidity: {ui_state['humidity']}%")
    layout_row(ctx, 1, [-1], 0)
    res, ui_state['temperature'] = slider(ctx, ui_state['temperature'], 18.0, 28.0)
    label(ctx, f"Target: {ui_state['temperature']:.1f}C")
    end_panel(ctx)
    
    # Right panel - Lighting summary
    begin_panel(ctx, "Lighting")
    label(ctx, f"Active: {ui_state['lights_on']}/{ui_state['total_lights']}")
    label(ctx, f"Power: {ui_state['lights_on'] * 0.05:.2f}kW")
    layout_row(ctx, 2, [70, -1], 0)
    if button(ctx, "All On"):
        ui_state['lights_on'] = ui_state['total_lights']
        for light in ui_state['lights']:
            ui_state['lights'][light]['on'] = True
    if button(ctx, "All Off"):
        ui_state['lights_on'] = 0
        for light in ui_state['lights']:
            ui_state['lights'][light]['on'] = False
    end_panel(ctx)
    
    # Second row - Security and Energy
    layout_row(ctx, 2, [155, -1], 85)
    
    # Security summary
    begin_panel(ctx, "Security")
    lock_status = "Locked" if ui_state['doors_locked'] else "Unlocked"
    label(ctx, f"Doors: {lock_status}")
    label(ctx, f"Windows: {ui_state['windows_open']} open")
    alarm_status = "Armed" if ui_state['alarm_armed'] else "Disarmed"
    label(ctx, f"Alarm: {alarm_status}")
    layout_row(ctx, 2, [70, -1], 0)
    if button(ctx, "Lock All"):
        ui_state['doors_locked'] = True
    if button(ctx, "Alarm" if not ui_state['alarm_armed'] else "Disarm"):
        ui_state['alarm_armed'] = not ui_state['alarm_armed']
    end_panel(ctx)
    
    # Energy summary
    begin_panel(ctx, "Energy")
    label(ctx, f"Usage: {ui_state['power_usage']:.2f}kW")
    label(ctx, f"Solar: {ui_state['solar_production']:.2f}kW")
    label(ctx, f"Grid: {ui_state['grid_import']:.2f}kW")
    label(ctx, f"Cost: ${ui_state['power_usage'] * 0.15:.2f}/hr")
    end_panel(ctx)
    
    # Quick status bar at bottom
    layout_row(ctx, 1, [-1], 0)
    
    # System status
    motion_detected = any(cam['motion'] for cam in ui_state['cameras'].values())
    status_msg = "MOTION DETECTED!" if motion_detected else "All systems normal"
    label(ctx, f"Status: {status_msg}")


def render_climate(ctx):
    """Climate control screen"""
    
    label(ctx, "=== CLIMATE CONTROL ===")
    
    # HVAC Master control
    layout_row(ctx, 3, [100, 100, -1], 0)
    res, ui_state['hvac_power'] = checkbox(ctx, "HVAC Power", ui_state['hvac_power'])
    label(ctx, f"Outdoor: {ui_state['outdoor_temp']:.1f}C")
    
    # Two column layout for zones
    zone_list = list(ui_state['climate_zones'].keys())
    
    for i in range(0, len(zone_list), 2):
        layout_row(ctx, 2, [155, -1], 75)
        
        # Left zone
        zone_name = zone_list[i]
        zone_data = ui_state['climate_zones'][zone_name]
        
        begin_panel(ctx, zone_name)
        label(ctx, f"Temp: {zone_data['temp']:.1f}C")
        label(ctx, f"Humid: {zone_data['humidity']}%")
        label(ctx, f"Mode: {zone_data['mode']}")
        layout_row(ctx, 1, [-1], 0)
        res, zone_data['target'] = slider(ctx, zone_data['target'], 15.0, 30.0)
        label(ctx, f"Target: {zone_data['target']:.1f}C")
        end_panel(ctx)
        
        # Right zone (if exists)
        if i + 1 < len(zone_list):
            zone_name = zone_list[i + 1]
            zone_data = ui_state['climate_zones'][zone_name]
            
            begin_panel(ctx, zone_name)
            label(ctx, f"Temp: {zone_data['temp']:.1f}C")
            label(ctx, f"Humid: {zone_data['humidity']}%")
            label(ctx, f"Mode: {zone_data['mode']}")
            layout_row(ctx, 1, [-1], 0)
            res, zone_data['target'] = slider(ctx, zone_data['target'], 15.0, 30.0)
            label(ctx, f"Target: {zone_data['target']:.1f}C")
            end_panel(ctx)


def render_lighting(ctx):
    """Lighting control screen"""
    
    label(ctx, "=== LIGHTING CONTROL ===")
    
    # Summary
    layout_row(ctx, 3, [100, 100, -1], 0)
    label(ctx, f"On: {ui_state['lights_on']}/{ui_state['total_lights']}")
    if button(ctx, "All On"):
        for light in ui_state['lights']:
            ui_state['lights'][light]['on'] = True
            ui_state['lights'][light]['brightness'] = 100
        ui_state['lights_on'] = len(ui_state['lights'])
    if button(ctx, "All Off"):
        for light in ui_state['lights']:
            ui_state['lights'][light]['on'] = False
            ui_state['lights'][light]['brightness'] = 0
        ui_state['lights_on'] = 0
    
    # Two column layout for lights
    light_list = list(ui_state['lights'].keys())
    
    for i in range(0, min(6, len(light_list)), 2):  # Show first 6 lights
        layout_row(ctx, 2, [155, -1], 60)
        
        # Left light
        light_name = light_list[i]
        light_data = ui_state['lights'][light_name]
        
        begin_panel(ctx, light_name)
        res, light_data['on'] = checkbox(ctx, "On", light_data['on'])
        if light_data['on']:
            label(ctx, f"Bright: {light_data['brightness']}%")
            layout_row(ctx, 1, [-1], 0)
            res, light_data['brightness'] = slider(ctx, light_data['brightness'], 0, 100)
        else:
            label(ctx, "OFF")
        end_panel(ctx)
        
        # Right light
        if i + 1 < len(light_list):
            light_name = light_list[i + 1]
            light_data = ui_state['lights'][light_name]
            
            begin_panel(ctx, light_name)
            res, light_data['on'] = checkbox(ctx, "On", light_data['on'])
            if light_data['on']:
                label(ctx, f"Bright: {light_data['brightness']}%")
                layout_row(ctx, 1, [-1], 0)
                res, light_data['brightness'] = slider(ctx, light_data['brightness'], 0, 100)
            else:
                label(ctx, "OFF")
            end_panel(ctx)
    
    # Update lights_on count
    ui_state['lights_on'] = sum(1 for light in ui_state['lights'].values() if light['on'])


def render_security(ctx):
    """Security monitoring screen"""
    
    label(ctx, "=== SECURITY SYSTEM ===")
    
    # Controls
    layout_row(ctx, 3, [100, 100, -1], 0)
    if button(ctx, "Arm" if not ui_state['alarm_armed'] else "Disarm"):
        ui_state['alarm_armed'] = not ui_state['alarm_armed']
    alarm_status = "ARMED" if ui_state['alarm_armed'] else "DISARMED"
    label(ctx, f"Alarm: {alarm_status}")
    
    # Cameras section
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "--- Cameras ---")
    
    # Two column camera list
    camera_list = list(ui_state['cameras'].keys())
    for i in range(0, len(camera_list), 2):
        layout_row(ctx, 2, [155, -1], 45)
        
        # Left camera
        cam_name = camera_list[i]
        cam_data = ui_state['cameras'][cam_name]
        
        begin_panel(ctx, cam_name)
        label(ctx, f"Status: {cam_data['status']}")
        motion_text = "MOTION!" if cam_data['motion'] else "Clear"
        label(ctx, f"Motion: {motion_text}")
        rec_text = "Recording" if cam_data['recording'] else "Idle"
        label(ctx, f"Rec: {rec_text}")
        end_panel(ctx)
        
        # Right camera
        if i + 1 < len(camera_list):
            cam_name = camera_list[i + 1]
            cam_data = ui_state['cameras'][cam_name]
            
            begin_panel(ctx, cam_name)
            label(ctx, f"Status: {cam_data['status']}")
            motion_text = "MOTION!" if cam_data['motion'] else "Clear"
            label(ctx, f"Motion: {motion_text}")
            rec_text = "Recording" if cam_data['recording'] else "Idle"
            label(ctx, f"Rec: {rec_text}")
            end_panel(ctx)
    
    # Sensors section
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "--- Sensors ---")
    
    # Show first 4 sensors in two columns
    sensor_list = list(ui_state['sensors'].keys())
    for i in range(0, min(4, len(sensor_list)), 2):
        layout_row(ctx, 2, [155, -1], 40)
        
        # Left sensor
        sens_name = sensor_list[i]
        sens_data = ui_state['sensors'][sens_name]
        
        begin_panel(ctx, sens_name)
        label(ctx, f"{sens_data['type']}: {sens_data['state']}")
        label(ctx, f"Battery: {sens_data['battery']}%")
        end_panel(ctx)
        
        # Right sensor
        if i + 1 < len(sensor_list):
            sens_name = sensor_list[i + 1]
            sens_data = ui_state['sensors'][sens_name]
            
            begin_panel(ctx, sens_name)
            label(ctx, f"{sens_data['type']}: {sens_data['state']}")
            label(ctx, f"Battery: {sens_data['battery']}%")
            end_panel(ctx)


def render_energy(ctx):
    """Energy monitoring screen with plots"""
    
    label(ctx, "=== ENERGY MONITOR ===")
    
    # Summary stats
    layout_row(ctx, 3, [100, 100, -1], 0)
    label(ctx, f"Usage: {ui_state['power_usage']:.2f}kW")
    label(ctx, f"Solar: {ui_state['solar_production']:.2f}kW")
    label(ctx, f"Grid: {ui_state['grid_import']:.2f}kW")
    
    # Energy usage plot
    layout_row(ctx, 1, [-1], 80)
    cv = canvas(ctx, 300, 70)
    
    # Draw plot background
    cv.rectangle(0, 0, 300, 70, (30, 30, 40, 255), filled=True)
    cv.text(5, 5, "Power Usage History (kW)", (200, 200, 200, 255))
    
    # Draw grid
    for i in range(0, 300, 30):
        cv.line(i, 20, i, 65, (60, 60, 80, 255))
    for i in range(20, 70, 10):
        cv.line(10, i, 290, i, (60, 60, 80, 255))
    
    # Draw energy history line
    history = ui_state['energy_history']
    x_step = 280 / len(history)
    for i in range(len(history) - 1):
        x1 = int(10 + i * x_step)
        y1 = int(65 - (history[i] / 3.0) * 45)
        x2 = int(10 + (i + 1) * x_step)
        y2 = int(65 - (history[i + 1] / 3.0) * 45)
        cv.line(x1, y1, x2, y2, (100, 255, 100, 255))
        cv.circle(x1, y1, 2, (100, 255, 100, 255), filled=True)
    
    # Update history with current value
    if ui_state['frame'] % 30 == 0:
        ui_state['energy_history'].append(ui_state['power_usage'])
        if len(ui_state['energy_history']) > 10:
            ui_state['energy_history'].pop(0)
    
    # Device power breakdown - two columns
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "--- Device Breakdown ---")
    
    device_list = list(ui_state['device_power'].keys())
    for i in range(0, len(device_list), 2):
        layout_row(ctx, 2, [155, -1], 0)
        
        # Left device
        device_name = device_list[i]
        power = ui_state['device_power'][device_name]
        label(ctx, f"{device_name}: {power:.2f}kW")
        
        # Right device
        if i + 1 < len(device_list):
            device_name = device_list[i + 1]
            power = ui_state['device_power'][device_name]
            label(ctx, f"{device_name}: {power:.2f}kW")
    
    # Cost estimate
    layout_row(ctx, 1, [-1], 0)
    daily_cost = ui_state['power_usage'] * 24 * 0.15
    label(ctx, f"Est. Daily Cost: ${daily_cost:.2f}")


def render_calendar(ctx):
    """Calendar and schedule screen"""
    
    label(ctx, "=== SCHEDULE & EVENTS ===")
    
    # Controls
    layout_row(ctx, 2, [155, -1], 0)
    res, ui_state['automations_enabled'] = checkbox(ctx, "Automations", ui_state['automations_enabled'])
    label(ctx, f"Events: {len(ui_state['events'])}")
    
    # Today's events - two columns
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "--- Today's Schedule ---")
    
    events = ui_state['events']
    for i in range(0, len(events), 2):
        layout_row(ctx, 2, [155, -1], 35)
        
        # Left event
        event = events[i]
        begin_panel(ctx, f"Event{i}")
        label(ctx, f"{event['time']} - {event['title']}")
        label(ctx, f"Type: {event['type']}")
        end_panel(ctx)
        
        # Right event
        if i + 1 < len(events):
            event = events[i + 1]
            begin_panel(ctx, f"Event{i+1}")
            label(ctx, f"{event['time']} - {event['title']}")
            label(ctx, f"Type: {event['type']}")
            end_panel(ctx)
    
    # Quick actions
    layout_row(ctx, 3, [100, 100, -1], 0)
    if button(ctx, "Morning"):
        ui_state['home_mode'] = 'Home'
        ui_state['lights_on'] = 8
    if button(ctx, "Evening"):
        ui_state['home_mode'] = 'Home'
        ui_state['lights_on'] = 12
    if button(ctx, "Night"):
        ui_state['home_mode'] = 'Night'
        ui_state['lights_on'] = 2


def render_network(ctx):
    """Network device map and status"""
    
    label(ctx, "=== NETWORK MAP ===")
    
    # Network canvas - topology visualization
    layout_row(ctx, 1, [-1], 90)
    cv = canvas(ctx, 300, 80)
    
    # Background
    cv.rectangle(0, 0, 300, 80, (20, 25, 35, 255), filled=True)
    cv.text(5, 5, "Network Topology", (200, 200, 200, 255))
    
    # Draw router at center
    cv.circle(150, 40, 8, (100, 150, 255, 255), filled=True)
    cv.text(135, 52, "Router", (255, 255, 255, 255))
    
    # Draw connected devices in a circle
    device_count = min(8, len(ui_state['network_devices']))
    for i, (dev_name, dev_data) in enumerate(list(ui_state['network_devices'].items())[:8]):
        angle = (i / device_count) * 2 * math.pi
        x = int(150 + 55 * math.cos(angle))
        y = int(40 + 25 * math.sin(angle))
        
        # Device status color
        if dev_data['status'] == 'Online':
            color = (100, 255, 100, 255)
        else:
            color = (255, 100, 100, 255)
        
        # Draw connection line
        cv.line(150, 40, x, y, (80, 80, 100, 255))
        
        # Draw device node
        cv.circle(x, y, 4, color, filled=True)
    
    # Device list - two columns
    layout_row(ctx, 1, [-1], 0)
    label(ctx, "--- Connected Devices ---")
    
    device_list = list(ui_state['network_devices'].keys())
    for i in range(0, min(8, len(device_list)), 2):
        layout_row(ctx, 2, [155, -1], 40)
        
        # Left device
        dev_name = device_list[i]
        dev_data = ui_state['network_devices'][dev_name]
        
        begin_panel(ctx, dev_name)
        label(ctx, f"{dev_data['status']}")
        label(ctx, f"Signal: {dev_data['signal']}%")
        label(ctx, f"IP: {dev_data['ip']}")
        end_panel(ctx)
        
        # Right device
        if i + 1 < len(device_list):
            dev_name = device_list[i + 1]
            dev_data = ui_state['network_devices'][dev_name]
            
            begin_panel(ctx, dev_name)
            label(ctx, f"{dev_data['status']}")
            label(ctx, f"Signal: {dev_data['signal']}%")
            label(ctx, f"IP: {dev_data['ip']}")
            end_panel(ctx)


def render_logs(ctx):
    """System logs and events"""
    
    label(ctx, "=== SYSTEM LOGS ===")
    
    # Log controls
    layout_row(ctx, 3, [80, 80, -1], 0)
    if button(ctx, "Refresh"):
        pass  # Refresh logs
    if button(ctx, "Clear"):
        ui_state['system_logs'].clear()
        ui_state['system_logs'].append({'time': '00:00', 'type': 'INFO', 'msg': 'Logs cleared'})
    label(ctx, f"Entries: {len(ui_state['system_logs'])}")
    
    # Log filter/legend
    layout_row(ctx, 3, [100, 100, -1], 0)
    label(ctx, "INFO: Normal")
    label(ctx, "WARN: Warning")
    label(ctx, "ERROR: Error")
    
    # Log panel - scrollable
    layout_row(ctx, 1, [-1], 145)
    begin_panel(ctx, "LogPanel")
    
    # Show logs in reverse order (newest first)
    for log in reversed(ui_state['system_logs'][-10:]):
        # Color based on type
        log_text = f"[{log['time']}] {log['type']}: {log['msg']}"
        label(ctx, log_text)
    
    end_panel(ctx)
    
    # Add test log button
    layout_row(ctx, 1, [-1], 0)
    if button(ctx, "Add Test Log Entry"):
        new_time = f"{14 + ui_state['frame'] // 3600}:{(ui_state['frame'] // 60) % 60:02d}"
        ui_state['system_logs'].append({
            'time': new_time,
            'type': 'INFO',
            'msg': f'Test event #{ui_state["frame"]}'
        })
        if len(ui_state['system_logs']) > 20:
            ui_state['system_logs'].pop(0)
