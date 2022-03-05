import yaml
import os

class Config:
    def __init__(self, path) -> None:
        self.filepath = path
        # Attributes as follows
        self.version = "0.1"
        self.log_level = "DEBUG"
        self.hotword = ""
    
    def read(self):
        if os.path.exists(self.filepath) == False:
            print("No config file found!")
            exit()
        with open(self.filepath, "r") as f:
            yaml_file = yaml.safe_load(f)
            try:
                self.version = yaml_file["version"]
                self.hotword = yaml_file["hotword"]
                self.log_level = yaml_file["log_level"]
            except AttributeError:
                print("Corrupt config file!")
                exit()
