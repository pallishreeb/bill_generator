from PIL import Image, ImageDraw
import os

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def create_app_icon(size=256):
    # Create a new image with a transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a blue circle
    circle_color = (41, 128, 185)  # Professional blue
    padding = size // 8
    draw.ellipse([padding, padding, size - padding, size - padding], fill=circle_color)
    
    # Add "INV" text in white
    try:
        from PIL import ImageFont
        font = ImageFont.truetype("Arial", size=size//3)
    except:
        font = ImageFont.load_default()
    
    text = "INV"
    text_color = (255, 255, 255)  # White
    
    # Get text size and center it
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_position = ((size - text_width) // 2, (size - text_height) // 2)
    
    # Draw the text
    draw.text(text_position, text, font=font, fill=text_color)
    
    return img

def create_sun_icon(size=32):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw sun circle
    sun_color = (243, 156, 18)  # Orange
    center = size // 2
    radius = size // 4
    draw.ellipse([center - radius, center - radius, 
                  center + radius, center + radius], 
                 fill=sun_color)
    
    # Draw rays
    ray_length = size // 4
    ray_positions = [
        (center, 0), (size, center),  # Top, Right
        (center, size), (0, center),  # Bottom, Left
        (size * 3//4, size * 1//4),   # Top-Right
        (size * 3//4, size * 3//4),   # Bottom-Right
        (size * 1//4, size * 3//4),   # Bottom-Left
        (size * 1//4, size * 1//4)    # Top-Left
    ]
    
    for x, y in ray_positions:
        draw.ellipse([x - 2, y - 2, x + 2, y + 2], fill=sun_color)
    
    return img

def create_moon_icon(size=32):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw full circle for the moon
    moon_color = (241, 196, 15)  # Yellow
    padding = size // 8
    draw.ellipse([padding, padding, size - padding, size - padding], 
                 fill=moon_color)
    
    # Draw slightly larger circle offset to create crescent
    overlay_color = (0, 0, 0, 0)  # Transparent
    offset = size // 4
    draw.ellipse([padding + offset, padding, 
                  size - padding + offset, size - padding], 
                 fill=overlay_color)
    
    return img

def main():
    # Create icons directory
    create_directory('icons')
    
    # Generate app icon
    app_icon = create_app_icon()
    app_icon.save('icons/app_icon.png')
    app_icon.save('icons/app.ico')
    
    # Generate theme icons
    sun_icon = create_sun_icon()
    moon_icon = create_moon_icon()
    sun_icon.save('icons/sun.png')
    moon_icon.save('icons/moon.png')
    
    print("Icons generated successfully!")

if __name__ == "__main__":
    main() 