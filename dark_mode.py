#!/usr/bin/env python3
"""
Script to add dark mode CSS and JS to all remaining HTML templates
"""

import os
import re

def add_dark_mode_to_template(template_path):
    """Add dark mode CSS and JS to a template file"""
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if already has dark mode CSS
        if 'dark-mode.css' in content:
            print(f"✓ {template_path} already has dark mode")
            return
        
        # Add CSS after title tag
        css_link = '    \n    <!-- Dark Mode CSS -->\n    <link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/dark-mode.css\') }}">\n    '
        
        if '<title>' in content and '</title>' in content:
            content = re.sub(
                r'(</title>)',
                r'\1' + css_link,
                content,
                count=1
            )
        
        # Add JS before closing body tag
        js_script = '\n    <!-- Dark Mode JavaScript -->\n    <script src="{{ url_for(\'static\', filename=\'js/dark-mode.js\') }}"></script>\n'
        
        if '</body>' in content:
            content = re.sub(
                r'(</body>)',
                js_script + r'\1',
                content,
                count=1
            )
        
        # Write back to file
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Updated {template_path}")
        
    except Exception as e:
        print(f"✗ Error updating {template_path}: {e}")

def main():
    templates_dir = 'templates'
    
    # Skip templates we've already updated
    skip_templates = {'dashboard.html', 'login.html', 'rooms.html'}
    
    if not os.path.exists(templates_dir):
        print("Templates directory not found!")
        return
    
    print("Adding dark mode to remaining templates...")
    
    for filename in os.listdir(templates_dir):
        if filename.endswith('.html') and filename not in skip_templates:
            template_path = os.path.join(templates_dir, filename)
            add_dark_mode_to_template(template_path)
    
    print("\n🌙 Dark mode implementation completed!")
    print("\nFeatures added:")
    print("• CSS variables for light/dark themes")
    print("• Floating toggle button (top-right)")
    print("• Persistent theme preference (localStorage)")
    print("• System theme detection")
    print("• Smooth transitions")
    print("• Bootstrap compatibility")
    print("• Keyboard accessibility")
    
    print("\nTo test:")
    print("1. Run your Flask app: python app.py")
    print("2. Look for the dark mode toggle button in the top-right corner")
    print("3. Click to switch between light and dark modes")

if __name__ == "__main__":
    main()
