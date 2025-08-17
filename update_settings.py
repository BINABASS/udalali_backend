import re

# Path to the settings file
settings_path = '/home/binos/Documents/abdulWAHID/both_front_back/udalali_back/udigi_udaga_backend/settings.py'

# Read the current settings
with open(settings_path, 'r') as f:
    content = f.read()

# Pattern to find and update INSTALLED_APPS
pattern = r'(INSTALLED_APPS = \[.*?]\s*])'
replacement = r'\1\n    "users.apps.UsersConfig",'

# Make the replacement
updated_content = re.sub(
    pattern,
    replacement,
    content,
    flags=re.DOTALL
)

# Write the updated content back to the file
with open(settings_path, 'w') as f:
    f.write(updated_content)

print("Successfully updated INSTALLED_APPS in settings.py")
