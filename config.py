import os

class Config:
    """Configuration settings for the Discord bot"""
    
    # Bot token from environment variable
    TOKEN = os.getenv('DISCORD_TOKEN', 'your_bot_token_here')
    
    # Bot owner ID (hardcoded for security) - Replace with your Discord user ID
    OWNER_ID = 1342772842424438806  # Replace with your actual Discord user ID
    
    # Command prefix
    PREFIX = '!'
    
    # Bot settings
    BOT_NAME = "Multi-Purpose Bot"
    BOT_VERSION = "1.0.0"
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if cls.TOKEN == 'your_bot_token_here':
            raise ValueError("Please set the DISCORD_TOKEN environment variable")
        
        if cls.OWNER_ID == 123456789012345678:
            print("WARNING: Please change the OWNER_ID in config.py to your Discord user ID")
        
        return True
