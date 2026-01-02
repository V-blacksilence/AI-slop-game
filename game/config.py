import json

class Config:
    def __init__(self):
        self.defaults = {
            'auto_save': True,
            'show_hitboxes': False,
            'music_volume': 0.7,
            'sfx_volume': 1.0,
            'screen_shake': True
        }
        self.settings = self.defaults.copy()
        self.load()
    
    def load(self):
        try:
            with open('config.json', 'r') as f:
                self.settings.update(json.load(f))
        except:
            self.save()  # Create default config
    
    def save(self):
        try:
            with open('config.json', 'w') as f:
                json.dump(self.settings, f, indent=4)
        except:
            pass