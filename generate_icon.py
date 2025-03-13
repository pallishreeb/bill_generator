from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    # Create a 256x256 image with a white background
    size = 256
    image = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw a blue circle
    margin = 10
    draw.ellipse([margin, margin, size-margin, size-margin], 
                 fill=(41, 128, 185, 255), outline=(52, 152, 219, 255), width=5)
    
    # Draw "INV" text
    try:
        font = ImageFont.truetype("Arial", 100)
    except:
        font = ImageFont.load_default()
    
    text = "IMS"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    # Draw text in white
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
    
    # Create icons directory if it doesn't exist
    if not os.path.exists('icons'):
        os.makedirs('icons')
    
    # Save as PNG first
    image.save('icons/app_icon.png')
    
    # Convert to ICO for Windows
    image.save('icons/app.ico', format='ICO')
    
    print("Icons generated successfully in the 'icons' directory!")

if __name__ == "__main__":
    create_icon() 